import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cce_2023_registration.settings")

app = Celery("cce_2023_registration")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
