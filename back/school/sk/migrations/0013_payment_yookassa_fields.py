from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sk', '0012_simplify_course_remove_modules_topics'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='idempotence_key',
            field=models.CharField(blank=True, db_index=True, help_text='Ключ идемпотентности запроса в ЮKassa', max_length=64),
        ),
        migrations.AddField(
            model_name='payment',
            name='lessons_count',
            field=models.PositiveIntegerField(default=0, help_text='Количество купленных занятий'),
        ),
        migrations.AddField(
            model_name='payment',
            name='yookassa_payment_id',
            field=models.CharField(blank=True, db_index=True, help_text='ID платежа в ЮKassa', max_length=64),
        ),
        migrations.AddField(
            model_name='payment',
            name='yookassa_status',
            field=models.CharField(blank=True, help_text='Текущий статус платежа в ЮKassa', max_length=32),
        ),
    ]
