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

### Features
- RESTful API for managing to-do lists
- User authentication and authorization
- CRUD operations for managing tasks
- MongoDB for data storage
- Docker for containerization

### Tech Stack
- **Language:** Python 3.10
- **Framework:** FastAPI
- **Database:** MongoDB
- **Containerization:** Docker

### Pipelines
WazowskiList employs two GitHub Actions pipelines to streamline development and release processes:

##### Test Pipeline
- **Trigger:** Activated whenever a push is made to the `dev` branch
- **Purpose:** This pipeline runs the test suite to ensure that new changes do not introduce bugs or regressions
- **Actions:** 
  - Pull the latest code from the `dev` branch
  - Set up the environment and dependencies
  - Execute the unit tests using Pytest

##### Release Pipeline
- **Trigger:** Initiated when a new tag is pushed to the `master` branch following the pattern `v*` (e.g., `v0.1.0`)
- **Purpose:** This pipeline automates the process of building, packaging, and releasing the application
- **Actions:**
  - Check out the code associated with the tag
  - Build a Docker image for the application
  - Push the Docker image to GitHub Packages
  - Create a new GitHub release with the associated tag
