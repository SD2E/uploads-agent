#!/usr/bin/env bash

# docker-compose -f docker-compose-consume.yml down
docker-compose down
docker-compose up --build -d
sleep 30
# docker-compose run --use-aliases --entrypoint celery celery_w1 -A proj call proj.test_actions.test_event
docker-compose run --use-aliases --entrypoint celery celery_w1 -A proj call proj.tasks.consume
