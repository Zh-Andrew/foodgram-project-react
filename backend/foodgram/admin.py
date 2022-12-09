from django.contrib import admin
from .models import Tag, Ingredient, Recipe, Amount, FavouriteRecipe, ShoppingList


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    ordering = ('name', )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('^name', )
    ordering = ('name', )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'image', 'text', 'get_ingredients', 'get_tags', 'cooking_time')
    ordering = ('pub_date', )

    def get_tags(self, obj):
        return '\n'.join([t.name for t in obj.tags.all()])

    def get_ingredients(self, obj):
        return '\n'.join([i.name for i in obj.ingredients.all()])


@admin.register(Amount)
class AmountAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'recipe', 'amount')


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(FavouriteRecipe)
class FavouriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
