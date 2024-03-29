from django.urls import include, path
from rest_framework import routers

from .views import (FavouriteRecipeAPI, IngredientViewSet, RecipeViewSet,
                    ShoppingListAPI, TagViewSet)

app_name = 'api'

router = routers.DefaultRouter()

router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('recipes/<int:id>/shopping_cart/',
         ShoppingListAPI.as_view(),
         name='shopping_cart'),
    path('recipes/<int:id>/favorite/',
         FavouriteRecipeAPI.as_view(),
         name='favorite'),
]
