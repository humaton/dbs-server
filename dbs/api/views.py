from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

import json
import copy

from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST

from ..models import TaskData, Task, Rpms, Registry, YumRepo, Image, ImageRegistryRelation

def JsonResponse(response):
    return HttpResponse(json.dumps(response), content_type="application/json")

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

@require_POST
def new_image(request):
    return HttpResponse("new image")

@require_POST
def move_image(request, image_id):
    return HttpResponse("move image {}".format(image_id))

@require_POST
def rebuild_image(request, image_id):
    return HttpResponse("rebuild image {}".format(image_id))

@require_POST
def invalidate(request, tag):
    return HttpResponse("invalidate tag {}".format(tag))
