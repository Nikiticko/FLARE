import json
import logging
from contextvars import ContextVar
from datetime import datetime, timezone


request_id_ctx = ContextVar("request_id", default=None)
request_meta_ctx = ContextVar("request_meta", default={})


RESERVED_LOG_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
}


def set_request_context(request_id=None, **meta):
    request_id_ctx.set(request_id)
    request_meta_ctx.set({k: v for k, v in meta.items() if v is not None})


def clear_request_context():
    request_id_ctx.set(None)
    request_meta_ctx.set({})


def get_request_id():
    return request_id_ctx.get()


def get_request_meta():
    return dict(request_meta_ctx.get() or {})


def merge_request_meta(**meta):
    current = get_request_meta()
    current.update({k: v for k, v in meta.items() if v is not None})
    request_meta_ctx.set(current)


def _iso_timestamp(record):
    return datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()


class RequestContextFilter(logging.Filter):
    def filter(self, record):
        request_id = get_request_id()
        meta = get_request_meta()

        if request_id and not getattr(record, "request_id", None):
            record.request_id = request_id

        for key, value in meta.items():
            if value is not None and not hasattr(record, key):
                setattr(record, key, value)

        return True


class StructuredJSONFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "timestamp": _iso_timestamp(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        event = getattr(record, "event", None)
        if event:
            payload["event"] = event

        request_id = getattr(record, "request_id", None)
        if request_id:
            payload["request_id"] = request_id

        for key, value in record.__dict__.items():
            if key in RESERVED_LOG_ATTRS or key.startswith("_"):
                continue
            if key in payload:
                continue
            if value is None:
                continue
            payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        if record.stack_info:
            payload["stack"] = self.formatStack(record.stack_info)

        return json.dumps(payload, ensure_ascii=False, default=str)


def get_client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def get_user_meta(user):
    if not user or not getattr(user, "is_authenticated", False):
        return {
            "user_id": None,
            "user_email": None,
            "user_role": None,
            "is_authenticated": False,
        }

    return {
        "user_id": getattr(user, "id", None),
        "user_email": getattr(user, "email", None),
        "user_role": getattr(user, "role", None),
        "is_authenticated": True,
    }


def log_security_event(logger, event, message, *, level=logging.INFO, request=None, user=None, **extra):
    payload = dict(extra)

    if request is not None:
        payload.update(
            {
                "ip": get_client_ip(request),
                "method": request.method,
                "path": request.path,
                "user_agent": request.META.get("HTTP_USER_AGENT"),
            }
        )

    payload.update(get_user_meta(user))
    logger.log(level, message, extra={"event": event, **payload})
