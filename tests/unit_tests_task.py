from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime

client = TestClient(app)


def get_jwt_token():
    user_data = {
        "username": "test_username",
        "password": "test_password"
    }
    response = client.post("/get", data=user_data)
    assert response.status_code == 200
    return response.json()['access_token']


token = get_jwt_token()


def test_create_task():
    """
    Testing endpoint for creating a new task
    """
    response = client.post(
        url="/tasks/",
        json={
            "title": "Task title",
            "description": "Task description",
            "status": "Not done"
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "title": "Task title",
        "description": "Task description",
        "status": "Not done",
        "created_at": datetime.utcnow()
    }


def test_update_existing_task():
    """
    Testing endpoint for updating existing task in the database
    """
    response = client.put(
        url="/tasks/{id}"
    )
