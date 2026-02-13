import base64
import json
import logging
import uuid
from decimal import Decimal
from urllib import error, request as urllib_request

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import JsonResponse
from rest_framework import serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AuditLog, LessonBalance, Payment

logger = logging.getLogger(__name__)
User = get_user_model()


class YooKassaCreatePaymentSerializer(serializers.Serializer):
    lessons_count = serializers.IntegerField(min_value=1, max_value=20)


def _get_yookassa_auth_header() -> str:
    shop_id = getattr(settings, "YOOKASSA_SHOP_ID", "")
    secret_key = getattr(settings, "YOOKASSA_SECRET_KEY", "")
    if not shop_id or not secret_key:
        raise ValueError("YOOKASSA credentials are not configured")

    auth_string = f"{shop_id}:{secret_key}".encode("utf-8")
    encoded = base64.b64encode(auth_string).decode("utf-8")
    return f"Basic {encoded}"


def _yookassa_request(method: str, path: str, payload=None, idempotence_key: str = ""):
    base_url = getattr(settings, "YOOKASSA_API_URL", "https://api.yookassa.ru/v3").rstrip("/")
    url = f"{base_url}/{path.lstrip('/')}"

    headers = {
        "Authorization": _get_yookassa_auth_header(),
        "Content-Type": "application/json",
    }
    if idempotence_key:
        headers["Idempotence-Key"] = idempotence_key

    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib_request.Request(url=url, data=data, headers=headers, method=method)

    try:
        with urllib_request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else {}
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8") if exc.fp else ""
        try:
            body = json.loads(raw) if raw else {"detail": "empty error response"}
        except json.JSONDecodeError:
            body = {"detail": raw or "unknown yookassa error"}
        return exc.code, body


def _append_query_param(url: str, key: str, value: str) -> str:
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}{key}={value}"


