from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Course, LessonBalance, Payment, ClientRequest

User = get_user_model()


class ApplicantCourseSerializer(serializers.ModelSerializer):
    """Публичный сериализатор для курса (название и описание)"""
    class Meta:
        model = Course
        fields = ("id", "title", "description")


class ApplicantBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonBalance
        fields = ("lessons_available", "updated_at")


class ApplicantPaymentCreateSerializer(serializers.Serializer):
    """
    То, что абитуриент отправляет при "оплате":
    - id курса
    - сумма
    - название пакета (опционально)
    """
    course_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    package_name = serializers.CharField(max_length=120, required=False, allow_blank=True)

    def validate_course_id(self, value):
        from .models import Course
        if not Course.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Курс не найден")
        return value


class ApplicantPaymentSerializer(serializers.ModelSerializer):
    """
    Просмотр истории оплат самим абитуриентом.
    """
    class Meta:
        model = Payment
        fields = ("id", "amount", "package_name", "paid_at", "confirmed")


class ApplicantClientRequestCreateSerializer(serializers.ModelSerializer):
    """
    Создание обращения к менеджеру абитуриентом.
    """
    class Meta:
        model = ClientRequest
        fields = ("comment",)

    def create(self, validated_data):
        # Автоматически устанавливаем клиента из request.user
        validated_data['client'] = self.context['request'].user
        return super().create(validated_data)
