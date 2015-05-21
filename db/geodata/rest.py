from wq.db import rest
from .models import Point, Observation, Weather
from .serializers import PointSerializer, ObservationSerializer
from .views import PointViewSet

rest.router.register_model(
    Point,
    serializer=PointSerializer,
    viewset=PointViewSet,
)
rest.router.register_model(
    Observation,
    serializer=ObservationSerializer
)

rest.router.register_model(Weather)

rest.router.add_page('index', {'url': ''})
