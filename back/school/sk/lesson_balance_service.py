from django.db import transaction
from rest_framework.exceptions import ValidationError

from .models import Lesson, LessonBalance


def _lock_balance(student):
    return LessonBalance.objects.select_for_update().get_or_create(student=student)


def _free_slots(lb: LessonBalance) -> int:
    return max(0, lb.lessons_available - lb.lessons_reserved)


def reserve_lesson_slot(lesson: Lesson):
    if lesson.is_trial or lesson.reserved_from_balance or lesson.status != Lesson.STATUS_PLANNED:
        return

    lb, _ = _lock_balance(lesson.student)
    if _free_slots(lb) <= 0:
        raise ValidationError({
            "student": "Недостаточно свободного баланса для планирования занятия."
        })

    lb.lessons_reserved += 1
    lb.save(update_fields=["lessons_reserved", "updated_at"])

    lesson.reserved_from_balance = True
    lesson.save(update_fields=["reserved_from_balance"])


def release_lesson_reserve(lesson: Lesson):
    if lesson.is_trial or not lesson.reserved_from_balance:
        return

    lb, _ = _lock_balance(lesson.student)
    if lb.lessons_reserved > 0:
        lb.lessons_reserved -= 1
        lb.save(update_fields=["lessons_reserved", "updated_at"])

    lesson.reserved_from_balance = False
    lesson.save(update_fields=["reserved_from_balance"])


def debit_lesson_balance(lesson: Lesson):
    if lesson.is_trial or lesson.debited_from_balance:
        return

    lb, _ = _lock_balance(lesson.student)

    if lesson.reserved_from_balance:
        if lb.lessons_reserved > 0:
            lb.lessons_reserved -= 1
    elif _free_slots(lb) <= 0:
        raise ValidationError({
            "student": "Недостаточно свободного баланса для списания занятия."
        })

    if lb.lessons_available <= 0:
        raise ValidationError({
            "student": "Недостаточно баланса для списания занятия."
        })

    lb.lessons_available -= 1
    lb.save(update_fields=["lessons_available", "lessons_reserved", "updated_at"])

    lesson.debited_from_balance = True
    lesson.reserved_from_balance = False
    lesson.save(update_fields=["debited_from_balance", "reserved_from_balance"])


def refund_debited_lesson(lesson: Lesson):
    if lesson.is_trial or not lesson.debited_from_balance:
        return

    lb, _ = _lock_balance(lesson.student)
    lb.lessons_available += 1
    lb.save(update_fields=["lessons_available", "updated_at"])

    lesson.debited_from_balance = False
    lesson.save(update_fields=["debited_from_balance"])


def apply_lesson_status_transition(lesson: Lesson, old_status: str, new_status: str):
    if lesson.is_trial or old_status == new_status:
        return

    with transaction.atomic():
        if new_status == Lesson.STATUS_PLANNED:
            if old_status == Lesson.STATUS_DONE:
                refund_debited_lesson(lesson)
            reserve_lesson_slot(lesson)
            return

        if new_status == Lesson.STATUS_DONE:
            debit_lesson_balance(lesson)
            return

        if new_status == Lesson.STATUS_CANCELLED:
            if old_status == Lesson.STATUS_PLANNED:
                release_lesson_reserve(lesson)
            elif old_status == Lesson.STATUS_DONE:
                refund_debited_lesson(lesson)
            return
