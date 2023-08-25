from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count, Q
from faker import Faker

from users.models import UserRole

User = get_user_model()


class Command(BaseCommand):
    help = "Fill database with fake users"

    def add_arguments(self, parser):
        parser.add_argument(
            "--amount",
            type=int,
            help="The number of users to be created",
        )

    def handle(self, **options):
        faker = Faker(["ru_RU"])
        amount = options.get("amount", 10)
        if amount < 1:
            raise ValueError("The number of users must be greater than 0")

        with transaction.atomic():
            for _ in range(amount):
                user = User.objects.create(
                    username=faker.user_name(),
                    email=faker.email(),
                    password=make_password(faker.password()),
                    first_name=faker.first_name(),
                    last_name=faker.last_name(),
                )
                user.userrole.role = faker.random_element(
                    elements=UserRole.ROLES
                )[0]
                user.userrole.save()

        moderators, admins, users = UserRole.objects.aggregate(
            moderators=Count("user", filter=Q(role=UserRole.MODERATOR)),
            admins=Count("user", filter=Q(role=UserRole.ADMIN)),
            users=Count("user", filter=Q(role=UserRole.USER)),
        ).values()

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created  {amount} users. Db contains: "
                f"{admins} admins, {moderators} moderators and {users} users"
            )
        )