class YooKassaCreatePaymentAPI(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user

        serializer = YooKassaCreatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        lessons_count = serializer.validated_data["lessons_count"]
        lesson_price = Decimal(str(getattr(settings, "LESSON_PRICE_RUB", 1000)))
        amount = lesson_price * Decimal(lessons_count)
        amount_value = f"{amount:.2f}"

        payment = Payment.objects.create(
            student=user,
            amount=amount,
            package_name=f"{lessons_count} занятий",
            lessons_count=lessons_count,
            confirmed=False,
            yookassa_status="pending",
        )

        idempotence_key = str(uuid.uuid4())
        success_url = getattr(settings, "YOOKASSA_RETURN_URL_SUCCESS", "https://flare-school.ru/payment/success")
        return_url = _append_query_param(success_url, "local_payment_id", str(payment.id))

        vat_code = int(getattr(settings, "YOOKASSA_VAT_CODE", 1))
        customer_email = (getattr(user, "email", "") or "").strip()
        customer_phone = (getattr(user, "phone", "") or "").strip()

        customer = {}
        if customer_email:
            customer["email"] = customer_email
        if customer_phone:
            customer["phone"] = customer_phone

        if not customer:
            payment.delete()
            return Response({"detail": "user must have email or phone for 54-ФЗ receipt"}, status=400)

        payload = {
            "amount": {
                "value": amount_value,
                "currency": "RUB",
            },
            "capture": True,
            "confirmation": {
                "type": "redirect",
                "return_url": return_url,
            },
            "description": f"Оплата {lessons_count} занятий в F.L.A.R.E.",
            "metadata": {
                "local_payment_id": str(payment.id),
                "student_id": str(user.id),
                "lessons_count": str(lessons_count),
            },
            "receipt": {
                "customer": customer,
                "items": [
                    {
                        "description": "Индивидуальные занятия",
                        "quantity": str(lessons_count),
                        "amount": {
                            "value": f"{lesson_price:.2f}",
                            "currency": "RUB",
                        },
                        "vat_code": vat_code,
                        "payment_mode": "full_prepayment",
                        "payment_subject": "service",
                    }
                ],
            },
        }

        try:
            status_code, yk_response = _yookassa_request(
                method="POST",
                path="payments",
                payload=payload,
                idempotence_key=idempotence_key,
            )
        except ValueError as exc:
            payment.delete()
            return Response({"detail": str(exc)}, status=500)

        if status_code >= 400:
            payment.delete()
            logger.error("YooKassa create payment failed: status=%s body=%s", status_code, yk_response)
            return Response({"detail": "failed to create payment", "provider": yk_response}, status=502)

        payment.yookassa_payment_id = yk_response.get("id", "")
        payment.yookassa_status = yk_response.get("status", "")
        payment.idempotence_key = idempotence_key
        payment.save(update_fields=["yookassa_payment_id", "yookassa_status", "idempotence_key"])

        confirmation_url = (yk_response.get("confirmation") or {}).get("confirmation_url")
        if not confirmation_url:
            return Response({"detail": "missing confirmation_url from provider"}, status=502)

        return Response(
            {
                "local_payment_id": payment.id,
                "payment_id": payment.yookassa_payment_id,
                "status": payment.yookassa_status,
                "confirmation_url": confirmation_url,
            },
            status=201,
        )


class YooKassaPaymentStatusAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            payment = Payment.objects.select_related("student").get(pk=pk)
        except Payment.DoesNotExist:
            return Response({"detail": "payment not found"}, status=404)

        user = request.user
        privileged_roles = (User.Roles.ADMIN, User.Roles.MANAGER)
        is_owner = payment.student_id == user.id
        is_privileged = getattr(user, "role", "") in privileged_roles or user.is_superuser

        if not is_owner and not is_privileged:
            return Response({"detail": "forbidden"}, status=403)

        return Response(
            {
                "id": payment.id,
                "confirmed": payment.confirmed,
                "status": payment.yookassa_status,
                "amount": str(payment.amount),
                "lessons_count": payment.lessons_count,
            }
        )


class YooKassaWebhookAPI(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        event = request.data.get("event")
        payment_object = request.data.get("object") or {}
        yookassa_payment_id = payment_object.get("id")

        if not yookassa_payment_id:
            return JsonResponse({"detail": "ok"}, status=200)

        try:
            status_code, provider_payment = _yookassa_request("GET", f"payments/{yookassa_payment_id}")
        except ValueError as exc:
            logger.error("YooKassa webhook config error: %s", exc)
            return JsonResponse({"detail": "ok"}, status=200)
        if status_code >= 400:
            logger.error(
                "YooKassa webhook verify failed: status=%s body=%s",
                status_code,
                provider_payment,
            )
            return JsonResponse({"detail": "ok"}, status=200)

        provider_status = provider_payment.get("status", "")

        try:
            payment = Payment.objects.select_for_update().select_related("student").get(
                yookassa_payment_id=yookassa_payment_id
            )
        except Payment.DoesNotExist:
            logger.warning("Webhook for unknown yookassa_payment_id=%s", yookassa_payment_id)
            return JsonResponse({"detail": "ok"}, status=200)

        payment.yookassa_status = provider_status
        payment.save(update_fields=["yookassa_status"])

        if provider_status != "succeeded":
            return JsonResponse({"detail": "ok"}, status=200)

        if payment.confirmed:
            return JsonResponse({"detail": "ok"}, status=200)

        lessons_to_add = payment.lessons_count
        if lessons_to_add <= 0:
            lesson_price = Decimal(str(getattr(settings, "LESSON_PRICE_RUB", 1000)))
            lessons_to_add = int(payment.amount / lesson_price)

        lb, _ = LessonBalance.objects.select_for_update().get_or_create(student=payment.student)
        lb.lessons_available += max(0, lessons_to_add)
        lb.save()

        old_role = payment.student.role
        role_changed = False
        if payment.student.role == User.Roles.APPLICANT and lessons_to_add > 0:
            payment.student.role = User.Roles.STUDENT
            payment.student.save(update_fields=["role"])
            role_changed = True

        payment.confirmed = True
        payment.save(update_fields=["confirmed"])

        AuditLog.objects.create(
            actor=None,
            action="YOOKASSA_PAYMENT_SUCCEEDED",
            meta={
                "event": event,
                "payment_id": payment.id,
                "yookassa_payment_id": yookassa_payment_id,
                "student": payment.student_id,
                "lessons_added": lessons_to_add,
                "old_role": old_role,
                "new_role": payment.student.role,
                "role_changed": role_changed,
            },
        )

        return JsonResponse({"detail": "ok"}, status=200)
