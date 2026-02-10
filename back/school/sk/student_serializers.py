from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Course, Lesson, LessonBalance, Payment, StudentProfile, ClientRequest

User = get_user_model()


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ("level", "xp", "season_currency")


class StudentDashboardSerializer(serializers.Serializer):
    """
    Объединённый ответ для /api/student/dashboard/
    """
    id = serializers.IntegerField()
    email = serializers.EmailField()
    student_full_name = serializers.CharField()
    role = serializers.CharField()
    balance = serializers.IntegerField()
    level = serializers.IntegerField()
    xp = serializers.IntegerField()
    season_currency = serializers.IntegerField()


class UnifiedDashboardSerializer(serializers.Serializer):
    """
    Объединённый ответ для /api/dashboard/ (работает для STUDENT и APPLICANT).
    StudentProfile опционален для абитуриентов.
    """
    id = serializers.IntegerField()
    email = serializers.EmailField()
    student_full_name = serializers.CharField()
    role = serializers.CharField()
    balance = serializers.IntegerField()
    level = serializers.IntegerField(required=False, allow_null=True)
    xp = serializers.IntegerField(required=False, allow_null=True)
    season_currency = serializers.IntegerField(required=False, allow_null=True)


class StudentCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ("id", "title", "description", "default_lessons", "default_price")


class StudentLessonSerializer(serializers.ModelSerializer):
    teacher_email = serializers.EmailField(source="teacher.email", read_only=True)
    teacher_full_name = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    feedback = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = (
            "id",
            "teacher", "teacher_email", "teacher_full_name",
            "course",
            "link",
            "scheduled_at",
            "status",
            "comment",
            "feedback",
            "debited_from_balance",
            "created_at",
        )

    def get_teacher_full_name(self, obj):
        """Получение ФИО преподавателя"""
        if obj.teacher:
            # Используем student_full_name (общее поле ФИО) или собираем из first_name/last_name
            if hasattr(obj.teacher, 'student_full_name') and obj.teacher.student_full_name:
                return obj.teacher.student_full_name.strip()
            first_name = getattr(obj.teacher, 'first_name', '') or ''
            last_name = getattr(obj.teacher, 'last_name', '') or ''
            full_name = f"{first_name} {last_name}".strip()
            if full_name:
                return full_name
            # Если нет имени, возвращаем email
            if hasattr(obj.teacher, 'email') and obj.teacher.email:
                return obj.teacher.email
        return None
    
    def get_course(self, obj):
        """Получение названия курса"""
        if obj.course:
            return obj.course.title
        return None
    
    def get_feedback(self, obj):
        """Безопасное получение обратной связи"""
        return getattr(obj, 'feedback', '')


class StudentBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonBalance
        fields = ("lessons_available", "updated_at")


class StudentPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("id", "amount", "package_name", "paid_at", "confirmed")


class StudentPaymentCreateSerializer(serializers.Serializer):
    """
    Заявка на оплату от ученика (похож на абитуриента).
    """
    course_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    package_name = serializers.CharField(max_length=120, required=False, allow_blank=True)

    def validate_course_id(self, value):
        from .models import Course
        if not Course.objects.filter(pk=value, is_active=True).exists():
            raise serializers.ValidationError("Курс не найден или не активен")
        return value


class StudentClientRequestCreateSerializer(serializers.ModelSerializer):
    """
    Создание обращения к менеджеру учеником.
    """
    class Meta:
        model = ClientRequest
        fields = ("comment",)

    def create(self, validated_data):
        # Автоматически устанавливаем клиента из request.user
        validated_data['client'] = self.context['request'].user
        return super().create(validated_data)
