#!/bin/sh

cd /opt

# celery -A proj worker -l debug --autoscale 1,8 --detach && touch worker.log

celery -A proj worker -l debug --concurrency=1 -n worker1@%h --detach
# celery -A proj worker -l debug --concurrency=1 -n worker2@%h --detach
# celery -A proj worker -l debug --concurrency=1 -n worker3@%h --detach

sleep 2

# celery -A proj flower -l info --basic_auth=${FLOWER_USERNAME}:${FLOWER_PASSWORD} --detach

# celery -A proj call proj.tasks.add --args='[2, 2]'

# sleep 6000
