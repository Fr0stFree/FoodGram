import re

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=40,
        unique=True,
        help_text="Название тега",
        verbose_name="Название Тэга",
    )
    color = models.CharField(
        unique=True,
        null=True,
        blank=True,
        max_length=6,
        validators=(
            RegexValidator(
                regex=r"^[A-F\d]{6}$",
                message="Цвет в формате HEX",
                flags=re.IGNORECASE,
            ),
        ),
        help_text="HEX-код цвета",
        verbose_name="HEX-код",
    )
    slug = models.SlugField(
        unique=True,
        help_text="URL адрес тэга",
        verbose_name="Адрес",
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name="Название",
        max_length=200,
        help_text="Название ингредиента",
    )
    unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=35,
        help_text="Единицы измерения",
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.name}"


class Recipe(models.Model):
    name = models.CharField(
        verbose_name="Название",
        max_length=200,
        help_text="Название рецепта",
    )
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор рецепта",
        help_text="Автор рецепта",
    )
    text = models.TextField(verbose_name="Описание")
    tags = models.ManyToManyField(
        to=Tag,
        verbose_name="Тэги",
        related_name="recipes",
        help_text="Тэги",
        blank=True,
    )
    ingredients = models.ManyToManyField(
        to=Ingredient,
        through="RecipeIngredient",
        verbose_name="Ингредиенты рецепта",
        help_text="Выберите ингредиенты",
    )
    image = models.ImageField(
        upload_to="recipes/",
        help_text="Изображение приготовленного блюда",
        verbose_name="Фото блюда",
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(
                limit_value=1,
                message="Не менее минуты",
            ),
        ),
        verbose_name="Время приготовления",
        help_text="Задайте время приготовления блюда",
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        to=Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredients",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(
                limit_value=1,
                message="Не менее одного ингредиента",
            ),
        ),
        verbose_name="Количество",
        help_text="Количество единиц ингредиента",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "ingredient"),
                name="recipe_ingredient_exists",
            ),
            models.CheckConstraint(
                check=models.Q(amount__gte=1), name="amount_gte_1"
            ),
        ]
        verbose_name = "Ингредиент из рецепта"
        verbose_name_plural = "Ингредиенты из рецепта"

    def __str__(self):
        return f"{self.recipe}: {self.ingredient} – {self.amount}"


class FavoriteRecipe(models.Model):
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="in_favorite",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="favorites",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "user"),
                name="unique_favorite",
            ),
        ]
        ordering = ["-id"]
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные рецепты"

    def __str__(self):
        return f"Рецепт {self.recipe} в избранном пользователя {self.user}"


class Busket(models.Model):
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="basket_set",
    )
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="users_set",
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("recipe", "user"),
                name="recipe_already_in_busket",
            ),
        )
        ordering = ["-id"]
        verbose_name = "Корзина покупок"
        verbose_name_plural = "Корзины покупок"

    def __str__(self):
        return f"Рецепт {self.recipe} {self.user}"
