#!/usr/bin/env python
"""
Скрипт для создания тестовых уроков со статусами:
- PLANNED (будущее)
- DONE (прошлое)
- CANCELLED (прошлое)

Пример:
  python manage_test_lessons.py
  python manage_test_lessons.py --per-student 2
"""
import argparse
import os
import random
import sys
import django

from datetime import timedelta

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "school.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from sk.models import Lesson, Course


def pick_random(items):
    if not items:
        return None
    return random.choice(items)


def normalized_time(base_dt, hour):
    local = timezone.localtime(base_dt)
    return local.replace(hour=hour, minute=0, second=0, microsecond=0)


def create_lesson(student, teacher, course, status, scheduled_at):
    comment = ""
    feedback = ""
    cancellation_reason = ""
    debited_from_balance = False

    if status == Lesson.STATUS_DONE:
        feedback = "Урок прошел хорошо, ученик усвоил материал."
        debited_from_balance = True
        comment = "Проведено по расписанию."
    elif status == Lesson.STATUS_CANCELLED:
        cancellation_reason = "Ученик не смог присутствовать."
        comment = "Отменено заранее."
    else:
        comment = "Запланировано."

    Lesson.objects.create(
        student=student,
        parent_full_name=student.parent_full_name or "",
        teacher=teacher,
        course=course,
        link="Discord",
        scheduled_at=scheduled_at,
        status=status,
        comment=comment,
        cancellation_reason=cancellation_reason,
        feedback=feedback,
        debited_from_balance=debited_from_balance,
        is_trial=False,
    )


def main():
    parser = argparse.ArgumentParser(description="Создание тестовых уроков")
    parser.add_argument("--per-student", type=int, default=1, help="Сколько уроков каждого статуса на ученика")
    args = parser.parse_args()

    User = get_user_model()
    students = list(User.objects.filter(role=User.Roles.STUDENT))
    teachers = list(User.objects.filter(role=User.Roles.TEACHER))
    courses = list(Course.objects.all())

    if not students:
        print("✗ Нет студентов для создания уроков")
        return

    now = timezone.now()
    created = 0

    for student in students:
        for i in range(args.per_student):
            teacher = pick_random(teachers)
            course = pick_random(courses)

            # CANCELLED: 2+ дней назад утром
            cancelled_at = normalized_time(now - timedelta(days=2 + i), hour=10 + i)
            create_lesson(student, teacher, course, Lesson.STATUS_CANCELLED, cancelled_at)
            created += 1

            # DONE: 1+ день назад днём
            done_at = normalized_time(now - timedelta(days=1 + i), hour=12 + i)
            create_lesson(student, teacher, course, Lesson.STATUS_DONE, done_at)
            created += 1

            # PLANNED: 1+ день в будущем вечером
            planned_at = normalized_time(now + timedelta(days=1 + i), hour=16 + i)
            create_lesson(student, teacher, course, Lesson.STATUS_PLANNED, planned_at)
            created += 1

    print("✓ Готово")
    print(f"Создано уроков: {created}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем")
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()
