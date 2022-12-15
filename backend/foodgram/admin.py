from django.contrib import admin

from .models import (Amount, FavouriteRecipe, Ingredient, Recipe, ShoppingList,
                     Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    ordering = ('name', )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('^name', )
    ordering = ('name', )


class AmountInLine(admin.TabularInline):
    model = Amount
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'favourite')
    search_fields = ('name', )
    list_filter = ('author', 'name', 'tags')
    readonly_fields = ('favourite', )
    filter_horizontal = ('tags',)

    def favourite(self, obj):
        return obj.favourite.all().count()

    favourite.short_description = 'Количество добавлений в избранное'


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user', )


@admin.register(FavouriteRecipe)
class FavouriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
