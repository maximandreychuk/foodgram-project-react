from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from recipes.models import Recipe
from rest_framework.pagination import BasePagination



class CustomPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'

class SubPagination(BasePagination):
    # def paginate_queryset(self, queryset, request, view=None):
    #     recipes_limit = request.get(recipes_limit)

    #     start = center - radius if center - radius > 0 else 0
    #     finish = center + radius
    #     return list(queryset[start:finish])

    def get_paginated_resposne(self, data):
        recipes_limit = self.request.get('recipes_limit')
        if recipes_limit:
            return Response({
                'links': {
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link()
                    },
                'count': self.page.paginator.count,
                'results': data['recipes'][:recipes_limit]
            })