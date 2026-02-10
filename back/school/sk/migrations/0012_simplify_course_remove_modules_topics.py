# Generated manually - упрощение курсов: удаление модулей и тем, добавление описания
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sk', '0011_add_course_to_lesson'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='description',
            field=models.TextField(
                blank=True,
                help_text='Описание курса с разметкой. Переносы строк и форматирование сохраняются.',
            ),
        ),
        migrations.DeleteModel(
            name='LessonTopic',
        ),
        migrations.DeleteModel(
            name='Module',
        ),
    ]
