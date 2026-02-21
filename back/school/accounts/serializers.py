from django.contrib.auth import get_user_model
from rest_framework import serializers
from io import BytesIO
from pathlib import Path

from django.core.files.uploadedfile import InMemoryUploadedFile
try:
    from PIL import Image
except ImportError:
    Image = None

User = get_user_model()

MAX_AVATAR_SIDE = 512
MAX_PHOTO_SIZE_BYTES = 2 * 1024 * 1024
MAX_GIF_SIZE_BYTES = 5 * 1024 * 1024
ALLOWED_PHOTO_FORMATS = {"JPEG", "PNG", "WEBP"}
ALLOWED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "email", "phone", "student_full_name", "parent_full_name",
            "password"
        )

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Пароль должен содержать минимум 8 символов")
        return value

    def create(self, validated):
        user = User(
            email=validated["email"].lower(),
            username=validated["email"].lower(),
            phone=validated.get("phone", ""),
            student_full_name=validated.get("student_full_name", ""),
            parent_full_name=validated.get("parent_full_name", ""),
            role=User.Roles.APPLICANT,  # по умолчанию — абитуриент
        )
        user.set_password(validated["password"])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class MeSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ("id", "email", "phone", "student_full_name",
                  "parent_full_name", "role", "role_display", "is_staff", "is_superuser", "avatar", "avatar_url")

    def get_avatar_url(self, obj):
        if not obj.avatar:
            return None
        request = self.context.get("request")
        if request is None:
            return obj.avatar.url
        return request.build_absolute_uri(obj.avatar.url)


class UpdateProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления профиля пользователя"""
    avatar_clear = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta:
        model = User
        fields = ("email", "phone", "student_full_name", "parent_full_name", "avatar", "avatar_clear")
        extra_kwargs = {
            "avatar": {"required": False, "allow_null": True},
        }
    
    def validate_email(self, value):
        # Проверяем, что email уникален (кроме текущего пользователя)
        user = self.instance
        if User.objects.filter(email=value.lower()).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value.lower()

    def validate_avatar(self, value):
        if value is None:
            return value

        file_name = getattr(value, "name", "avatar")
        suffix = Path(file_name).suffix.lower()

        if suffix not in ALLOWED_SUFFIXES:
            raise serializers.ValidationError("Поддерживаются JPG, PNG, WEBP и GIF")

        if Image is None:
            if suffix == ".gif":
                if value.size > MAX_GIF_SIZE_BYTES:
                    raise serializers.ValidationError("GIF должен быть не больше 5 МБ")
            else:
                if value.size > MAX_PHOTO_SIZE_BYTES:
                    raise serializers.ValidationError("Фото должно быть не больше 2 МБ")
            return value

        if suffix == ".gif":
            if value.size > MAX_GIF_SIZE_BYTES:
                raise serializers.ValidationError("GIF должен быть не больше 5 МБ")

            try:
                image = Image.open(value)
                width, height = image.size
                if image.format != "GIF":
                    raise serializers.ValidationError("Для анимированного аватара поддерживается только GIF")
                if width > MAX_AVATAR_SIDE or height > MAX_AVATAR_SIDE:
                    raise serializers.ValidationError("GIF должен быть не больше 512x512 пикселей")
            except serializers.ValidationError:
                raise
            except Exception:
                raise serializers.ValidationError("Не удалось обработать GIF файл")
            finally:
                value.seek(0)

            return value

        if value.size > MAX_PHOTO_SIZE_BYTES:
            raise serializers.ValidationError("Фото должно быть не больше 2 МБ")

        try:
            image = Image.open(value)
            image.load()
            if image.format not in ALLOWED_PHOTO_FORMATS:
                raise serializers.ValidationError("Поддерживаются JPG, PNG и WEBP")
        except serializers.ValidationError:
            raise
        except Exception:
            raise serializers.ValidationError("Не удалось обработать изображение")
        finally:
            value.seek(0)

        if image.mode not in ("RGB",):
            image = image.convert("RGB")

        resampling = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
        image.thumbnail((MAX_AVATAR_SIDE, MAX_AVATAR_SIDE), resampling)

        output = BytesIO()
        image.save(output, format="WEBP", quality=82, optimize=True)
        output.seek(0)

        output_name = f"{Path(file_name).stem}.webp"
        return InMemoryUploadedFile(
            output,
            field_name="avatar",
            name=output_name,
            content_type="image/webp",
            size=output.getbuffer().nbytes,
            charset=None,
        )

    def update(self, instance, validated_data):
        old_avatar = instance.avatar if instance.avatar else None
        has_new_avatar = "avatar" in validated_data and validated_data.get("avatar") is not None
        avatar_clear = validated_data.pop("avatar_clear", False)
        if avatar_clear and instance.avatar:
            instance.avatar.delete(save=False)
            instance.avatar = None

        updated_instance = super().update(instance, validated_data)

        if has_new_avatar and old_avatar:
            new_avatar = updated_instance.avatar
            old_name = getattr(old_avatar, "name", "")
            new_name = getattr(new_avatar, "name", "")
            if old_name and old_name != new_name:
                old_avatar.delete(save=False)

        return updated_instance


class ChangePasswordSerializer(serializers.Serializer):
    """Смена пароля: старый пароль + новый (мин. 8 символов)"""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Неверный текущий пароль")
        return value

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Пароль должен содержать минимум 8 символов")
        return value
