from kombu import Queue, Exchange
from .private_settings import BROKER_URL

CELERY_TIMEZONE = 'Asia/Yekaterinburg'
CELERYD_TASK_SOFT_TIME_LIMIT = 86400

from celery.schedules import crontab, timedelta

CELERYBEAT_SCHEDULE = {
}

CELERY_TASK_RESULT_EXPIRES = 302400  # 1 week
CELERY_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
)

CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_EXCHANGE = 'default'
CELERY_DEFAULT_ROUTING_KEY = 'default'
