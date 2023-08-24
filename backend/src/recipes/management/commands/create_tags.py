from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from recipes.models import Tag


class Command(BaseCommand):
    help = "Fill database with tags"

    def add_arguments(self, parser):
        parser.add_argument(
            "--amount",
            type=int,
            help="The number of tags to be created",
        )

    def handle(self, **options):
        faker = Faker(["en-US"])
        amount = options.get("amount", 10)
        if amount < 1:
            raise ValueError("The number of users must be greater than 0")

        with transaction.atomic():
            for _ in range(amount):
                Tag.objects.create(
                    name=faker.word(),
                    color=faker.hex_color().replace("#", "").upper(),
                    slug=faker.text(faker.random_int(5, 50)).replace(" ", "-").rstrip(".").lower(),
                )
