from django.db import transaction
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
from .student_serializers import (
    StudentDashboardSerializer,
    UnifiedDashboardSerializer,
    StudentCourseSerializer,
    StudentLessonSerializer,
    StudentBalanceSerializer,
    StudentPaymentSerializer,
    StudentPaymentCreateSerializer,
    StudentProfileSerializer,
    StudentClientRequestCreateSerializer,
)

User = get_user_model()


# ===== UNIFIED DASHBOARD =====

class UnifiedDashboardAPI(APIView):
    """
    Унифицированный ЛК для STUDENT и APPLICANT.
    ФИО, роль, баланс, и опционально: уровень, XP, внутренняя валюта (для STUDENT).
    GET /api/dashboard/
    """
    permission_classes = [IsAuthenticated, IsStudentOrApplicantOrTeacherOrManagerOrAdmin]

    def get(self, request):
        user = request.user
        bal, _ = LessonBalance.objects.get_or_create(student=user)
        
        # StudentProfile опционален - может отсутствовать у абитуриентов
        profile = None
        if hasattr(user, 'student_profile'):
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
        }
        ser = UnifiedDashboardSerializer(data)
        return Response(ser.data)


# ===== DASHBOARD =====

class StudentDashboardAPI(APIView):
    """
    ЛК ученика: ФИО, роль, баланс, уровень, XP, внутренняя валюта.
    GET /api/student/dashboard/
    """
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
        }
        ser = StudentDashboardSerializer(data)
        return Response(ser.data)


# ===== COURSES =====

class StudentCoursesListAPI(generics.ListAPIView):
    """
    Список доступных курсов для ученика.
    GET /api/student/courses/
    """
    permission_classes = [IsAuthenticated, IsStudentOrAdmin]
    serializer_class = StudentCourseSerializer

    def get_queryset(self):
        return Course.objects.filter(is_active=True).order_by("id")


# ===== LESSONS (расписание + история) =====

class StudentLessonsListAPI(generics.ListAPIView):
    """
    Список уроков ученика/абитуриента.
    GET /api/student/lessons/?status=PLANNED|DONE|CANCELLED&ordering=scheduled_at
    """
    permission_classes = [IsAuthenticated, IsStudentOrApplicantOrTeacherOrManagerOrAdmin]
    serializer_class = StudentLessonSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status"]
    ordering_fields = ["scheduled_at", "created_at", "id"]
    ordering = ["scheduled_at"]

    def get_queryset(self):
        return Lesson.objects.select_related("teacher").filter(student=self.request.user)


# ===== BALANCE =====

class StudentBalanceAPI(APIView):
    """
    Баланс ученика.
    GET /api/student/balance/
    """
    permission_classes = [IsAuthenticated, IsStudentOrAdmin]

    def get(self, request):
        bal, _ = LessonBalance.objects.get_or_create(student=request.user)
        ser = StudentBalanceSerializer(bal)
        return Response(ser.data)


# ===== PAYMENTS (история + создание заявки) =====

class StudentPaymentsListAPI(generics.ListAPIView):
    """
    История оплат ученика.
    GET /api/student/payments/
    """
    permission_classes = [IsAuthenticated, IsStudentOrAdmin]
    serializer_class = StudentPaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(student=self.request.user).order_by("-paid_at")


class StudentCreatePaymentAPI(APIView):
    """
    Создание записи оплаты учеником (кнопка "Оплатить").
    POST /api/student/payments/create/
    Body: {"course_id": 1, "amount": "5000.00", "package_name": "8 занятий Python"}
    """
    permission_classes = [IsAuthenticated, IsStudentOrAdmin]

    @transaction.atomic
    def post(self, request):
        ser = StudentPaymentCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        course_id = ser.validated_data["course_id"]
        amount = ser.validated_data["amount"]
        package_name = ser.validated_data.get("package_name") or ""

        payment = Payment.objects.create(
            student=request.user,
            amount=amount,
            package_name=package_name or f"Оплата курса #{course_id}",
            confirmed=False,   # подтверждает менеджер/админ
        )

        return Response(StudentPaymentSerializer(payment).data, status=201)


# ===== SEASON SUMMARY =====

class StudentSeasonSummaryAPI(APIView):
    """
    Краткая инфа для кнопки "Система сезонов" в ЛК:
    уровень, XP, внутренняя валюта.
    На фронте эта кнопка может вести на отдельную страницу,
    где уже будут сложные механики.
    GET /api/student/season/summary/
    """
    permission_classes = [IsAuthenticated, IsStudentOrAdmin]

    def get(self, request):
        profile, _ = StudentProfile.objects.get_or_create(user=request.user)
        ser = StudentProfileSerializer(profile)
        return Response(ser.data)


# ===== ОБРАЩЕНИЯ К МЕНЕДЖЕРУ =====

class StudentCreateClientRequestAPI(APIView):
    """
    Создание обращения к менеджеру учеником.
    POST /api/student/requests/create/
    Body: {"comment": "Текст комментария (необязательно)"}
    """
    permission_classes = [IsAuthenticated, IsStudentOrApplicantOrTeacherOrManagerOrAdmin]

    def post(self, request):
        ser = StudentClientRequestCreateSerializer(data=request.data, context={'request': request})
        ser.is_valid(raise_exception=True)
        request_obj = ser.save()
        return Response({
            "id": request_obj.id,
            "comment": request_obj.comment,
            "status": request_obj.status,
            "created_at": request_obj.created_at,
        }, status=201)
