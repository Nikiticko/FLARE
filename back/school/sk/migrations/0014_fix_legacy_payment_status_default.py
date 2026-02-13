from django.db import migrations


def fix_legacy_payment_status_default(apps, schema_editor):
    connection = schema_editor.connection
    table_name = 'sk_payment'

    with connection.cursor() as cursor:
        columns = {
            column.name for column in connection.introspection.get_table_description(cursor, table_name)
        }

        if 'status' not in columns:
            return

        cursor.execute(
            """
            UPDATE sk_payment
            SET status = 'PENDING'
            WHERE status IS NULL OR status = ''
            """
        )

        cursor.execute(
            """
            ALTER TABLE sk_payment
            MODIFY COLUMN status VARCHAR(32) NOT NULL DEFAULT 'PENDING'
            """
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('sk', '0013_payment_yookassa_fields'),
    ]

    operations = [
        migrations.RunPython(fix_legacy_payment_status_default, reverse_code=noop_reverse),
    ]
