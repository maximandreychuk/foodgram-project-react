from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path('', views.index, name='recipes'),
    path('group/<slug:slug>/', views.group_posts, name='group_page'),
]
