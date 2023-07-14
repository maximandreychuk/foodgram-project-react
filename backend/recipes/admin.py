from django.contrib import admin
from recipes.models import (
    Favourite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingList,
    Tag,
)


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'get_tags',
        'author',
        'get_ingredients',
        'name',
        'image',
        'text',
        'cooking_time',
        'in_favorited',
    )

    list_filter = ('author', 'name', 'tags',)

    @admin.display(description='в избранном')
    def in_favorited(self, obj):
        return obj.favourites.count()

    @admin.display(description='тэги')
    def get_tags(self, obj):
        return [i.name for i in obj.tags.all()]

    @admin.display(description='ингредиенты')
    def get_ingredients(self, obj):
        return [i.name for i in obj.ingredients.all()]


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    list_filter = ('name',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(ShoppingList)
admin.site.register(IngredientRecipe)
admin.site.register(Favourite)
