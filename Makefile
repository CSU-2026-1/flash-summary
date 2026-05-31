devbox: 
	docker compose -f docker-compose.dev.yaml run --rm devbox bash
devbox-up:
	docker compose -f docker-compose.dev.yaml up -d dind
devbox-down:
	docker compose -f docker-compose.dev.yaml down
inner-up:
	docker compose up -d dind
inner-down:
	docker compose down
inner-logs:
	docker compose logs -f