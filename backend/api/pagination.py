from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from recipes.models import Recipe
from rest_framework.pagination import BasePagination


class CustomPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'
