from api.views import (
    DownloadShoppingList,
    FavouriteAddDelete,
    IngredientViewSet,
    RecipeViewSet,
    ShoppingListAddAndDelete,
    SubscribeAndUnsubscribe,
    Subscriptions,
    TagViewSet,
)
from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipe')
router.register('ingredients', IngredientViewSet, basename='ingredient')
router.register('tags', TagViewSet, basename='tag')


urlpatterns = [
    path('users/subscriptions/', Subscriptions.as_view()),
    path('recipes/download_shopping_cart/',
         DownloadShoppingList.as_view()),
    re_path(r'^users/(?P<pk>\d+)/subscribe/$',
            SubscribeAndUnsubscribe.as_view()),
    re_path(r'^recipes/(?P<pk>\d+)/favorite/$',
            FavouriteAddDelete.as_view()),
    re_path(r'^recipes/(?P<pk>\d+)/shopping_cart/$',
            ShoppingListAddAndDelete.as_view()),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
]
