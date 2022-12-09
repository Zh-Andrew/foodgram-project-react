from django.db import models
from users.models import User


class Ingredient(models.Model):
    """Модель для ингредиентов к рецепту"""
    name = models.CharField(
        max_length=150,
        verbose_name='Наименование ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель для подготовки тэгов"""

    COLOR_CHOICES = (
        ('#FFA500', 'Orange'),
        ('#008000', 'Green'),
        ('#9400D3', 'DarkViolet')
    )

    name = models.CharField(
        max_length=40,
        verbose_name='Наименование тэга'
    )
    color = models.CharField(
        max_length=40,
        choices=COLOR_CHOICES,
        verbose_name='Цвет тэга'
    )
    slug = models.SlugField(
        max_length=40,
        unique=True
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.slug


class Recipe(models.Model):
    """Модель для создания рецепта"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        upload_to='media/',
        blank=True,
        verbose_name='Изображение рецепта'
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='Amount',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        verbose_name='Тэги рецептов'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления, мин.'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['pub_date']

    def __str__(self):
        return self.name


class TagRecipe(models.Model):
    """
    Промежуточная модель для связи тегов с рецептами.
    """
    recipe = models.ForeignKey(
        Recipe,
        related_name='tag_recipe',
        on_delete=models.SET_NULL,
        null=True
    )
    tag = models.ForeignKey(
        Tag,
        related_name='tag_recipe',
        on_delete=models.SET_NULL,
        null=True
    )


class Amount(models.Model):
    """
    Промежуточная модель определяет количество
    ингредиентов необходимых для рецепта
    """
    amount = models.PositiveIntegerField(
        verbose_name='Количество от ингредиента'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='amount',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='amount',
        on_delete=models.CASCADE
    )


class FavouriteRecipe(models.Model):
    """
    Модель определяет рецепты, которые находятся
    у авторизованного пользователя в избранном.
    """
    user = models.ForeignKey(
        User,
        related_name='favourite',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favourite',
        on_delete=models.CASCADE
    )


class ShoppingList(models.Model):
    """
    Модель определяет ингредиенты для покупки
    для приготовления блюда по рецепту
    """
    user = models.ForeignKey(
        User,
        related_name='shopping',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='shopping',
        on_delete=models.CASCADE
    )
