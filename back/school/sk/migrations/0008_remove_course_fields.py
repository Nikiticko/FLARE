# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sk', '0007_module_lessontopic'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='description',
        ),
        migrations.RemoveField(
            model_name='course',
            name='default_lessons',
        ),
        migrations.RemoveField(
            model_name='course',
            name='default_price',
        ),
        migrations.RemoveField(
            model_name='course',
            name='is_active',
        ),
    ]






