import json
import requests
from celery import group

from .celery import app
from .config import settings


@app.task
def notify_system_ready():
    msg = 'Uploads-Manager is ready to accept uploads'
    # Run notifications in parallel
    notifications = group(
        slack_message.s(msg)

    )
    notifications.apply_async()
    return True


@app.task
def notify_success(key):
    msg = 'Upload succeeded [s3://{0}]'.format(key)
    # Run notifications in parallel
    notifications = group(
        mailgun_message.s(msg),
        slack_message.s(msg)

    )
    notifications.apply_async()
    return True


@app.task
def notify_failure(key):
    msg = 'Upload succeeded [s3://{0}]'.format(key)
    # Run notifications in parallel
    notifications = group(
        mailgun_message.s(msg),
        slack_message.s(msg)
    )
    notifications.apply_async()
    return True


@app.task
def mailgun_message(messsage, subject=settings['mailgun']['subject'],
                    recipient=settings['mailgun']['recipient'],
                    sender=settings['mailgun']['sender']):

    api_url = settings['mailgun']['api_url']
    api_key = settings['mailgun']['api_key']

    msg = {'from': sender,
           'to': recipient,
           'subject': subject,
           'text': messsage}

    request = requests.post(
        api_url,
        auth=('api', api_key),
        data=msg)

    request.raise_for_status()
    return request.status_code


@app.task
def slack_message(message,
                  channel=settings['slack']['channel'],
                  username=settings['slack']['username'],
                  icon_emoji=settings['slack']['icon_emoji']):

    webhook_url = settings['slack']['webhook']

    payload = {'text': message,
               'icon_emoji': icon_emoji,
               'channel': channel,
               'username': username}

    request = requests.post(webhook_url,
                            data=json.dumps(payload),
                            headers={'Content-type': 'application/json'}
                            ).content

    try:
        request.raise_for_status()
        return request.status_code
    except AttributeError:
        return 200
    except Exception:
        raise
