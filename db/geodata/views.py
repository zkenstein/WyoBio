from wq.db.rest.views import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class ObservationViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
