from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)


@pytest.fixture
def mock_create_task_data() -> dict:
    """Fixture that provides mock data for creating a task.

    Returns:
        dict: A dictionary containing the task title, description, and status.
    """
    return {
        "title": "Task title",
        "description": "Task description",
        "status": "Not done"
    }


@pytest.fixture
def mock_create_user_data() -> dict:
    """Fixture that provides mock data for creating a user.

    Returns:
        dict: A dictionary containing the user's username and password.
    """
    return {
        "username": "test_username",
        "password": "test_password"
    }


@pytest.fixture
def jwt_token(mock_create_user_data) -> str:
    """Fixture that registers a user, logs in, and retrieves a JWT token.

    Args:
        mock_create_user_data (dict): The mock data used to register and authenticate the user.

    Returns:
        str: The JWT token for the authenticated user.
    """
    response = client.post(
        url="/get",
        json=mock_create_user_data
    )
    assert response.status_code == 200
    return response.json()['access_token']


@pytest.fixture
def create_task(jwt_token: str, mock_create_task_data: dict) -> dict:
    """Fixture that creates a task using the JWT token for authorization.

    Args:
        jwt_token (str): The JWT token for the authenticated user.
        mock_create_task_data (dict): The mock data for creating the task.

    Returns:
        dict: A dictionary containing the details of the created task, including its ID.
    """
    response = client.post(
        url="/tasks/",
        json=mock_create_task_data,
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.status_code == 200
    return response.json()


def test_create_task(create_task: dict):
    """Test creating a new task.

    Args:
        create_task (dict): The created task data, provided by the create_task fixture.

    Asserts:
        The created task has the correct title, description, status, owner, and an ID.
    """
    created_task = create_task

    assert created_task['title'] == "Task title"
    assert created_task['description'] == "Task description"
    assert created_task['status'] == "Not done"
    assert created_task['owner'] == "test_username"
    assert "id" in created_task


def test_update_task(jwt_token: str, create_task: dict):
    """Test updating an existing task.

    Args:
        jwt_token (str): The JWT token for the authenticated user.
        create_task (dict): The created task data, provided by the create_task fixture.

    Asserts:
        The updated task has the correct title, description, status, and owner.
    """
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


def test_get_task(jwt_token: str, create_task: dict):
    """Test retrieving a task.

    Args:
        jwt_token (str): The JWT token for the authenticated user.
        create_task (dict): The created task data, provided by the create_task fixture.

    Asserts:
        The retrieved task has the correct title, description, status, and owner.
    """
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


def test_delete_task(jwt_token: str, create_task: dict):
    """Test deleting a task.

    Args:
        jwt_token (str): The JWT token for the authenticated user.
        create_task (dict): The created task data, provided by the create_task fixture.

    Asserts:
        The task is successfully deleted (status code 200).
    """
    task_id = create_task['id']

    response = client.delete(
        url=f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {jwt_token}"}
    )

    assert response.status_code == 200
