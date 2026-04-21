from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from .lesson_balance_service import (
    apply_lesson_status_transition,
    debit_lesson_balance,
    release_lesson_reserve,
    reserve_lesson_slot,
)
from .models import AuditLog, Lesson, LessonBalance, Payment, PaymentSettings
from .payment_api_views import _finalize_successful_payment, sync_recent_pending_yookassa_payments


User = get_user_model()


class BaseBusinessLogicTestCase(TestCase):
    password = "testpass123"

    def setUp(self):
        self.client = APIClient()

    def create_user(self, email, role, **extra):
        user = User.objects.create_user(
            username=email,
            email=email,
            password=self.password,
            role=role,
            **extra,
        )
        return user

    def create_lesson(self, student, teacher=None, **extra):
        defaults = {
            "student": student,
            "teacher": teacher,
            "scheduled_at": timezone.now() + timezone.timedelta(days=1),
            "status": Lesson.STATUS_PLANNED,
        }
        defaults.update(extra)
        return Lesson.objects.create(**defaults)


class LessonBalanceServiceTests(BaseBusinessLogicTestCase):
    def setUp(self):
        super().setUp()
        self.student = self.create_user("student@example.com", User.Roles.STUDENT)
        self.teacher = self.create_user("teacher@example.com", User.Roles.TEACHER)
        self.balance = LessonBalance.objects.create(
            student=self.student,
            lessons_available=3,
            lessons_reserved=0,
        )

    def test_reserve_lesson_slot_marks_lesson_and_balance(self):
        lesson = self.create_lesson(self.student, self.teacher)

        reserve_lesson_slot(lesson)

        lesson.refresh_from_db()
        self.balance.refresh_from_db()
        self.assertTrue(lesson.reserved_from_balance)
        self.assertEqual(self.balance.lessons_reserved, 1)
        self.assertEqual(self.balance.lessons_available, 3)

    def test_reserve_lesson_slot_fails_when_no_free_balance(self):
        self.balance.lessons_reserved = 3
        self.balance.save(update_fields=["lessons_reserved"])
        lesson = self.create_lesson(self.student, self.teacher)

        with self.assertRaises(ValidationError):
            reserve_lesson_slot(lesson)

    def test_debit_reserved_lesson_consumes_reserve_and_balance(self):
        lesson = self.create_lesson(self.student, self.teacher)
        reserve_lesson_slot(lesson)

        debit_lesson_balance(lesson)

        lesson.refresh_from_db()
        self.balance.refresh_from_db()
        self.assertTrue(lesson.debited_from_balance)
        self.assertFalse(lesson.reserved_from_balance)
        self.assertEqual(self.balance.lessons_available, 2)
        self.assertEqual(self.balance.lessons_reserved, 0)

    def test_status_transition_planned_done_cancelled_refunds_correctly(self):
        lesson = self.create_lesson(self.student, self.teacher)
        reserve_lesson_slot(lesson)

        apply_lesson_status_transition(lesson, Lesson.STATUS_PLANNED, Lesson.STATUS_DONE)
        lesson.refresh_from_db()
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.lessons_available, 2)
        self.assertEqual(self.balance.lessons_reserved, 0)
        self.assertTrue(lesson.debited_from_balance)

        apply_lesson_status_transition(lesson, Lesson.STATUS_DONE, Lesson.STATUS_CANCELLED)
        lesson.refresh_from_db()
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.lessons_available, 3)
        self.assertEqual(self.balance.lessons_reserved, 0)
        self.assertFalse(lesson.debited_from_balance)

    def test_status_transition_done_back_to_planned_re_reserves_slot(self):
        lesson = self.create_lesson(self.student, self.teacher)
        reserve_lesson_slot(lesson)
        apply_lesson_status_transition(lesson, Lesson.STATUS_PLANNED, Lesson.STATUS_DONE)

        apply_lesson_status_transition(lesson, Lesson.STATUS_DONE, Lesson.STATUS_PLANNED)

        lesson.refresh_from_db()
        self.balance.refresh_from_db()
        self.assertFalse(lesson.debited_from_balance)
        self.assertTrue(lesson.reserved_from_balance)
        self.assertEqual(self.balance.lessons_available, 3)
        self.assertEqual(self.balance.lessons_reserved, 1)

    def test_trial_lesson_does_not_change_balance(self):
        lesson = self.create_lesson(self.student, self.teacher, is_trial=True)

        reserve_lesson_slot(lesson)
        debit_lesson_balance(lesson)
        release_lesson_reserve(lesson)
        apply_lesson_status_transition(lesson, Lesson.STATUS_PLANNED, Lesson.STATUS_DONE)

        lesson.refresh_from_db()
        self.balance.refresh_from_db()
        self.assertFalse(lesson.reserved_from_balance)
        self.assertFalse(lesson.debited_from_balance)
        self.assertEqual(self.balance.lessons_available, 3)
        self.assertEqual(self.balance.lessons_reserved, 0)


