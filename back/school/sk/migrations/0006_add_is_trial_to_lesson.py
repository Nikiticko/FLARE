# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sk', '0005_alter_auditlog_actor_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='is_trial',
            field=models.BooleanField(default=False, help_text='True, если это пробное занятие (не списывается с баланса)'),
        ),
    ]







