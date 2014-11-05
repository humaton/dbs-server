from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from django.conf.urls import patterns, url


from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = patterns('',
    url(r'^tasks$', views.ListTasksCall.as_view()),
    url(r'^images$', views.ListImagesCall.as_view()),
    url(r'^image/(?P<image_id>[a-zA-Z0-9]+)/status$', views.ImageStatusCall.as_view()),
    url(r'^image/(?P<image_id>[a-zA-Z0-9]+)/deps$', views.ImageDepsCall.as_view()),
    url(r'^image/(?P<image_id>[a-zA-Z0-9]+)/info$', views.ImageInfoCall.as_view()),
    url(r'^task/(?P<task_id>[0-9]+)/status$', views.TaskStatusCall.as_view()),

    url(r'^image/new$', csrf_exempt(views.NewImageCall.as_view())),
    url(r'^image/move/(?P<image_id>[a-zA-Z0-9]+)$', csrf_exempt(views.MoveImageCall.as_view())),
    url(r'^image/rebuild/(?P<image_id>[a-zA-Z0-9]+)$', csrf_exempt(views.RebuildImageCall.as_view())),
    url(r'^image/invalidate/(?P<image_id>[a-zA-Z0-9:]+)$', csrf_exempt(views.InvalidateImageCall.as_view())),
)
