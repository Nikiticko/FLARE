from django.core.management.base import BaseCommand

from sk.payment_api_views import sync_recent_pending_yookassa_payments


class Command(BaseCommand):
    help = "Synchronize recent pending YooKassa payments and confirm successful ones."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit-per-user",
            type=int,
            default=5,
            help="Maximum number of recent pending payments to check per user.",
        )
        parser.add_argument(
            "--max-age-hours",
            type=int,
            default=48,
            help="Only inspect payments created within this many hours.",
        )

    def handle(self, *args, **options):
        stats = sync_recent_pending_yookassa_payments(
            limit_per_user=options["limit_per_user"],
            max_age_hours=options["max_age_hours"],
        )
        self.stdout.write(
            self.style.SUCCESS(
                "checked={checked} confirmed={confirmed} users={users}".format(**stats)
            )
        )
