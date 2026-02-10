#!/usr/bin/env python
"""
Скрипт для удаления всех пользователей кроме superadmin.

Пример:
  python clear_users.py
  python clear_users.py --keep-email admin@example.com
  python clear_users.py --dry-run  # только показать, что будет удалено
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


def clear_users(keep_emails=None, dry_run=False):
    """
    Удаляет всех пользователей кроме суперадминов и указанных email.
    
    :param keep_emails: список email, которые НЕ удалять
    :param dry_run: если True, только показать что будет удалено
    :return: количество удалённых пользователей
    """
    User = get_user_model()
    keep_emails = keep_emails or []
    keep_emails_lower = [e.lower() for e in keep_emails]
    
    # Находим всех пользователей для удаления
    users_to_delete = User.objects.exclude(is_superuser=True)
    
    if keep_emails_lower:
        users_to_delete = users_to_delete.exclude(email__iexact__in=keep_emails_lower)
        # Django не поддерживает __iexact__in, поэтому фильтруем вручную
        users_to_delete = [u for u in users_to_delete if u.email.lower() not in keep_emails_lower]
    else:
        users_to_delete = list(users_to_delete)
    
    if dry_run:
        print("=== DRY RUN — ничего не будет удалено ===\n")
    
    print(f"Найдено пользователей для удаления: {len(users_to_delete)}\n")
    
    if users_to_delete:
        print("Будут удалены:")
        for user in users_to_delete:
            print(f"  - {user.email} ({user.role})")
        print()
    
    # Показываем кого оставляем
    superusers = User.objects.filter(is_superuser=True)
    if superusers.exists():
        print("Суперадмины (останутся):")
        for user in superusers:
            print(f"  + {user.email}")
        print()
    
    if dry_run:
        print("=== DRY RUN завершён ===")
        return 0
    
    # Удаляем
    deleted_count = 0
    for user in users_to_delete:
        user.delete()
        deleted_count += 1
    
    return deleted_count


def main():
    parser = argparse.ArgumentParser(description="Удаление всех пользователей кроме superadmin")
    parser.add_argument(
        "--keep-email", 
        type=str, 
        action="append",
        default=[],
        help="Email пользователя, которого НЕ удалять (можно указать несколько раз)"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="Только показать что будет удалено, без реального удаления"
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Не спрашивать подтверждение"
    )
    args = parser.parse_args()
    
    if not args.dry_run and not args.yes:
        print("⚠️  ВНИМАНИЕ: Это действие удалит всех пользователей кроме суперадминов!")
        print("   Все связанные данные (уроки, платежи и т.д.) также будут удалены.\n")
        confirm = input("Введите 'yes' для подтверждения: ")
        if confirm.lower() != 'yes':
            print("Отменено.")
            return
    
    deleted = clear_users(keep_emails=args.keep_email, dry_run=args.dry_run)
    
    if not args.dry_run:
        print(f"✓ Удалено пользователей: {deleted}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем")
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()
