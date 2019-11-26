import json
import requests
from celery import group

from .celery import app
from .config import settings


@app.task(bind=True)
def notify_heartbeat(self):
    """Send a heartbeat notification
    """
    msg = ':heart: Heartbeat - Uploads Manager'
    notifications = group(slack_message.s(msg))
    notifications.apply_async()
    return True


@app.task(bind=True, rate_limit='4/h')
def notify_system_ready(self):
    """Notify stakeholders that the system is ready for action
    """
    msg = 'Uploads-Manager is ready to accept uploads'
    # Run notifications in parallel
    notifications = group(slack_message.s(msg), statusio_message.s('UP'))
    notifications.apply_async()
    return True


@app.task(bind=True, rate_limit='4/h')
def notify_system_error(self, message=None):
    """Notify stakeholders that the system has experienced an error
    """
    msg = 'Uploads-Manager has encountered an error.'
    if message is not None:
        msg = msg + ' ({})'.format(message)
    # Run notifications in parallel
    notifications = group(mailgun_message.s(msg), slack_message.s(msg),
                          statusio_message.s('DOWN'))
    notifications.apply_async()
    return True


@app.task(bind=True)
def notify_success(self, key):
    """Notify stakeholders that a file was uploaded
    """
    msg = 'Upload succeeded [s3://{0}]'.format(key)
    # Run notifications in parallel
    notifications = group(mailgun_message.s(msg), slack_message.s(msg))
    notifications.apply_async()
    return True


@app.task(bind=True)
def notify_failure(self, key):
    """Notify stakeholders that a file upload failed
    """
    msg = 'Upload failed [s3://{0}]'.format(key)
    # Run notifications in parallel
    notifications = group(mailgun_message.s(msg), slack_message.s(msg))
    notifications.apply_async()
    return True


@app.task(bind=True, rate_limit='100/h')
def mailgun_message(self,
                    messsage,
                    subject=settings['mailgun']['subject'],
                    recipient=settings['mailgun']['recipient'],
                    sender=settings['mailgun']['sender']):
    """Send a message using Mailgun

    Rate-limited to 100 messages/hour
    """

    api_url = settings['mailgun']['api_url']
    api_key = settings['mailgun']['api_key']

    msg = {
        'from': sender,
        'to': recipient,
        'subject': subject,
        'text': messsage
    }

    # Allow email notifications to be admnistratively disabled
    if settings['notifications']['email']:
        request = requests.post(
            api_url,
            auth=('api', api_key),
            data=msg,
            timeout=(settings['requests']['connect_timeout'],
                     settings['requests']['read_timeout']))

        request.raise_for_status()
        return request.status_code
    else:
        return 'Skipped'


@app.task(bind=True, rate_limit='1000/h')
def slack_message(self,
                  message,
                  channel=settings['slack']['channel'],
                  username=settings['slack']['username'],
                  icon_emoji=settings['slack']['icon_emoji']):
    """Send a message using Slack

    Rate-limited to 1000 messages/hour
    """

    webhook_url = settings['slack']['webhook']

    payload = {
        'text': message,
        'icon_emoji': icon_emoji,
        'channel': channel,
        'username': username
    }

    # Allow Slack notifications to be admnistratively disabled
    if settings['notifications']['slack']:
        request = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers={
                'Content-type': 'application/json'
            },
            timeout=(settings['requests']['connect_timeout'],
                     settings['requests']['read_timeout'])).content
        try:
            request.raise_for_status()
            return request.status_code
        except AttributeError:
            return 200
        except Exception:
            raise
    else:
        return 'Skipped'


@app.task(bind=True, rate_limit='12/h')
def statusio_message(self, status, message=None):
    """Updates the Status.IO report for Uploads Manager
    """

    webhook_url = 'https://api.status.io/v2/component/status/update'

    if message is None:
        message = 'Status was automatically updated'

    STATUS_IO_CODES = {'UP': 100, 'DOWN': 500}
    if status in STATUS_IO_CODES:
        status = STATUS_IO_CODES[status]
    else:
        status = 100

    headers = {
        'x-api-id': settings['statusio']['api_id'],
        'x-api-key': settings['statusio']['api_key']
    }

    payload = {
        'statuspage_id': settings['statusio']['statuspage_id'],
        'component': settings['statusio']['component'],
        'container': settings['statusio']['container'],
        'details': message,
        'current_status': status
    }

    # Allow Status.IO notifications to be admnistratively disabled
    if settings['notifications']['statusio']:
        r = requests.post(
            webhook_url,
            json=payload,
            headers=headers,
            timeout=(settings['requests']['connect_timeout'],
                     settings['requests']['read_timeout'])).content
        try:
            # request.raise_for_status()
            return r.decode('ascii')
        except AttributeError:
            return -1
        except Exception:
            raise
    else:
        return 'Skipped'
