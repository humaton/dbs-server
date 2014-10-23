from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^tasks/$',    views.task_list),
    url(r'^images/$',   views.image_list),
    url(r'^$',           views.home),
)

