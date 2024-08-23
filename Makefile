# This Makefile is used for simplyfing the process of creating docker image and running docker container
# in GitHub Actions pipeline for testing the application

DOCKER_IMAGE_NAME=fastapi-app-dev
COMPOSE_FILE=docker-compose.dev.yml

build:
	sudo docker build -t $(DOCKER_IMAGE_NAME) .

run:
	sudo docker-compose -f $(COMPOSE_FILE) up -d --build

down:
	sudo docker stop $(DOCKER_IMAGE_NAME)

test:
	sudo docker exec -it $(DOCKER_IMAGE_NAME) pytest tests/unit_tests_auth.py
	sudo docker exec -it $(DOCKER_IMAGE_NAME) pytest tests/unit_tests_task.py

# order of execution
ci: build run test down