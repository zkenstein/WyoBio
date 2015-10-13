from wq.db import rest
from .models import Point, Observation, Habitat, Weather, Phenology, Species
from django.conf import settings
from .serializers import (
    PointSerializer, ObservationSerializer, SpeciesSerializer,
)
from .views import ObservationViewSet

def point_filter(qs, request):
    if request.user.is_authenticated():
        return qs.filter(userid=request.user.id)
    else:
        return qs.none()

def observation_filter(qs, request):
    points = point_filter(Point.objects.all(), request)
    pntids = points.values_list('pntid', flat=True)
    return qs.filter(point_id__in=pntids)

rest.router.register_model(
    Point,
    serializer=PointSerializer,
    filter=point_filter,
    per_page=100,
    max_local_pages=1,
    # partial=True,
)
rest.router.register_model(
    Observation,
    serializer=ObservationSerializer,
    viewset=ObservationViewSet,
    filter=observation_filter,
    per_page=100,
    max_local_pages=1,
    reversed=True,
    # partial=True,
)

rest.router.register_model(Habitat)
rest.router.register_model(Weather)
rest.router.register_model(Phenology)
rest.router.register_model(
    Species,
    lookup="elcode",
    serializer=SpeciesSerializer,
    per_page=100000,
)

rest.router.add_page('index', {'url': ''})
rest.router.add_page('about', {'url': 'about'})
rest.router._extra_pages['login'][0]['postsave'] = 'index'
rest.router.set_extra_config(
    debug=settings.DEBUG,
	mobile_analytics_id=settings.MOBILE_ANALYTICS_ID,
	web_analytics_id=settings.WEB_ANALYTICS_ID,
)