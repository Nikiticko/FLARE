from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_user_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.FileField(blank=True, null=True, upload_to='avatars/%Y/%m/', verbose_name='Аватар'),
        ),
    ]
