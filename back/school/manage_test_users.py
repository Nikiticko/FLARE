#!/usr/bin/env python
"""
Скрипт для создания тестовых пользователей.

Пример:
  python manage_test_users.py
  python manage_test_users.py --admins 3 --students 5 --domain example.com
"""
import argparse
import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "school.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.conf import settings


DEFAULT_PASSWORD = "6969"


def get_default_domain() -> str:
    root_email = getattr(settings, "ROOT_ADMIN_EMAIL", "") or ""
    if "@" in root_email:
        return root_email.split("@", 1)[1]
    return "example.com"


def build_email(prefix: str, index: int, domain: str) -> str:
    return f"{prefix}{index}@{domain}"


def upsert_user(email, role, is_staff=False, is_superuser=False, password=DEFAULT_PASSWORD, full_name=""):
    User = get_user_model()
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            "username": email.lower(),
            "role": role,
            "is_staff": is_staff,
            "is_superuser": is_superuser,
            "is_active": True,
            "student_full_name": full_name,
        },
    )

    changed = False
    if user.username != email.lower():
        user.username = email.lower()
        changed = True
    if user.role != role:
        user.role = role
        changed = True
    if user.is_staff != is_staff:
        user.is_staff = is_staff
        changed = True
    if user.is_superuser != is_superuser:
        user.is_superuser = is_superuser
        changed = True
    if full_name and user.student_full_name != full_name:
        user.student_full_name = full_name
        changed = True

    # Пароль устанавливаем всегда
    user.set_password(password)
    changed = True

    if changed:
        user.save()

    return created


ROLE_NAMES = {
    "admin": "Админ",
    "manager": "Менеджер", 
    "teacher": "Преподаватель",
    "student": "Ученик",
    "applicant": "Абитуриент",
}


def create_users(prefix, count, role, is_staff=False, is_superuser=False, domain="example.com", password=DEFAULT_PASSWORD):
    created = 0
    role_name = ROLE_NAMES.get(prefix, prefix.capitalize())
    for i in range(1, count + 1):
        email = build_email(prefix, i, domain)
        full_name = f"{role_name} Тестовый {i}"
        if upsert_user(email, role, is_staff=is_staff, is_superuser=is_superuser, password=password, full_name=full_name):
            created += 1
    return created


def main():
    User = get_user_model()

    parser = argparse.ArgumentParser(description="Создание тестовых пользователей")
    parser.add_argument("--admins", type=int, default=2, help="Количество админов")
    parser.add_argument("--managers", type=int, default=2, help="Количество менеджеров")
    parser.add_argument("--teachers", type=int, default=2, help="Количество учителей")
    parser.add_argument("--students", type=int, default=2, help="Количество учеников")
    parser.add_argument("--applicants", type=int, default=2, help="Количество абитуриентов")
    parser.add_argument("--domain", type=str, default=get_default_domain(), help="Домен для email")
    parser.add_argument("--password", type=str, default=DEFAULT_PASSWORD, help="Пароль для всех")
    args = parser.parse_args()

    total_created = 0

    total_created += create_users(
        prefix="admin",
        count=args.admins,
        role=User.Roles.ADMIN,
        is_staff=True,
        is_superuser=True,
        domain=args.domain,
        password=args.password,
    )
    total_created += create_users(
        prefix="manager",
        count=args.managers,
        role=User.Roles.MANAGER,
        is_staff=False,
        is_superuser=False,
        domain=args.domain,
        password=args.password,
    )
    total_created += create_users(
        prefix="teacher",
        count=args.teachers,
        role=User.Roles.TEACHER,
        is_staff=False,
        is_superuser=False,
        domain=args.domain,
        password=args.password,
    )
    total_created += create_users(
        prefix="student",
        count=args.students,
        role=User.Roles.STUDENT,
        is_staff=False,
        is_superuser=False,
        domain=args.domain,
        password=args.password,
    )
    total_created += create_users(
        prefix="applicant",
        count=args.applicants,
        role=User.Roles.APPLICANT,
        is_staff=False,
        is_superuser=False,
        domain=args.domain,
        password=args.password,
    )

    print("✓ Готово")
    print(f"Создано новых пользователей: {total_created}")
    print(f"Пароль для всех: {args.password}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем")
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()
