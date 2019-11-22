from __future__ import absolute_import, unicode_literals

import json
import os
import pika
import sys

from celery import chain, group

from .celery import app
from .config import settings

# Workflow components
from .actors_actions import upload_launch, upload_monitor
from .fsevents_actions import fsevent_create, fsevent_get_key_id
from .notification_actions import (
    notify_success, notify_failure, notify_system_ready)

NAME = 'mproc'


@app.task
def noop(*args):
    return args


@app.task
def process_fsevent_wkflw(event):
    jobs = chain([fsevent_create.s(event),
                  fsevent_get_key_id.s(),
                  upload_launch.s(),
                  upload_monitor.s(),
                  noop.s(),
                  notify_success.si(event['Key'])]
                 )
    jobs.apply_async()


def handle_event(channel, method_frame, properties, body):
    """Pika coonnection callback
    """
    event = json.loads(body)
    process_fsevent_wkflw.delay(event)
    # process.apply_async((event), countdown=3)
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)


@app.task
def consume():
    """Long-running RabbitMQ consumer task
    """
    url = os.environ.get('CLOUDAMQP_URL',
                         settings['cloud_amqp']['uri'])
    params = pika.URLParameters(url)

    # Connection
    try:
        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        # Queues and exchanges
        exch = settings['routing'].get('exchange').get('name', 'amq.direct')
        queuename = settings['routing'].get(
            'source').get('queue', NAME + '.queue')
        rkey = settings['routing'].get('source').get('routing_key', '*')
        result = channel.queue_declare(
            queue=queuename,
            durable=settings['routing'].get('source').get('durable', True),
            exclusive=settings['routing'].get(
                'source').get('exclusive', False),
            arguments=settings['routing'].get('source').get('x-args'))

        # Bind
        channel.queue_bind(result.method.queue,
                           exchange=exch,
                           routing_key=rkey)

        # Attach to callback function
        channel.basic_consume(result.method.queue, handle_event)

    except Exception:
        raise

    try:
        notify_system_ready.s().apply_async()
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
        connection.close()
#            sys.exit(0)
    except Exception:
        raise

    return True
