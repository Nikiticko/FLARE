from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from django.contrib.auth import get_user_model

from accounts.permissions import (
    IsStudentOrAdmin,
    IsStudentOrApplicantOrTeacherOrManagerOrAdmin,
)
from .models import Course, Lesson, LessonBalance, Payment, StudentProfile, ClientRequest
from .payment_api_views import sync_pending_yookassa_payments_for_user
from .student_serializers import (
    StudentDashboardSerializer,
    UnifiedDashboardSerializer,
    StudentCourseSerializer,
    StudentLessonSerializer,
    StudentBalanceSerializer,
    StudentPaymentSerializer,
    StudentProfileSerializer,
    StudentClientRequestCreateSerializer,
)

User = get_user_model()


def _normalized_avatar_url(user):
    avatar = getattr(user, "avatar", None)
    if not avatar:
        return None
    raw_url = avatar.url or ""
    if raw_url.startswith("http://") or raw_url.startswith("https://"):
        return raw_url
    if raw_url.startswith("/media/"):
        return raw_url
    if raw_url.startswith("media/"):
        return f"/{raw_url}"
    return f"/media/{raw_url.lstrip('/')}"


class UnifiedDashboardAPI(APIView):
    """Unified dashboard for student and applicant roles."""

    permission_classes = [IsAuthenticated, IsStudentOrApplicantOrTeacherOrManagerOrAdmin]

    def get(self, request):
        user = request.user
        sync_pending_yookassa_payments_for_user(user)
        user.refresh_from_db()
        bal, _ = LessonBalance.objects.get_or_create(student=user)

        profile = None
        if hasattr(user, "student_profile"):
            profile = user.student_profile

        data = {
            "id": user.id,
            "email": user.email,
            "student_full_name": getattr(user, "student_full_name", ""),
            "role": getattr(user, "role", ""),
            "balance": bal.lessons_available,
            "level": profile.level if profile else None,
            "xp": profile.xp if profile else None,
            "season_currency": profile.season_currency if profile else None,
            "avatar": _normalized_avatar_url(user),
            "avatar_url": _normalized_avatar_url(user),
        }
        ser = UnifiedDashboardSerializer(data)
        return Response(ser.data)


class StudentDashboardAPI(APIView):
    """Legacy student dashboard endpoint."""

    permission_classes = [IsAuthenticated, IsStudentOrAdmin]

    def get(self, request):
        user = request.user
        bal, _ = LessonBalance.objects.get_or_create(student=user)
        profile, _ = StudentProfile.objects.get_or_create(user=user)

        data = {
            "id": user.id,
            "email": user.email,
            "student_full_name": getattr(user, "student_full_name", ""),
            "role": getattr(user, "role", ""),
            "balance": bal.lessons_available,
            "level": profile.level,
            "xp": profile.xp,
            "season_currency": profile.season_currency,
            "avatar": _normalized_avatar_url(user),
            "avatar_url": _normalized_avatar_url(user),
        }
        ser = StudentDashboardSerializer(data)
        return Response(ser.data)


class StudentCoursesListAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsStudentOrAdmin]
    serializer_class = StudentCourseSerializer

    def get_queryset(self):
        return Course.objects.filter(is_active=True).order_by("id")


class StudentLessonsListAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsStudentOrApplicantOrTeacherOrManagerOrAdmin]
    serializer_class = StudentLessonSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status"]
    ordering_fields = ["scheduled_at", "created_at", "id"]
    ordering = ["scheduled_at"]

    def get_queryset(self):
        return Lesson.objects.select_related("teacher").filter(student=self.request.user)


class StudentBalanceAPI(APIView):
    permission_classes = [IsAuthenticated, IsStudentOrAdmin]

    def get(self, request):
        sync_pending_yookassa_payments_for_user(request.user)
        request.user.refresh_from_db()
        bal, _ = LessonBalance.objects.get_or_create(student=request.user)
        ser = StudentBalanceSerializer(bal)
        return Response(ser.data)


class StudentPaymentsListAPI(generics.ListAPIView):
    """Payment history only. Payment creation now goes through /api/payments/."""

    permission_classes = [IsAuthenticated, IsStudentOrAdmin]
    serializer_class = StudentPaymentSerializer

    def get_queryset(self):
        sync_pending_yookassa_payments_for_user(self.request.user)
        return Payment.objects.filter(student=self.request.user).order_by("-paid_at")


class StudentSeasonSummaryAPI(APIView):
    permission_classes = [IsAuthenticated, IsStudentOrAdmin]

    def get(self, request):
        profile, _ = StudentProfile.objects.get_or_create(user=request.user)
        ser = StudentProfileSerializer(profile)
        return Response(ser.data)


class StudentCreateClientRequestAPI(APIView):
    permission_classes = [IsAuthenticated, IsStudentOrApplicantOrTeacherOrManagerOrAdmin]

    def post(self, request):
        ser = StudentClientRequestCreateSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        request_obj = ser.save()
        return Response(
            {
                "id": request_obj.id,
                "comment": request_obj.comment,
                "status": request_obj.status,
                "created_at": request_obj.created_at,
            },
            status=201,
        )
