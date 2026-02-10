from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import LessonBalance, StudentProfile

User = settings.AUTH_USER_MODEL

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_balance_for_student(sender, instance, created, **kwargs):
    if created:
        # Создаём баланс только для будущего студента/абитуриента
        LessonBalance.objects.get_or_create(student=instance)
        StudentProfile.objects.get_or_create(user=instance)
