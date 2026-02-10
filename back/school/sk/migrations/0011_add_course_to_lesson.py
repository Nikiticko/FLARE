# Generated manually
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sk', '0010_alter_course_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='course',
            field=models.ForeignKey(
                blank=True,
                help_text='Курс, по которому проводится занятие',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='lessons',
                to='sk.course'
            ),
        ),
    ]


