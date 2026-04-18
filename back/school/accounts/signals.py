import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_root_admin(sender, **kwargs):
    User = get_user_model()
    root_email = getattr(settings, "ROOT_ADMIN_EMAIL", None)

    if root_email:
        default_password = os.getenv("ROOT_ADMIN_PASSWORD", "ChangeMe123!@#")

        user, created = User.objects.get_or_create(
            email=root_email,
            defaults={
                "username": root_email.lower(),
                "role": User.Roles.ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if created:
            user.set_password(default_password)
            user.save()
            print(f"Root admin created: {root_email}")
            print("Important: change the root admin password after first login.")
        else:
            if user.role != User.Roles.ADMIN or not user.is_staff or not user.is_superuser:
                user.role = User.Roles.ADMIN
                user.is_staff = True
                user.is_superuser = True
                if not user.username or user.username != root_email.lower():
                    user.username = root_email.lower()
                user.save()

    seed_emails = getattr(settings, "ADMIN_SEED_EMAILS", [])
    if len(seed_emails) > 1:
        admin2_email = seed_emails[1]
        admin2_password = os.getenv("ADMIN2_PASSWORD", None)

        if admin2_password:
            count_whitelist_su = User.objects.filter(
                email__in=seed_emails, is_superuser=True
            ).count()

            if count_whitelist_su < 2:
                user2, created2 = User.objects.get_or_create(
                    email=admin2_email,
                    defaults={
                        "username": admin2_email.lower(),
                        "role": User.Roles.ADMIN,
                        "is_staff": True,
                        "is_superuser": True,
                    },
                )

                if created2:
                    user2.set_password(admin2_password)
                    user2.save()
                    print(f"Second admin created: {admin2_email}")
                elif not user2.is_superuser and count_whitelist_su < 2:
                    user2.role = User.Roles.ADMIN
                    user2.is_staff = True
                    user2.is_superuser = True
                    user2.set_password(admin2_password)
                    user2.save()
                    print(f"Second admin promoted to superuser: {admin2_email}")
