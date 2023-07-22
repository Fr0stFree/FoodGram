import json
import os

from django.conf import settings
from django.db import migrations


def load_ingedients(apps, schema_editor):
    path = os.path.join(
        settings.BASE_DIR, os.pardir, "data", "ingredients.json"
    )
    with open(path, "r", encoding="UTF-8") as jsonfile:
        ingredients = json.load(jsonfile)

    Ingredient = apps.get_model("recipes", "Ingredient")
    for ingredient in ingredients:
        Ingredient.objects.get_or_create(
            name=ingredient.get("name"),
            unit=ingredient.get("measurement_unit"),
        )


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(load_ingedients),
    ]
