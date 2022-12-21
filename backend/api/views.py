from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from foodgram.models import (Amount, FavouriteRecipe, Ingredient, Recipe,
                             ShoppingList, Tag)

from .filters import IngredientSearchFilter, RecipeFilterSet
from .pagination import LimitPagePagination
from .permissions import IsAdminOrOwnerOrReadOnly, IsAdminOrReadOnly
from .serializers import (FavouriteRecipeSerializer, IngredientSerializer,
                          RecipePostSerializer, RecipeSerializer,
                          ShoppingListSerializer, TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly, )
    filter_backends = (IngredientSearchFilter, )
    search_fields = ('^name', )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = LimitPagePagination
    permission_classes = (IsAdminOrOwnerOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilterSet

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT', 'PATCH'):
            return RecipePostSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,)

    @action(detail=False,
            methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredient_list = 'Cписок покупок:'
        ingredients = Amount.objects.filter(
            recipe__shopping__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        for num, i in enumerate(ingredients):
            ingredient_list += (
                f'\n{i["ingredient__name"]} - '
                f'{i["amount"]} {i["ingredient__measurement_unit"]}'
            )
            if num < ingredients.count() - 1:
                ingredient_list += ', '
        file = 'shopping_list'
        response = HttpResponse(
            ingredient_list, 'Content-Type: application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{file}.pdf"'
        return response


class ShoppingListAPI(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, id):
        data = {
            'user': request.user.id,
            'recipe': id
        }
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
        shopping_list_obj = ShoppingList.objects.filter(
            user=user, recipe=recipe)
        if shopping_list_obj.exists():
            shopping_list_obj.delete()
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
        favourite_recipe_obj = FavouriteRecipe.objects.filter(user=user, recipe=recipe)
        if favourite_recipe_obj.exists():
            favourite_recipe_obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            'Рецепта не было в избранном',
            status=status.HTTP_400_BAD_REQUEST
        )
