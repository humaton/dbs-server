Build service for dbs
=====================

Build system which builds docker images using celery.


Setup
-----

## Install dependencies:

```
dnf install python-celery python-redis redis python-docker-py docker-io docker-registry GitPython
```

## Start services:

### Redis

```
systemctl start redis.service
```

### Registry

```
systemctl start docker-registry.service
```

### Celery

To start a celery worker, you have to be in directory where `celeryconfig.py` persists:

```
dbs celery worker -l INFO
# or
./manage.py celery worker -l INFO
```


Usage
-----

### dock

Setup [https://github.com/DBuildService/dock](dock) and make it avaiable on `${PYTHONPATH}`.


Either run test suite:

```
py.test -s dbs_builder/test.py
```

or try it yourself

```
from dbs_builder.task_api import TaskApi
t = TaskApi()
t.build_docker_image(build_image="buildroot-fedora",
                     git_url="github.com/TomasTomecek/docker-hello-world.git",
                     local_tag="fedora-celery-build",)
```

Interaction with build service is done through `TaskApi` class from `task_api.py` module.