class PaymentBusinessLogicTests(BaseBusinessLogicTestCase):
    def setUp(self):
        super().setUp()
        PaymentSettings.objects.create(singleton_key=1, lesson_price_rub=1200)
        self.applicant = self.create_user(
            "applicant@example.com",
            User.Roles.APPLICANT,
            phone="+79991234567",
        )
        self.manager = self.create_user("manager@example.com", User.Roles.MANAGER)

    def test_finalize_successful_payment_adds_balance_and_promotes_role(self):
        payment = Payment.objects.create(
            student=self.applicant,
            amount=Decimal("3600.00"),
            lessons_count=3,
            confirmed=False,
            yookassa_payment_id="yk-1",
        )

        _finalize_successful_payment(payment.id)

        payment.refresh_from_db()
        self.applicant.refresh_from_db()
        balance = LessonBalance.objects.get(student=self.applicant)
        self.assertTrue(payment.confirmed)
        self.assertEqual(balance.lessons_available, 3)
        self.assertEqual(self.applicant.role, User.Roles.STUDENT)
        self.assertTrue(AuditLog.objects.filter(action="YOOKASSA_PAYMENT_SUCCEEDED").exists())

    def test_finalize_successful_payment_is_idempotent(self):
        payment = Payment.objects.create(
            student=self.applicant,
            amount=Decimal("2400.00"),
            lessons_count=2,
            confirmed=False,
            yookassa_payment_id="yk-2",
        )

        _finalize_successful_payment(payment.id)
        _finalize_successful_payment(payment.id)

        balance = LessonBalance.objects.get(student=self.applicant)
        self.assertEqual(balance.lessons_available, 2)
        self.assertEqual(
            AuditLog.objects.filter(action="YOOKASSA_PAYMENT_SUCCEEDED", meta__payment_id=payment.id).count(),
            1,
        )

    def test_manager_payment_confirmation_is_disabled(self):
        payment = Payment.objects.create(
            student=self.applicant,
            amount=Decimal("1000.00"),
            confirmed=False,
        )
        self.client.force_authenticate(self.manager)

        response = self.client.post(
            f"/api/manager/payments/{payment.id}/confirm/",
            {"lessons_to_add": 4},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        payment.refresh_from_db()
        self.assertFalse(payment.confirmed)
        self.assertFalse(AuditLog.objects.filter(action="MANAGER_CONFIRM_PAYMENT").exists())

    def test_manager_balance_delta_promotes_applicant_when_positive(self):
        self.client.force_authenticate(self.manager)

        response = self.client.patch(
            f"/api/manager/students/{self.applicant.id}/balance/update/",
            {"delta": 2},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.applicant.refresh_from_db()
        balance = LessonBalance.objects.get(student=self.applicant)
        self.assertEqual(balance.lessons_available, 2)
        self.assertEqual(self.applicant.role, User.Roles.STUDENT)
        self.assertTrue(AuditLog.objects.filter(action="MANAGER_UPDATE_BALANCE").exists())

    @patch("sk.payment_api_views._yookassa_request")
    def test_sync_recent_pending_yookassa_payments_confirms_successful_entries(self, mock_request):
        second_user = self.create_user(
            "another-applicant@example.com",
            User.Roles.APPLICANT,
            phone="+79990000000",
        )
        first_payment = Payment.objects.create(
            student=self.applicant,
            amount=Decimal("1200.00"),
            lessons_count=1,
            confirmed=False,
            yookassa_payment_id="yk-batch-1",
            yookassa_status="pending",
        )
        second_payment = Payment.objects.create(
            student=second_user,
            amount=Decimal("2400.00"),
            lessons_count=2,
            confirmed=False,
            yookassa_payment_id="yk-batch-2",
            yookassa_status="pending",
        )
        mock_request.return_value = (200, {"status": "succeeded"})

        stats = sync_recent_pending_yookassa_payments(limit_per_user=5, max_age_hours=48)

        self.assertEqual(stats["checked"], 2)
        self.assertEqual(stats["confirmed"], 2)
        first_payment.refresh_from_db()
        second_payment.refresh_from_db()
        self.assertTrue(first_payment.confirmed)
        self.assertTrue(second_payment.confirmed)


@override_settings(
    YOOKASSA_SHOP_ID="shop-id",
    YOOKASSA_SECRET_KEY="secret-key",
    YOOKASSA_RETURN_URL_SUCCESS="https://example.com/payment/success",
)
class PaymentApiTests(BaseBusinessLogicTestCase):
    def setUp(self):
        super().setUp()
        PaymentSettings.objects.create(singleton_key=1, lesson_price_rub=1500)
        self.student = self.create_user(
            "student-pay@example.com",
            User.Roles.STUDENT,
            phone="+79991234567",
        )
        self.manager = self.create_user("manager-pay@example.com", User.Roles.MANAGER)
        self.applicant = self.create_user(
            "applicant-pay@example.com",
            User.Roles.APPLICANT,
            phone="+79991112233",
        )

    @patch("sk.payment_api_views._yookassa_request")
    def test_create_yookassa_payment_persists_pending_payment(self, mock_request):
        mock_request.return_value = (
            200,
            {
                "id": "yk-payment-id",
                "status": "pending",
                "confirmation": {"confirmation_url": "https://pay.example/redirect"},
            },
        )
        self.client.force_authenticate(self.student)

        response = self.client.post("/api/payments/create/", {"lessons_count": 2}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        payment = Payment.objects.get(student=self.student)
        self.assertEqual(payment.amount, Decimal("3000.00"))
        self.assertEqual(payment.lessons_count, 2)
        self.assertEqual(payment.yookassa_payment_id, "yk-payment-id")
        self.assertEqual(response.data["confirmation_url"], "https://pay.example/redirect")

    def test_create_yookassa_payment_rejects_user_without_email_or_phone(self):
        user = self.create_user("nophone@example.com", User.Roles.STUDENT, phone="")
        user.email = ""
        user.username = "nophone-user"
        user.save(update_fields=["email", "username"])
        self.client.force_authenticate(user)

        response = self.client.post("/api/payments/create/", {"lessons_count": 1}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Payment.objects.filter(student=user).count(), 0)

    def test_legacy_applicant_payment_creation_is_disabled(self):
        self.client.force_authenticate(self.applicant)

        response = self.client.post(
            "/api/applicant/payments/create/",
            {"course_id": 1, "amount": "5000.00", "package_name": "legacy"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_410_GONE)
        self.assertEqual(Payment.objects.filter(student=self.applicant).count(), 0)

    def test_manager_payment_create_endpoint_is_read_only(self):
        self.client.force_authenticate(self.manager)

        response = self.client.post(
            "/api/manager/payments/",
            {"student": self.student.id, "amount": "1500.00", "lessons_count": 1},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_admin_payment_confirm_endpoint_is_disabled(self):
        admin = self.create_user("admin-pay@example.com", User.Roles.ADMIN)
        payment = Payment.objects.create(
            student=self.student,
            amount=Decimal("1500.00"),
            lessons_count=1,
            confirmed=False,
        )
        self.client.force_authenticate(admin)

        response = self.client.post(
            f"/api/admin/payments/{payment.id}/confirm/",
            {"lessons_to_add": 1},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        payment.refresh_from_db()
        self.assertFalse(payment.confirmed)

    @patch("sk.payment_api_views._yookassa_request")
    def test_payment_status_by_status_token_syncs_success_and_confirms(self, mock_request):
        payment = Payment.objects.create(
            student=self.student,
            amount=Decimal("3000.00"),
            lessons_count=2,
            confirmed=False,
            yookassa_payment_id="yk-status-1",
            yookassa_status="pending",
            idempotence_key="status-token-1",
        )
        mock_request.return_value = (200, {"status": "succeeded"})

        response = self.client.get(f"/api/payments/{payment.id}/status/?status_token=status-token-1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payment.refresh_from_db()
        balance = LessonBalance.objects.get(student=self.student)
        self.assertTrue(payment.confirmed)
        self.assertEqual(payment.yookassa_status, "succeeded")
        self.assertEqual(balance.lessons_available, 2)
        self.assertTrue(AuditLog.objects.filter(action="YOOKASSA_PAYMENT_SYNC_SUCCEEDED").exists())

    @patch("sk.payment_api_views._yookassa_request")
    def test_auth_me_syncs_recent_pending_payment(self, mock_request):
        payment = Payment.objects.create(
            student=self.student,
            amount=Decimal("3000.00"),
            lessons_count=2,
            confirmed=False,
            yookassa_payment_id="yk-me-sync-1",
            yookassa_status="pending",
        )
        mock_request.return_value = (200, {"status": "succeeded"})
        self.client.force_authenticate(self.student)

        response = self.client.get("/api/auth/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payment.refresh_from_db()
        balance = LessonBalance.objects.get(student=self.student)
        self.student.refresh_from_db()
        self.assertTrue(payment.confirmed)
        self.assertEqual(payment.yookassa_status, "succeeded")
        self.assertEqual(balance.lessons_available, 2)
        self.assertEqual(self.student.role, User.Roles.STUDENT)

    @patch("sk.payment_api_views._yookassa_request")
    def test_dashboard_syncs_recent_pending_payment(self, mock_request):
        payment = Payment.objects.create(
            student=self.student,
            amount=Decimal("1500.00"),
            lessons_count=1,
            confirmed=False,
            yookassa_payment_id="yk-dashboard-sync-1",
            yookassa_status="pending",
        )
        mock_request.return_value = (200, {"status": "succeeded"})
        self.client.force_authenticate(self.student)

        response = self.client.get("/api/dashboard/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payment.refresh_from_db()
        balance = LessonBalance.objects.get(student=self.student)
        self.assertTrue(payment.confirmed)
        self.assertEqual(payment.yookassa_status, "succeeded")
        self.assertEqual(balance.lessons_available, 1)

    @patch("sk.payment_api_views._yookassa_request")
    def test_payment_status_requires_owner_or_manager_without_status_token(self, mock_request):
        outsider = self.create_user("outsider@example.com", User.Roles.STUDENT)
        payment = Payment.objects.create(
            student=self.student,
            amount=Decimal("1500.00"),
            lessons_count=1,
            confirmed=False,
            yookassa_payment_id="yk-status-2",
            yookassa_status="pending",
        )
        mock_request.return_value = (200, {"status": "pending"})

        self.client.force_authenticate(outsider)
        response = self.client.get(f"/api/payments/{payment.id}/status/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.manager)
        response = self.client.get(f"/api/payments/{payment.id}/status/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
