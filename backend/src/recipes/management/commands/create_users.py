from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count, Q, F, Sum, Avg, Max, Min, Aggregate
from faker import Faker

from users.models import UserRole, Follow

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
                user = User.objects.create_user(
                    username=faker.user_name(),
                    email=faker.email(),
                    password=faker.password(),
                    first_name=faker.first_name(),
                    last_name=faker.last_name(),
                )
                UserRole.objects.create(
                    user=user,
                    role=faker.random_element(
                        elements=[role[0] for role in UserRole.ROLES]
                    )
                )
            for _ in range(faker.random_int(min=1, max=amount)):
                user_ids = User.objects.values_list("id", flat=True)
                Follow.objects.create(
                    follower_id=faker.random_element(elements=user_ids),
                    author_id=faker.random_element(elements=user_ids),
                )

        moderators, admins, users = UserRole.objects.aggregate(
            moderators=Count("user", filter=Q(role=UserRole.MODERATOR)),
            admins=Count("user", filter=Q(role=UserRole.ADMIN)),
            users=Count("user", filter=Q(role=UserRole.USER)),
        ).values()

        follows = Follow.objects.count()

        self.stdout.write(self.style.SUCCESS(f"Created {users} users",))
