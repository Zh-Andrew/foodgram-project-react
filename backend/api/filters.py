from django_filters.rest_framework import FilterSet, filters
from foodgram.models import Recipe


class RecipeFilterSet(FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favourited = filters.BooleanFilter(method='filter_is_favourited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favourited', 'is_in_shopping_cart')

    def filter_is_favourited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favourite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(shopping__user=self.request.user)
        return queryset
