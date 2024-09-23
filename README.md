# WazowskiList
![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.1-green)
![Motor](https://img.shields.io/badge/Motor-3.5.1-red)
![Pydantic](https://img.shields.io/badge/Pydantic-2.8.2-lightgrey)
![Pytest](https://img.shields.io/badge/pytest-8.3.2-yellow)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

![Preview of the project](static/wazowski.gif)

## Overview
WazowskiList is a basic backend project built with FastAPI, providing RESTful API for managing to-do lists.

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Pipelines](#pipelines)
  - [Test Pipeline](#test-pipeline)
  - [Release Pipeline](#release-pipeline)
- [REST requests examples](#rest-requests-examples-with-curl)
  - [Authentication related](#authentication-related-requests-examples)
  - [Task related](#task-related-requests-examples)


### Features
- RESTful API for managing to-do lists
- User authentication and authorization based in JWT tokens
- CRUD operations for managing tasks
- MongoDB for data storage
- Docker for containerization
- Redis for storing tasks (reminding emails to send)
- Celery for sending reminding emails on time

### Tech Stack
- **Language:** Python 3.10
- **Framework:** FastAPI
- **Database:** MongoDB
- **Containerization:** Docker

### Pipelines
WazowskiList employs two GitHub Actions pipelines to streamline development and release processes:

##### Test Pipeline
- **Trigger:** Activated whenever a push is made to the `dev` branch
- **Purpose:** This pipeline runs the tests to ensure, that new changes do not introduce bugs, and pre-commit hooks for auto-formatting files
- **Actions:**
  - Pull the latest code from the `dev` branch
  - Set up the environment and dependencies
  - Execute pre-commit hooks
  - Execute the unit tests using Pytest

##### Release Pipeline
- **Trigger:** Initiated when a new tag is pushed to the `master` branch following the pattern `*.*.*` (e.g., `0.1.0`)
- **Purpose:** This pipeline automates the process of building, packaging, and releasing the application
- **Actions:**
  - Check out the code associated with the tag
  - Build a Docker image for the application
  - Push the Docker image to GitHub Packages
  - Create a new GitHub release with the associated tag

### REST requests examples with `curl`
REST requests in this project can be conditionally separated to:
1) **authentication-related**
2) **task-related**

### Authentication-related requests examples
1) **Register a new user**

Before starting exploring API you'll need to register a new user by providing following fields:
- `username`
- `password`
- `full_name` (optional)
- `email` (optional)
```
curl -X POST "domain:port/api/auth/register"
  -H "Content-Type: application/json"
  -H "accept: application/json"
  -d '{
    "username": "your_username",
    "password": "your_password",
    "email": "email@gmail.com",
    "full_name": "Mister User"
   }'
```
2) **Generate a token**

For every request, except `/register` token is required.
In order to prevent API abuse.
```
curl -X POST "domain:port/api/auth/token"
  -H "Content-Type: application/json"
  -H "accept: application/json"
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```
3) **Updated user information**

If you want to update already registered users information you can
use this endpoint.
fields:
- `username` (optional)
- `password` (optional)
- `full_name` (optional)
- `email` (optional)
```
curl -X POST "domain:portapi/auth/users/me"
  -H "Content-Type: application/json"
  -H "accept: application/json"
  -d '{
    "username": "new_username",
    "password": "new_password",
    "email": "new_email@gmail.com",
    "full_name": "Miss User"
  }'
  -H "Authorization: Bearer your_token"
```
4) **User information**

You can also get a current login user information
```
curl -X GET "domain:port/api/auth/users/me"
  -H "Content-Type: application/json"
  -H "accept: application/json"
  -H "Authorization: Bearer your_token"
```
### Task-related requests examples
1) **Create a new task**

For creating a new task you should use this endpoint with following fields:
- `title`
- `description` (optional)
- `status`
- `label`
- `deadline` (optional)

When you're creating a new task, API automatically sets it
a generated unique `UUID4` `id` field and in the response from
this endpoint `id` field is included.

```
curl -X POST "domain:port/api/core-app/tasks"
  -H "Content-Type: application/json"
  -H "accept: application/json"
  -d '{
    "title": "task title",
    "description": "task description",
    "status": "task status",
    "label": "task label",
    "deadline": "YYYY-MM-DD"
  }'
  -H "Authorization: Bearer your_token"
```
2) **Update task**

In case if you've created a task or few tasks, but would like to change or add
some information you should use this endpoint.
- `title` (optional)
- `description` (optional)
- `status` (optional)
- `label` (optional)
- `deadline` (optional)

Request requires providing `UUID4` `id` field which was generated by privious endpoint
and should be used in this one for correctly identifying task.

```
curl -X PUT "domain:port/api/core-app/tasks{id}"
  -H "Content-Type: application/json"
  -H "accept: application/json"
  -d '{
    "title": "new task title",
    "description": "new task description",
    "status": "new task status",
    "label": "new task label",
    "deadline": "YYYY-MM-DD"
  }'
  -H "Authorization: Bearer your_token"
```
3) **Get task**

For getting tasks from the database use this endpoint.
Endpoint provides functionality for adding wide range of filters:
- `task_status`: include only tasks with provided status
- `sort_by` and `sort_order`: sort task based on `created_at`/`updated_at` fields in `ascending`/`descending` order
- `include_labels`: list of labels tasks which that will be included
- `max_deadline`: the latest deadline to include tasks up to (inclusive)
- `min_deadline`: the earliest deadline to include tasks from (inclusive)
- `skip`: skip pagination
- `limit`: limit pagination

```
curl -X GET "
    domain:port/api/core-app/tasks
    ?task_status=completed
    &sort_by=created_at
    &sort_order=desc
    &include_labels=work
    &include_labels=personal
    &max_deadline=2024-12-31
    &min_deadline=2024-01-01
    &skip=0
    &limit=50
  "
  -H "Content-Type: application/json"
  -H "accept: application/json"
  -H "Authorization: Bearer your_token"
```
4) **Delete task**

For deleting task you should use this endpoint.
Again `id` must be in a `UUID4` format.
```
curl -X DELETE "domain:port/api/core-app/tasks{id}"
  -H "Content-Type: application/json"
  -H "accept: application/json"
  -H "Authorization: Bearer your_token"
```
