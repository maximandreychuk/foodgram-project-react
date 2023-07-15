from django.shortcuts import get_object_or_404
from recipes.models import Recipe
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# не помню(не понял) как через миксин, через наследование сделал..
class AddAndDeleteAPIview(APIView):
    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = self.serializer_class(
            recipe,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        self.model.objects.create(
            user=request.user, 
            recipe=recipe
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        queryset = get_object_or_404(
            self.model,
            user=request.user,
            recipe=get_object_or_404(Recipe, pk=pk)
        )
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
