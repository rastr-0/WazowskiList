# WazowskiList

![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.1-green)
![Motor](https://img.shields.io/badge/Motor-3.5.1-red)
![Pydantic](https://img.shields.io/badge/Pydantic-2.8.2-lightgrey)
![Pytest](https://img.shields.io/badge/pytest-8.3.2-yellow)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

![Preview of the project](static/wazowski.gif)

## Overview

WazowskiList allows users to manage their to-do lists efficiently. The application supports user authentication, task
CRUD operations, and scheduled email reminders using Redis + Celery.
---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation--running)
- [REST requests examples](#rest-requests-examples-with-curl)
    - [Authentication](#authentication-requests-examples)
    - [Tasks](#tasks-requests-examples)
    - [Reminders](#reminders-requests-examples)
- [Project Pipelines](#pipelines)
    - [Test Pipeline](#test)
    - [Release Pipeline](#release)
- [ToDo](#todo)

---

### Features

- RESTful API for task and reminder management
- Asynchronous operations using FastAPI and Motor
- User authentication and authorization (JWT-based)
- Scheduled email reminders (Celery + Redis)
- Modular and scalable project structure
- Fully containerized with Docker
- Test suite using Pytest

---

### Tech Stack

| Layer          | Tool / Tech     |
|----------------|-----------------|
| **Language**   | Python 3.10     |
| **Framework**  | FastAPI         |
| **Database**   | MongoDB         |
| **ORM**        | Motor (asyncio) |
| **Container**  | Docker          |
| **Task Queue** | Celery + Redis  |
| **Testing**    | Pytest          |

---

### Installation & Running

#### Clone repository

```bash
git clone https://github.com/rastr-0/WazowskiList.git
cd WazowskiList
```
Make sure you have Docker and Make installed on your system

#### Running

You can start all required services (FastAPI backend, MongoDB, Redis, Celery workers, and Flower monitor) by simply running:

```bash
make run
```
which is equivalent to the command

```bash
docker-compose -f docker-compose.yml up -d --build
```

For running tests and pre-commit hooks:
```bash
make ci
```
---

### REST requests examples with `curl`

REST requests in this project can be conditionally separated to:

1) **authentication**
2) **tasks**
3) **reminders**

#### Authentication requests examples

1) **Register a new user**

Before starting exploring API you'll need to register a new user by providing following fields:

- `username`
- `password`
- `full_name` (optional)
- `email` (optional)

```bash
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

```bash
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

```bash
curl -X POST "domain:port/api/auth/users/me"
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

```bash
curl -X GET "domain:port/api/auth/users/me"
  -H "Content-Type: application/json"
  -H "accept: application/json"
  -H "Authorization: Bearer your_token"
```

#### Tasks requests examples

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

```bash
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

if you've created one or more tasks, but would like to change or add
some information you can use this endpoint.

- `title` (optional)
- `description` (optional)
- `status` (optional)
- `label` (optional)
- `deadline` (optional)

Request requires providing `UUID4` `id` field which was generated by previous endpoint
and should be used in this one for correctly identifying task.

```bash
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

```bash
curl -X GET "domain:port/api/core-app/tasks
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

To delete a task use following endpoint.
`id` again must be in a `UUID4` format.

```bash
curl -X DELETE "domain:port/api/core-app/tasks/$TASK_ID"
  -H "Content-Type: application/json"
  -H "accept: application/json"
  -H "Authorization: Bearer $TOKEN"
```

#### Reminders requests examples

1) **Create a new reminder**

Reminder can be created with the specific time to be sent or,
by default, it is sent one hour before deadline of the task.

Each reminder is created for one individual task, so, endpoint
depends on the task `id`.

```bash
curl -X POST "domain:port/api/schedule/reminder?task_id=$TASK_ID"
-H "Content-Type: application/json"
-H "accept: application/json"
-H "Authorization: Bearer $TOKEN"
-d '{
  "message": "Extremely important reminder 1",
  "reminder_time": YYYY-MM-DD(T)HH:MM
}'
```

2) **Update reminder**

For updating reminder is needed a unique `id` which is returned with the rest of information after creating a reminder.

```bash
curl -X PUT "domain:port/api/schedule/reminder?reminder_id=$REMINDER_ID"
-H "Content-Type: application/json"
-H "accept: application/json"
-H "Authorization: Bearer $TOKEN"
-d '{
  "reminder_time": "YYYY-MM-DD(T)HH:MM",
  "message": "Changed reminder message!"
}'
```

3) **Delete reminder**

Deletion is also, obviously, depends on the `id`.
```bash
curl -X DELETE "domain:port/api/schedule/reminder?reminder_id=$REMINDER_ID"
-H "Content-Type: application/json"
-H "accept: application/json"
-H "Authorization: Bearer $TOKEN"
```

---
### Pipelines

The project has two pipelines: **test** & **release**

##### Test

- **Trigger:** Activated whenever a push is made to the `dev` branch
- **Purpose:** Runs the tests to ensure, that new changes do not introduce bugs, and pre-commit hooks for
  auto-formatting files
- **Actions:**
    - Pull the latest code from the `dev` branch
    - Set up the environment and dependencies
    - Execute pre-commit hooks
    - Execute the unit tests using Pytest

##### Release

- **Trigger:** Initiated when a new tag is pushed to the `master` branch following the pattern `*.*.*` (e.g., `0.1.0`)
- **Purpose:** Automates the process of building, packaging, and releasing the application
- **Actions:**
    - Check out the code associated with the tag
    - Build a Docker image for the application
    - Push the Docker image to GitHub Packages
    - Create a new GitHub release with the associated tag

---
### ToDo

- Authentication
    - [X] User registration
    - [X] Access token generation (JWT)
    - [X] Update user info (e.g. password, email)
    - [X] Retrieve user info (own profile)
    - [ ] Role-based access control (e.g. admin, regular)
    - [ ] OAuth2 with Google/GitHub
- Task Management
    - [X] Task creation
    - [X] Task update
    - [X] Task deletion
    - [X] Get one or more tasks
    - [X] Task email reminders (schedule, update, delete)
    - [ ] Task sharing with other users
- Security & Robustness
    - [ ] Rate limiting
    - [ ] More tests
- UI
    - [ ] basic UI
