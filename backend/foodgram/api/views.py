from api.filters import RecipeFilter
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
    UserSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import (
    Favourite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingList,
    Tag,
)
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import Follow, User


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all() 
    http_method_names = ('get', 'post', 'patch', 'delete',)
    permissions_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_class = RecipeFilter
    ordering = ('-id',)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return ReadOnlyRecipeSerializer
        return RecipeWriteSerializer


class IngredientViewSet(mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('^name',)
    pagination_class = None


class TagViewSet(mixins.RetrieveModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class Subscriptions(APIView):
    permission_classes=(IsAuthenticated,)

    @action(detail=False)
    def get(self, request):
        subscriptions = User.objects.filter(following__user=request.user)
        serializer = FollowSerializer(
            subscriptions, 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscribeAndUnsubscribe(APIView):
    permission_classes=(IsAuthenticated,)
    
    def post(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        serializer = FollowSerializer(
            author, 
            data=request.data, 
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        Follow.objects.create(user=request.user, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        subscription = get_object_or_404(
            Follow,
            user=request.user,
            author=get_object_or_404(User, pk=pk)
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavouriteAddDelete(APIView):
    permission_classes=(IsAuthenticated,)
    
    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = FavouriteSerializer(
            recipe,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        Favourite.objects.create(user=request.user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        unfollow = get_object_or_404(
            Favourite,
            user=request.user,
            recipe=get_object_or_404(Recipe, pk=pk)
        )
        unfollow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingListAddAndDelete(APIView):
    permission_classes=(IsAuthenticated,)
    
    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = ShoppingListSerializer(
            recipe,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        ShoppingList.objects.create(
            user=request.user,
            recipe=recipe
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        removingfromthelist = get_object_or_404(
            ShoppingList,
            user=request.user,
            recipe=get_object_or_404(Recipe, pk=pk)
        )
        removingfromthelist.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingList(APIView):
    permission_classes=(IsAuthorOrReadOnly,)

    def get(self, request):
        if not request.user.shopping_lists.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_lists__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        shopping_list = 'Список покупок: '
        for ingredient in ingredients:
            shopping_list += (
                f"\n{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['amount']}")
        file = 'shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
        return response

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })