from django_filters import rest_framework


class RecipeFilter(rest_framework.FilterSet):
    author = rest_framework.NumberFilter(
        field_name='author__id',
        lookup_expr='contains')

    tags = rest_framework.CharFilter(
        field_name='tags__slug',
        lookup_expr='contains')

    is_favorited = rest_framework.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    def get_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favourites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_lists__user=self.request.user)
        return queryset
