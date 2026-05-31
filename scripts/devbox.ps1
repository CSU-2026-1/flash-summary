$ErrorActionPreference = "Stop"

docker compose -f docker-compose.dev.yaml up -d --build
docker compose -f docker-compose.dev.yaml run --rm devbox bash