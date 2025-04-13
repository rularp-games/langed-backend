import os
from celery import Celery
from django.conf import settings
from django.apps import apps

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'langed.settings')

app = Celery('langed')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])
