from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Course, Lesson, LessonBalance, Payment, StudentProfile, ClientRequest

User = get_user_model()


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ("level", "xp", "season_currency")


class StudentDashboardSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    student_full_name = serializers.CharField()
    role = serializers.CharField()
    balance = serializers.IntegerField()
    level = serializers.IntegerField()
    xp = serializers.IntegerField()
    season_currency = serializers.IntegerField()
    avatar = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    avatar_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class UnifiedDashboardSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    student_full_name = serializers.CharField()
    role = serializers.CharField()
    balance = serializers.IntegerField()
    level = serializers.IntegerField(required=False, allow_null=True)
    xp = serializers.IntegerField(required=False, allow_null=True)
    season_currency = serializers.IntegerField(required=False, allow_null=True)
    avatar = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    avatar_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class StudentCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ("id", "title", "description")


class StudentLessonSerializer(serializers.ModelSerializer):
    teacher_email = serializers.EmailField(source="teacher.email", read_only=True)
    teacher_full_name = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    feedback = serializers.CharField(required=False, allow_blank=True, read_only=True)

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
        if obj.teacher:
            if hasattr(obj.teacher, "student_full_name") and obj.teacher.student_full_name:
                return obj.teacher.student_full_name.strip()
            first_name = getattr(obj.teacher, "first_name", "") or ""
            last_name = getattr(obj.teacher, "last_name", "") or ""
            full_name = f"{first_name} {last_name}".strip()
            if full_name:
                return full_name
            if hasattr(obj.teacher, "email") and obj.teacher.email:
                return obj.teacher.email
        return None

    def get_course(self, obj):
        course = getattr(obj, "course", None)
        if course:
            return course.title
        return None


class StudentBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonBalance
        fields = ("lessons_available", "updated_at")


class StudentPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("id", "amount", "package_name", "lessons_count", "paid_at", "confirmed")


class StudentClientRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientRequest
        fields = ("comment",)

    def create(self, validated_data):
        validated_data["client"] = self.context["request"].user
        return super().create(validated_data)
