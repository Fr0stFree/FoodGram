from django.conf import settings
from django.contrib import admin

from .models import (
    Busket,
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag,
)


@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "color",
        "slug",
    )
    search_fields = [
        "name",
    ]
    ordering = [
        "color",
    ]
    empty_value_display = settings.EMPTY_VALUE


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "unit",
        "get_recipes_count",
    )
    search_fields = ("name",)
    ordering = ("unit",)
    empty_value_display = settings.EMPTY_VALUE

    def get_recipes_count(self, obj):
        return RecipeIngredient.objects.filter(ingredient=obj.id).count()

    get_recipes_count.short_description = "Использований в рецептах"


@admin.register(RecipeIngredient)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "recipe",
        "ingredient",
        "amount",
    )
    list_filter = ("id", "recipe", "ingredient")


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "author",
        "in_favorite",
    )
    list_filter = (
        "name",
        "author",
        "tags",
    )
    readonly_fields = ("in_favorite",)
    empty_value_display = settings.EMPTY_VALUE

    def in_favorite(self, obj):
        return obj.in_favorite.all().count()

    in_favorite.short_description = "Количество добавлений в избранное"


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "recipe",
    )


@admin.register(Busket)
class BusketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "recipe",
    )
