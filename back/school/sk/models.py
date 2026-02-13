from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Payment(models.Model):
    """
    Оплата от ученика (или его родителя).
    Менеджер/админ после оплаты подтверждает её и начисляет занятия на баланс.
    """
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    package_name = models.CharField(
        max_length=120,
        blank=True,
        help_text="Название пакета/тарифа",
    )
    paid_at = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(
        default=False,
        help_text="Оплата подтверждена (начислены занятия)",
    )
    lessons_count = models.PositiveIntegerField(
        default=0,
        help_text="Количество купленных занятий",
    )
    yookassa_payment_id = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        help_text="ID платежа в ЮKassa",
    )
    yookassa_status = models.CharField(
        max_length=32,
        blank=True,
        help_text="Текущий статус платежа в ЮKassa",
    )
    idempotence_key = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        help_text="Ключ идемпотентности запроса в ЮKassa",
    )

    def __str__(self):
        return f"Payment(id={self.id}, student={self.student}, amount={self.amount}, confirmed={self.confirmed})"


class LessonBalance(models.Model):
    """
    Баланс доступных занятий у ученика.
    """
    student = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="lesson_balance",
    )
    lessons_available = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"LessonBalance(student={self.student}, lessons_available={self.lessons_available})"


class Lesson(models.Model):
    """
    Урок / занятие.

    Через него мы:
    - строим расписание,
    - считаем отчёты,
    - списываем занятия с баланса.
    """

    STATUS_PLANNED = "PLANNED"
    STATUS_DONE = "DONE"
    STATUS_CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (STATUS_PLANNED, "Запланировано"),
        (STATUS_DONE, "Проведено"),
        (STATUS_CANCELLED, "Отменено"),
    ]

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="lessons_as_student",
    )
    # ФИО родителя фиксируем на момент создания урока
    parent_full_name = models.CharField(max_length=255, blank=True)

    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lessons_as_teacher",
    )

    course = models.ForeignKey(
        'Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lessons",
        help_text="Курс, по которому проводится занятие",
    )

    link = models.CharField(
        max_length=300,
        blank=True,
        help_text="Ссылка на урок (Zoom/Discord/и т.п.)",
    )

    scheduled_at = models.DateTimeField(
        help_text="Дата и время начала урока",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PLANNED,
    )

    comment = models.TextField(blank=True)
    cancellation_reason = models.TextField(
        blank=True,
        help_text="Причина отмены занятия (заполняется при статусе CANCELLED)",
    )
    feedback = models.TextField(
        blank=True,
        help_text="Обратная связь по занятию (заполняется при статусе DONE)",
    )
    debited_from_balance = models.BooleanField(
        default=False,
        help_text="True, если занятие уже списано с баланса",
    )
    is_trial = models.BooleanField(
        default=False,
        help_text="True, если это пробное занятие (не списывается с баланса)",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lesson(id={self.id}, student={self.student}, teacher={self.teacher}, at={self.scheduled_at}, status={self.status})"


class AuditLog(models.Model):
    """
    Лог действий админов/менеджеров/учителей.
    Можно потом строить историю изменений.
    """
    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_actions",
    )
    action = models.CharField(max_length=120)
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"AuditLog(action={self.action}, actor={self.actor}, created_at={self.created_at})"


class Course(models.Model):
    """
    Курс. Содержит название и описание с разметкой (переносы строк сохраняются).
    """
    title = models.CharField(max_length=200)
    description = models.TextField(
        blank=True,
        help_text="Описание курса с разметкой. Переносы строк и форматирование сохраняются.",
    )
    # ВРЕМЕННО УБРАНО: created_at и updated_at будут добавлены после применения миграций
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.title


class StudentProfile(models.Model):
    """
    Профиль ученика для геймификации (уровень, XP, внутренняя валюта сезона).
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    level = models.PositiveIntegerField(default=1)
    xp = models.PositiveIntegerField(default=0)
    season_currency = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"StudentProfile({self.user}): lvl={self.level}, xp={self.xp}"


class ClientRequest(models.Model):
    """
    Обращение клиента (абитуриента/ученика) к менеджеру.
    """
    STATUS_SENT = "SENT"
    STATUS_RESPONDED = "RESPONDED"

    STATUS_CHOICES = [
        (STATUS_SENT, "Отправлено"),
        (STATUS_RESPONDED, "Есть реакция на обращение"),
    ]

    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="client_requests",
        help_text="Клиент, который отправил обращение",
    )
    comment = models.TextField(
        blank=True,
        help_text="Комментарий клиента (необязательное поле)",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_SENT,
        help_text="Статус обращения",
    )
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="responded_requests",
        help_text="Менеджер, который отреагировал на обращение",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Дата и время реакции менеджера",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Обращение клиента"
        verbose_name_plural = "Обращения клиентов"

    def __str__(self):
        return f"ClientRequest(id={self.id}, client={self.client.email}, status={self.status})"
