from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipesViewSet, TagViewSet

app_name = "recipes"

api_recipes_router_v1 = DefaultRouter()
api_recipes_router_v1.register(
    prefix="tags", viewset=TagViewSet, basename="tags"
)
api_recipes_router_v1.register(
    prefix="ingredients", viewset=IngredientViewSet, basename="ingredients"
)
api_recipes_router_v1.register(
    prefix="recipes", viewset=RecipesViewSet, basename="recipes"
)

urlpatterns = [
    path(r"", include(api_recipes_router_v1.urls)),
]
