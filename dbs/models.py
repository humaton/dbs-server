from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from django.db import models

class TaskData(models.Model):
    json = models.TextField()

class Task(models.Model):
    celery_id = models.CharField(max_length=42, blank=True, null=True)
    date_started = models.DateTimeField(auto_now_add=True)
    date_finished = models.DateTimeField(null=True, blank=True)
    builddev_id = models.CharField(max_length=38)

    STATUS_PENDING  = 'P'
    STATUS_RUNNING  = 'R'
    STATUS_FAILED   = 'F'
    STATUS_SUCCESS  = 'S'

    _STATUS_NAMES = {
        STATUS_PENDING: 'Pending',
        STATUS_RUNNING: 'Running',
        STATUS_FAILED:  'Failed',
        STATUS_SUCCESS: 'Successful',
    }

    status = models.CharField(max_length=1, choices=_STATUS_NAMES.items(),
                default=STATUS_PENDING)

    TYPE_BUILD  = 'B'
    TYPE_MOVE   = 'M'

    _TYPE_NAMES = {
        TYPE_BUILD: 'Build',
        TYPE_MOVE:  'Move',
    }
    type = models.CharField(max_length=1, choices=_TYPE_NAMES.items())

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
    parent = models.ForeignKey('self', null=True, blank=True)  # base images doesnt have parents
    task = models.OneToOneField(Task, null=True, blank=True)

    STATUS_BUILD    = 'B'
    STATUS_TESTING  = 'T'
    STATUS_STABLE   = 'S'
    STATUS_BASE     = '_'

    _STATUS_NAMES = {
        STATUS_BUILD:   'Built',
        STATUS_TESTING: 'Pushed-Testing',
        STATUS_STABLE:  'Pushed-Stable',
        STATUS_BASE:    'Base-Image',
    }
    status = models.CharField(max_length=1, choices=_STATUS_NAMES.items(),
                default=STATUS_BUILD)

    rpms = models.ManyToManyField(Rpms)  # FIXME: improve this model to: Content(type=RPM)

    # base images won't have dockerfile
    dockerfile = models.ForeignKey('Dockerfile', null=True, blank=True)

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
