from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Attachment


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
