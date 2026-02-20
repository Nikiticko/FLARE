from django.contrib.auth import get_user_model
from django.db import transaction
from django.conf import settings
from pathlib import Path
from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from accounts.permissions import IsAdminRole
from .models import Payment, Lesson, LessonBalance, AuditLog, Course, PaymentSettings
from .admin_serializers import (
    AdminUserListSerializer,
    AdminUserDetailSerializer,
    AdminSetRoleSerializer,
    PaymentSerializer,
    LessonSerializer,
    AdminLessonCreateSerializer,
    AdminLessonUpdateSerializer,
    LessonBalanceSerializer,
    AuditLogSerializer,
    CourseSerializer,
    CourseCreateUpdateSerializer,
    PaymentSettingsSerializer,
    PaymentSettingsUpdateSerializer,
)

User = get_user_model()


def _parse_backend_log_line(line):
    raw = (line or '').rstrip('\n')
    parts = raw.split('|', 3)
    if len(parts) == 4:
        return {
            'timestamp': parts[0],
            'level': parts[1],
            'logger': parts[2],
            'message': parts[3],
            'raw': raw,
        }

    return {
        'timestamp': None,
        'level': 'UNKNOWN',
        'logger': None,
        'message': raw,
        'raw': raw,
    }


# ======= USERS =======


class AdminUserListAPI(generics.ListAPIView):
    """
    Список всех пользователей (поиск/фильтры):
    ?role=STUDENT|TEACHER|... & search=часть_email_или_ФИО
    """
    permission_classes = [IsAuthenticated, IsAdminRole]
    serializer_class = AdminUserListSerializer
    queryset = User.objects.all().order_by("-date_joined")
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["role", "is_superuser"]
    search_fields = ["email", "student_full_name", "parent_full_name"]
    ordering_fields = ["id", "email", "date_joined"]


class AdminUserByEmailAPI(APIView):
    """
    Поиск пользователя по email для создания урока.
    GET /api/admin/users/by-email/?email=user@example.com
    """
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        email = request.query_params.get('email', '').strip().lower()
        if not email:
            return Response({"detail": "email parameter required"}, status=400)
        
        try:
            user = User.objects.get(email__iexact=email)
            return Response({
                "id": user.id,
                "email": user.email,
                "student_full_name": user.student_full_name,
                "parent_full_name": user.parent_full_name,
                "role": user.role,
            })
        except User.DoesNotExist:
            return Response({"detail": "user not found"}, status=404)
        except User.MultipleObjectsReturned:
            return Response({"detail": "multiple users found"}, status=400)


class AdminUserDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/admin/users/{id}/      — детальная инфа
    PATCH  /api/admin/users/{id}/      — редактирование (email, phone, ФИО)
    DELETE /api/admin/users/{id}/      — удаление пользователя
    """
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = AdminUserDetailSerializer

    def perform_update(self, serializer):
        old_email = serializer.instance.email
        user = serializer.save()
        AuditLog.objects.create(
            actor=self.request.user,
            action="UPDATE_USER",
            meta={
                "user_id": user.id,
                "old_email": old_email,
                "new_email": user.email,
            },
        )

    def perform_destroy(self, instance):
        user_id = instance.id
        email = instance.email
        instance.delete()
        AuditLog.objects.create(
            actor=self.request.user,
            action="DELETE_USER",
            meta={"user_id": user_id, "email": email},
        )


class AdminSetRoleAPI(APIView):
    """
    Назначение роли пользователю: PATCH /api/admin/users/{id}/set-role/
    body: {"role": "TEACHER"}
    """
    permission_classes = [IsAuthenticated, IsAdminRole]

    def patch(self, request, pk):
        from django.conf import settings
        from accounts.permissions import is_root_admin
        
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "user not found"}, status=404)

        # защищаем root admin — ему нельзя менять роль
        if is_root_admin(user):
            return Response({"detail": "cannot change role of ROOT ADMIN"}, status=400)

        ser = AdminSetRoleSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        new_role = ser.validated_data["role"]

        user.role = new_role
        user.is_staff = new_role == "ADMIN"
        if new_role == "ADMIN":
            user.is_superuser = False  # суперюзер только у root-admin
        user.save()

        AuditLog.objects.create(
            actor=request.user,
            action="SET_ROLE",
            meta={"user_id": user.id, "email": user.email, "new_role": new_role},
        )
        return Response(AdminUserListSerializer(user).data)


class AdminResetPasswordAPI(APIView):
    """
    Сброс пароля пользователя администратором на базовый "12345678"
    POST /api/admin/users/{id}/reset-password/
    """
    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request, pk):
        from accounts.permissions import is_root_admin
        
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "user not found"}, status=404)

        # защищаем root admin
        if is_root_admin(user):
            return Response({"detail": "cannot reset password of ROOT ADMIN"}, status=400)

        # сбрасываем пароль на базовый
        default_password = "12345678"
        user.set_password(default_password)
        user.save()

        AuditLog.objects.create(
            actor=request.user,
            action="RESET_PASSWORD",
            meta={"user_id": user.id, "email": user.email},
        )
        
        return Response({"detail": f"Пароль сброшен на {default_password}"})


# ======= PAYMENTS / BALANCE =======


class AdminPaymentListAPI(generics.ListCreateAPIView):
    """
    GET: список платежей (фильтры: confirmed, student)
    POST: создать запись оплаты (обычно создаёт менеджер, но админ может всё)
    """
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = Payment.objects.select_related("student").all().order_by("-paid_at")
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["confirmed", "student"]
    ordering_fields = ["paid_at", "amount", "id"]


class AdminPaymentConfirmAPI(APIView):
    """
    Подтверждение оплаты и начисление занятий на баланс.
    POST /api/admin/payments/{id}/confirm/
    body: {"lessons_to_add": 4}
    """
    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request, pk):
        try:
            payment = Payment.objects.select_related("student").get(pk=pk)
        except Payment.DoesNotExist:
            return Response({"detail": "payment not found"}, status=404)

        if payment.confirmed:
            return Response({"detail": "already confirmed"}, status=400)

        lessons_to_add = int(request.data.get("lessons_to_add", 0))
        if lessons_to_add <= 0:
            return Response({"detail": "lessons_to_add must be > 0"}, status=400)

        with transaction.atomic():
            lb, _ = LessonBalance.objects.select_for_update().get_or_create(
                student=payment.student
            )
            lb.lessons_available += lessons_to_add
            lb.save()

            payment.confirmed = True
            payment.save()

            AuditLog.objects.create(
                actor=request.user,
                action="CONFIRM_PAYMENT",
                meta={
                    "payment_id": payment.id,
                    "student": payment.student_id,
                    "lessons_added": lessons_to_add,
                },
            )

        return Response({"detail": "ok"})


class AdminBalanceGetAPI(generics.RetrieveAPIView):
    """
    Получить текущий баланс занятий ученика:
    GET /api/admin/students/{student_id}/balance/
    """
    permission_classes = [IsAuthenticated, IsAdminRole]
    serializer_class = LessonBalanceSerializer
    lookup_field = "student"
    lookup_url_kwarg = "student_id"

    def get_queryset(self):
        return LessonBalance.objects.select_related("student").all()


# ======= LESSONS =======


class AdminLessonListAPI(generics.ListCreateAPIView):
    """
    GET: список занятий (фильтры: status, student, teacher)
    POST: создать занятие (назначить)
    Может использовать student_email и teacher_email вместо ID.
    """
    permission_classes = [IsAuthenticated, IsAdminRole]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "student", "teacher"]
    ordering_fields = ["scheduled_at", "created_at", "id"]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AdminLessonCreateSerializer
        return LessonSerializer

    def get_queryset(self):
        return Lesson.objects.select_related("student", "teacher").all().order_by(
            "-created_at"
        )

    def perform_create(self, serializer):
        lesson = serializer.save()
        # Автоматически заполняем parent_full_name из профиля ученика, если не указано
        if not lesson.parent_full_name and lesson.student:
            lesson.parent_full_name = lesson.student.parent_full_name or ''
            lesson.save(update_fields=['parent_full_name'])
        AuditLog.objects.create(
            actor=self.request.user,
            action="CREATE_LESSON",
            meta={
                "lesson_id": lesson.id,
                "student": lesson.student_id,
                "student_email": lesson.student.email,
                "teacher": lesson.teacher_id,
                "teacher_email": lesson.teacher.email if lesson.teacher else None,
                "scheduled_at": lesson.scheduled_at.isoformat(),
            },
        )


class AdminLessonUpdateAPI(generics.UpdateAPIView):
    """
    Частичное обновление урока админом:
    PATCH /api/admin/lessons/{id}/
    """
    permission_classes = [IsAuthenticated, IsAdminRole]
    serializer_class = AdminLessonUpdateSerializer
    queryset = Lesson.objects.select_related("student", "teacher").all()
    http_method_names = ["patch", "options", "head"]
    
    def get_serializer_class(self):
        # Для ответа используем полный сериализатор
        if self.request.method in ['PATCH', 'PUT']:
            return AdminLessonUpdateSerializer
        return LessonSerializer
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[Admin] Updating lesson ID: {instance.id}")
        logger.info(f"[Admin] Request data: {request.data}")
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Возвращаем полные данные обновленного урока
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        
        # Обновляем объект из БД
        instance.refresh_from_db()
        
        # Используем полный сериализатор для ответа
        from rest_framework.response import Response
        response_serializer = LessonSerializer(instance)
        response_data = response_serializer.data
        
        logger.info(f"[Admin] Response data ID: {response_data.get('id')}")
        logger.info(f"[Admin] Response data keys: {list(response_data.keys())}")
        
        return Response(response_data)

    def perform_update(self, serializer):
        lesson = serializer.save()
        AuditLog.objects.create(
            actor=self.request.user,
            action="UPDATE_LESSON",
            meta={
                "lesson_id": lesson.id,
                "student": lesson.student_id,
                "teacher": lesson.teacher_id,
                "status": lesson.status,
            },
        )


class AdminLessonDebitAPI(APIView):
    """
    Списание занятия с баланса:
    POST /api/admin/lessons/{id}/debit/
    body: {"mark_done": true/false}
    """
    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request, pk):
        mark_done = bool(request.data.get("mark_done", True))
        try:
            les = Lesson.objects.select_related("student").get(pk=pk)
        except Lesson.DoesNotExist:
            return Response({"detail": "lesson not found"}, status=404)

        if les.debited_from_balance:
            return Response({"detail": "already debited"}, status=400)

        with transaction.atomic():
            lb, _ = LessonBalance.objects.select_for_update().get_or_create(
                student=les.student
            )
            if lb.lessons_available <= 0:
                return Response({"detail": "no lessons available"}, status=400)

            lb.lessons_available -= 1
            lb.save()

            les.debited_from_balance = True
            if mark_done:
                les.status = Lesson.STATUS_DONE
            les.save()

            AuditLog.objects.create(
                actor=request.user,
                action="DEBIT_LESSON",
                meta={
                    "lesson_id": les.id,
                    "student": les.student_id,
                    "mark_done": mark_done,
                },
            )
        return Response({"detail": "ok"})


# ======= AUDIT LOG =======


class AdminAuditLogListAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    serializer_class = AuditLogSerializer
    queryset = AuditLog.objects.select_related("actor").all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["action", "actor__email"]
    ordering_fields = ["created_at", "id"]
    ordering = ["-created_at"]


class AdminBackendLogListAPI(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        levels_param = request.query_params.get('levels', '')
        requested_levels = {
            level.strip().upper()
            for level in levels_param.split(',')
            if level.strip()
        }
        search = request.query_params.get('search', '').strip().lower()

        try:
            limit = int(request.query_params.get('limit', '500'))
        except ValueError:
            limit = 500
        limit = max(1, min(limit, 5000))

        log_dir = Path(settings.LOG_DIR)
        base_file = log_dir / 'backend.log'
        log_files = sorted(log_dir.glob('backend.log*'), key=lambda path: path.stat().st_mtime, reverse=True)

        if base_file.exists() and base_file not in log_files:
            log_files.insert(0, base_file)

        entries = []

        for file_path in log_files:
            if len(entries) >= limit:
                break
            if not file_path.is_file():
                continue

            try:
                with file_path.open('r', encoding='utf-8', errors='replace') as file_obj:
                    lines = file_obj.readlines()
            except OSError:
                continue

            for line in reversed(lines):
                parsed = _parse_backend_log_line(line)

                if requested_levels and parsed['level'] not in requested_levels:
                    continue

                if search and search not in parsed['raw'].lower():
                    continue

                entries.append(parsed)
                if len(entries) >= limit:
                    break

        return Response({'count': len(entries), 'results': entries})


# ======= COURSES =======


class AdminCourseListCreateAPI(generics.ListCreateAPIView):
    """
    GET: список всех курсов
    POST: создать новый курс
    """
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CourseCreateUpdateSerializer
        return CourseSerializer

    def get_queryset(self):
        return Course.objects.all().order_by('id')

    def create(self, request, *args, **kwargs):
        """Переопределяем create, чтобы возвращать полные данные курса после создания"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Возвращаем полные данные курса
        full_serializer = CourseSerializer(serializer.instance)
        return Response(full_serializer.data, status=status.HTTP_201_CREATED)


class AdminCourseDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: детали курса
    PATCH: обновить курс
    DELETE: удалить курс
    """
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = Course.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return CourseCreateUpdateSerializer
        return CourseSerializer

    def update(self, request, *args, **kwargs):
        """Переопределяем update, чтобы возвращать полные данные курса после обновления"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Возвращаем полные данные курса
        full_serializer = CourseSerializer(instance)
        return Response(full_serializer.data)


class AdminLessonPriceAPI(APIView):
    """
    Управление стоимостью одного занятия.
    GET /api/admin/settings/lesson-price/
    PATCH /api/admin/settings/lesson-price/ {"lesson_price_rub": 1200}
    """
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        settings_obj, _ = PaymentSettings.objects.get_or_create(singleton_key=1)
        return Response(PaymentSettingsSerializer(settings_obj).data)

    def patch(self, request):
        settings_obj, _ = PaymentSettings.objects.get_or_create(singleton_key=1)
        serializer = PaymentSettingsUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_price = settings_obj.lesson_price_rub
        new_price = serializer.validated_data["lesson_price_rub"]

        settings_obj.lesson_price_rub = new_price
        settings_obj.save(update_fields=["lesson_price_rub", "updated_at"])

        AuditLog.objects.create(
            actor=request.user,
            action="UPDATE_LESSON_PRICE",
            meta={
                "old_price": old_price,
                "new_price": new_price,
            },
        )

        return Response(PaymentSettingsSerializer(settings_obj).data)
