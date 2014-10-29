from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from django.db import models

class TaskData(models.Model):
    json = models.TextField()

class Task(models.Model):
    celery_id = models.CharField(max_length=42, blank=True, null=True)
    date_started = models.DateTimeField(auto_now_add=True)
    date_finished = models.DateTimeField(null=True, blank=True)
    builddev_id = models.CharField(max_length=38)

    STATUS_PENDING  = 1
    STATUS_RUNNING  = 2
    STATUS_FAILED   = 3
    STATUS_SUCCESS  = 4

    _STATUS_NAMES = {
        STATUS_PENDING: 'Pending',
        STATUS_RUNNING: 'Running',
        STATUS_FAILED:  'Failed',
        STATUS_SUCCESS: 'Successful',
    }

    status = models.IntegerField(choices=_STATUS_NAMES.items())

    TYPE_BUILD  = 1
    TYPE_MOVE   = 2

    _TYPE_NAMES = {
        TYPE_BUILD: 'Build',
        TYPE_MOVE:  'Move',
    }
    type = models.IntegerField(choices=_TYPE_NAMES.items())

    owner = models.CharField(max_length=38)
    task_data = models.ForeignKey(TaskData)

    def get_type(self):
        return self._TYPE_NAMES[self.type]

    def get_status(self):
        return self._STATUS_NAMES[self.status]

class Rpms(models.Model):
    nvr = models.CharField(max_length=38)
    component = models.CharField(max_length=38)

class Registry(models.Model):
    url = models.URLField()

class YumRepo(models.Model):
    url = models.URLField()

class Image(models.Model):
    hash = models.CharField(max_length=64, primary_key=True)
    base_registry = models.ForeignKey(Registry, related_name='base', null=True, blank=True)
    base_tag = models.CharField(max_length=38, null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True)
    task = models.OneToOneField(Task, null=True, blank=True)

    STATUS_BUILD    = 1
    STATUS_TESTING  = 2
    STATUS_STABLE   = 3
    STATUS_BASE     = 4

    _STATUS_NAMES = {
        STATUS_BUILD:   'Built',
        STATUS_TESTING: 'Pushed-Testing',
        STATUS_STABLE:  'Pushed-Stable',
        STATUS_BASE:    'Base-Image',
    }
    status = models.IntegerField(choices=_STATUS_NAMES.items())

    rpms = models.ManyToManyField(Rpms)
    registries = models.ManyToManyField(Registry)

    def get_status(self):
        return self._STATUS_NAMES[self.status]



class ImageRegistryRelation(models.Model):
    tag = models.CharField(max_length=38)
    image = models.ForeignKey(Image)
    registry = models.ForeignKey(Registry)
