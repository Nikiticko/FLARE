#!/usr/bin/env python
"""
Скрипт диагностики: проверка наличия полей feedback и cancellation_reason в БД.

Использование:
    python diagnose_migrations.py
"""
import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "school.settings")
django.setup()

from django.db import connection
from sk.models import Lesson
from django.core.management import call_command


def check_table_structure():
    """Проверка структуры таблицы sk_lesson в БД"""
    print("=" * 70)
    print("1. ПРОВЕРКА СТРУКТУРЫ ТАБЛИЦЫ В БАЗЕ ДАННЫХ")
    print("=" * 70)
    
    with connection.cursor() as cursor:
        # MySQL запрос для получения структуры таблицы
        cursor.execute("DESCRIBE sk_lesson;")
        columns = cursor.fetchall()
        
        column_names = [col[0] for col in columns]
        
        print(f"\nВсего колонок в таблице sk_lesson: {len(column_names)}\n")
        
        # Проверяем наличие нужных нам полей
        has_cancellation_reason = 'cancellation_reason' in column_names
        has_feedback = 'feedback' in column_names
        
        if has_cancellation_reason:
            print("✅ Поле 'cancellation_reason' НАЙДЕНО в таблице")
        else:
            print("❌ Поле 'cancellation_reason' ОТСУТСТВУЕТ в таблице!")
        
        if has_feedback:
            print("✅ Поле 'feedback' НАЙДЕНО в таблице")
        else:
            print("❌ Поле 'feedback' ОТСУТСТВУЕТ в таблице!")
        
        print("\n" + "-" * 70)
        print("Полный список колонок:")
        print("-" * 70)
        for col in columns:
            print(f"  - {col[0]:<30} {col[1]:<15} {col[2]}")
        
        return has_cancellation_reason, has_feedback


def check_model_fields():
    """Проверка полей в Django модели"""
    print("\n" + "=" * 70)
    print("2. ПРОВЕРКА ПОЛЕЙ В DJANGO МОДЕЛИ")
    print("=" * 70 + "\n")
    
    # Получаем все поля модели
    model_fields = [f.name for f in Lesson._meta.get_fields()]
    
    has_cancellation_reason_model = 'cancellation_reason' in model_fields
    has_feedback_model = 'feedback' in model_fields
    
    if has_cancellation_reason_model:
        print("✅ Поле 'cancellation_reason' ОПРЕДЕЛЕНО в модели")
    else:
        print("❌ Поле 'cancellation_reason' ОТСУТСТВУЕТ в модели!")
    
    if has_feedback_model:
        print("✅ Поле 'feedback' ОПРЕДЕЛЕНО в модели")
    else:
        print("❌ Поле 'feedback' ОТСУТСТВУЕТ в модели!")
    
    print("\n" + "-" * 70)
    print("Все поля модели Lesson:")
    print("-" * 70)
    for field_name in model_fields:
        print(f"  - {field_name}")
    
    return has_cancellation_reason_model, has_feedback_model


def check_migrations():
    """Проверка применённых миграций"""
    print("\n" + "=" * 70)
    print("3. ПРОВЕРКА ПРИМЕНЁННЫХ МИГРАЦИЙ")
    print("=" * 70 + "\n")
    
    from django.db.migrations.recorder import MigrationRecorder
    recorder = MigrationRecorder(connection)
    applied_migrations = recorder.applied_migrations()
    
    sk_migrations = [m for m in applied_migrations if m[0] == 'sk']
    sk_migrations_sorted = sorted(sk_migrations, key=lambda x: x[1])
    
    print(f"Всего применено миграций для приложения 'sk': {len(sk_migrations_sorted)}\n")
    
    # Ищем конкретно миграцию 0004
    migration_0004_applied = ('sk', '0004_add_lesson_feedback_fields') in applied_migrations
    
    if migration_0004_applied:
        print("✅ Миграция '0004_add_lesson_feedback_fields' ПРИМЕНЕНА")
    else:
        print("❌ Миграция '0004_add_lesson_feedback_fields' НЕ ПРИМЕНЕНА!")
    
    print("\n" + "-" * 70)
    print("Список всех применённых миграций 'sk':")
    print("-" * 70)
    for app, migration in sk_migrations_sorted:
        indicator = "✓" if (app, migration) != ('sk', '0004_add_lesson_feedback_fields') or migration_0004_applied else "✗"
        print(f"  {indicator} {migration}")
    
    return migration_0004_applied


