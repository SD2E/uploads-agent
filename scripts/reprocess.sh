#!/usr/bin/env bash

TASK="proj.tasks.reprocess_fsevent"
EVENT_ID=$1

docker-compose run --use-aliases --entrypoint celery celery_w1 -A proj call ${TASK} --args="[\"${EVENT_ID}\"]"
