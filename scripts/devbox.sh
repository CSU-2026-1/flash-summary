#!/usr/bin/env bash
set -e
# This script is used to run the devbox in a container. It is used for development and testing purposes.
docker compose -f docker-compose.dev.yaml up -d dind
docker compose -f docker-compose.dev.yaml run --rm devbox bash 