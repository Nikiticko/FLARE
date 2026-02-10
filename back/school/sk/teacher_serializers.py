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
    cancellation_reason = serializers.SerializerMethodField()
    feedback = serializers.SerializerMethodField()
    student_balance = serializers.SerializerMethodField()

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
        if obj.course:
            return obj.course.title
        return None
    
    def get_course_id(self, obj):
        """ID курса для подстановки при создании/редактировании"""
        return obj.course_id if obj.course_id else None
    
    def get_cancellation_reason(self, obj):
        """Безопасное получение причины отмены"""
        return getattr(obj, 'cancellation_reason', '')
    
    def get_feedback(self, obj):
        """Безопасное получение обратной связи"""
        return getattr(obj, 'feedback', '')
    
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
    - курс (становится курсом по умолчанию для ученика)
    """
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), required=False, allow_null=True)
    link = serializers.CharField(required=False, allow_blank=True, max_length=300)
    
    class Meta:
        model = Lesson
        fields = ("status", "comment", "link", "cancellation_reason", "feedback", "course")

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
        
        # Получаем обратную связь (новую или существующую) - безопасно через getattr
        feedback = attrs.get('feedback')
        if feedback is None:
            if self.instance:
                feedback = getattr(self.instance, 'feedback', '') or ''
            else:
                feedback = ''
        # Если передана пустая строка, сохраняем её (позволяет очистить поле)
        elif feedback == '':
            feedback = ''
        # Обновляем attrs с актуальным значением
        attrs['feedback'] = feedback
        
        # Если статус меняется на CANCELLED, нужна причина отмены
        if status_changed and final_status == Lesson.STATUS_CANCELLED:
            if not cancellation_reason or not cancellation_reason.strip():
                raise serializers.ValidationError({
                    "cancellation_reason": "Причина отмены обязательна при отмене занятия"
                })
        
        # Если статус меняется на DONE, нужна обратная связь
        if status_changed and final_status == Lesson.STATUS_DONE:
            if not feedback or not feedback.strip():
                raise serializers.ValidationError({
                    "feedback": "Обратная связь обязательна при завершении занятия"
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
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), required=False, allow_null=True)
    link = serializers.CharField(required=False, allow_blank=True, default="Discord", max_length=300)
    comment = serializers.CharField(required=False, allow_blank=True)
    scheduled_at = serializers.DateTimeField(required=True)

    class Meta:
        model = Lesson
        fields = ("student", "student_email", "course", "scheduled_at", "link", "comment")

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
