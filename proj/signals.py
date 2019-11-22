from celery.signals import celeryd_after_setup


@celeryd_after_setup.connect
def capture_worker_name(sender, instance, **kwargs):
    instance.app.conf.WORKER_NAME = str(sender)
