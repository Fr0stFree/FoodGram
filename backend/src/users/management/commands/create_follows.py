from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count

from users.models import Follow

User = get_user_model()


class Command(BaseCommand):
    help = "Fill database with follow connections between users"

    def add_arguments(self, parser):
        parser.add_argument(
            "--amount",
            type=int,
            help="The number of follows to be created",
        )

    def handle(self, **options):
        amount = options.get("amount", 5)

        if amount < 1:
            raise ValueError("The number of follows must be greater than 0")

        users_without_follows = User.objects.annotate(
            follows_count=Count("follower", distinct=True)
        ).filter(follows_count=0)
        if (users_amount := users_without_follows.count()) < amount:
            raise ValueError(
                f"The number of follows must be less than or equal to {users_amount}"
            )

        with transaction.atomic():
            for _ in range(amount):
                user = users_without_follows.order_by("?").first()
                author = User.objects.exclude(pk=user.pk).order_by("?").first()
                Follow.objects.create(
                    follower=user,
                    author=author,
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {amount} follows between users"
            )
        )
