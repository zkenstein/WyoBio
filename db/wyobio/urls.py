from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from wq.db import rest
rest.autodiscover()

from images.views import generate

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^generate/(?P<size>\d+)/(?P<image>\d+)\.(?P<format>.+)$', generate),
    url(r'^', include(rest.router.urls))
)
