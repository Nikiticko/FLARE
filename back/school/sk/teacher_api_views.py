from django.contrib.auth import get_user_model
from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from accounts.permissions import IsTeacherOrAdmin
from .models import Lesson, AuditLog, LessonBalance
from django.db import transaction
from .lesson_balance_service import apply_lesson_status_transition, reserve_lesson_slot
from .teacher_serializers import (
    TeacherLessonSerializer,
    TeacherLessonUpdateSerializer,
    TeacherLessonCreateSerializer,
    TeacherStudentSerializer,
)

User = get_user_model()


# ======= УРОКИ / РАСПИСАНИЕ =======


class TeacherLessonsListCreateAPI(generics.ListCreateAPIView):
    """
    GET: Список всех уроков учителя (и будущие, и прошедшие).
    POST: Создать урок для своего ученика.

    Фильтры:
      - status=PLANNED|DONE|CANCELLED
      - student=<id>

    Параметр сортировки:
      - ?ordering=scheduled_at или -scheduled_at
    """
    permission_classes = [IsTeacherOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "student"]
    search_fields = [
        "student__email",
        "student__student_full_name",
        "parent_full_name",
    ]
    ordering_fields = ["scheduled_at", "created_at", "id"]
    ordering = ["-scheduled_at"]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TeacherLessonCreateSerializer
        return TeacherLessonSerializer

    def get_queryset(self):
        from django.utils.dateparse import parse_date
        from django.utils import timezone
        
        user = self.request.user
        qs = Lesson.objects.select_related("student", "teacher").all()
        # если не админ и не суперюзер — показываем только свои уроки
        if not (user.is_superuser or getattr(user, "role", None) == "ADMIN"):
            qs = qs.filter(teacher=user)
        
        # Фильтрация по датам
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            try:
                date_from_parsed = parse_date(date_from)
                if date_from_parsed:
                    # Начало дня
                    date_from_dt = timezone.make_aware(
                        timezone.datetime.combine(date_from_parsed, timezone.datetime.min.time())
                    )
                    qs = qs.filter(scheduled_at__gte=date_from_dt)
            except (ValueError, TypeError):
                pass
        
        if date_to:
            try:
                date_to_parsed = parse_date(date_to)
                if date_to_parsed:
                    # Конец дня
                    date_to_dt = timezone.make_aware(
                        timezone.datetime.combine(date_to_parsed, timezone.datetime.max.time())
                    )
                    qs = qs.filter(scheduled_at__lte=date_to_dt)
            except (ValueError, TypeError):
                pass
        
        return qs

    def perform_create(self, serializer):
        teacher = self.request.user

        with transaction.atomic():
            lesson = serializer.save(teacher=teacher)
            if not lesson.parent_full_name and lesson.student:
                lesson.parent_full_name = lesson.student.parent_full_name or ''
                lesson.save(update_fields=['parent_full_name'])

            reserve_lesson_slot(lesson)

            AuditLog.objects.create(
                actor=teacher,
                action="TEACHER_CREATE_LESSON",
                meta={
                    "lesson_id": lesson.id,
                    "student": lesson.student_id,
                    "student_email": lesson.student.email,
                    "scheduled_at": lesson.scheduled_at.isoformat(),
                    "reserved_from_balance": lesson.reserved_from_balance,
                },
            )


class TeacherLessonDetailAPI(generics.RetrieveAPIView):
    """
    Детальная карточка урока (доступна только своему учителю и админам).
    """
    permission_classes = [IsTeacherOrAdmin]
    serializer_class = TeacherLessonSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Lesson.objects.select_related("student", "teacher").all()
        if not (user.is_superuser or getattr(user, "role", None) == "ADMIN"):
            qs = qs.filter(teacher=user)
        return qs


