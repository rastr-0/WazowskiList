# This Makefile is used for simplyfing the process of creating docker image and running docker container
# in GitHub Actions pipeline for testing the application

DOCKER_IMAGE_NAME=fastapi-app-dev
COMPOSE_FILE=docker-compose.dev.yml
COMPOSE_PROJECT_NAME=fastapi_ci

build:
	sudo docker build -t $(DOCKER_IMAGE_NAME) .

run:
	sudo docker-compose -f $(COMPOSE_FILE) up -d --build

down:
	sudo docker stop $(DOCKER_IMAGE_NAME)
	docker-compose -f $(COMPOSE_FILE) down --volumes

pre-commit-hooks:
	sudo docker exec -t $(DOCKER_IMAGE_NAME) bash -c "cd /docker_app && pre-commit install && pre-commit run --all-files"

test:
	sudo docker exec -t $(DOCKER_IMAGE_NAME) pytest tests/tests_auth.py
	sudo docker exec -t $(DOCKER_IMAGE_NAME) pytest tests/tests_task.py

# order of execution
ci: build run pre-commit-hooks test down
