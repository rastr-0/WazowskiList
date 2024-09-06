from fastapi.testclient import TestClient


def test_create_task(create_task: dict) -> None:
    """Test creating a new task"""
    created_task = create_task

    assert created_task['title'] == "Task title"
    assert created_task['description'] == "Task description"
    assert created_task['status'] == "Not done"
    assert created_task['owner'] == "test_username"
    assert created_task['label'] == "important"


def test_update_task(client: TestClient, jwt_token, create_task: dict) -> None:
    """Test updating an existing task"""
    task_id = create_task['id']
    token = jwt_token('updated')

    update_data = {
        "title": "Updated title",
        "description": "Updated description",
        "status": "Done",
        "label": "extremely important"
    }
    response = client.put(
        url=f"/tasks/{task_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    updated_task = response.json()

    assert updated_task['title'] == "Updated title"
    assert updated_task['description'] == "Updated description"
    assert updated_task['status'] == "Done"
    assert updated_task['owner'] == "test_username"
    assert updated_task['label'] == "extremely important"


def test_get_task(client: TestClient, jwt_token, create_task: dict) -> None:
    """Test retrieving a task"""
    token = jwt_token("updated")

    response = client.get(
        url="/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    tasks = response.json()['tasks']
    # `tasks` is dict containing a list of ResponseTask models
    # since we have only 1 task in a database
    # we should use 0 index for getting its data

    assert tasks[0]['title'] == "Updated title"
    assert tasks[0]['description'] == "Updated description"
    assert tasks[0]['status'] == "Done"
    assert tasks[0]['owner'] == "test_username"
    assert tasks[0]['label'] == "extremely important"


def test_delete_task(client: TestClient, jwt_token, create_task: dict) -> None:
    """Test deleting a task"""
    token = jwt_token('updated')
    task_id = create_task['id']

    response = client.delete(
        url=f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