class TeacherLessonUpdateAPI(generics.UpdateAPIView):
    """
    Частичное обновление урока учителем:
    - статус (PLANNED / DONE / CANCELLED)
    - комментарий
    - при необходимости ссылка

    PATCH /api/teacher/lessons/<id>/update/
    """
    permission_classes = [IsTeacherOrAdmin]
    serializer_class = TeacherLessonUpdateSerializer
    http_method_names = ["patch", "options", "head"]

    def get_queryset(self):
        user = self.request.user
        qs = Lesson.objects.select_related("student", "teacher").all()
        if not (user.is_superuser or getattr(user, "role", None) == "ADMIN"):
            qs = qs.filter(teacher=user)
        return qs
    
    def get_serializer_class(self):
        # Для ответа используем полный сериализатор с балансом
        if self.request.method in ['PATCH', 'PUT']:
            return TeacherLessonUpdateSerializer
        return TeacherLessonSerializer
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Updating lesson ID: {instance.id}")
        logger.info(f"Request data: {request.data}")
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Возвращаем полные данные обновленного урока
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        
        # Обновляем объект из БД
        instance.refresh_from_db()
        
        # Используем полный сериализатор для ответа
        response_serializer = TeacherLessonSerializer(instance)
        response_data = response_serializer.data
        
        logger.info(f"Response data ID: {response_data.get('id')}")
        logger.info(f"Response data keys: {list(response_data.keys())}")
        logger.info(f"Response feedback: {response_data.get('feedback')}")
        logger.info(f"Response cancellation_reason: {response_data.get('cancellation_reason')}")
        
        return Response(response_data)

    def perform_update(self, serializer):
        old_status = self.get_object().status
        
        # Сохраняем урок (миграции применены, все поля должны быть в БД)
        lesson = serializer.save()
        
        new_status = lesson.status
        status_changed = new_status != old_status
        
        if status_changed:
            apply_lesson_status_transition(lesson, old_status, new_status)
        
        # Синхронизация комментария: если комментарий изменился, обновляем его во всех уроках с этим учеником
        # (комментарий общий для всех уроков с учеником, независимо от учителя)
        if 'comment' in serializer.validated_data:
            new_comment = serializer.validated_data['comment']
            # Обновляем комментарий во всех уроках с этим учеником
            Lesson.objects.filter(
                student=lesson.student
            ).exclude(id=lesson.id).update(comment=new_comment)
        
        AuditLog.objects.create(
            actor=self.request.user,
            action="TEACHER_UPDATE_LESSON",
            meta={
                "lesson_id": lesson.id,
                "student": lesson.student_id,
                "status": lesson.status,
                "old_status": old_status,
                "is_trial": getattr(lesson, 'is_trial', False),
                "debited_from_balance": lesson.debited_from_balance,
                "reserved_from_balance": lesson.reserved_from_balance,
                "cancellation_reason": getattr(lesson, 'cancellation_reason', None) if lesson.status == Lesson.STATUS_CANCELLED else None,
                "has_feedback": bool(getattr(lesson, 'feedback', '')) if lesson.status == Lesson.STATUS_DONE else None,
            },
        )
        
        # Обновляем объект из БД, чтобы получить актуальные данные
        lesson.refresh_from_db()


# ======= ЖУРНАЛ УЧЕНИКОВ =======


class TeacherStudentsListAPI(generics.ListAPIView):
    """
    Список учеников, у которых есть уроки с данным преподавателем.

    Поиск:
      - ?search=строка  (по email / ФИО ученика / ФИО родителя)
    """
    permission_classes = [IsTeacherOrAdmin]
    serializer_class = TeacherStudentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["email", "student_full_name", "parent_full_name"]

    def get_queryset(self):
        user = self.request.user
        qs = User.objects.filter(lessons_as_student__isnull=False).distinct()
        if not (user.is_superuser or getattr(user, "role", None) == "ADMIN"):
            qs = qs.filter(lessons_as_student__teacher=user).distinct()
        return qs


class TeacherStudentLessonsAPI(generics.ListAPIView):
    """
    Журнал по конкретному ученику (все его занятия).
    Доступен только его учителю и админам.

    GET /api/teacher/students/<student_id>/lessons/
    """
    permission_classes = [IsTeacherOrAdmin]
    serializer_class = TeacherLessonSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status"]
    ordering_fields = ["scheduled_at", "created_at", "id"]
    ordering = ["-scheduled_at"]

    def get_queryset(self):
        user = self.request.user
        student_id = self.kwargs["student_id"]
        qs = Lesson.objects.select_related("student", "teacher").filter(
            student_id=student_id
        )
        if not (user.is_superuser or getattr(user, "role", None) == "ADMIN"):
            qs = qs.filter(teacher=user)
        return qs


