#!/usr/bin/env bash

TASK="proj.periodic_actions.monthly"

docker-compose run --use-aliases --entrypoint celery celery_w1 -A proj call ${TASK}
