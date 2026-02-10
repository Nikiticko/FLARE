from django.db import migrations


def sync_username_with_email(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    for user in User.objects.all().only("id", "email", "username"):
        if user.email and user.username != user.email:
            User.objects.filter(pk=user.pk).update(username=user.email)


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(sync_username_with_email, migrations.RunPython.noop),
    ]
