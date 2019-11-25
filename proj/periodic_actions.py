from celery import group
from celery_singleton import Singleton
from .celery import app
from .config import settings


@app.task(bind=True, base=Singleton)
def hourly(self):
    g = group()
    g.apply_async()
    return 'Hourly task completed'


@app.task(bind=True, base=Singleton)
def daily(self):
    g = group()
    g.apply_async()
    return 'Daily task completed'


@app.task(bind=True, base=Singleton)
def weekly(self):
    g = group()
    g.apply_async()
    return 'Weekly task completed'


@app.task(bind=True, base=Singleton)
def monthly(self):
    g = group()
    g.apply_async()
    return 'Monthly task completed'
