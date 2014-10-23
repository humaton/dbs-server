from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from django.conf.urls import patterns, include, url

from . import api, web

from django.contrib import admin

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^v1/',    include('dbs.api.urls')),
    url(r'^',       include('dbs.web.urls')),
)
