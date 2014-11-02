
from task_api import TaskApi


def test_build_image():
    api = TaskApi()
    api.build_docker_image("buildroot-fedora",
                           "github.com/TomasTomecek/docker-hello-world.git",
                           "test-celery-priv",
    )


