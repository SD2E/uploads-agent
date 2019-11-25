#!/usr/bin/env bash

TASK="proj.tasks.consume"

docker-compose run --use-aliases --entrypoint celery celery_w1 -A proj call ${TASK}
