from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Payment, Lesson, LessonBalance, AuditLog, Course, PaymentSettings

User = get_user_model()


class AdminUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "phone",
            "student_full_name",
            "parent_full_name",
            "role",
            "is_staff",
            "is_superuser",
        )


class AdminUserDetailSerializer(serializers.ModelSerializer):
    """
    Детальный просмотр/редактирование пользователя в админке.
    Роль тут только для отображения — менять её отдельным эндпоинтом.
    """
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "phone",
            "student_full_name",
            "parent_full_name",
            "role",
            "is_staff",
            "is_superuser",
        )
        read_only_fields = ("id", "role", "is_staff", "is_superuser")


class AdminSetRoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(
        choices=[
            ("ADMIN", "ADMIN"),
            ("MANAGER", "MANAGER"),
            ("TEACHER", "TEACHER"),
            ("STUDENT", "STUDENT"),
            ("APPLICANT", "APPLICANT"),
        ]
    )


class PaymentSerializer(serializers.ModelSerializer):
    student_email = serializers.EmailField(source="student.email", read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "student",
            "student_email",
            "amount",
            "package_name",
            "lessons_count",
            "paid_at",
            "confirmed",
        )


class LessonBalanceSerializer(serializers.ModelSerializer):
    student_email = serializers.EmailField(source="student.email", read_only=True)

    class Meta:
        model = LessonBalance
        fields = ("student", "student_email", "lessons_available", "updated_at")


class LessonSerializer(serializers.ModelSerializer):
    student_email = serializers.EmailField(source="student.email", read_only=True)
    teacher_email = serializers.EmailField(source="teacher.email", read_only=True)
    student_balance = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    course_id = serializers.SerializerMethodField()
    
    # Явно объявляем поля из модели для чтения/записи
    cancellation_reason = serializers.CharField(required=False, allow_blank=True)
    feedback = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Lesson
        fields = (
            "id",
            "student",
            "student_email",
            "parent_full_name",
            "teacher",
            "teacher_email",
            "student_balance",
            "course",
            "course_id",
            "link",
            "scheduled_at",
            "status",
            "comment",
            "cancellation_reason",
            "feedback",
            "debited_from_balance",
            "is_trial",
            "created_at",
        )
    
    def get_course(self, obj):
        """Получение названия курса"""
        course = getattr(obj, 'course', None)
        if course:
            return course.title
        return None
    
    def get_course_id(self, obj):
        """ID курса для подстановки при создании/редактировании"""
        return getattr(obj, 'course_id', None)
    
    def get_student_balance(self, obj):
        """Получение баланса ученика"""
        try:
            balance = LessonBalance.objects.get(student=obj.student)
            return balance.lessons_available
        except LessonBalance.DoesNotExist:
            return 0


