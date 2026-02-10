from django.db import transaction
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from accounts.permissions import IsApplicantOrAdmin
from .models import Course, LessonBalance, Payment, ClientRequest
from .applicant_serializers import (
    ApplicantCourseSerializer,
    ApplicantBalanceSerializer,
    ApplicantPaymentCreateSerializer,
    ApplicantPaymentSerializer,
    ApplicantClientRequestCreateSerializer,
)


class PublicCoursesListAPI(generics.ListAPIView):
    """
    Публичный список курсов (для главной страницы).
    GET /api/applicant/courses/public/
    """
    permission_classes = [AllowAny]
    serializer_class = ApplicantCourseSerializer

    def get_queryset(self):
        return Course.objects.all().order_by("id")


class ApplicantCoursesListAPI(generics.ListAPIView):
    """
    Просмотр возможных курсов (только активные).
    GET /api/applicant/courses/
    """
    permission_classes = [IsAuthenticated, IsApplicantOrAdmin]
    serializer_class = ApplicantCourseSerializer

    def get_queryset(self):
        return Course.objects.all().order_by("id")


class ApplicantBalanceAPI(APIView):
    """
    Информация о балансе абитуриента.
    GET /api/applicant/balance/
    """
    permission_classes = [IsAuthenticated, IsApplicantOrAdmin]

    def get(self, request):
        bal, _ = LessonBalance.objects.get_or_create(student=request.user)
        ser = ApplicantBalanceSerializer(bal)
        return Response(ser.data)


class ApplicantPaymentsListAPI(generics.ListAPIView):
    """
    История оплат абитуриента.
    GET /api/applicant/payments/
    """
    permission_classes = [IsAuthenticated, IsApplicantOrAdmin]
    serializer_class = ApplicantPaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(student=self.request.user).order_by("-paid_at")


class ApplicantCreatePaymentAPI(APIView):
    """
    Создание записи оплаты абитуриентом.
    В реальной жизни здесь была бы интеграция с платёжкой,
    но по ТЗ достаточно зафиксировать факт оплаты:
      - создаём Payment с confirmed=False
      - менеджер/админ потом подтверждает и начисляет занятия
    POST /api/applicant/payments/create/
    Body: {"course_id": 1, "amount": "5000.00", "package_name": "8 занятий"}
    """
    permission_classes = [IsAuthenticated, IsApplicantOrAdmin]

    @transaction.atomic
    def post(self, request):
        ser = ApplicantPaymentCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        course_id = ser.validated_data["course_id"]
        amount = ser.validated_data["amount"]
        package_name = ser.validated_data.get("package_name") or ""

        payment = Payment.objects.create(
            student=request.user,
            amount=amount,
            package_name=package_name or f"Оплата курса #{course_id}",
            confirmed=False,  # подтверждает менеджер/админ
        )

        return Response(ApplicantPaymentSerializer(payment).data, status=201)


# ===== ОБРАЩЕНИЯ К МЕНЕДЖЕРУ =====

class ApplicantCreateClientRequestAPI(APIView):
    """
    Создание обращения к менеджеру абитуриентом.
    POST /api/applicant/requests/create/
    Body: {"comment": "Текст комментария (необязательно)"}
    """
    permission_classes = [IsAuthenticated, IsApplicantOrAdmin]

    def post(self, request):
        ser = ApplicantClientRequestCreateSerializer(data=request.data, context={'request': request})
        ser.is_valid(raise_exception=True)
        request_obj = ser.save()
        return Response({
            "id": request_obj.id,
            "comment": request_obj.comment,
            "status": request_obj.status,
            "created_at": request_obj.created_at,
        }, status=201)
