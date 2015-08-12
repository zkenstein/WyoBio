from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from geodata.models import Attachment
from PIL import Image, ImageOps
from io import BytesIO
import os
from django.conf import settings


def generate(request, size, image, format):
    attachment = get_object_or_404(Attachment, pk=image)
    size = int(size)
    if not attachment.content_type.startswith('image/'):
        return HttpResponse(
            # Redirect to no image image
        )
        
    img = Image.open(BytesIO(attachment.data))
    
    if hasattr(img, '_getexif'):
        exif = img._getexif()
    else:
        exif = None
    if exif:
        orientation = exif.get(0x0112, 1)
    else:
        orientation = 1

    rotate = {
        3: Image.ROTATE_180,
        6: Image.ROTATE_270,
        8: Image.ROTATE_90
    }
    if orientation in rotate:
        img = img.transpose(rotate[orientation])

    if size < 256:
        img = ImageOps.fit(img, (size, size), Image.ANTIALIAS)
    elif size < 600:
        img.thumbnail((size, size), Image.ANTIALIAS)
    else:
        width, height = img.size
        if width > size:
            ratio = float(size) / float(width)
            height = int(height * ratio)
            img = img.resize((size, height), Image.ANTIALIAS)

    tdir = os.path.join(settings.MEDIA_ROOT, str(size))
    try:
        os.makedirs(tdir)
    except OSError:
        pass
    img.save(os.path.join(tdir, "%s.jpg" % attachment.pk), 'JPEG')
    data = BytesIO()
    img.save(data, 'JPEG')
    data.seek(0)
    return HttpResponse(
        data.read(),
        content_type='image/jpeg'
     )