from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from wq.db import rest
rest.autodiscover()

from geodata.views import view_image

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^viewimage/(?P<attachment_id>[0-9]+)', view_image),
    url(r'^', include(rest.router.urls))
)
