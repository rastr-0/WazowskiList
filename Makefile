# This Makefile is used for simplyfing the process of creating docker image and running docker container
# in GitHub Actions pipeline for testing the application

DOCKER_COMPOSE=sudo docker-compose -f docker-compose.yml
SERVICE_NAME=app

down:
	$(DOCKER_COMPOSE) down --volumes

build:
	$(DOCKER_COMPOSE) build

run:
	$(DOCKER_COMPOSE) up -d --build

pre-commit-hooks:
	$(DOCKER_COMPOSE) exec -T $(SERVICE_NAME) \
		bash -c "cd /docker_app && pre-commit install && pre-commit run --all-files"

test:
	$(DOCKER_COMPOSE) exec -T $(SERVICE_NAME) pytest tests/tests_auth.py
	$(DOCKER_COMPOSE) exec -T $(SERVICE_NAME) pytest tests/tests_task.py


# order of execution
.PHONY: ci
ci:
	$(MAKE) build
	$(MAKE) run
	$(MAKE) pre-commit-hooks
	$(MAKE) test
	$(MAKE) down
