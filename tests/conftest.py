from fastapi.testclient import TestClient
from app.main import app
import pytest

"""
This file defines fixtures for both `auth` and `task` unit tests: 
    - client
    - jwt_token
    - mock_used_data
    - mock_task_data
    - create_task 
"""


@pytest.fixture(scope="session")
def client() -> TestClient:
    """
    Fixture to create a TestClient FastAPI instance.

    This is important to run it using `with` statement, because
    otherwise, FastAPI won't trigger @lifetime event
    and database won't be properly initialized
    """
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def mock_user_data() -> dict:
    """Fixture that provides mock data for creating and updating users

    Returns:
        dict: A dictionary containing basic user's data and updated user's data
    """
    return {
        "basic": {
            "username": "username",
            "password": "password",
            "email": "email@gmail.com",
            "full_name": "User"
        },
        "updated": {
            "username": "test_username",
            "password": "test_password",
            "email": "test_email@gmail.com",
            "full_name": "Test User"
        }
    }


@pytest.fixture(scope="session")
def jwt_token(client, mock_user_data):
    """Fixture that registers a user, logs in, and retrieves a JWT token

    Args:
        client (TestClient): Fixture that creates a FastAPI TestClient instance
        mock_user_data (dict): The mock data used to register and authenticate the user

    Returns:
        function: A function that returns the JWT token for the specified user type
    """

    def _generate_token(data_key: str) -> str:
        user_data = mock_user_data[data_key]
        response = client.post(
            url="/token",
            data={
                "username": user_data['username'],
                "password": user_data['password']
            }
        )
        assert response.status_code == 200
        return response.json()['access_token']

    return _generate_token


@pytest.fixture(scope="session")
def mock_task_data() -> dict:
    """Fixture that provides mock data for creating a task

    Returns:
        dict: A dictionary containing the task title, description, and status
    """
    return {
        "title": "Task title",
        "description": "Task description",
        "status": "Not done"
    }


@pytest.fixture(scope="session")
def create_task(client: TestClient, jwt_token, mock_task_data: dict) -> dict:
    """Fixture that creates a task using the JWT token for authorization

    Args:
        client (TestClient): Fixture that creates a FastAPI TestClient instance
        jwt_token: Fixture that provides a JWT token for requests
        mock_task_data (dict): The mock data used

        """
    token = jwt_token('updated')

    response = client.post(
        url="/tasks",
        json={
            "title": mock_task_data['title'],
            "description": mock_task_data['description'],
            "status": mock_task_data['status']
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    task = response.json()

    return {
        "id": task['_id'],
        "title": task['title'],
        "description": task['description'],
        "status": task['status'],
        "owner": task['owner']
    }
