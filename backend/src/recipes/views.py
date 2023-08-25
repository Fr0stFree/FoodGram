import datetime as dt

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from main.pagination import LimitPageNumberPaginator
from .filters import IngredientFilter, RecipeFilter
from .models import Ingredient, Recipe, Tag, RecipeIngredient
from .permissions import IsAdminOrReadOnly, IsAuthorOrAdmin
from .serializers import (
    AddRecipeSerializer,
    AddShowRecipeSerializer,
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer,
)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_classes = {
        "retrieve": AddShowRecipeSerializer,
        "list": AddShowRecipeSerializer,
    }
    default_serializer_class = AddRecipeSerializer
    permission_classes = (IsAuthorOrAdmin,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = LimitPageNumberPaginator

    def get_serializer_class(self):
        return self.serializer_classes.get(
            self.action,
            self.default_serializer_class,
        )

    @action(
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
        methods=["POST", "DELETE"],
    )
    def favorite(self, request, pk=None):
        recipe = self.get_object()

        match request.method:
            case "DELETE":
                try:
                    request.user.favorites.get(recipe=recipe).delete()
                    return Response(
                        data={"success": f"{recipe} удален из избранного"},
                        status=status.HTTP_204_NO_CONTENT,
                    )
                except ObjectDoesNotExist:
                    return Response(
                        data={"error": f"{recipe} не найден в избранном"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            case "POST":
                try:
                    request.user.favorites.create(recipe=recipe)
                    serializer = RecipeSerializer(instance=recipe)
                    return Response(
                        data=serializer.data, status=status.HTTP_201_CREATED
                    )
                except IntegrityError as error:
                    if "unique_favorite" in str(error):
                        return Response(
                            data={"error": f"{recipe} уже в избранном"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    raise error

    @action(
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
        methods=["POST", "DELETE"],
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()

        match request.method:
            case "DELETE":
                try:
                    request.user.users_set.get(recipe=recipe).delete()
                    return Response(
                        data={"success": f"{recipe} удален из корзины"},
                        status=status.HTTP_204_NO_CONTENT,
                    )
                except ObjectDoesNotExist:
                    return Response(
                        data={"error": f"{recipe} не найден в корзине"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            case "POST":
                try:
                    request.user.users_set.create(recipe=recipe)
                    serializer = RecipeSerializer(instance=recipe)
                    return Response(
                        data=serializer.data, status=status.HTTP_201_CREATED
                    )
                except IntegrityError as error:
                    if "recipe_already_in_busket" in str(error):
                        return Response(
                            data={"error": f"{recipe} уже в корзине"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    raise error

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        if not request.user.users_set.exists():
            return Response(
                data={"error": "Список покупок пуст"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__basket_set__user=request.user
            )
            .values("ingredient__name", "ingredient__unit")
            .annotate(amount=Sum("amount"))
        )

        shopping_list = (
            f"Список покупок для: {request.user.username}\n\n"
            f"Дата: {dt.date.today():%Y-%m-%d}\n\n"
        )
        shopping_list += "\n".join(
            [
                f'{ingredient["ingredient__name"]}, '
                f'{ingredient["amount"]} '
                f'{ingredient["ingredient__unit"]}'
                for ingredient in ingredients
            ]
        )
        filename = (
            f"{request.user.username}_"
            f"{dt.date.today():%Y-%m-%d}_shopping_list.txt"
        )

        response = HttpResponse(
            content=shopping_list,
            content_type="text.txt; charset=utf-8",
        )
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
