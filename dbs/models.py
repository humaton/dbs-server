from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from django.db import models

class TaskData(models.Model):
    json = models.TextField()

class Task(models.Model):
    date_started = models.DateTimeField()
    date_finished = models.DateTimeField(null=True, blank=True)
    builddev_id = models.CharField(max_length=38)

    STATUS_CHOICES = (
            (1, 'Pending'),
            (2, 'Running'),
            (3, 'Failed'),
            (4, 'Successful'),
            )
    status = models.IntegerField(choices=STATUS_CHOICES)

    TYPE_CHOICES = (
            (1, 'Build'),
            (2, 'Move'),
            )
    type = models.IntegerField(choices=TYPE_CHOICES)

    owner = models.CharField(max_length=38)
    task_data = models.ForeignKey(TaskData)

    def get_type(self):
        return dict(self.TYPE_CHOICES)[self.type]

    def get_status(self):
        return dict(self.STATUS_CHOICES)[self.status]

class Rpms(models.Model):
    nvr = models.CharField(max_length=38)
    component = models.CharField(max_length=38)

class Registry(models.Model):
    url = models.URLField()

class YumRepo(models.Model):
    url = models.URLField()

class Image(models.Model):
    hash = models.CharField(max_length=64, primary_key=True)
    base_registry = models.ForeignKey(Registry, related_name='base')
    base_tag = models.CharField(max_length=38)

    STATUS_CHOICES = (
            (1, 'Built'),
            (2, 'Pushed-Testing'),
            (3, 'Pushed-Stable'),
            )
    status = models.IntegerField(choices=STATUS_CHOICES)

    rpms = models.ManyToManyField(Rpms)
    registries = models.ManyToManyField(Registry)

    def get_status(self):
        return dict(self.STATUS_CHOICES)[self.status]



class ImageRegistryRelation(models.Model):
    tag = models.CharField(max_length=38)
    image = models.ForeignKey(Image)
    registry = models.ForeignKey(Registry)