def check_data_presence():
    """Проверка наличия данных в полях"""
    print("\n" + "=" * 70)
    print("4. ПРОВЕРКА НАЛИЧИЯ ДАННЫХ В ПОЛЯХ")
    print("=" * 70 + "\n")
    
    try:
        # Проверяем уроки с разными статусами
        done_lessons = Lesson.objects.filter(status=Lesson.STATUS_DONE)
        cancelled_lessons = Lesson.objects.filter(status=Lesson.STATUS_CANCELLED)
        
        print(f"Проведённых уроков (DONE): {done_lessons.count()}")
        print(f"Отменённых уроков (CANCELLED): {cancelled_lessons.count()}\n")
        
        # Проверяем наличие обратной связи
        done_with_feedback = 0
        done_without_feedback = 0
        
        for lesson in done_lessons[:100]:  # Проверяем первые 100
            feedback = getattr(lesson, 'feedback', '')
            if feedback and feedback.strip():
                done_with_feedback += 1
            else:
                done_without_feedback += 1
        
        print(f"Проведённых уроков С обратной связью: {done_with_feedback}")
        print(f"Проведённых уроков БЕЗ обратной связи: {done_without_feedback}")
        
        if done_lessons.count() > 0 and done_with_feedback == 0:
            print("⚠️  ВНИМАНИЕ: Все проведённые уроки БЕЗ обратной связи!")
        
        # Проверяем причины отмены
        cancelled_with_reason = 0
        cancelled_without_reason = 0
        
        for lesson in cancelled_lessons[:100]:  # Проверяем первые 100
            cancellation_reason = getattr(lesson, 'cancellation_reason', '')
            if cancellation_reason and cancellation_reason.strip():
                cancelled_with_reason += 1
            else:
                cancelled_without_reason += 1
        
        print(f"\nОтменённых уроков С причиной отмены: {cancelled_with_reason}")
        print(f"Отменённых уроков БЕЗ причины отмены: {cancelled_without_reason}")
        
        if cancelled_lessons.count() > 0 and cancelled_with_reason == 0:
            print("⚠️  ВНИМАНИЕ: Все отменённые уроки БЕЗ причины отмены!")
        
        # Примеры данных
        print("\n" + "-" * 70)
        print("Примеры уроков:")
        print("-" * 70)
        
        sample_done = done_lessons.first()
        if sample_done:
            feedback = getattr(sample_done, 'feedback', 'N/A')
            print(f"\nПример DONE урока (ID={sample_done.id}):")
            print(f"  Обратная связь: {feedback[:100] if feedback else '(пусто)'}...")
        
        sample_cancelled = cancelled_lessons.first()
        if sample_cancelled:
            reason = getattr(sample_cancelled, 'cancellation_reason', 'N/A')
            print(f"\nПример CANCELLED урока (ID={sample_cancelled.id}):")
            print(f"  Причина отмены: {reason[:100] if reason else '(пусто)'}...")
    
    except Exception as e:
        print(f"❌ Ошибка при проверке данных: {e}")


def main():
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "ДИАГНОСТИКА ПРОБЛЕМЫ С УРОКАМИ" + " " * 22 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    # 1. Проверка структуры таблицы
    db_has_cr, db_has_fb = check_table_structure()
    
    # 2. Проверка модели
    model_has_cr, model_has_fb = check_model_fields()
    
    # 3. Проверка миграций
    migration_applied = check_migrations()
    
    # 4. Проверка данных
    check_data_presence()
    
    # Итоговый вывод
    print("\n" + "=" * 70)
    print("ИТОГОВАЯ ДИАГНОСТИКА")
    print("=" * 70 + "\n")
    
    if db_has_cr and db_has_fb and model_has_cr and model_has_fb and migration_applied:
        print("✅ Всё в порядке: поля есть в модели, в БД, миграция применена")
        print("\n💡 Если данные пропали, возможные причины:")
        print("   1. Данные были введены ДО применения миграции")
        print("   2. Была выполнена очистка через UPDATE запрос в БД")
        print("   3. Был баг в коде, который очистил поля")
    else:
        print("❌ ОБНАРУЖЕНА ПРОБЛЕМА!\n")
        
        if not migration_applied:
            print("🔧 РЕШЕНИЕ: Применить миграцию 0004")
            print("   Команда: python manage.py migrate sk 0004_add_lesson_feedback_fields")
        
        if not db_has_cr or not db_has_fb:
            print("🔧 РЕШЕНИЕ: Добавить отсутствующие колонки в БД")
            print("   Команда: python manage.py migrate sk")
        
        if model_has_cr != db_has_cr or model_has_fb != db_has_fb:
            print("⚠️  НЕСООТВЕТСТВИЕ: модель и БД не синхронизированы")
            print("   Запустите: python manage.py migrate")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
