import json
import os

from django.conf import settings
from django.db import migrations


def load_ingredients(apps, schema_editor):
    path = os.path.join(settings.BASE_DIR, "fixtures", "ingredients.json")
    with open(path, "r", encoding="UTF-8") as jsonfile:
        ingredients = json.load(jsonfile)

    Ingredient = apps.get_model("recipes", "Ingredient")
    for ingredient in ingredients:
        Ingredient.objects.get_or_create(
            name=ingredient.get("name"),
            unit=ingredient.get("measurement_unit"),
        )


def delete_ingredients(apps, schema_editor):
    Ingredient = apps.get_model("recipes", "Ingredient")
    Ingredient.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(load_ingredients, delete_ingredients),
    ]
