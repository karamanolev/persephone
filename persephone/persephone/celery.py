import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'persephone.settings')

app = Celery('persephone')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
