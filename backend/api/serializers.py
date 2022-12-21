from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from foodgram.models import (Amount, FavouriteRecipe, Ingredient, Recipe,
                             ShoppingList, Tag, TagRecipe)
from users.models import Subscription, User
from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):
    color = serializers.ChoiceField(choices=Tag.COLOR_CHOICES)

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class AmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = Amount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AmountPostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Amount
        fields = ('id', 'amount')


# class Base64ImageField(serializers.ImageField):
#     def to_internal_value(self, data):
#         if isinstance(data, str) and data.startswith('data:image'):
#             format, imgstr = data.split(';base64,')
#             ext = format.split('/')[-1]
#             data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
#
#         return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author',
                  'ingredients', 'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_ingredients(self, obj):
        queryset = Amount.objects.filter(recipe=obj)
        return AmountSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        author = self.context.get('request').user
        return FavouriteRecipe.objects.filter(
            user=author, recipe=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        author = self.context.get('request').user
        return ShoppingList.objects.filter(user=author, recipe=obj.id).exists()


class RecipePostSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = AmountPostSerializer(many=True, source='amount')
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('tags', 'ingredients', 'name',
                  'image', 'text', 'cooking_time')

    def create_ingredients(self, recipe, ingredients):
        Amount.objects.bulk_create(
            Amount(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients
        )

    def create_tags(self, recipe, tags):
        TagRecipe.objects.bulk_create(
            TagRecipe(
                recipe=recipe,
                tag=tag
            ) for tag in tags
        )

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('amount')
        recipe = Recipe.objects.create(**validated_data)
        self.create_tags(recipe, tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        TagRecipe.objects.filter(recipe=instance).delete()
        Amount.objects.filter(recipe=instance).delete()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('amount')
        self.create_tags(instance, tags)
        self.create_ingredients(instance, ingredients)
        instance.save()
        return instance


class ShowFavouriteShoppingSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingListSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingList.objects.all(),
                fields=('user', 'recipe')
            )
        ]

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if ShoppingList.objects.filter(
                user=request.user, recipe=recipe
        ).exists():
            raise ValidationError({
                'errors': 'Рецепт уже находится в вашем списке продуктов'
            })
        return data

    def to_representation(self, instance):
        return ShowFavouriteShoppingSerializer(instance.recipe, context={
            'request': self.context.get('request')
        }).data


class FavouriteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavouriteRecipe
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=FavouriteRecipe.objects.all(),
                fields=('user', 'recipe')
            )
        ]

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if FavouriteRecipe.objects.filter(
                user=request.user, recipe=recipe
        ).exists():
            raise ValidationError({
                'errors': 'Рецепт уже находится в избранном'
            })
        return data

    def to_representation(self, instance):
        return ShowFavouriteShoppingSerializer(instance.recipe, context={
            'request': self.context.get('request')
        }).data


class ShowSubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения подписок текущего пользователя"""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipes = Recipe.objects.filter(author=obj)
        limit = request.query_params.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        return ShowFavouriteShoppingSerializer(
            recipes, many=True, context={'request': request}
        ).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('user', 'author')

    def validate(self, data):
        get_object_or_404(User, username=data['author'])
        if self.context['request'].user == data['author']:
            raise serializers.ValidationError({
                'errors': 'Нельзя подписаться на самого себя.'
            })
        if Subscription.objects.filter(
            user=self.context['request'].user,
            author=data['author']
        ):
            raise serializers.ValidationError({
                'errors': 'Подписка на автора уже существует.'
            })
        return data

    def to_representation(self, instance):
        return ShowSubscriptionSerializer(
            instance.author,
            context={'request': self.context.get('request')}
        ).data
