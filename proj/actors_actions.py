from agavepy.agave import Agave, AgaveError
from celery_singleton import Singleton

from .celery import app
from .config import settings
from .fsevents_actions import fsevent_update
from .notification_actions import notify_failure


class ActorExecutionInProgress(Exception):
    """Raise when a task execution has not run to completion
    """
    pass


# Task must launch within 8 hours
@app.task(bind=True,
          autoretry_for=(AgaveError, ),
          retry_backoff=True,
          time_limit=28800)
def upload_launch(self, key_event_id):
    """Launch instance of Abaco upload manager

    Retries failed attempts using exponential backoff

    Arguments:
        key_event_id (tuple): (key:str, x-amz-request-id:str)
    Returns:
        tuple: (actor_id:str, execution_id:str, event_id:str)
    """
    # See https://stackoverflow.com/questions/23857005/get-the-name-of-celery-worker-from-inside-a-celery-task
    # for better ways of doing this
    worker = self.request.hostname.split('@')[0]
    # Probably init this on worker setup as well...
    ag = Agave(api_server=settings['api']['server'],
               username=settings['api']['username'],
               password=settings['api']['password'],
               api_key=settings['api']['clients'][worker]['api_key'],
               api_secret=settings['api']['clients'][worker]['api_secret'])
    msg = {
        'uri': 's3://{0}'.format(key_event_id[0]),
        'event_id': key_event_id[1]
    }
    try:
        resp = ag.actors.sendMessage(actorId=settings['actor_id'],
                                     body={'message': msg})
    except Exception as exc:
        raise AgaveError('Failed to launch task: {0}'.format(exc))

    return (settings['actor_id'], resp['executionId'], key_event_id[1])


# Task must complete within a day
@app.task(bind=True,
          autoretry_for=(
              AgaveError,
              ActorExecutionInProgress,
          ),
          retry_backoff=True,
          default_retry_delay=1,
          max_retries=60,
          time_limit=86400)
def upload_monitor(self, actor_exec_event, *args, **kwargs):
    """Monitor a running instance of Abaco uploads manager

    Implements polling via Celery retry

    Arguments:
        actor_exec_event (tuple): (actor_id:str, execution_id:str, event_id:str)
    Returns:
        tuple: (actor_id:str, execution_id:str, status:str, event_id:str)
    """
    actor_id = actor_exec_event[0]
    execution_id = actor_exec_event[1]
    event_id = actor_exec_event[2]

    worker = self.request.hostname.split('@')[0]
    # Probably init this on worker setup as well...
    ag = Agave(api_server=settings['api']['server'],
               username=settings['api']['username'],
               password=settings['api']['password'],
               api_key=settings['api']['clients'][worker]['api_key'],
               api_secret=settings['api']['clients'][worker]['api_secret'])

    try:
        status = ag.actors.getExecution(actorId=actor_id,
                                        executionId=execution_id).get(
                                            'status', None)
    except Exception as exc:
        raise AgaveError('Failed to poll task: {0}'.format(exc))

    fsevent_update.s((event_id, status)).apply_async()

    if status not in ['COMPLETE', 'ERROR']:
        raise ActorExecutionInProgress
    else:
        return (actor_id, execution_id, status, event_id)
