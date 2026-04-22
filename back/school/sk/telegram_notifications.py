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


def _mask_token(token: str) -> str:
    if not token:
        return "-"
    if len(token) <= 10:
        return "***"
    return f"{token[:6]}...{token[-4:]}"


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
        "Успешная покупка\n"
        f"Email клиента: {student_email}\n"
        f"Имя родителя: {parent_full_name}\n"
        f"Количество занятий: {lessons_count}\n"
        f"Сумма: {_format_amount(amount)} RUB\n"
        f"Дата и время: {paid_at_local.strftime('%d.%m.%Y %H:%M:%S')}"
    )


def send_successful_payment_notification(payment) -> bool:
    if not _telegram_notifications_enabled():
        logger.info(
            "Telegram notification skipped: missing config payment_id=%s bot_configured=%s chat_configured=%s",
            payment.id,
            bool(getattr(settings, "TELEGRAM_BOT_TOKEN", "").strip()),
            bool(getattr(settings, "TELEGRAM_NOTIFICATIONS_CHAT_ID", "").strip()),
        )
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
    except error.HTTPError as exc:
        raw_body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        try:
            parsed_body = json.loads(raw_body) if raw_body else {"detail": "empty error response"}
        except json.JSONDecodeError:
            parsed_body = {"detail": raw_body or "invalid telegram error response"}

        logger.warning(
            "Telegram notification HTTP error: payment_id=%s status=%s chat_id=%s token=%s body=%s",
            payment.id,
            exc.code,
            chat_id,
            _mask_token(bot_token),
            parsed_body,
        )
        return False
    except error.URLError as exc:
        logger.warning(
            "Telegram notification request error: payment_id=%s chat_id=%s token=%s error=%s",
            payment.id,
            chat_id,
            _mask_token(bot_token),
            exc,
        )
        return False
    except json.JSONDecodeError as exc:
        logger.warning(
            "Telegram notification decode error: payment_id=%s chat_id=%s error=%s",
            payment.id,
            chat_id,
            exc,
        )
        return False

    logger.info(
        "Telegram notification sent for successful payment: payment_id=%s student_id=%s chat_id=%s",
        payment.id,
        payment.student_id,
        chat_id,
    )
    return True
