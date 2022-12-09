from rest_framework import viewsets, filters, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from foodgram.models import Tag, Ingredient, Recipe, ShoppingList, FavouriteRecipe
from .serializers import (TagSerializer, IngredientSerializer, RecipeSerializer,
                          RecipePostSerializer, ShoppingListSerializer,
                          FavouriteRecipeSerializer)
from api.pagination import LimitPagePagination
from api.permissions import IsAdminOrOwnerOrReadOnly, IsAdminOrReadOnly


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly, )
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name', )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = LimitPagePagination
    permission_classes = (IsAdminOrOwnerOrReadOnly, )

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT', 'PATCH'):
            return RecipePostSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,)


class ShoppingListAPI(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, id):
        data = {
            'user': request.user.id,
            'recipe': id
        }
        if ShoppingList.objects.filter(
            user=request.user,
            recipe__id=id
        ).exists():
            return Response(
                'Рецепт уже находится в вашем списке продуктов',
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = ShoppingListSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        if ShoppingList.objects.filter(
            user=user,
            recipe=recipe
        ).exists():
            ShoppingList.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            'Рецепт не был добавлен в список для покупок',
            status=status.HTTP_400_BAD_REQUEST
        )


class FavouriteRecipeAPI(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, id):
        data = {
            'user': request.user.id,
            'recipe': id
        }
        if FavouriteRecipe.objects.filter(
            user=request.user, recipe__id=id
        ).exists():
            return Response(
                'Рецепт уже находится в избранном',
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = FavouriteRecipeSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        if FavouriteRecipe.objects.filter(user=user, recipe=recipe).exists():
            FavouriteRecipe.objects.filter(
                user=user, recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            'Рецепта не было в избранном',
            status=status.HTTP_400_BAD_REQUEST
        )
