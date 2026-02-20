from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sk", "0015_paymentsettings"),
    ]

    operations = [
        migrations.AddField(
            model_name="lessonbalance",
            name="lessons_reserved",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="lesson",
            name="reserved_from_balance",
            field=models.BooleanField(
                default=False,
                help_text="True, если под занятие зарезервирован слот баланса",
            ),
        ),
    ]
