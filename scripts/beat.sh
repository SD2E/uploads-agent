#!/usr/bin/env bash

TASK="proj.notification_actions.notify_heartbeat"

docker-compose run --use-aliases --entrypoint celery celery_w1 -A proj call ${TASK}
