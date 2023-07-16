from rest_framework import mixins, viewsets


class OnlyReadViewSet(mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    pass
