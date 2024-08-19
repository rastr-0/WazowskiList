from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)


@pytest.fixture
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


@pytest.fixture
def jwt_token(mock_user_data):
    """Fixture that registers a user, logs in, and retrieves a JWT token

    Args:
        mock_user_data (dict): The mock data used to register and authenticate the user

    Returns:
        function: A function that returns the JWT token for the specified user type
    """

    def _generate_token(data_key: str) -> str:
        user_data = mock_user_data[data_key]
        response = client.post(
            url="/get",
            json=user_data
        )
        assert response.status_code == 200
        return response.json()['access_token']

    return _generate_token


def test_create_user(mock_user_data):
    """Test creating a new user"""
    response = client.post(
        url="/register",
        json=mock_user_data["basic"]
    )

    assert response.status_code == 200
    created_user = response.json()

    assert created_user['username'] == "username"
    assert created_user['email'] == "email@gmail.com"


def test_login_for_access_token(mock_user_data, jwt_token):
    """Test creating access token"""
    response = client.post(
        url="/token",
        json={"username": mock_user_data["basic"]["username"], "password": mock_user_data["basic"]["password"]}
    )

    assert response.status_code == 200
    created_token = response.json()

    assert created_token['token_type'] == 'bearer'


def test_update_current_user(mock_user_data, jwt_token):
    """Test updating current user"""
    token = jwt_token("basic")
    response = client.put(
        url="/users/me",
        json=mock_user_data["updated"],
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    updated_data = response.json()

    assert updated_data['username'] == "test_username"
    assert updated_data['email'] == "test_email@gmail.com"


def test_get_current_user(jwt_token):
    """Test getting current user"""
    token = jwt_token("updated")
    response = client.get(
        url='/users/me',
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    user_data = response.json()

    assert user_data['username'] == "test_username"
    assert user_data['email'] == "test_email@gmail.com"
