.PHONY: devbox devbox-up devbox-down devbox-logs inner-up inner-down inner-ps inner-logs inner-test
devbox: 
	docker compose -f docker-compose.dev.yml run --rm devbox bash
devbox-up:
	docker compose -f docker-compose.dev.yml up -d dind
devbox-down:
	docker compose -f docker-compose.dev.yml down
devbox-logs:
	docker compose -f docker-compose.dev.yml logs -f
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
