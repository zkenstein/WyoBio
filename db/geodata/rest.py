from wq.db import rest
from .models import Point, Observation, Weather
from .serializers import PointSerializer, ObservationSerializer
from .views import ObservationViewSet

rest.router.register_model(
    Point,
    serializer=PointSerializer,
)
rest.router.register_model(
    Observation,
    serializer=ObservationSerializer,
    viewset=ObservationViewSet,
)

rest.router.register_model(Weather)

rest.router.add_page('index', {'url': ''})
