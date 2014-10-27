from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

import json
import copy
from datetime import datetime
from functools import partial

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from ..models import TaskData, Task, Rpms, Registry, YumRepo, Image, ImageRegistryRelation
from dbs_builder.task_api import TaskApi

def JsonResponse(response):
    return HttpResponse(json.dumps(response, indent=4),
                        content_type="application/json")

builder_api = TaskApi()

@require_GET
def list_tasks(request):
    response = []

    for task in Task.objects.all():
        response.append({"id": task.id,
                         "type": task.get_type_display(),
                         "status": task.get_status_display(),
                         "owner": task.owner,
                         "started": str(task.date_started),
                         "finished": str(task.date_finished),
                         "builddev-id": task.builddev_id,
                        })
        
    return JsonResponse(response)

@require_GET
def list_images(request):
    response = []

    for img in Image.objects.all():
        rpms = []
        for rpm in img.rpms.all():
            rpms.append({"nvr": rpm.nvr,
                         "component": rpm.component,
                         })

        registries = []
        for reg in img.registries.all():
            registries.append({"url": reg.url})

        response.append({"hash": img.hash,
                         "base_registry": img.base_registry.url,
                         "base_tag": img.base_tag,
                         "status": img.get_status_display(),
                         "rpms": copy.copy(rpms),
                         "registries": copy.copy(registries),
                        })
        
    return JsonResponse(response)

@require_GET
def image_status(request, image_id):
    img = Image.objects.filter(hash=image_id).first()
    response = {"image_id": image_id,
                "status": img.get_status_display()}

    return JsonResponse(response)

@require_GET
def image_deps(request, image_id):
    deps = []
    for img in Image.objects.filter(base_tag=image_id).all():
        deps.append(img.hash)

    response = {"image_id": image_id,
                "deps": deps}

    return JsonResponse(response)

@require_GET
def image_info(request, image_id):
    img = Image.objects.filter(hash=image_id).first()

    rpms = []
    for rpm in img.rpms.all():
        rpms.append({"nvr": rpm.nvr,
                     "component": rpm.component,
                     })

    registries = []
    for reg in img.registries.all():
        registries.append({"url": reg.url})

    response = {"hash": img.hash,
                "base_registry": img.base_registry.url,
                "base_tag": img.base_tag,
                "status": img.get_status_display(),
                "rpms": copy.copy(rpms),
                "registries": copy.copy(registries),
               }
        
    return JsonResponse(response)

@require_GET
def task_status(request, task_id):
    task = Task.objects.filter(id=task_id).first()
    response = {"image_id": task_id,
                "status": task.get_status_display()}

    return JsonResponse(response)


def validate_rest_input(required_args, optional_args, request):
    # request.body -- requets sent as json
    # request.POST -- sent as application/*form*
    data_sources = []
    try:
        data_sources.append(json.loads(request.body))
    except ValueError:
        pass
    data_sources.append(request.POST)

    req_is_valid = False
    for source in data_sources:
        for req_arg in required_args:
            try:
                source[req_arg]
            except KeyError:
                req_is_valid = False
                break
            req_is_valid = True
        if req_is_valid:
            break
    if not req_is_valid and required_args:
        raise RuntimeError("request is missing '%s'" % req_arg)
    for arg in source:
        if arg not in optional_args and arg not in required_args:
            raise RuntimeError("Invalid argument '%s' supplied" % arg)
    return source


def translate_args(translation_dict, values):
    """
    translate keys in dict values using translation_dict
    """
    response = {}
    for key, value in values.items():
        try:
            response[translation_dict[key]] = value
        except KeyError:
            response[key] = value
    return response

def new_image_callback(task_id, image_hash):
    t = Task.objects.filter(id=task_id).first()
    t.date_finished = datetime.now()
    if image_hash:
        t.status = 4
    else:
        t.status = 3
    t.save()

@csrf_exempt
@require_POST
def new_image(request):
    required_args = ['git_url', ]
    optional_args = ['git_dockerfile_path', 'git_commit', 'parent_registry', 'target_registries', 'repos', 'tag']
    args = validate_rest_input(required_args, optional_args, request)

    # TODO: if there is slash / in here, it fails to push the image
    local_tag = 'user-project'  # FIXME

    td = TaskData(json=json.dumps(request.POST))
    td.save()

    t = Task(date_started=datetime.now(), builddev_id="buildroot-fedora", status=1,
             type=1, owner="system", task_data=td)
    t.save()

    callback = partial(new_image_callback, t.id)

    args.update({'build_image': "buildroot-fedora", 'local_tag': local_tag,
                 'callback': callback})
    task_id = builder_api.build_docker_image(**args)
    print(task_id)
    return JsonResponse({'task_id': task_id})

@csrf_exempt
@require_POST
def move_image(request, image_id):
    required_args = ['source_registry', 'target_registry', 'tags']
    args = validate_rest_input(required_args, [], request)
    args['image_name'] = image_id
    task_id = builder_api.push_docker_image(**args)
    print(task_id)
    return JsonResponse({'task_id': task_id})

@require_POST
def rebuild_image(request, image_id):
    return HttpResponse("rebuild image {}".format(image_id))

@require_POST
def invalidate(request, tag):
    return HttpResponse("invalidate tag {}".format(tag))
