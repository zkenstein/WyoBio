from wq.db import rest
from .models import Point, Observation
from .serializers import PointSerializer, ObservationSerializer

rest.router.register_model(
    Point,
    serializer=PointSerializer
)
rest.router.register_model(
    Observation,
    serializer=ObservationSerializer
)

rest.router.add_page('index', {'url': ''})
