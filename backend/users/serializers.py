from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from rest_framework import serializers
from .models import User, Subscription
from foodgram.models import Recipe
# from api.serializers import ShowFavouriteShoppingSerializer


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя. Наследуется от djoser"""

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'password', 'first_name', 'last_name',)


class CustomUserSerializer(UserSerializer):
    """Сериализатор модели пользователя. Наследуется от djoser"""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='Подписка уже существует'
            )
        ]

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()


# class ShowSubscriptionSerializer(serializers.ModelSerializer):
#     """Сериализатор для отображения подписок текущего пользователя"""
#
#     is_subscribed = serializers.SerializerMethodField()
#     recipes = serializers.SerializerMethodField()
#     recipes_count = serializers.SerializerMethodField()
#
#     class Meta:
#         model = User
#         fields = (
#             'id',
#             'email',
#             'username',
#             'first_name',
#             'last_name',
#             'is_subscribed',
#             'recipes',
#             'recipes_count'
#         )
#
#     def get_is_subscribed(self, obj):
#         user = self.context.get('request').user
#         if user.is_anonymous:
#             return False
#         return Subscription.objects.filter(user=user, author=obj).exists()
#
#     def get_recipes(self, obj):
#         request = self.context.get('request')
#         if not request or request.user.is_anonymous:
#             return False
#         recipes = Recipe.objects.filter(author=obj)
#         limit = request.query_params.get('recipes_limit')
#         if limit:
#             recipes = recipes[:int(limit)]
#         return ShowFavouriteShoppingSerializer(
#             recipes, many=True, context={'request': request}
#         ).data
#
#     def get_recipes_count(self, obj):
#         return Recipe.objects.filter(author=obj).count()
