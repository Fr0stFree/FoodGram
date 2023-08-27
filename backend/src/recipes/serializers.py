from django.contrib.auth import get_user_model
from django.db.models import F
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.serializers import CustomUserSerializer

from .models import (
    Busket,
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag,
)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):

    def to_representation(self, instance: Tag):
        data = super().to_representation(instance)
        if not data["color"].startswith("#"):
            data["color"] = "#" + data["color"]
        return data

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "unit",
        )


class ShowIngredientsInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    unit = serializers.ReadOnlyField(source="ingredient.unit")

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "name",
            "unit",
            "amount",
        )


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class AddShowRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_busket = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_busket",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return ShowIngredientsInRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False

        return FavoriteRecipe.objects.filter(
            recipe=obj, user=request.user
        ).exists()

    def get_is_in_busket(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False

        return Busket.objects.filter(recipe=obj, user=request.user).exists()


class AddIngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class AddRecipeSerializer(serializers.ModelSerializer):
    ingredients = AddIngredientRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField()
    name = serializers.CharField(max_length=200)
    cooking_time = serializers.IntegerField()
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
            "author",
        )

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise ValidationError("Добавьте ингредиенты")

        if any([int(ingredient["amount"]) <= 0 for ingredient in ingredients]):
            raise ValidationError("Неверно указан объем ингредиентов")

        ingredient_ids = [ingredient["id"] for ingredient in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise ValidationError("Уникальность ингредиентов не соблюдена")

        return ingredients

    def validate_cooking_time(self, value):
        if value <= 0:
            raise ValidationError("Неверно указано время приготовления")
        return value

    def __add_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            ingredient_id = ingredient["id"]
            amount = ingredient["amount"]
            if RecipeIngredient.objects.filter(
                recipe=recipe,
                ingredient=ingredient_id,
            ).exists():
                amount += F("amount")

            RecipeIngredient.objects.update_or_create(
                recipe=recipe,
                ingredient=ingredient_id,
                defaults={"amount": amount},
            )

    def create(self, validated_data):
        author = self.context.get("request").user
        tags_data = validated_data.pop("tags")
        ingredients_data = validated_data.pop("ingredients")
        image = validated_data.pop("image")
        recipe = Recipe.objects.create(
            image=image, author=author, **validated_data
        )
        self.__add_ingredients(ingredients_data, recipe)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        self.__add_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return super().update(recipe, validated_data)

    def to_representation(self, recipe):
        data = AddShowRecipeSerializer(
            instance=recipe,
            context={"request": self.context.get("request")},
        ).data
        return data


class ShowFavoriteRecipeShopListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        write_only=True,
    )

    class Meta:
        model = FavoriteRecipe
        fields = ("user", "recipe")

    def validate(self, data):
        user = data["user"]
        recipe_id = data["recipe"].id
        if FavoriteRecipe.objects.filter(
            user=user, recipe__id=recipe_id
        ).exists():
            raise ValidationError("Вы уже добавили рецепт в избранное")
        return data

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return ShowFavoriteRecipeShopListSerializer(
            instance.recipe, context=context
        ).data


class BusketSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Busket
        fields = ("user", "recipe")

    def validate(self, data):
        user = data["user"]
        recipe_id = data["recipe"].id
        if Busket.objects.filter(
            user=user,
            recipe__id=recipe_id,
        ).exists():
            raise ValidationError("Вы уже добавили рецепт в корзину")
        return data

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return ShowFavoriteRecipeShopListSerializer(
            instance.recipe, context=context
        ).data
