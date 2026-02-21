from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from rest_framework import permissions, status
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    RegisterSerializer, LoginSerializer, AdminLoginSerializer, MeSerializer, UpdateProfileSerializer,
    ChangePasswordSerializer,
)

User = get_user_model()

def issue_tokens_for_user(user: User):
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }

class RegisterAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        # По UX можно сразу логинить — но в ТЗ достаточно регистрации:
        tokens = issue_tokens_for_user(user)
        return Response({
            "user": MeSerializer(user, context={"request": request}).data,
            "tokens": tokens
        }, status=status.HTTP_201_CREATED)


class LoginAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data["email"].lower()
        password = ser.validated_data["password"]
        user = authenticate(username=email, password=password)
        if not user:
            return Response({"detail": "Неверный email или пароль"}, status=400)
        tokens = issue_tokens_for_user(user)
        return Response({"user": MeSerializer(user, context={"request": request}).data, "tokens": tokens})


class AdminLoginAPI(APIView):
    """
    Спец-вход по белому списку.
    Первые 2 из белого списка получают/повышаются до ADMIN (is_superuser/is_staff).
    """
    permission_classes = [AllowAny]

    def post(self, request):
        ser = AdminLoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data["email"].lower()
        password = ser.validated_data["password"]

        whitelist = getattr(settings, "ADMIN_SEED_EMAILS", [])
        if email not in whitelist:
            return Response({"detail": "Email не разрешён для админ-входа"}, status=403)

        user = User.objects.filter(email=email).first()
        # текущих суперюзеров из белого списка
        count_whitelist_su = User.objects.filter(email__in=whitelist, is_superuser=True).count()

        if user is None:
            if count_whitelist_su >= 2:
                return Response({"detail": "Лимит админов исчерпан"}, status=403)
            user = User.objects.create_user(
                email=email, username=email, password=password,
                role=User.Roles.ADMIN, is_staff=True, is_superuser=True
            )
        else:
            # проверка пароля
            auth_user = authenticate(username=email, password=password)
            if not auth_user:
                return Response({"detail": "Неверный пароль"}, status=400)
            if (user.email in whitelist) and not user.is_superuser:
                if count_whitelist_su >= 2:
                    return Response({"detail": "Лимит админов исчерпан"}, status=403)
                user.is_superuser = True
                user.is_staff = True
                user.role = User.Roles.ADMIN
                user.save()

        tokens = issue_tokens_for_user(user)
        return Response({"user": MeSerializer(user, context={"request": request}).data, "tokens": tokens})


class MeAPI(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        return Response(MeSerializer(request.user, context={"request": request}).data)
    
    def patch(self, request):
        """Обновление профиля текущего пользователя"""
        serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(MeSerializer(request.user, context={"request": request}).data)


class VerifyPasswordAPI(APIView):
    """Проверка текущего пароля (без смены)"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_password = request.data.get("old_password")
        if not old_password:
            return Response({"detail": "Введите текущий пароль"}, status=400)
        if request.user.check_password(old_password):
            return Response({"valid": True})
        return Response({"detail": "Неверный пароль"}, status=400)


class ChangePasswordAPI(APIView):
    """Смена пароля текущего пользователя"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = ChangePasswordSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        request.user.set_password(ser.validated_data["new_password"])
        request.user.save()
        return Response({"detail": "Пароль успешно изменён"})


class LogoutAPI(APIView):
    """
    Чёрный список refresh-токена (если включишь simplejwt blacklist).
    Можно и без него: на фронте просто удалить токены из хранилища.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response({"detail": "refresh token required"}, status=400)
        try:
            token = RefreshToken(refresh)
            token.blacklist()  # сработает, если rest_framework_simplejwt.token_blacklist в INSTALLED_APPS
        except Exception:
            pass
        return Response({"detail": "ok"})
