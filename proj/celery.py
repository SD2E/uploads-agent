from __future__ import absolute_import, unicode_literals
from celery import Celery
import os

username = os.environ.get('RABBITMQ_USERNAME', 'guest')
password = os.environ.get('RABBITMQ_PASSWORD', 'guest')
hostname = os.environ.get('RABBITMQ_HOST', 'localhost')
port = os.environ.get('RABBITMQ_PORT', '5672')
vhost = os.environ.get('RABBITMQ_VHOST', '')

app = Celery('proj',
             broker='amqp://{0}:{1}@{2}:{3}/{4}'.format(
                 username, password, hostname, port, vhost),
             backend='redis://redis:6379',
             include=['proj.signals',
                      'proj.actors_actions',
                      'proj.fsevents_actions',
                      'proj.notification_actions',
                      'proj.test_actions',
                      'proj.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=36000,
)

if __name__ == '__main__':
    app.start()
