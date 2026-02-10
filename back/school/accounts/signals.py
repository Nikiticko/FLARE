from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.conf import settings
import os


@receiver(post_migrate)
def create_root_admin(sender, **kwargs):
    """
    Создание 'вшитого' администратора при первом запуске.
    Пароль можно задать через переменную окружения ROOT_ADMIN_PASSWORD,
    иначе используется безопасный дефолтный пароль.
    
    Также можно создать второго админа из ADMIN_SEED_EMAILS через переменную
    окружения ADMIN2_PASSWORD (только если его ещё нет).
    """
    User = get_user_model()
    root_email = getattr(settings, "ROOT_ADMIN_EMAIL", None)

    # Создание Root Admin
    if root_email:
        # Получаем пароль из переменной окружения или используем дефолтный
        default_password = os.getenv("ROOT_ADMIN_PASSWORD", "ChangeMe123!@#")
        
        user, created = User.objects.get_or_create(
            email=root_email,
            defaults={
                "username": root_email.lower(),
                "role": User.Roles.ADMIN,
                "is_staff": True,
                "is_superuser": True,
            }
        )
        
        if created:
            user.set_password(default_password)
            user.save()
            print(f"✓ Root admin создан: {root_email}")
            print(f"⚠ ВАЖНО: Смените пароль после первого входа!")
        else:
            # Обновляем права существующего пользователя, если они были изменены
            if user.role != User.Roles.ADMIN or not user.is_staff or not user.is_superuser:
                user.role = User.Roles.ADMIN
                user.is_staff = True
                user.is_superuser = True
                # Убеждаемся, что username = email
                if not user.username or user.username != root_email.lower():
                    user.username = root_email.lower()
                user.save()

    # Создание второго админа из белого списка (если задан пароль через переменную окружения)
    seed_emails = getattr(settings, "ADMIN_SEED_EMAILS", [])
    if len(seed_emails) > 1:
        admin2_email = seed_emails[1]  # Второй из списка
        admin2_password = os.getenv("ADMIN2_PASSWORD", None)
        
        if admin2_password:
            # Проверяем лимит суперпользователей
            count_whitelist_su = User.objects.filter(
                email__in=seed_emails, is_superuser=True
            ).count()
            
            if count_whitelist_su < 2:
                user2, created2 = User.objects.get_or_create(
                    email=admin2_email,
                    defaults={
                        "username": admin2_email.lower(),
                        "role": User.Roles.ADMIN,
                        "is_staff": True,
                        "is_superuser": True,
                    }
                )
                
                if created2:
                    user2.set_password(admin2_password)
                    user2.save()
                    print(f"✓ Второй админ создан: {admin2_email}")
                elif not user2.is_superuser and count_whitelist_su < 2:
                    # Повышаем до админа, если ещё есть место
                    user2.role = User.Roles.ADMIN
                    user2.is_staff = True
                    user2.is_superuser = True
                    user2.set_password(admin2_password)
                    user2.save()
                    print(f"✓ Второй админ повышен до суперпользователя: {admin2_email}")
