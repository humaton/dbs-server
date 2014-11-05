from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

import json
from django.core.exceptions import ObjectDoesNotExist

from django.db import models


class TaskDataQuerySet(models.QuerySet):
    pass


class TaskData(models.Model):
    json = models.TextField()

    objects = TaskDataQuerySet.as_manager()


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

    status = models.IntegerField(choices=_STATUS_NAMES.items(), default=STATUS_PENDING)

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


class ImageQuerySet(models.QuerySet):
    def taskdata_for_imageid(self, image_id):
        return json.loads(self.get(hash=image_id).task.task_data.json)

    def children(self, image_id):
        return self.filter(parent=image_id)

    def children_as_list(self, image_id):
        return self.children(image_id).values_list('hash', flat=True)

    def invalidate(self, image_id):
        """
        TODO:
        make this more efficient

        :param image_id:
        :return:
        """
        count = 0
        to_invalidate = [image_id]
        while True:
            try:
                parent_image = to_invalidate.pop()
            except IndexError:
                break
            count += self.filter(hash=parent_image, image__is_invalidated=False).update(is_invalidated=True)
            to_invalidate.extend(self.children_as_list(parent_image))
        return count


class Image(models.Model):
    hash = models.CharField(max_length=64, primary_key=True)
    parent = models.ForeignKey('self', null=True, blank=True)  # base images doesnt have parents
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
    status = models.IntegerField(choices=_STATUS_NAMES.items(), default=STATUS_BUILD)

    rpms = models.ManyToManyField(Rpms)  # FIXME: improve this model to: Content(type=RPM)

    # base images won't have dockerfile
    dockerfile = models.ForeignKey('Dockerfile', null=True, blank=True)

    is_invalidated = models.BooleanField(default=False)

    objects = ImageQuerySet.as_manager()

    def __unicode__(self):
        return u"%s: %s" % (self.hash[:12], self.get_status())

    def get_status(self):
        return self._STATUS_NAMES[self.status]

    @classmethod
    def create(cls, image_id, status, tags=None, task=None, parent=None, dockerfile=None):
        image, _ = cls.objects.get_or_create(hash=image_id, status=status)
        image.task = task
        image.parent = parent
        if dockerfile:
            image.dockerfile = dockerfile
        image.save()
        for tag in tags:
            t, _ = Tag.objects.get_or_create(name=tag)
            t.save()
            rel = ImageRegistryRelation(tag=t, image=image)
            rel.save()
        return image

    @property
    def tags(self):
        return Tag.objects.for_image_as_list(self)


class TagQuerySet(models.QuerySet):
    def for_image(self, image):
        return self.filter(registry_bindings__image=image)

    def for_image_as_list(self, image):
        return list(self.for_image(image).values_list('name', flat=True))


# TODO: do relations with this
class Tag(models.Model):
    name = models.CharField(max_length=64)

    objects = TagQuerySet.as_manager()


class ImageRegistryRelation(models.Model):
    tag = models.ForeignKey(Tag, related_name="registry_bindings")
    image = models.ForeignKey(Image)
    registry = models.ForeignKey(Registry, blank=True, null=True)


class Dockerfile(models.Model):
    content = models.TextField()
