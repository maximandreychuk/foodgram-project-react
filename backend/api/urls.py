from api.views import (
    DownloadShoppingList,
    Favourite,
    IngredientViewSet,
    RecipeViewSet,
    ShoppingList,
    Subscribe,
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
    path('recipes/download_shopping_cart/',
         DownloadShoppingList.as_view()),
    path('users/subscriptions/',
         Subscriptions.as_view()),
    re_path(r'^users/(?P<pk>\d+)/subscribe/$',
            Subscribe.as_view()),
    re_path(r'^recipes/(?P<pk>\d+)/favorite/$',
            Favourite.as_view()),
    re_path(r'^recipes/(?P<pk>\d+)/shopping_cart/$',
            ShoppingList.as_view()),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
