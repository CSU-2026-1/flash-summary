.PHONY: devbox devbox-up devbox-down devbox-logs inner-up inner-down inner-ps inner-logs inner-test
devbox: 
	docker compose -f docker-compose.dev.yaml run --rm devbox bash
devbox-up:
	docker compose -f docker-compose.dev.yaml up -d dind
devbox-down:
	docker compose -f docker-compose.dev.yaml down
devbox-logs:
	docker compose -f docker-compose.dev.yaml logs -f
inner-up:
	docker compose up -d dind
inner-down:
	docker compose down
inner-ps:
	docker compose ps
inner-logs:
	docker compose logs -f
inner-test:
	python -m compileall backend/app