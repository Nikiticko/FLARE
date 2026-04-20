import logging
import time
import uuid

from .logging_utils import (
    clear_request_context,
    get_client_ip,
    get_user_meta,
    merge_request_meta,
    set_request_context,
)


request_logger = logging.getLogger("school.request")
error_logger = logging.getLogger("school.error")


class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        started_at = time.perf_counter()

        request.request_id = request_id
        set_request_context(
            request_id=request_id,
            method=request.method,
            path=request.path,
            ip=get_client_ip(request),
        )

        try:
            response = self.get_response(request)
        except Exception:
            duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
            error_logger.exception(
                "Unhandled backend exception",
                extra={
                    "event": "http.unhandled_exception",
                    "status_code": 500,
                    "duration_ms": duration_ms,
                    **get_user_meta(getattr(request, "user", None)),
                },
            )
            raise
        else:
            duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
            status_code = getattr(response, "status_code", 200)
            response["X-Request-ID"] = request_id

            merge_request_meta(status_code=status_code, duration_ms=duration_ms)

            level = logging.INFO
            if status_code >= 500:
                level = logging.ERROR
            elif status_code >= 400 or duration_ms >= 1000:
                level = logging.WARNING

            request_logger.log(
                level,
                f"{request.method} {request.path} -> {status_code}",
                extra={
                    "event": "http.request",
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                    "query_params": dict(request.GET.lists()),
                    **get_user_meta(getattr(request, "user", None)),
                },
            )
            return response
        finally:
            clear_request_context()
