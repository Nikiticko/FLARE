# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sk', '0006_add_is_trial_to_lesson'),
    ]

    operations = [
        # Добавляем поля created_at и updated_at в Course
        # Для существующих записей устанавливаем текущее время
        migrations.AddField(
            model_name='course',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='course',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        # Делаем поля обязательными после заполнения
        migrations.AlterField(
            model_name='course',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Создаем модель Module
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('order', models.PositiveIntegerField(default=0, help_text='Порядок отображения модулей')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modules', to='sk.course')),
            ],
            options={
                'ordering': ['order', 'id'],
                'unique_together': {('course', 'order')},
            },
        ),
        # Создаем модель LessonTopic
        migrations.CreateModel(
            name='LessonTopic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Название темы занятия', max_length=200)),
                ('description', models.TextField(blank=True, help_text='Описание темы')),
                ('order', models.PositiveIntegerField(default=0, help_text='Порядок отображения тем в модуле')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topics', to='sk.module')),
            ],
            options={
                'ordering': ['order', 'id'],
                'unique_together': {('module', 'order')},
            },
        ),
    ]






