#!/usr/bin/env bash

TASK="proj.notification_actions.statusio_message"
MSG="DOWN"

docker-compose run --use-aliases --entrypoint celery celery_w1 -A proj call ${TASK} --args="[\"${MSG}\"]"