class AdminLessonCreateSerializer(serializers.ModelSerializer):
    """
    Создание урока админом.
    Может указать student_email и teacher_email вместо ID.
    """
    student = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    teacher = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), required=False, allow_null=True)
    student_email = serializers.EmailField(write_only=True, required=False)
    teacher_email = serializers.EmailField(write_only=True, required=False)
    link = serializers.CharField(required=False, allow_blank=True, default="Discord", max_length=300)
    comment = serializers.CharField(required=False, allow_blank=True)
    is_trial = serializers.BooleanField(required=False, default=False, help_text="Пробное занятие (не списывается с баланса)")

    class Meta:
        model = Lesson
        fields = ("student", "student_email", "teacher", "teacher_email", "course", "scheduled_at", "link", "comment", "is_trial")

    def validate_link(self, value):
        """Пустая ссылка заменяется на Discord по умолчанию"""
        if not value or not str(value).strip():
            return "Discord"
        return str(value).strip()

    def validate(self, attrs):
        # Если передан email, находим пользователя по email
        if attrs.get('student_email'):
            student_email = attrs.pop('student_email', '').strip()
            if student_email:
                try:
                    student = User.objects.get(email__iexact=student_email)
                    attrs['student'] = student
                except User.DoesNotExist:
                    raise serializers.ValidationError({"student_email": "Student with this email not found"})
                except User.MultipleObjectsReturned:
                    raise serializers.ValidationError({"student_email": "Multiple students with this email found"})
        
        if attrs.get('teacher_email'):
            teacher_email = attrs.pop('teacher_email', '').strip()
            if teacher_email:
                try:
                    teacher = User.objects.get(email__iexact=teacher_email)
                    attrs['teacher'] = teacher
                except User.DoesNotExist:
                    raise serializers.ValidationError({"teacher_email": "Teacher with this email not found"})
                except User.MultipleObjectsReturned:
                    raise serializers.ValidationError({"teacher_email": "Multiple teachers with this email found"})
        
        # Проверяем, что хотя бы один способ указания пользователя есть
        if not attrs.get('student'):
            raise serializers.ValidationError({"student": "Either student or student_email is required"})
        
        if not attrs.get('teacher'):
            raise serializers.ValidationError({"teacher": "Either teacher or teacher_email is required"})
        
        # ВРЕМЕННО УБРАНА валидация is_trial до применения миграций
        # Просто проверяем баланс
        student = attrs.get('student')
        if student:
            from .models import LessonBalance
            student_role = getattr(student, 'role', None)
            lb, _ = LessonBalance.objects.get_or_create(student=student)
            
            # Обычные занятия можно создавать только для учеников с положительным балансом
            if student_role != 'STUDENT':
                raise serializers.ValidationError({
                    "student": "Обычные занятия можно создавать только для учеников."
                })
            free_slots = lb.lessons_available - lb.lessons_reserved
            if free_slots <= 0:
                raise serializers.ValidationError({
                    "student": "Нет свободных занятий для планирования. Пополните баланс ученика."
                })
        
        return attrs


class AdminLessonUpdateSerializer(serializers.ModelSerializer):
    """
    Обновление урока админом.
    Может менять время, ссылку, статус, комментарий, преподавателя.
    Ссылка обязательна; пустое значение заменяется на Discord.
    """
    teacher_email = serializers.EmailField(write_only=True, required=False, allow_blank=True)
    teacher = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), required=False, allow_null=True)
    link = serializers.CharField(required=False, allow_blank=True, max_length=300)
    cancellation_reason = serializers.CharField(required=False, allow_blank=True)
    feedback = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Lesson
        fields = ("scheduled_at", "status", "link", "comment", "teacher", "teacher_email", "course", "cancellation_reason", "feedback")

    def validate_link(self, value):
        """Пустая ссылка заменяется на Discord по умолчанию"""
        if not value or not str(value).strip():
            return "Discord"
        return str(value).strip()
    
    def validate(self, attrs):
        # Обработка teacher_email
        teacher_email = attrs.pop('teacher_email', None)
        if teacher_email:
            teacher_email = teacher_email.strip() if isinstance(teacher_email, str) else None
            if teacher_email:
                try:
                    teacher = User.objects.get(email__iexact=teacher_email)
                    attrs['teacher'] = teacher
                except User.DoesNotExist:
                    raise serializers.ValidationError({"teacher_email": "Teacher with this email not found"})
                except User.MultipleObjectsReturned:
                    raise serializers.ValidationError({"teacher_email": "Multiple teachers with this email found"})
        return attrs


class AuditLogSerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source="actor.email", read_only=True)

    class Meta:
        model = AuditLog
        fields = ("id", "actor", "actor_email", "action", "meta", "created_at")


# ======= COURSES =======


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для курса (название и описание)"""
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = (
            "id", "title", "description", "created_at", "updated_at"
        )
        read_only_fields = ("id", "created_at", "updated_at")
    
    def get_created_at(self, obj):
        """Безопасное получение даты создания"""
        return getattr(obj, 'created_at', None)
    
    def get_updated_at(self, obj):
        """Безопасное получение даты обновления"""
        return getattr(obj, 'updated_at', None)


class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления курса"""
    class Meta:
        model = Course
        fields = ("title", "description")


class PaymentSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentSettings
        fields = ("lesson_price_rub", "updated_at")


class PaymentSettingsUpdateSerializer(serializers.Serializer):
    lesson_price_rub = serializers.IntegerField(min_value=1, max_value=100000)