class TeacherStudentByEmailAPI(APIView):
    """
    Поиск ученика по email для создания урока.
    Проверяет, что ученик назначен данному учителю.
    GET /api/teacher/students/by-email/?email=student@example.com
    """
    permission_classes = [IsTeacherOrAdmin]

    def get(self, request):
        email = request.query_params.get('email', '').strip().lower()
        if not email:
            return Response({"detail": "email parameter required"}, status=400)
        
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({"detail": "user not found"}, status=404)
        except User.MultipleObjectsReturned:
            return Response({"detail": "multiple users found"}, status=400)
        
        # Проверяем, что это ученик учителя (есть хотя бы один урок с этим учителем)
        teacher = request.user
        if not (teacher.is_superuser or getattr(teacher, "role", None) == "ADMIN"):
            has_lesson = Lesson.objects.filter(
                student=user,
                teacher=teacher
            ).exists()
            if not has_lesson:
                return Response({
                    "detail": "this student is not assigned to you",
                    "is_my_student": False
                }, status=403)

        lb, _ = LessonBalance.objects.get_or_create(student=user)
        
        return Response({
            "id": user.id,
            "email": user.email,
            "student_full_name": user.student_full_name,
            "parent_full_name": user.parent_full_name,
            "role": user.role,
            "lessons_available": lb.lessons_available,
            "lessons_reserved": lb.lessons_reserved,
            "lessons_free_for_planning": max(0, lb.lessons_available - lb.lessons_reserved),
            "is_my_student": True,
        })


class TeacherStudentsAutocompleteAPI(APIView):
    """
    Получить список учеников учителя для автодополнения.
    GET /api/teacher/students/autocomplete/?search=test
    """
    permission_classes = [IsTeacherOrAdmin]

    def get(self, request):
        from django.db import models
        search = request.query_params.get('search', '').strip()
        teacher = request.user
        
        # Получаем всех учеников, у которых есть уроки с этим учителем
        if teacher.is_superuser or getattr(teacher, "role", None) == "ADMIN":
            # Админ видит всех учеников
            students = User.objects.filter(role__in=['STUDENT', 'APPLICANT']).distinct()
        else:
            # Учитель видит только своих учеников
            students = User.objects.filter(
                lessons_as_student__teacher=teacher
            ).distinct()
        
        if search:
            students = students.filter(
                models.Q(email__icontains=search) |
                models.Q(student_full_name__icontains=search) |
                models.Q(parent_full_name__icontains=search)
            )
        
        # Ограничиваем количество результатов
        students = students[:50]
        
        return Response([{
            "id": student.id,
            "email": student.email,
            "student_full_name": student.student_full_name,
            "parent_full_name": student.parent_full_name,
            "role": student.role,
        } for student in students])


class TeacherAutocompleteAPI(APIView):
    """
    Получить список email учеников учителя для автодополнения.
    GET /api/teacher/autocomplete/
    """
    permission_classes = [IsTeacherOrAdmin]

    def get(self, request):
        teacher = request.user
        
        # Получаем всех учеников, у которых есть хотя бы один урок с этим учителем
        if teacher.is_superuser or getattr(teacher, "role", None) == "ADMIN":
            # Админ видит всех учеников
            students = User.objects.filter(role__in=[User.Roles.STUDENT, User.Roles.APPLICANT]).values('email', 'student_full_name', 'id')
        else:
            # Учитель видит только своих учеников
            student_ids = Lesson.objects.filter(teacher=teacher).values_list('student_id', flat=True).distinct()
            students = User.objects.filter(id__in=student_ids).values('email', 'student_full_name', 'id')
        
        results = [{"email": s['email'], "id": s['id'], "name": s.get('student_full_name', '')} for s in students]
        return Response(results)
