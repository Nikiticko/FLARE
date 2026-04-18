from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.middleware.csrf import get_token

from rest_framework import status
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .cookie_utils import issue_tokens_for_user, set_auth_cookies, clear_auth_cookies
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    AdminLoginSerializer,
    MeSerializer,
    UpdateProfileSerializer,
    ChangePasswordSerializer,
)

User = get_user_model()


class RegisterAPI(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        tokens = issue_tokens_for_user(user)
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
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data["email"].lower()
        password = ser.validated_data["password"]
        user = authenticate(username=email, password=password)
        if not user:
            return Response({"detail": "Неверный email или пароль"}, status=400)

        tokens = issue_tokens_for_user(user)
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
        ser = AdminLoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data["email"].lower()
        password = ser.validated_data["password"]

        whitelist = getattr(settings, "ADMIN_SEED_EMAILS", [])
        if email not in whitelist:
            return Response({"detail": "Email не разрешён для админ-входа"}, status=403)

        user = User.objects.filter(email=email).first()
        count_whitelist_su = User.objects.filter(email__in=whitelist, is_superuser=True).count()

        if user is None:
            if count_whitelist_su >= 2:
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
                return Response({"detail": "Неверный пароль"}, status=400)
            if user.email in whitelist and not user.is_superuser:
                if count_whitelist_su >= 2:
                    return Response({"detail": "Лимит админов исчерпан"}, status=403)
                user.is_superuser = True
                user.is_staff = True
                user.role = User.Roles.ADMIN
                user.save()

        tokens = issue_tokens_for_user(user)
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
        return Response(MeSerializer(request.user, context={"request": request}).data)

    def patch(self, request):
        serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(MeSerializer(request.user, context={"request": request}).data)


class VerifyPasswordAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_password = request.data.get("old_password")
        if not old_password:
            return Response({"detail": "Введите текущий пароль"}, status=400)
        if request.user.check_password(old_password):
            return Response({"valid": True})
        return Response({"detail": "Неверный пароль"}, status=400)


class ChangePasswordAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = ChangePasswordSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        request.user.set_password(ser.validated_data["new_password"])
        request.user.save()
        return Response({"detail": "Пароль успешно изменён"})


class CSRFTokenAPI(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response({"csrfToken": get_token(request)})


class CookieTokenRefreshAPI(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH_NAME)
        if not refresh_token:
            response = Response({"detail": "refresh token required"}, status=401)
            return clear_auth_cookies(response)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
        except TokenError:
            response = Response({"detail": "token is invalid or expired"}, status=401)
            return clear_auth_cookies(response)

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
        refresh_token = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH_NAME)
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass

        response = Response({"detail": "ok"})
        return clear_auth_cookies(response)
