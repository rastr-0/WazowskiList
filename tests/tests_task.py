from fastapi.testclient import TestClient
from app.main import app
import pytest

from tests.unit_tests_auth import mock_user_data


@pytest.fixture
def client():
    """
    Fixture to create a TestClient FastAPI instance.

    This is important to run it using `with` statement, because
    otherwise, FastAPI won't trigger @lifetime event
    and database won't be properly initialized
    """
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_create_task_data() -> dict:
    """Fixture that provides mock data for creating a task

    Returns:
        dict: A dictionary containing the task title, description, and status
    """
    return {
        "title": "Task title",
        "description": "Task description",
        "status": "Not done"
    }


@pytest.fixture
def mock_create_user_data() -> dict:
    """Fixture that provides mock data for of the user

    Returns:
        dict: A dictionary containing the user's username and password
    """
    return {
        "username": "test_username",
        "password": "test_password"
    }


@pytest.fixture
def jwt_token(client: TestClient, mock_create_user_data) -> str:
    """Fixture that registers a user, logs in, and retrieves a JWT token

    Args:
        client (TestClient): Fixture that creates a FastAPI TestClient instance
        mock_create_user_data (dict): The mock data used to register and authenticate the user

    Returns:
        str: The JWT token for the authenticated user
    """
    response = client.post(
        url="/token",
        data={
            "username": mock_create_user_data['username'],
            "password": mock_create_user_data['password']
        }
    )
    assert response.status_code == 200
    return response.json()['access_token']


@pytest.fixture(scope="module")
def create_task(client: TestClient, jwt_token: str, mock_create_task_data: dict) -> dict:
    """Fixture that creates a task using the JWT token for authorization"""
    response = client.post(
        url="/tasks",
        json={
            "title": mock_create_task_data['title'],
            "description": mock_create_task_data['description'],
            "status": mock_create_task_data['status']
        },
        headers={"Authorization": f"Bearer {jwt_token}"}
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


def test_create_task(create_task: dict):
    """Test creating a new task"""
    created_task = create_task

    assert created_task['title'] == "Task title"
    assert created_task['description'] == "Task description"
    assert created_task['status'] == "Not done"
    assert created_task['owner'] == "test_username"


def test_update_task(client: TestClient, jwt_token: str, create_task: dict):
    """Test updating an existing task"""
    task_id = create_task['id']
    update_data = {
        "title": "Updated title",
        "description": "Updated description",
        "status": "Done"
    }
    response = client.put(
        url=f"/tasks/{task_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {jwt_token}"}
    )

    assert response.status_code == 200
    updated_task = response.json()

    assert updated_task['title'] == "Updated title"
    assert updated_task['description'] == "Updated description"
    assert updated_task['status'] == "Done"
    assert updated_task['owner'] == "test_username"


def test_get_task(client: TestClient, jwt_token: str, create_task: dict):
    """Test retrieving a task"""
    response = client.get(
        url="/tasks",
        headers={"Authorization": f"Bearer {jwt_token}"}
    )

    assert response.status_code == 200
    get_task = response.json()

    assert get_task['title'] == "Updated title"
    assert get_task['description'] == "Updated description"
    assert get_task['status'] == "Done"
    assert get_task['owner'] == "test_username"


def test_delete_task(client: TestClient, jwt_token: str, create_task: dict):
    """Test deleting a task"""
    task_id = create_task['id']

    response = client.delete(
        url=f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {jwt_token}"}
    )

    assert response.status_code == 200
