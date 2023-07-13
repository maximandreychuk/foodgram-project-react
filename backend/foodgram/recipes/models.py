from django.db import models
from django.core.validators import MinValueValidator
from foodgram.settings import RECIPES_LENGTH
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        'Название', 
        max_length=RECIPES_LENGTH
    )
    measurement_unit = models.CharField(
        'Единица измерения', 
        max_length=RECIPES_LENGTH
    )

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        'Название', 
        max_length=RECIPES_LENGTH
    )
    color = models.CharField(
        'Цвет',
        max_length=RECIPES_LENGTH,
        unique=True,
    )
    slug = models.SlugField(
        'Уникальный слаг',
        unique=True,
        max_length=RECIPES_LENGTH
    )

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes')
    name = models.CharField(
        'Название', 
        max_length=RECIPES_LENGTH
    )
    text = models.TextField('Текст')
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/images',
        null=True,
        default=None
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='IngredientRecipe'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
    )
    cooking_time = models.IntegerField('Время приготовления')


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, 
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredientrecipes')
    amount = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )

    class Meta:  
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_recipe'
            )
        ]


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_lists',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_lists'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='already_in_the_list'
            )
        ]


class Favourite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favourites',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favourites'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='already_in_favorites'
            )
        ]
