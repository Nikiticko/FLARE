from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sk', '0014_fix_legacy_payment_status_default'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('singleton_key', models.PositiveSmallIntegerField(default=1, editable=False, unique=True)),
                ('lesson_price_rub', models.PositiveIntegerField(default=1000)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
