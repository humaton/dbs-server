Build service for dbs
=====================

Build system which builds docker images using celery.


Setup
-----

## Install dependencies:

```
dnf install python-celery python-redis redis python-docker-py docker-io docker-registry
```

## Start services:

### Redis

```
systemctl start redis.service
```

### Registry

```
systemctl start docker-registry.serivce
```

### Celery

To start a celery worker, you have to be in directory where `celeryconfig.py` persists:
```
celery -A dbs_worker.docker_tasks worker -l INFO
```


Usage
-----

### dock

Setup [https://github.com/DBuildService/dock](dock) and make it avaiable on `${PYTHONPATH}`.


And you can finally build your image:

```
python task_api.py
```

Interaction with build service is done through `TaskApi` class from `task_api.py` module.

