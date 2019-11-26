from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery.schedules import crontab
import os
WORKER_NAME = os.environ.get('RABBITMQ_WORKER_NAME', 'celery_worker')

username = os.environ.get('RABBITMQ_USERNAME', 'guest')
password = os.environ.get('RABBITMQ_PASSWORD', 'guest')
hostname = os.environ.get('RABBITMQ_HOST', 'localhost')
port = os.environ.get('RABBITMQ_PORT', '5672')
vhost = os.environ.get('RABBITMQ_VHOST', '')

app = Celery('proj',
             broker='amqp://{0}:{1}@{2}:{3}/{4}'.format(
                 username, password, hostname, port, vhost),
             backend='redis://redis:6379',
             include=[
                 'proj.signals', 'proj.actors_actions',
                 'proj.fsevents_actions', 'proj.notification_actions',
                 'proj.periodic_actions', 'proj.test_actions', 'proj.tasks'
             ])

# Optional configuration, see the application user guide.
app.conf.update(result_expires=36000, )

# Set up beat schedule
app.conf.beat_schedule = {
    # Confirms the scheduler is running
    'heartbeat-hourly': {
        'task': 'proj.notification_actions.notify_heartbeat',
        'schedule': crontab(minute=15, hour='*/1')
    },
    # Every hour on the hour
    'batch-hourly': {
        'task': 'proj.periodic_actions.hourly',
        'schedule': crontab(minute=0, hour='*/1')
    },
    # Every day at 5:05 PM
    'batch-daily': {
        'task': 'proj.periodic_actions.daily',
        'schedule': crontab(minute=5, hour=17)
    },
    # Every week Friday 5:10 PM
    'batch-weekly': {
        'task': 'proj.periodic_actions.weekly',
        'schedule': crontab(minute=10, hour=17, day_of_week=5)
    },
    # First of every month 5:15
    'batch-monthly': {
        'task': 'proj.periodic_actions.weekly',
        'schedule': crontab(minute=15, hour=17, day_of_month=1)
    },
}

if __name__ == '__main__':
    app.start()
