from api.filters import RecipeFilter
from api.mixins import OnlyReadViewSet
from api.pagination import CustomPagination
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from api.serializers import (
    FavouriteSerializer,
    FollowSerializer,
    IngredientSerializer,
    ReadOnlyRecipeSerializer,
    RecipeWriteSerializer,
    ShoppingListSerializer,
    TagSerializer,
    UserCreateSerializer,
    UserSerializer
)
from api.utils import AddAndDeleteAPIview
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from recipes.models import (
    Favourite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingList,
    Tag,
)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import Follow, User


class Favourite(AddAndDeleteAPIview):
    permission_classes = (IsAuthenticated,)
    serializer_class = FavouriteSerializer
    model = Favourite

    def post(self, request, pk):
        return super().post(request, pk)

    def delete(self, request, pk):
        return super().delete(request, pk)


class ShoppingList(AddAndDeleteAPIview):
    permission_classes = (IsAuthenticated,)
    serializer_class = ShoppingListSerializer
    model = ShoppingList

    def post(self, request, pk):
        return super().post(request, pk)

    def delete(self, request, pk):
        return super().delete(request, pk)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ('get', 'post', 'patch', 'delete',)
    pagination_class = CustomPagination
    permissions_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_class = RecipeFilter
    ordering = ('-id',)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return ReadOnlyRecipeSerializer
        return RecipeWriteSerializer


class IngredientViewSet(OnlyReadViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('^name',)


class TagViewSet(OnlyReadViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class SubscribeViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return UserCreateSerializer
        return UserSerializer

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        subscriptions = User.objects.filter(following__user=request.user)
        result=self.paginate_queryset(subscriptions)
        serializer = FollowSerializer(
            result,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, pk):
        if request.method == 'POST':
            author = get_object_or_404(User, pk=pk)
            serializer = FollowSerializer(
                author,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=request.user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            subscription = get_object_or_404(
                Follow,
                user=request.user,
                author=get_object_or_404(User, pk=pk)
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingList(APIView):
    permission_classes = (IsAuthorOrReadOnly,)

    def get(self, request):
        if not request.user.shopping_lists.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_lists__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        shopping_list = 'Список покупок: '
        shopping_list += '\n'.join(
            [
                f'\n{ingredient["ingredient__name"]} '
                f'({ingredient["ingredient__measurement_unit"]})'
                f' — {ingredient["amount"]}'
                for ingredient in ingredients
            ]
        )
        file = 'shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
        return response
