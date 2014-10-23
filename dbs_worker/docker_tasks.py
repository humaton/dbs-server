from celery import Celery
from dock.core import DockerBuilder, DockerTasker


#s/app/celery/ -- doesn't work on F20
celery = Celery('image_build')
celery.config_from_object('celeryconfig')


@celery.task
def build_image(build_image, git_url, local_tag, git_dockerfile_path=None,
                git_commit=None, source_registry=None, target_registry=None,
                tag=None, repos=None, store_results=True):
    """
    build docker image from provided arguments

    :param build_image: name of the build image (supplied docker image is built inside this image)
    :param git_url: url to git repo
    :param local_tag: image is known within the service with this tag
    :param git_dockerfile_path: path to dockerfile within git repo (default is ./Dockerfile)
    :param git_commit: which commit to checkout (master by default)
    :param source_registry: pull base image from this registry
    :param target_registry: push built image to this registry
    :param tag: tag image with this tag (and push it to target_repo if specified)
    :param repos: list of yum repos to enable in image
    :param store_results: if set to True, store built image and associated buildroot
                          in local docker registry
    :return: dict with data from docker inspect
    """
    db = DockerBuilder(git_url, local_tag, git_dockerfile_path, git_commit, repos)
    if source_registry:
        db.pull_base_image(source_registry)

    db.build(build_image)
    if store_results:
        db.push_buildroot('localhost:5000')
        db.push_built_image('localhost:5000')
    if target_registry:
        db.push_built_image(target_registry, tag)

    inspect_data = db.inspect_built_image()  # dict with lots of data, see man docker-inspect
    # TODO: postbuild_data = run_postbuild_plugins(d, private_tag)
    return inspect_data


@celery.task
def push_image(image_name, source_registry, target_registry, tags):
    """
    pull image from source_registry and push it to target_registry (with provided tags)

    :param image_name: image to pull
    :param source_registry: registry to pull image from
    :param target_registry: registry to push image to
    :param tags: list of tags to tag image with before pushing it to target registry
    :return: None
    """
    if not hasattr(tags, '__iter__'):
        raise RuntimeError("argument tags is not iterable")
    d = DockerTasker()
    final_tag = d.pull_image(image_name, source_registry)
    for tag in tags:
        d.tag_and_push_image(final_tag, tag, registry=target_registry)


@celery.task
def submit_results():
    """
    TODO: implement this
    """
    # 2 requests, one for 'finished', other for data
