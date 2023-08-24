from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from recipes.models import Recipe, Ingredient, Tag, RecipeIngredient

User = get_user_model()


class Command(BaseCommand):
    help = "Fill database with recipes"
    POSSIBLE_COOKING_TIMES = [5, 10, 15, 20, 25, 30, 40, 50, 60, 90, 120]
    POSSIBLE_INGREDIENT_AMOUNTS = [1, 2, 3, 5, 10, 20, 50, 100]

    def add_arguments(self, parser):
        parser.add_argument(
            "--amount",
            type=int,
            help="The number of recipes to be created",
        )

    def handle(self, **options):
        faker = Faker(["ru_RU"])
        amount = options.get("amount", 10)
        if amount < 1:
            raise ValueError("The number of recipes must be greater than 0")

        authors = User.objects.all().order_by("?")[:amount]

        with transaction.atomic():
            for author in authors:
                tags = Tag.objects.all().order_by("?")[:faker.random_int(0, 3)]
                image = faker.image()
                ingredients = Ingredient.objects.all().order_by("?")[:faker.random_int(2, 10)]

                recipe = Recipe.objects.create(
                    author=author,
                    name=faker.sentence(faker.random_int(1, 2)).rstrip("."),
                    text=faker.text(faker.random_int(50, 200)),
                    cooking_time=faker.random_element(
                        elements=self.POSSIBLE_COOKING_TIMES
                    ),
                )
                for ingredient in ingredients:
                    RecipeIngredient.objects.create(
                        recipe=recipe,
                        ingredient=ingredient,
                        amount=faker.random_element(
                            elements=self.POSSIBLE_INGREDIENT_AMOUNTS
                        ),
                    )

                recipe.tags.set(tags)
                recipe.ingredients.set(ingredients)
                recipe.image.save(_get_image_name(faker), ContentFile(image))

                recipe.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {amount} recipes"
            )
        )


def _get_image_name(faker: Faker) -> str:
    return faker.file_name(
        category="image",
        extension=faker.file_extension(category="image")
    ).replace(" ", "_")
