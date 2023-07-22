from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from djoser.conf import settings
from djoser.utils import login_user, logout_user
from djoser.views import TokenCreateView, TokenDestroyView
from rest_framework import filters, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from main.pagination import LimitPageNumberPaginator

from .models import Follow
from .serializers import FollowSerializer

User = get_user_model()


class Status201TokenCreateView(TokenCreateView):
    def _action(self, serializer):
        token = login_user(self.request, serializer.user)
        token_serializer_class = settings.SERIALIZERS.token
        return Response(
            data=token_serializer_class(token).data,
            status=status.HTTP_201_CREATED,
        )


class Status201TokenDestroyView(TokenDestroyView):
    def post(self, request):
        logout_user(request)
        return Response(status=status.HTTP_201_CREATED)


class APIFollowView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, id):
        user = get_object_or_404(User, id=request.user.id)
        author = get_object_or_404(User, id=id)

        try:
            Follow.objects.create(follower=user, author=author)
        except IntegrityError:
            content = {
                "error": f"Оформление подписки на {author.username} невозможно"
            }
            return Response(data=content, status=status.HTTP_400_BAD_REQUEST)

        serializer = FollowSerializer(
            instance=author,
            context={"request": request},
        )
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = get_object_or_404(User, username=request.user.username)
        author = get_object_or_404(User, id=id)
        try:
            Follow.objects.get(follower=user, author=author).delete()
        except ObjectDoesNotExist:
            content = {"error": f"Вы не подписаны на {author.username}"}
            return Response(data=content, status=status.HTTP_400_BAD_REQUEST)

        content = {"success": f"Вы успешно отписались от {author.username}"}
        return Response(data=content, status=status.HTTP_204_NO_CONTENT)


class FollowViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = LimitPageNumberPaginator
    filter_backends = (filters.SearchFilter,)
    search_fields = ("^following__user",)

    def get_queryset(self):
        user = self.request.user
        new_queryset = User.objects.filter(author__follower=user)
        return new_queryset
