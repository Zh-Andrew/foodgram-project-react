from djoser.views import UserViewSet
from django.shortcuts import get_object_or_404
from requests import Response
from rest_framework import permissions, status
from rest_framework.decorators import action

from api.pagination import LimitPagePagination
from api.serializers import ShowSubscriptionSerializer
from .models import User, Subscription


class CustomUserViewSet(UserViewSet):
    pagination_class = LimitPagePagination

    @action(
        detail=True,
        methods=['POST', ],
        permission_classes=permissions.IsAuthenticated)
    def subscribe(self, request, pk):
        user = request.user
        author = get_object_or_404(User, pk=pk)
        if request.user == author:
            return Response(
                'Нельзя подписаться на самого себя',
                status=status.HTTP_400_BAD_REQUEST
            )
        if Subscription.objects.filter(user=user, author=author).exists():
            return Response(
                'Вы уже подписаны на данного пользователя',
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription = Subscription.objects.create(user=user, author=author)
        serializer = ShowSubscriptionSerializer(
            subscription, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=['DELETE', ],
    )
    def del_subscribe(self, request, pk):
        user = request.user
        author = get_object_or_404(User, pk=pk)
        subscription = get_object_or_404(
            Subscription,
            user=user,
            author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=permissions.IsAuthenticated
    )
    def subscriptions(self, request):
        user = request.user
        pages = self.paginate_queryset(
            Subscription.objects.filter(user=user)
        )
        serializer = ShowSubscriptionSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
