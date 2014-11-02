from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app
