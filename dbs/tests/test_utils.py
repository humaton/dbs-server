from dbs.tasks import build_image


def test_build_image():
    """
    requires docker and docker-registry to be started
    """
    build_image(
        build_image="buildroot-fedora",
        git_url="https://github.com/TomasTomecek/docker-hello-world.git",
        local_tag="fedora-celery-build",
    )

