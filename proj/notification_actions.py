import json
import requests
from celery import group

from .celery import app
from .config import settings


@app.task(bind=True, rate_limit='4/h')
def notify_system_ready(self):
    """Notify stakeholders that the system is ready for action
    """
    msg = 'Uploads-Manager is ready to accept uploads'
    # Run notifications in parallel
    notifications = group(slack_message.s(msg))
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
    notifications = group(mailgun_message.s(msg), slack_message.s(msg))
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
        return 200


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
        return 200
