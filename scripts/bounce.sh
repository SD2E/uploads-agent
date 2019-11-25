#!/usr/bin/env bash

# docker-compose -f docker-compose-consume.yml down
docker-compose down
docker-compose up --build -d
