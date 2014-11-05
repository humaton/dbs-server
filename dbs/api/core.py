from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

import json
import logging
from datetime import datetime
from functools import partial
from django.core.exceptions import ObjectDoesNotExist

from dbs.models import Task, TaskData, Dockerfile, Image
from dbs.task_api import TaskApi


logger = logging.getLogger(__name__)
builder_api = TaskApi()


class ErrorDuringRequest(Exception):
    """ indicate that there was an error during processing request; e.g. 404, invalid sth... """


def new_image_callback(task_id, response_tuple):
    try:
        response_hash, df = response_tuple
    except (TypeError, ValueError):
        response_hash, df = None, None
    t = Task.objects.filter(id=task_id).first()
    t.date_finished = datetime.now()
    if response_hash:
        image_id = response_hash['built_img_info']['Id']
        parent_image_id = response_hash['base_img_info']['Id']
        image_tags = response_hash['built_img_info']['RepoTags']
        parent_tags = response_hash['base_img_info']['RepoTags']
        parent_image = Image.create(parent_image_id, Image.STATUS_BASE, tags=parent_tags)
        df_model = Dockerfile(content=df)
        df_model.save()
        image = Image.create(image_id, Image.STATUS_BUILD, tags=image_tags,
                             task=t, parent=parent_image, dockerfile=df_model)
        t.status = Task.STATUS_SUCCESS
    else:
        t.status = Task.STATUS_FAILED
    t.save()


def build(post_args, **kwargs):
    """ initiate a new build """
    owner = "testuser"  # XXX: hardcoded
    logger.debug("post_args = %s", post_args)
    local_tag = "%s/%s" % (owner, post_args['tag'])

    td = TaskData(json=json.dumps(post_args))
    td.save()

    t = Task(builddev_id="buildroot-fedora", status=Task.STATUS_PENDING,
             type=Task.TYPE_BUILD, owner=owner, task_data=td)
    t.save()

    callback = partial(new_image_callback, t.id)

    post_args.update({'build_image': "buildroot-fedora", 'local_tag': local_tag,
                 'callback': callback})
    task_id = builder_api.build_docker_image(**post_args)
    t.celery_id = task_id
    t.save()
    return t.id


def rebuild(post_args, image_id, **kwargs):
    try:
        data = Image.objects.taskdata_for_imageid(image_id)
    except (ObjectDoesNotExist, AttributeError) as ex:
        logger.error("%s", repr(ex))
        raise ErrorDuringRequest("Image does not exist or was not built from task.")
    else:
        if post_args:
            data.update(post_args)
        return build(data)


def move_image_callback(task_id, response):
    logger.debug("move callback: %s %s", task_id, response)
    t = Task.objects.filter(id=task_id).first()
    t.date_finished = datetime.now()
    if response and response.get("error", False):
        t.status = Task.STATUS_FAILED
    else:
        t.status = Task.STATUS_SUCCESS
    t.save()


def move_image(post_args, image_id, **kwargs):
    post_args['image_name'] = image_id
    td = TaskData(json=json.dumps(post_args))
    td.save()
    owner = "testuser"  # XXX: hardcoded
    t = Task(status=Task.STATUS_PENDING, type=Task.TYPE_MOVE, owner=owner, task_data=td)
    t.save()
    callback = partial(move_image_callback, t.id)
    post_args['callback'] = callback
    task_id = builder_api.push_docker_image(**post_args)
    t.celery_id = task_id
    t.save()
    return t.id


def invalidate(post_args, image_id, **kwargs):
    response = Image.objects.invalidate(image_id)
    return response