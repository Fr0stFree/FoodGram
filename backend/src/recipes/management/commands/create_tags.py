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
            raise ValueError("The number of tags must be greater than 0")

        with transaction.atomic():
            for _ in range(amount):
                Tag.objects.create(
                    name=faker.word(),
                    color=_get_hex_color(faker),
                    slug=_get_slug_string(faker),
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {amount} tags"
            )
        )


def _get_hex_color(faker: Faker) -> str:
    return faker.hex_color().replace("#", "").upper()


def _get_slug_string(faker: Faker) -> str:
    text = faker.text(faker.random_int(5, 50))
    return text.replace(" ", "-").rstrip(".").lower()
