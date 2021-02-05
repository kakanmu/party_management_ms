from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Setting the default settings module for the Celery program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'party_data_management_ms.settings')
pdms_app = Celery('party_data_management_ms')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
pdms_app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
pdms_app.autodiscover_tasks()