from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from django.conf.urls import patterns, url


from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = patterns('',
    url(r'^tasks$', views.list_tasks),
    url(r'^images$', views.list_images),
    url(r'^image/(?P<image_id>[a-zA-Z0-9]+)/status$', views.image_status),
    url(r'^image/(?P<image_id>[a-zA-Z0-9]+)/deps$', views.image_deps),
    url(r'^image/(?P<image_id>[a-zA-Z0-9]+)/info$', views.image_info),
    url(r'^task/(?P<task_id>[0-9]+)/status$', views.task_status),

    url(r'^image/new$', csrf_exempt(views.NewImageCall.as_view())),
    url(r'^image/move/(?P<image_id>[a-zA-Z0-9]+)$', views.move_image),
    url(r'^image/rebuild/(?P<image_id>[a-zA-Z0-9]+)$', csrf_exempt(views.RebuildImageCall.as_view())),
    url(r'^image/invalidatechilds/(?P<tag>[a-zA-Z0-9]+)$', views.invalidate),
)
