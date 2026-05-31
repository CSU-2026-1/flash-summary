$ErrorActionPreference = "Stop"

docker compose -f docker-compose.dev.yml up -d dind
docker compose -f docker-compose.dev.yml run --rm devbox bash