import json
import logging
from decimal import Decimal
from urllib import error, parse, request as urllib_request

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def _telegram_notifications_enabled() -> bool:
    bot_token = getattr(settings, "TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = getattr(settings, "TELEGRAM_NOTIFICATIONS_CHAT_ID", "").strip()
    return bool(bot_token and chat_id)


def _format_amount(amount: Decimal) -> str:
    return f"{amount:.2f}".replace(".", ",")


def build_successful_payment_message(payment) -> str:
    student = getattr(payment, "student", None)
    student_email = getattr(student, "email", "") or "-"
    parent_full_name = getattr(student, "parent_full_name", "") or "-"
    lessons_count = int(getattr(payment, "lessons_count", 0) or 0)
    amount = getattr(payment, "amount", Decimal("0.00")) or Decimal("0.00")
    paid_at = getattr(payment, "paid_at", None) or timezone.now()
    paid_at_local = timezone.localtime(paid_at)

    return (
        "Успешная автопокупка занятий\n"
        f"Email клиента: {student_email}\n"
        f"ФИО родителя: {parent_full_name}\n"
        f"Количество занятий: {lessons_count}\n"
        f"Сумма: {_format_amount(amount)} RUB\n"
        f"Дата и время: {paid_at_local.strftime('%d.%m.%Y %H:%M:%S')}"
    )


def send_successful_payment_notification(payment) -> bool:
    if not _telegram_notifications_enabled():
        return False

    bot_token = settings.TELEGRAM_BOT_TOKEN.strip()
    chat_id = settings.TELEGRAM_NOTIFICATIONS_CHAT_ID.strip()
    timeout_seconds = int(getattr(settings, "TELEGRAM_NOTIFICATIONS_TIMEOUT_SECONDS", 10))
    message = build_successful_payment_message(payment)
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = parse.urlencode(
        {
            "chat_id": chat_id,
            "text": message,
        }
    ).encode("utf-8")
    req = urllib_request.Request(url=url, data=payload, method="POST")

    try:
        with urllib_request.urlopen(req, timeout=max(1, timeout_seconds)) as resp:
            response_body = resp.read().decode("utf-8")
            parsed = json.loads(response_body) if response_body else {}
            if resp.status >= 400 or not parsed.get("ok", False):
                logger.warning(
                    "Telegram notification failed: status=%s body=%s payment_id=%s",
                    resp.status,
                    parsed,
                    payment.id,
                )
                return False
    except error.URLError as exc:
        logger.warning(
            "Telegram notification request error: payment_id=%s error=%s",
            payment.id,
            exc,
        )
        return False
    except json.JSONDecodeError as exc:
        logger.warning(
            "Telegram notification decode error: payment_id=%s error=%s",
            payment.id,
            exc,
        )
        return False

    logger.info(
        "Telegram notification sent for successful payment: payment_id=%s student_id=%s",
        payment.id,
        payment.student_id,
    )
    return True
