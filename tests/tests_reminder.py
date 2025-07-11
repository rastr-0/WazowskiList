from unittest.mock import patch
from fastapi.testclient import TestClient


@patch("app.services.scheduler.schedule_reminder.delay")
def test_create_reminder(mock_delay, client: TestClient, jwt_token, create_task: dict) -> None:
    """Test creating new reminder (Celery mocked)"""
    token = jwt_token('updated')
    task_id = create_task['id']

    reminder_data = {
        "reminder_time": "2024-12-10T23:00:00",
        "message": "Reminder message"
    }

    response = client.post(
        url=f"/api/schedule/reminder?task_id={task_id}",
        json=reminder_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
