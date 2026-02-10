from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Lesson, LessonBalance, Payment, ClientRequest, Course

User = get_user_model()


class ManagerClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "phone", "student_full_name", "parent_full_name", "role")


class ManagerLessonSerializer(serializers.ModelSerializer):
    student_email = serializers.EmailField(source="student.email", read_only=True)
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
            "student",
            "student_email",
            "parent_full_name",
            "teacher",
            "teacher_email",
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


class ManagerLessonCreateSerializer(serializers.ModelSerializer):
    """
    Создание урока менеджером.
    Может указать student_email и teacher_email вместо ID.
    """
    student_email = serializers.EmailField(write_only=True, required=False, allow_blank=True)
    teacher_email = serializers.EmailField(write_only=True, required=False, allow_blank=True)
    student = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    teacher = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), required=False, allow_null=True)
    scheduled_at = serializers.DateTimeField(required=True)
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
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Validating lesson creation with attrs: {attrs}")
        
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
        
        teacher_email = attrs.pop('teacher_email', None)
        if teacher_email:
            teacher_email = teacher_email.strip() if isinstance(teacher_email, str) else None
            if teacher_email:
                try:
                    teacher = User.objects.get(email__iexact=teacher_email)
                    attrs['teacher'] = teacher
                    logger.info(f"Found teacher: {teacher.id} - {teacher.email}")
                except User.DoesNotExist:
                    logger.warning(f"Teacher not found: {teacher_email}")
                    raise serializers.ValidationError({"teacher_email": "Teacher with this email not found"})
                except User.MultipleObjectsReturned:
                    logger.warning(f"Multiple teachers found: {teacher_email}")
                    raise serializers.ValidationError({"teacher_email": "Multiple teachers with this email found"})
        
        # Проверяем, что хотя бы один способ указания пользователя есть
        if not attrs.get('student'):
            logger.error("Student is required but not provided")
            raise serializers.ValidationError({"student": "Either student or student_email is required"})
        
        if not attrs.get('teacher'):
            logger.error("Teacher is required but not provided")
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
            if lb.lessons_available <= 0:
                raise serializers.ValidationError({
                    "student": "Нельзя создать урок для ученика с нулевым балансом. Пополните баланс ученика."
                })
        
        logger.info(f"Validation successful. Final attrs: student={attrs.get('student')}, teacher={attrs.get('teacher')}")
        return attrs


class ManagerLessonUpdateSerializer(serializers.ModelSerializer):
    """
    Менеджер может менять время, ссылку, статус, комментарий, преподавателя.
    При отмене занятия (статус CANCELLED) обязательна причина отмены.
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

    def save(self, **kwargs):
        # Миграции применены, поля должны быть в БД
        # Просто сохраняем как обычно
        return super().save(**kwargs)

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
        
        # Получаем текущий статус (новый или существующий)
        new_status = attrs.get('status')
        old_status = self.instance.status if self.instance else None
        
        # Определяем финальный статус
        final_status = new_status if new_status is not None else old_status
        
        # Проверяем, меняется ли статус
        status_changed = new_status is not None and new_status != old_status
        
        # Получаем причину отмены (новую или существующую) - безопасно через getattr
        cancellation_reason = attrs.get('cancellation_reason')
        if cancellation_reason is None:
            if self.instance:
                cancellation_reason = getattr(self.instance, 'cancellation_reason', '') or ''
            else:
                cancellation_reason = ''
        # Если передана пустая строка, сохраняем её (позволяет очистить поле)
        elif cancellation_reason == '':
            cancellation_reason = ''
        # Обновляем attrs с актуальным значением
        attrs['cancellation_reason'] = cancellation_reason
        
        # Если статус меняется на CANCELLED, нужна причина отмены
        if status_changed and final_status == Lesson.STATUS_CANCELLED:
            if not cancellation_reason or not cancellation_reason.strip():
                raise serializers.ValidationError({
                    "cancellation_reason": "Причина отмены обязательна при отмене занятия"
                })
        
        # Получаем обратную связь (новую или существующую)
        feedback = attrs.get('feedback')
        if feedback is None:
            if self.instance:
                feedback = getattr(self.instance, 'feedback', '') or ''
            else:
                feedback = ''
        elif feedback == '':
            feedback = ''
        attrs['feedback'] = feedback
        
        # Если статус меняется на DONE, нужна обратная связь
        if status_changed and final_status == Lesson.STATUS_DONE:
            if not feedback or not feedback.strip():
                raise serializers.ValidationError({
                    "feedback": "Обратная связь обязательна при завершении занятия"
                })
        
        return attrs


class ManagerBalanceSerializer(serializers.ModelSerializer):
    student_email = serializers.EmailField(source="student.email", read_only=True)

    class Meta:
        model = LessonBalance
        fields = ("student", "student_email", "lessons_available", "updated_at")


class ManagerPaymentSerializer(serializers.ModelSerializer):
    student_email = serializers.EmailField(source="student.email", read_only=True)

    class Meta:
        model = Payment
        fields = ("id", "student", "student_email", "amount", "package_name", "paid_at", "confirmed")


# ===== ОБРАЩЕНИЯ КЛИЕНТОВ =====

class ClientRequestCreateSerializer(serializers.ModelSerializer):
    """
    Создание обращения клиентом.
    """
    class Meta:
        model = ClientRequest
        fields = ("comment",)

    def create(self, validated_data):
        # Автоматически устанавливаем клиента из request.user
        validated_data['client'] = self.context['request'].user
        return super().create(validated_data)


class ClientRequestSerializer(serializers.ModelSerializer):
    """
    Сериализатор для просмотра обращений (менеджер).
    """
    client_email = serializers.EmailField(source="client.email", read_only=True)
    manager_email = serializers.EmailField(source="manager.email", read_only=True, allow_null=True)

    class Meta:
        model = ClientRequest
        fields = (
            "id",
            "client",
            "client_email",
            "comment",
            "status",
            "manager",
            "manager_email",
            "created_at",
            "responded_at",
        )


class ClientRequestUpdateSerializer(serializers.ModelSerializer):
    """
    Обновление статуса обращения менеджером.
    """
    class Meta:
        model = ClientRequest
        fields = ("status",)

    def update(self, instance, validated_data):
        new_status = validated_data.get('status')
        
        # Если статус меняется на RESPONDED, фиксируем менеджера и время
        if new_status == ClientRequest.STATUS_RESPONDED and instance.status != ClientRequest.STATUS_RESPONDED:
            from django.utils import timezone
            validated_data['manager'] = self.context['request'].user
            validated_data['responded_at'] = timezone.now()
        
        return super().update(instance, validated_data)
