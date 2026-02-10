# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sk', '0003_studentprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='cancellation_reason',
            field=models.TextField(blank=True, help_text='Причина отмены занятия (заполняется при статусе CANCELLED)'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='feedback',
            field=models.TextField(blank=True, help_text='Обратная связь по занятию (заполняется при статусе DONE)'),
        ),
    ]







