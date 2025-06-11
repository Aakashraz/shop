import os
from celery import Celery


# Set the default Django settings module for the 'celery' program.
# Since Celery is not started by Django, it's started by the command line. So we manually set
# DJANGO_SETTINGS_MODULE to 'myshop.settings' to make sure:
# Django’s settings are available before any imports.
# Celery has the full context of your Django project.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')

# Create a Celery application instance with the name 'myshop'
app = Celery('myshop')

# Tells Celery to read configuration settings from your settings.py, using the prefix CELERY_.
# For example, CELERY_BROKER_URL, CELERY_RESULT_BACKEND, etc.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover tasks from all registered Django app configs
app.autodiscover_tasks()
