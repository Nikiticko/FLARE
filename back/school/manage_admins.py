#!/usr/bin/env python
"""
Скрипт для управления паролями админов
Использование: python manage_admins.py
"""
import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school.settings')
django.setup()

from accounts.models import User
from django.conf import settings
from getpass import getpass


def set_admin_password(email, password=None, interactive=True):
    """Установить пароль для админа"""
    try:
        user = User.objects.get(email=email)
        
        if password is None and interactive:
            password = getpass(f"Введите новый пароль для {email}: ")
            password_confirm = getpass("Подтвердите пароль: ")
            if password != password_confirm:
                print("✗ Пароли не совпадают!")
                return False
        
        if not password:
            print("✗ Пароль не может быть пустым!")
            return False
            
        user.set_password(password)
        user.save()
        print(f"✓ Пароль для {email} успешно изменён")
        return True
    except User.DoesNotExist:
        print(f"✗ Пользователь {email} не найден")
        return False
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False


def create_admin_if_not_exists(email, password=None, role="ADMIN", is_superuser=True):
    """Создать админа, если его ещё нет"""
    try:
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email.lower(),
                "role": role,
                "is_staff": True,
                "is_superuser": is_superuser,
            }
        )
        
        if created:
            if password:
                user.set_password(password)
            else:
                password = getpass(f"Введите пароль для нового админа {email}: ")
                user.set_password(password)
            user.save()
            print(f"✓ Админ {email} создан")
            return True
        else:
            print(f"ℹ Админ {email} уже существует")
            return False
    except Exception as e:
        print(f"✗ Ошибка при создании: {e}")
        return False


def show_admins():
    """Показать список всех админов"""
    admins = User.objects.filter(role="ADMIN").order_by("email")
    
    if not admins.exists():
        print("Админы не найдены")
        return
    
    print("\n=== Список админов ===")
    for admin in admins:
        root_marker = " (ROOT)" if admin.email == getattr(settings, "ROOT_ADMIN_EMAIL", None) else ""
        superuser_marker = " [SUPERUSER]" if admin.is_superuser else ""
        print(f"  • {admin.email}{root_marker}{superuser_marker}")
        print(f"    Роль: {admin.get_role_display()}, Staff: {admin.is_staff}, Superuser: {admin.is_superuser}")
    print()


def main():
    print("=== Управление паролями админов ===\n")
    
    # Получаем настройки
    root_email = getattr(settings, "ROOT_ADMIN_EMAIL", None)
    seed_emails = getattr(settings, "ADMIN_SEED_EMAILS", [])
    
    # Показываем текущих админов
    show_admins()
    
    # Меню
    print("Выберите действие:")
    print("1. Изменить пароль для Root Admin")
    print("2. Изменить пароль для второго админа")
    print("3. Изменить пароли для обоих админов")
    print("4. Создать админа из белого списка")
    print("5. Показать список админов")
    print("0. Выход")
    
    choice = input("\nВаш выбор: ").strip()
    
    if choice == "1":
        if root_email:
            set_admin_password(root_email)
        else:
            print("✗ ROOT_ADMIN_EMAIL не настроен в settings.py")
    
    elif choice == "2":
        if len(seed_emails) > 1:
            admin2_email = seed_emails[1]  # Второй из списка
            set_admin_password(admin2_email)
        else:
            print("✗ Второй админ не настроен в ADMIN_SEED_EMAILS")
    
    elif choice == "3":
        if root_email:
            print(f"\nИзменение пароля для Root Admin ({root_email}):")
            set_admin_password(root_email)
        
        if len(seed_emails) > 1:
            admin2_email = seed_emails[1]
            print(f"\nИзменение пароля для второго админа ({admin2_email}):")
            set_admin_password(admin2_email)
    
    elif choice == "4":
        print("\nДоступные email из белого списка:")
        for i, email in enumerate(seed_emails, 1):
            exists = User.objects.filter(email=email).exists()
            marker = " (существует)" if exists else " (не создан)"
            print(f"  {i}. {email}{marker}")
        
        try:
            idx = int(input("\nВыберите номер (или 0 для отмены): ")) - 1
            if 0 <= idx < len(seed_emails):
                email = seed_emails[idx]
                password = getpass(f"Введите пароль для {email}: ")
                create_admin_if_not_exists(email, password)
            else:
                print("Отменено")
        except (ValueError, IndexError):
            print("✗ Неверный выбор")
    
    elif choice == "5":
        show_admins()
    
    elif choice == "0":
        print("Выход...")
        return
    
    else:
        print("✗ Неверный выбор")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем")
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()













