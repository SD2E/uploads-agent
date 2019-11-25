#!/usr/bin/env bash

TASK="proj.notification_actions.mail_message"
MSG=$1

docker-compose run --use-aliases --entrypoint celery celery_w1 -A proj call ${TASK} --args="[\"${MSG}\"]"
