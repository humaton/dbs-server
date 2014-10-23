from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from django.contrib import admin
from .models import TaskData, Task, Rpms, Registry, YumRepo, Image, ImageRegistryRelation

admin.site.register(TaskData)
admin.site.register(Task)
admin.site.register(Rpms)
admin.site.register(Registry)
admin.site.register(YumRepo)
admin.site.register(Image)
admin.site.register(ImageRegistryRelation)
