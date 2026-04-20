import logging

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.middleware.csrf import get_token

from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from school.logging_utils import log_security_event
from sk.models import AuditLog

from .cookie_utils import clear_auth_cookies, issue_tokens_for_user, set_auth_cookies
from .serializers import (
    AdminLoginSerializer,
    ChangePasswordSerializer,
    LoginSerializer,
    MeSerializer,
    RegisterSerializer,
    UpdateProfileSerializer,
)

User = get_user_model()

auth_logger = logging.getLogger("school.auth")
security_logger = logging.getLogger("school.security")


def _write_auth_audit(action, *, actor=None, **meta):
    AuditLog.objects.create(actor=actor, action=action, meta=meta)


class RegisterAPI(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = issue_tokens_for_user(user)

        log_security_event(
            auth_logger,
            "auth.register.success",
            "User registered successfully",
            request=request,
            user=user,
            registered_user_id=user.id,
        )
        _write_auth_audit(
            "AUTH_REGISTER_SUCCESS",
            actor=user,
            registered_user_id=user.id,
            email=user.email,
            role=user.role,
        )

        response = Response(
            {"user": MeSerializer(user, context={"request": request}).data},
            status=status.HTTP_201_CREATED,
        )
        return set_auth_cookies(
            response,
            request,
            access_token=tokens["access"],
            refresh_token=tokens["refresh"],
        )


class LoginAPI(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"].lower()
        password = serializer.validated_data["password"]
        user = authenticate(username=email, password=password)

        if not user:
            log_security_event(
                security_logger,
                "auth.login.failed",
                "Login failed",
                level=logging.WARNING,
                request=request,
                login_email=email,
                reason="invalid_credentials",
            )
            _write_auth_audit(
                "AUTH_LOGIN_FAILED",
                email=email,
                reason="invalid_credentials",
            )
            return Response({"detail": "Неверный email или пароль"}, status=400)

        tokens = issue_tokens_for_user(user)
        log_security_event(
            auth_logger,
            "auth.login.success",
            "Login succeeded",
            request=request,
            user=user,
            login_email=email,
        )
        _write_auth_audit(
            "AUTH_LOGIN_SUCCESS",
            actor=user,
            email=user.email,
            role=user.role,
        )

        response = Response({"user": MeSerializer(user, context={"request": request}).data})
        return set_auth_cookies(
            response,
            request,
            access_token=tokens["access"],
            refresh_token=tokens["refresh"],
        )


class AdminLoginAPI(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"].lower()
        password = serializer.validated_data["password"]
        whitelist = getattr(settings, "ADMIN_SEED_EMAILS", [])

        if email not in whitelist:
            log_security_event(
                security_logger,
                "auth.admin_login.failed",
                "Admin login rejected by whitelist",
                level=logging.WARNING,
                request=request,
                login_email=email,
                reason="email_not_allowed",
            )
            _write_auth_audit(
                "AUTH_ADMIN_LOGIN_FAILED",
                email=email,
                reason="email_not_allowed",
            )
            return Response({"detail": "Email не разрешён для админ-входа"}, status=403)

        user = User.objects.filter(email=email).first()
        count_whitelist_su = User.objects.filter(email__in=whitelist, is_superuser=True).count()

        if user is None:
            if count_whitelist_su >= 2:
                log_security_event(
                    security_logger,
                    "auth.admin_login.failed",
                    "Admin login rejected by whitelist limit",
                    level=logging.WARNING,
                    request=request,
                    login_email=email,
                    reason="admin_limit_reached",
                )
                _write_auth_audit(
                    "AUTH_ADMIN_LOGIN_FAILED",
                    email=email,
                    reason="admin_limit_reached",
                )
                return Response({"detail": "Лимит админов исчерпан"}, status=403)

            user = User.objects.create_user(
                email=email,
                username=email,
                password=password,
                role=User.Roles.ADMIN,
                is_staff=True,
                is_superuser=True,
            )
        else:
            auth_user = authenticate(username=email, password=password)
            if not auth_user:
                log_security_event(
                    security_logger,
                    "auth.admin_login.failed",
                    "Admin login failed",
                    level=logging.WARNING,
                    request=request,
                    login_email=email,
                    reason="invalid_credentials",
                )
                _write_auth_audit(
                    "AUTH_ADMIN_LOGIN_FAILED",
                    email=email,
                    reason="invalid_credentials",
                )
                return Response({"detail": "Неверный пароль"}, status=400)

            if user.email in whitelist and not user.is_superuser:
                if count_whitelist_su >= 2:
                    log_security_event(
                        security_logger,
                        "auth.admin_login.failed",
                        "Admin privilege escalation blocked by whitelist limit",
                        level=logging.WARNING,
                        request=request,
                        login_email=email,
                        reason="admin_limit_reached",
                    )
                    _write_auth_audit(
                        "AUTH_ADMIN_LOGIN_FAILED",
                        email=email,
                        reason="admin_limit_reached",
                    )
                    return Response({"detail": "Лимит админов исчерпан"}, status=403)

                user.is_superuser = True
                user.is_staff = True
                user.role = User.Roles.ADMIN
                user.save()

        tokens = issue_tokens_for_user(user)
        log_security_event(
            auth_logger,
            "auth.admin_login.success",
            "Admin login succeeded",
            request=request,
            user=user,
            login_email=email,
        )
        _write_auth_audit(
            "AUTH_ADMIN_LOGIN_SUCCESS",
            actor=user,
            email=user.email,
            role=user.role,
        )

        response = Response({"user": MeSerializer(user, context={"request": request}).data})
        return set_auth_cookies(
            response,
            request,
            access_token=tokens["access"],
            refresh_token=tokens["refresh"],
        )


class MeAPI(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        log_security_event(
            auth_logger,
            "auth.me.success",
            "Fetched current user profile",
            request=request,
            user=request.user,
        )
        return Response(MeSerializer(request.user, context={"request": request}).data)

    def patch(self, request):
        serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        updated_fields = sorted(serializer.validated_data.keys())
        log_security_event(
            auth_logger,
            "auth.me.updated",
            "Updated current user profile",
            request=request,
            user=request.user,
            updated_fields=updated_fields,
        )
        _write_auth_audit(
            "AUTH_PROFILE_UPDATED",
            actor=request.user,
            updated_fields=updated_fields,
        )

        return Response(MeSerializer(request.user, context={"request": request}).data)


class VerifyPasswordAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_password = request.data.get("old_password")
        if not old_password:
            return Response({"detail": "Введите текущий пароль"}, status=400)

        if request.user.check_password(old_password):
            log_security_event(
                auth_logger,
                "auth.password.verify.success",
                "Password verification succeeded",
                request=request,
                user=request.user,
            )
            return Response({"valid": True})

        log_security_event(
            security_logger,
            "auth.password.verify.failed",
            "Password verification failed",
            level=logging.WARNING,
            request=request,
            user=request.user,
            reason="invalid_password",
        )
        return Response({"detail": "Неверный пароль"}, status=400)


class ChangePasswordAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()

        log_security_event(
            auth_logger,
            "auth.password.changed",
            "Password changed successfully",
            request=request,
            user=request.user,
        )
        _write_auth_audit("AUTH_PASSWORD_CHANGED", actor=request.user)
        return Response({"detail": "Пароль успешно изменён"})


class CSRFTokenAPI(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        log_security_event(
            auth_logger,
            "auth.csrf.issued",
            "Issued CSRF token",
            request=request,
            user=getattr(request, "user", None),
        )
        return Response({"csrfToken": get_token(request)})


class CookieTokenRefreshAPI(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH_NAME)
        if not refresh_token:
            log_security_event(
                security_logger,
                "auth.token.refresh.failed",
                "Refresh token missing",
                level=logging.WARNING,
                request=request,
                reason="missing_refresh_cookie",
            )
            _write_auth_audit(
                "AUTH_TOKEN_REFRESH_FAILED",
                reason="missing_refresh_cookie",
            )
            response = Response({"detail": "refresh token required"}, status=401)
            return clear_auth_cookies(response)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
        except TokenError:
            log_security_event(
                security_logger,
                "auth.token.refresh.failed",
                "Refresh token rejected",
                level=logging.WARNING,
                request=request,
                reason="invalid_or_expired_refresh_token",
            )
            _write_auth_audit(
                "AUTH_TOKEN_REFRESH_FAILED",
                reason="invalid_or_expired_refresh_token",
            )
            response = Response({"detail": "token is invalid or expired"}, status=401)
            return clear_auth_cookies(response)

        user = None
        try:
            user = refresh.user
        except Exception:
            user = None

        log_security_event(
            auth_logger,
            "auth.token.refresh.success",
            "Access token refreshed",
            request=request,
            user=user,
        )
        _write_auth_audit(
            "AUTH_TOKEN_REFRESH_SUCCESS",
            actor=user,
            user_id=getattr(user, "id", None),
        )

        response = Response({"detail": "ok"})
        return set_auth_cookies(
            response,
            request,
            access_token=access_token,
            refresh_token=refresh_token,
        )


class LogoutAPI(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        actor = request.user if getattr(request.user, "is_authenticated", False) else None
        refresh_token = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH_NAME)

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                log_security_event(
                    security_logger,
                    "auth.logout.blacklist_failed",
                    "Failed to blacklist refresh token during logout",
                    level=logging.WARNING,
                    request=request,
                    user=actor,
                )

        log_security_event(
            auth_logger,
            "auth.logout",
            "Logout completed",
            request=request,
            user=actor,
        )
        _write_auth_audit(
            "AUTH_LOGOUT",
            actor=actor,
            user_id=getattr(actor, "id", None),
        )

        response = Response({"detail": "ok"})
        return clear_auth_cookies(response)
