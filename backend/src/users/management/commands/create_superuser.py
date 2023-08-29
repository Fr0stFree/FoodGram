import os

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from users.models import UserRole

User = get_user_model()


class Command(BaseCommand):
    help = "Create superuser"

    def handle(self, **options):
        admin_username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
        admin_email = os.environ.get(
            "DJANGO_SUPERUSER_EMAIL", "admin@fake.com"
        )
        admin_password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "admin")
        admin = User.objects.create(
            username=admin_username,
            email=admin_email,
            password=make_password(admin_password),
            first_name="Mr.",
            last_name="Admin",
            is_active=True,
        )
        admin.userrole.role = UserRole.ADMIN
        admin.userrole.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created superuser: {admin_username} "
                f"Email: {admin_email} Password: {admin_password}"
            )
        )
