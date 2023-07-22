from django.core.exceptions import ObjectDoesNotExist
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from main.pagination import LimitPageNumberPaginator

from .filters import IngredientFilter, RecipeFilter
from .models import Ingredient, Recipe, Tag
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

    def __recipe_update(self, related_manager):
        recipe = self.get_object()
        if self.request.method == "DELETE":
            try:
                related_manager.get(recipe_id=recipe.id).delete()
            except ObjectDoesNotExist:
                return Response(
                    data={"error": f"{recipe} не найден"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                data={"success": f"{recipe} успешно удален"},
                status=status.HTTP_204_NO_CONTENT,
            )

        if related_manager.filter(recipe=recipe).exists():
            return Response(
                data={"error": f"{recipe} уже в списке"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        related_manager.create(recipe=recipe)
        serializer = RecipeSerializer(instance=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
        methods=["POST", "DELETE"],
    )
    def favorite(self, request, pk=None):
        return self.__recipe_update(request.user.favorites)

    @action(
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
        methods=["POST", "DELETE"],
    )
    def busket(self, request, pk=None):
        return self.__recipe_update(request.user.shopping_user)


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
