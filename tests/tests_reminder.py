from fastapi.testclient import TestClient


def test_create_reminder(client: TestClient, jwt_token, create_task: dict) -> None:
    """Test creating new reminder"""
    token = jwt_token('updated')
    task_id = create_task['id']

    reminder_data = {
        "message": "Reminder message"
    }

    response = client.post(
        url=f"/api/schedule/reminder?{task_id}",
        json=reminder_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
