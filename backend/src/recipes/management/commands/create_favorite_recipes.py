import random as rd

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from recipes.models import Recipe, FavoriteRecipe

User = get_user_model()


class Command(BaseCommand):
    help = "Fill database with users' favorite recipes"

    def add_arguments(self, parser):
        parser.add_argument(
            "--amount",
            type=int,
            help="For how many users to create favorite recipes",
        )

    def handle(self, **options):
        amount = options.get("amount", 10)
        if amount < 1:
            raise ValueError("The number of recipes must be greater than 0")

        users = User.objects.all().order_by("?")[:amount]

        with transaction.atomic():
            for user in users:
                recipes = Recipe.objects.all().order_by("?")[:rd.randint(1, 6)]

                for recipe in recipes:
                    created, attempts = False, 0

                    while not created or attempts < 10:
                        _, created = FavoriteRecipe.objects.get_or_create(
                            user=user,
                            recipe=recipe,
                        )
                        attempts += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created favorite recipes for {amount} users"
            )
        )

