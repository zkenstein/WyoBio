from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Attachment
from wq.db.rest.views import ModelViewSet
from rest_framework.permissions import AllowAny
from django.contrib.gis.geos import Point


def view_image(request, attachment_id):
    img = get_object_or_404(Attachment, pk=attachment_id)

    #try:
    #    img = Attachment.objects.get(pk=attachment_id)
    #except Attachment.DoesNotExist:
    #    raise Http404()
    
    return HttpResponse(
        content_type=img.content_type,
        content=img.data
    )

class PointViewSet(ModelViewSet):
    permission_classes = [AllowAny]
    def perform_create(self, serializer):
        # FIXME: Move to serializer
        lat = self.request.POST.get('latitude', None)
        lng = self.request.POST.get('longitude', None)
        if lat and lng:
            pt = Point([float(lng), float(lat)], srid=4326)
            pt.transform(3857)
        else:
            pt = None
        serializer.save(geometry=pt)
        
