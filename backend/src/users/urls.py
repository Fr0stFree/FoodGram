from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "users"

api_router_v1 = DefaultRouter()
api_router_v1.register(
    prefix="users/subscriptions",
    viewset=views.FollowViewSet,
    basename="subscriptions",
)

urlpatterns = [
    path("", include(api_router_v1.urls)),
    path("", include("djoser.urls")),
    path(
        route="auth/token/login/",
        view=views.Status201TokenCreateView.as_view(),
        name="login",
    ),
    path(
        route="auth/token/logout/",
        view=views.Status201TokenDestroyView.as_view(),
        name="logout",
    ),
    path(
        route="users/<int:id>/subscribe/",
        view=views.APIFollowView.as_view(),
        name="follow-author",
    ),
]
