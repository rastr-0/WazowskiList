from pydantic import BaseModel, Field, ConfigDict, EmailStr
import uuid
from datetime import datetime


class User(BaseModel):
    """
    Pydantic model representing user

    Attributes:
        id (uuid.UUID): ID of the user
        username (str): Username of the user
        email (EmailStr): E-mail of the user
        hashed_password (str): Hashed password of the user
        created_at (datetime): Timestamp when user was created
        updated_at (datetime): Timestamp when user was updated
        model_config (ConfigDict): Example of usage for OpenAPI
    """
    id: uuid.UUID = Field(
        alias="_id",
        description="Auto generated ID for each user",
        default_factory=uuid.uuid4
    )
    username: str = Field(
        description="Userame of the user"
    )
    email: EmailStr | None = Field(
        default=None,
        description="E-mail of the user"
    )
    full_name: str | None = Field(
        default=None,
        description="Full name of the user"
    )
    hashed_password: str = Field(
        description="Hashed password of the user"
    )
    created_at: datetime = Field(
        description="Timestamp when user was created",
        default_factory=datetime.utcnow
    )
    updated_at: datetime | None = Field(
        default=None,
        description="Timestamp when user was updated"
    )
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": "3c8c663c-5b4d-4df7-93ae-2aa5978822dc",
                    "username": "test_user",
                    "email": "user_email@gmail.com",
                    "hashed_password": "",
                    "created_at": "2024, 7, 18, 14, 26, 41, 110735",
                    "updated_at": "2024, 8, 20, 15, 24, 10, 201381"
                }
            ]
        }
    )
