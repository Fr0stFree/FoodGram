from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import Recipe

from .models import Follow

User = get_user_model()


class UserCreationSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get("password")

        for field in ("first_name", "last_name"):
            if not 1 <= len(attrs.get(field)) <= 150:
                raise serializers.ValidationError(
                    {field: "Недопустимая длина поля"}
                )

        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as exc:
            serializer_error = serializers.as_serializer_error(exc)
            raise serializers.ValidationError(
                {"password": serializer_error["non_field_errors"]}
            )

        return attrs


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False

        return Follow.objects.filter(
            follower=self.context["request"].user,
            author=obj,
        ).exists()


class FollowRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class FollowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        if not user:
            return False
        return Follow.objects.filter(follower=user, author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get("request")
        limit_recipes = request.query_params.get("recipes_limit")
        recipes = obj.recipes.all()

        if limit_recipes:
            recipes[: int(limit_recipes)]

        context = {"request": request}
        return FollowRecipeSerializer(
            instance=recipes,
            many=True,
            context=context,
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
