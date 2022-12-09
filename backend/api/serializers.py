import base64
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from rest_framework import serializers

from foodgram.models import Tag, Ingredient, Recipe, Amount, FavouriteRecipe, ShoppingList, TagRecipe
from users.serializers import CustomUserSerializer
from users.models import User, Subscription


# class CustomUserCreateSerializer(UserCreateSerializer):
#     """Сериализатор для создания пользователя. Наследуется от djoser"""
#
#     email = serializers.EmailField(
#         validators=[UniqueValidator(queryset=User.objects.all())]
#     )
#     username = serializers.CharField(
#         validators=[UniqueValidator(queryset=User.objects.all())]
#     )
#     first_name = serializers.CharField(required=True)
#     last_name = serializers.CharField(required=True)
#
#     class Meta:
#         model = User
#         fields = ('email', 'id', 'username', 'password', 'first_name', 'last_name',)
#
#
# class CustomUserSerializer(UserSerializer):
#     """Сериализатор модели пользователя. Наследуется от djoser"""
#
#     is_subscribed = serializers.SerializerMethodField()
#
#     class Meta:
#         model = User
#         fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')
#         validators = [
#             UniqueTogetherValidator(
#                 queryset=Subscription.objects.all(),
#                 fields=('user', 'author'),
#                 message='Подписка уже существует'
#             )
#         ]
#
#     def get_is_subscribed(self, obj):
#         user = self.context.get('request').user
#         if user.is_anonymous:
#             return False
#         return Subscription.objects.filter(user=user, author=obj).exists()
#
#
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
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = Amount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AmountPostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Amount
        fields = ('id', 'amount')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField()
    is_favourited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author',
                  'ingredients', 'is_favourited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_ingredients(self, obj):
        queryset = Amount.objects.filter(recipe=obj)
        return AmountSerializer(queryset, many=True).data

    def get_is_favourited(self, obj):
        author = self.context.get('request').user
        return FavouriteRecipe.objects.filter(user=author, recipe=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        author = self.context.get('request').user
        return ShoppingList.objects.filter(user=author, recipe=obj.id).exists()


class RecipePostSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = AmountPostSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('tags', 'ingredients', 'name',
                  'image', 'text', 'cooking_time')

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)

        for tag in tags:
            TagRecipe.objects.create(recipe=recipe, tag=tag)

        for ingredient in ingredients:
            ingredient_amount = ingredient['amount']
            ingredient = Ingredient.objects.get(id=ingredient['id'])
            Amount.objects.create(
                recipe=recipe, ingredient=ingredient,
                amount=ingredient_amount,
            )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        ingredients = []
        for ingredient in validated_data.get('ingredients'):
            obj, _ = Amount.objects.get_or_create(**ingredient)
            ingredients.append(obj)
        instance.ingredients.set(ingredients)
        instance.save()
        tags = []
        for tag in validated_data.get('tags'):
            obj, _ = TagRecipe.objects.get_or_create(**tag)
            tags.append(obj)
        instance.ingredients.set(tags)
        instance.save()
        return instance


class ShowFavouriteShoppingSerializer(serializers.ModelSerializer):

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

    def to_representation(self, instance):
        return ShowFavouriteShoppingSerializer(instance.recipe, context={
            'request': self.context.get('request')
        }).data
