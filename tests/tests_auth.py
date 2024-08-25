from starlette.testclient import TestClient


def test_create_user(client: TestClient, mock_user_data: dict) -> None:
    """Test creating a new user"""
    response = client.post(
        url="/register",
        json=mock_user_data["basic"]
    )

    assert response.status_code == 200
    created_user = response.json()

    assert created_user['username'] == "username"
    assert created_user['email'] == "email@gmail.com"


def test_login_for_access_token(client: TestClient, mock_user_data: dict) -> None:
    """Test creating an access token"""
    response = client.post(
        url="/token",
        data={
            "username": mock_user_data['basic']['username'],
            "password": mock_user_data['basic']['password']
        }
    )

    assert response.status_code == 200
    created_token = response.json()

    assert created_token['token_type'] == 'bearer'


def test_update_current_user(client: TestClient, mock_user_data: dict, jwt_token) -> None:
    """Test updating a current user"""
    token = jwt_token("basic")
    response = client.post(
        url="/users/me",
        json={
            "username": mock_user_data['updated']['username'],
            "password": mock_user_data['updated']['password'],
            "email": mock_user_data['updated']['email'],
            "full_name": mock_user_data['updated']['full_name']
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    print(response.json())
    assert response.status_code == 200
    updated_data = response.json()

    assert updated_data['username'] == "test_username"
    assert updated_data['email'] == "test_email@gmail.com"


def test_get_current_user(client: TestClient, jwt_token) -> None:
    """Test getting a current user"""
    token = jwt_token("updated")
    response = client.get(
        url='/users/me',
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    user_data = response.json()

    assert user_data['username'] == "test_username"
