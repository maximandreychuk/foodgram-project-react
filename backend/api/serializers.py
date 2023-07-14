import webcolors

from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (
    Favourite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingList,
    Tag,
)
from rest_framework import serializers
from users.models import User


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class UserCreateSerializer(UserCreateSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name',
            'last_name', 'password')


class UserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.follower.filter(author=obj).exists()


class FollowRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'recipes', 'is_subscribed', 'recipes_count',
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return user.follower.filter(author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = FollowRecipeSerializer(
            recipes, many=True, context={
                'request': request})
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor(required=True)

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    measurement_unit = serializers.ReadOnlyField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class ReadOnlyRecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipeSerializer(
        many=True, source='ingredientrecipes'
    )
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time',
            'is_favorited', 'is_in_shopping_cart',
        )
        read_only_fields = ('author',)

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return 'Зарегистрируйтесь, чтобы добавить рецепт в избранное'
        return user.favourites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return 'Зарегистрируйтесь, чтобы добавить рецепт в список покупок'
        return user.shopping_lists.filter(recipe=obj).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)
    ingredients = IngredientRecipeSerializer(many=True)
    tags = serializers.SlugRelatedField(
        slug_field='id',
        many=True,
        queryset=Tag.objects.all(),
        required=True
    )

    class Meta:
        fields = (
            'id', 'tags', 'ingredients', 'author',
            'name', 'image', 'text', 'cooking_time',
        )
        model = Recipe
        read_only_fields = ('author',)

    def _create_ingredient_recipe_objects(self, ingredients, recipe):

        for ingredient in ingredients:
            ingredient_amount = ingredient.pop('amount')
            ingredient_obj = get_object_or_404(
                Ingredient, id=ingredient['ingredient']['id']
            )
            IngredientRecipe.objects.get_or_create(
                recipe=recipe,
                ingredient=ingredient_obj,
                amount=ingredient_amount
            )
            recipe.ingredients.add(ingredient_obj)
        return recipe

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        return self._create_ingredient_recipe_objects(ingredients, recipe)

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self._create_ingredient_recipe_objects(ingredients, recipe=instance)
        return instance

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return ReadOnlyRecipeSerializer(instance, context=context).data

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError('Укажите хотя бы один тэг')
        return value

    def validate_cooking_time(self, value):
        if int(value) <= 0:
            raise serializers.ValidationError(
                'Время приготовления не должно быть меньше 0')
        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Добавьте хотя бы один ингредиент')
        return value


class FavouriteSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Favourite
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url)

    def validate(self, data):
        user = self.context.get('request').user
        if user.favourites.filter(recipe=self.instance).exists():
            raise serializers.ValidationError(
                'Вы уже добавили этот рецепт в избранное')
        return data


class ShoppingListSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField()
    image = serializers.SerializerMethodField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = ShoppingList
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url)

    def validate(self, data):
        user = self.context.get('request').user
        if user.shopping_lists.filter(recipe=self.instance).exists():
            raise serializers.ValidationError(
                'Вы уже добавили этот рецепт в cписок покупок')
        return data
