# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'ADMIN', 'Администратор'
        MANAGER = 'MANAGER', 'Менеджер'
        TEACHER = 'TEACHER', 'Учитель'
        STUDENT = 'STUDENT', 'Ученик'
        APPLICANT = 'APPLICANT', 'Абитуриент'

    # по ТЗ — добавляем поля
    email = models.EmailField('Email', unique=True)
    phone = models.CharField('Телефон', max_length=32, blank=True)
    student_full_name = models.CharField('ФИО ученика', max_length=255, blank=True)
    parent_full_name = models.CharField('ФИО родителя', max_length=255, blank=True)
    parent_password_hash = models.CharField('Хеш пароля родителя', max_length=255, blank=True)
    avatar = models.FileField('Аватар', upload_to='avatars/%Y/%m/', blank=True, null=True)

    role = models.CharField(
        'Роль',
        max_length=20,
        choices=Roles.choices,
        default=Roles.APPLICANT,
    )

    def save(self, *args, **kwargs):
        # гарантируем username=email (чтобы можно было логиниться через стандартный backend)
        if self.email and self.username != self.email:
            self.username = self.email
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.email} ({self.get_role_display()})'
