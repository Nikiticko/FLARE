#!/usr/bin/env python
"""
Скрипт для анализа AuditLog и поиска информации о потерянных данных.

Использование:
    python check_audit_log.py
    python check_audit_log.py --export audit_report.txt
"""
import argparse
import os
import sys
import django
from datetime import datetime

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "school.settings")
django.setup()

from sk.models import AuditLog, Lesson
from django.contrib.auth import get_user_model

User = get_user_model()


def analyze_audit_logs(export_file=None):
    """
    Анализирует AuditLog и ищет информацию о потерянных данных.
    """
    print("=" * 80)
    print("АНАЛИЗ ЛОГОВ ДЕЙСТВИЙ (AuditLog)")
    print("=" * 80 + "\n")
    
    # Получаем все логи обновления уроков
    update_logs = AuditLog.objects.filter(
        action="TEACHER_UPDATE_LESSON"
    ).order_by('-created_at')
    
    print(f"Всего логов обновления уроков: {update_logs.count()}\n")
    
    # Статистика
    lessons_with_feedback_in_log = set()
    lessons_with_cancellation_in_log = set()
    lessons_changed_to_done = set()
    lessons_changed_to_cancelled = set()
    
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("ДЕТАЛЬНЫЙ ОТЧЁТ ПО ОБНОВЛЕНИЯМ УРОКОВ")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    for log in update_logs:
        lesson_id = log.meta.get('lesson_id')
        if not lesson_id:
            continue
        
        old_status = log.meta.get('old_status')
        new_status = log.meta.get('status')
        has_feedback = log.meta.get('has_feedback')
        cancellation_reason = log.meta.get('cancellation_reason')
        actor_email = log.actor.email if log.actor else 'Unknown'
        timestamp = log.created_at
        
        # Собираем статистику
        if has_feedback:
            lessons_with_feedback_in_log.add(lesson_id)
        if cancellation_reason:
            lessons_with_cancellation_in_log.add(lesson_id)
        if new_status == Lesson.STATUS_DONE:
            lessons_changed_to_done.add(lesson_id)
        if new_status == Lesson.STATUS_CANCELLED:
            lessons_changed_to_cancelled.add(lesson_id)
        
        # Формируем отчёт
        report_lines.append(f"Урок ID {lesson_id}")
        report_lines.append(f"  Дата: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"  Учитель: {actor_email}")
        report_lines.append(f"  Изменение статуса: {old_status} → {new_status}")
        if has_feedback:
            report_lines.append(f"  ✓ Была добавлена обратная связь (текст потерян)")
        if cancellation_reason:
            report_lines.append(f"  ✓ Была указана причина отмены: {cancellation_reason[:150]}")
        report_lines.append("")
    
    # Выводим статистику
    print("СТАТИСТИКА ПО ЛОГАМ:")
    print("-" * 80)
    print(f"Уроков переведено в статус DONE: {len(lessons_changed_to_done)}")
    print(f"  Из них имели обратную связь: {len(lessons_with_feedback_in_log)}")
    print(f"  ПОТЕРЯЛИ обратную связь: {len(lessons_changed_to_done - lessons_with_feedback_in_log)}")
    print()
    print(f"Уроков переведено в статус CANCELLED: {len(lessons_changed_to_cancelled)}")
    print(f"  Из них имели причину отмены: {len(lessons_with_cancellation_in_log)}")
    print(f"  ПОТЕРЯЛИ причину отмены: {len(lessons_changed_to_cancelled - lessons_with_cancellation_in_log)}")
    print()
    
    # Проверяем текущее состояние в БД
    print("\nТЕКУЩЕЕ СОСТОЯНИЕ В БАЗЕ ДАННЫХ:")
    print("-" * 80)
    
    done_lessons = Lesson.objects.filter(status=Lesson.STATUS_DONE)
    cancelled_lessons = Lesson.objects.filter(status=Lesson.STATUS_CANCELLED)
    
    # Проверяем сколько уроков DONE имеют обратную связь сейчас
    done_with_feedback_now = 0
    for lesson in done_lessons:
        if getattr(lesson, 'feedback', '').strip():
            done_with_feedback_now += 1
    
    # Проверяем сколько уроков CANCELLED имеют причину отмены сейчас
    cancelled_with_reason_now = 0
    for lesson in cancelled_lessons:
        if getattr(lesson, 'cancellation_reason', '').strip():
            cancelled_with_reason_now += 1
    
    print(f"Проведённых уроков (DONE): {done_lessons.count()}")
    print(f"  С обратной связью СЕЙЧАС: {done_with_feedback_now}")
    print(f"  БЕЗ обратной связи СЕЙЧАС: {done_lessons.count() - done_with_feedback_now}")
    print()
    print(f"Отменённых уроков (CANCELLED): {cancelled_lessons.count()}")
    print(f"  С причиной отмены СЕЙЧАС: {cancelled_with_reason_now}")
    print(f"  БЕЗ причины отмены СЕЙЧАС: {cancelled_lessons.count() - cancelled_with_reason_now}")
    print()
    
    # Подсчёт потерянных данных
    potential_lost_feedback = len(lessons_with_feedback_in_log) - done_with_feedback_now
    potential_lost_reasons = len(lessons_with_cancellation_in_log) - cancelled_with_reason_now
    
    if potential_lost_feedback > 0 or potential_lost_reasons > 0:
        print("\n⚠️  ОБНАРУЖЕНА ПОТЕРЯ ДАННЫХ:")
        print("-" * 80)
        if potential_lost_feedback > 0:
            print(f"❌ Потеряно обратных связей: ~{potential_lost_feedback}")
        if potential_lost_reasons > 0:
            print(f"❌ Потеряно причин отмены: ~{potential_lost_reasons}")
        print()
        print("💡 Данные были введены, но не сохранены в БД из-за отсутствия колонок.")
        print("   Восстановление возможно только из бэкапов БД.")
    else:
        print("\n✅ Потери данных не обнаружено (или логи неполные)")
    
    # Экспорт в файл
    if export_file:
        with open(export_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        print(f"\n✓ Детальный отчёт сохранён в: {export_file}")
    
    print("\n" + "=" * 80 + "\n")
    
    # Список уроков, которые потеряли данные
    print("УРОКИ, КОТОРЫЕ ПОТЕРЯЛИ ОБРАТНУЮ СВЯЗЬ:")
    print("-" * 80)
    
    lost_feedback_lessons = lessons_with_feedback_in_log
    count = 0
    for lesson_id in sorted(lost_feedback_lessons):
        try:
            lesson = Lesson.objects.get(id=lesson_id)
            current_feedback = getattr(lesson, 'feedback', '').strip()
            if not current_feedback:  # Если сейчас пусто, значит потеряно
                student_email = lesson.student.email if lesson.student else 'N/A'
                teacher_email = lesson.teacher.email if lesson.teacher else 'N/A'
                print(f"  Урок #{lesson_id}: {student_email} ← {teacher_email}")
                print(f"    Дата: {lesson.scheduled_at.strftime('%Y-%m-%d')}")
                count += 1
                if count >= 20:
                    remaining = len(lost_feedback_lessons) - count
                    if remaining > 0:
                        print(f"  ... и ещё {remaining} уроков")
                    break
        except Lesson.DoesNotExist:
            pass
    
    if count == 0:
        print("  (нет потерянных)")
    
    print("\n" + "=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Анализ AuditLog для поиска потерянных данных")
    parser.add_argument(
        "--export",
        type=str,
        help="Путь к файлу для экспорта детального отчёта"
    )
    args = parser.parse_args()
    
    analyze_audit_logs(export_file=args.export)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
