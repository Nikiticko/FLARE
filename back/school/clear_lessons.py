#!/usr/bin/env python
"""
Скрипт для удаления всех уроков.

Пример:
  python clear_lessons.py
  python clear_lessons.py --dry-run  # только показать, что будет удалено
  python clear_lessons.py --yes      # без подтверждения
"""
import argparse
import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "school.settings")
django.setup()

from sk.models import Lesson


def clear_lessons(dry_run=False):
    """
    Удаляет все уроки.
    
    :param dry_run: если True, только показать что будет удалено
    :return: количество удалённых уроков
    """
    lessons = Lesson.objects.all()
    total = lessons.count()
    
    if dry_run:
        print("=== DRY RUN — ничего не будет удалено ===\n")
    
    print(f"Найдено уроков для удаления: {total}\n")
    
    if total > 0:
        # Статистика по статусам
        planned = lessons.filter(status=Lesson.STATUS_PLANNED).count()
        done = lessons.filter(status=Lesson.STATUS_DONE).count()
        cancelled = lessons.filter(status=Lesson.STATUS_CANCELLED).count()
        
        print("Статистика:")
        print(f"  - Запланировано: {planned}")
        print(f"  - Проведено: {done}")
        print(f"  - Отменено: {cancelled}")
        print()
        
        # Показываем первые 10 для примера
        print("Примеры уроков (первые 10):")
        for lesson in lessons[:10]:
            student_email = lesson.student.email if lesson.student else "N/A"
            teacher_email = lesson.teacher.email if lesson.teacher else "N/A"
            print(f"  - ID:{lesson.id} | {lesson.scheduled_at} | {student_email} -> {teacher_email} | {lesson.status}")
        
        if total > 10:
            print(f"  ... и ещё {total - 10}")
        print()
    
    if dry_run:
        print("=== DRY RUN завершён ===")
        return 0
    
    # Удаляем
    deleted_count, _ = Lesson.objects.all().delete()
    
    return deleted_count


def main():
    parser = argparse.ArgumentParser(description="Удаление всех уроков")
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
        print("⚠️  ВНИМАНИЕ: Это действие удалит ВСЕ уроки!")
        print("   Это действие необратимо.\n")
        confirm = input("Введите 'yes' для подтверждения: ")
        if confirm.lower() != 'yes':
            print("Отменено.")
            return
    
    deleted = clear_lessons(dry_run=args.dry_run)
    
    if not args.dry_run:
        print(f"✓ Удалено уроков: {deleted}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем")
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()
