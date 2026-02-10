from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Lesson, LessonBalance, Course

User = get_user_model()


class TeacherLessonSerializer(serializers.ModelSerializer):
    """
    Карточка урока для учителя (просмотр).
    """
    student_email = serializers.EmailField(source="student.email", read_only=True)
    student_name = serializers.CharField(source="student.student_full_name", read_only=True)
    parent_full_name = serializers.CharField(read_only=True)
    teacher_email = serializers.EmailField(source="teacher.email", read_only=True)
    
    # Используем SerializerMethodField для полей, которые могут отсутствовать в БД
    course = serializers.SerializerMethodField()
    course_id = serializers.SerializerMethodField()
    student_balance = serializers.SerializerMethodField()
    
    # Явно объявляем поля из модели для чтения/записи
    cancellation_reason = serializers.CharField(required=False, allow_blank=True)
    feedback = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Lesson
        fields = (
            "id",
            "student", "student_email", "student_name",
            "parent_full_name",
            "teacher", "teacher_email",
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
            "student_balance",
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


class TeacherLessonUpdateSerializer(serializers.ModelSerializer):
    """
    Что учитель может менять в карточке урока:
    - статус (PLANNED/DONE/CANCELLED)
    - комментарий/отметку (синхронизируется для всех уроков с этим учеником)
    - причину отмены (обязательна при статусе CANCELLED)
    - обратную связь (обязательна при статусе DONE)
    - ссылку (обязательна; пустое значение — Discord по умолчанию)
    """
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), required=False, allow_null=True)
    link = serializers.CharField(required=False, allow_blank=True, max_length=300)
    cancellation_reason = serializers.CharField(required=False, allow_blank=True)
    feedback = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Lesson
        fields = ("status", "comment", "link", "course", "cancellation_reason", "feedback")

    def validate_link(self, value):
        """Пустая ссылка заменяется на Discord по умолчанию"""
        if not value or not str(value).strip():
            return "Discord"
        return str(value).strip()

    def save(self, **kwargs):
        # Миграция применена, поля должны быть в БД
        # Просто сохраняем как обычно
        return super().save(**kwargs)

    def validate(self, attrs):
        """
        Валидация полей в зависимости от статуса:
        - При статусе CANCELLED требуется cancellation_reason
        - При статусе DONE требуется feedback
        """
        status = attrs.get('status')
        
        # Если статус изменен на CANCELLED, проверяем наличие причины
        if status == Lesson.STATUS_CANCELLED:
            cancellation_reason = attrs.get('cancellation_reason', '').strip()
            if not cancellation_reason:
                raise serializers.ValidationError({
                    "cancellation_reason": "Причина отмены обязательна при статусе CANCELLED"
                })
        
        # Если статус изменен на DONE, проверяем наличие обратной связи
        if status == Lesson.STATUS_DONE:
            feedback = attrs.get('feedback', '').strip()
            if not feedback:
                raise serializers.ValidationError({
                    "feedback": "Обратная связь обязательна при статусе DONE"
                })
        
        return attrs


class TeacherLessonCreateSerializer(serializers.ModelSerializer):
    """
    Создание урока учителем.
    Учитель может указать student_email вместо ID.
    Учитель автоматически назначается как teacher.
    """
    student_email = serializers.EmailField(write_only=True, required=False, allow_blank=True)
    student = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    # ВРЕМЕННО УБРАНО: course будет доступен после применения миграций
    # course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), required=False, allow_null=True)
    link = serializers.CharField(required=False, allow_blank=True, default="Discord", max_length=300)
    comment = serializers.CharField(required=False, allow_blank=True)
    scheduled_at = serializers.DateTimeField(required=True)

    class Meta:
        model = Lesson
        fields = ("student", "student_email", "scheduled_at", "link", "comment")

    def validate_link(self, value):
        """Пустая ссылка заменяется на Discord по умолчанию"""
        if not value or not str(value).strip():
            return "Discord"
        return str(value).strip()

    def validate(self, attrs):
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Validating teacher lesson creation with attrs: {attrs}")
        
        # Если передан email, находим пользователя по email
        student_email = attrs.pop('student_email', None)
        if student_email:
            student_email = student_email.strip() if isinstance(student_email, str) else None
            if student_email:
                try:
                    student = User.objects.get(email__iexact=student_email)
                    attrs['student'] = student
                    logger.info(f"Found student: {student.id} - {student.email}")
                except User.DoesNotExist:
                    logger.warning(f"Student not found: {student_email}")
                    raise serializers.ValidationError({"student_email": "Student with this email not found"})
                except User.MultipleObjectsReturned:
                    logger.warning(f"Multiple students found: {student_email}")
                    raise serializers.ValidationError({"student_email": "Multiple students with this email found"})
        
        # Проверяем, что хотя бы один способ указания ученика есть
        if not attrs.get('student'):
            logger.error("Student is required but not provided")
            raise serializers.ValidationError({"student": "Either student or student_email is required"})
        
        # Валидация: учитель может создавать уроки только для учеников (STUDENT) с положительным балансом
        student = attrs.get('student')
        if student:
            # Проверяем роль: учитель может ставить занятия только ученикам
            student_role = getattr(student, 'role', None)
            if student_role != 'STUDENT':
                raise serializers.ValidationError({
                    "student": "Учитель может создавать занятия только для учеников (не для абитуриентов). Для создания пробного занятия обратитесь к менеджеру."
                })
            
            # Проверяем баланс: должен быть положительным
            lb, _ = LessonBalance.objects.get_or_create(student=student)
            if lb.lessons_available <= 0:
                raise serializers.ValidationError({
                    "student": "Нельзя создать урок для ученика с нулевым балансом. Обратитесь к менеджеру для пополнения баланса."
                })
        
        logger.info(f"Validation successful. Final attrs: student={attrs.get('student')}")
        return attrs


class TeacherStudentSerializer(serializers.ModelSerializer):
    """
    Список учеников учителя (для журнала).
    """
    class Meta:
        model = User
        fields = ("id", "email", "student_full_name", "parent_full_name")
