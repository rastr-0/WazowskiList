from pydantic import BaseModel, Field, ConfigDict, EmailStr, create_model
from typing import Optional
from datetime import datetime


class CreateUser(BaseModel):
    """
    Pydantic model for creating user

    Attributes:
        username (str): Username of new user
        password (str): Password of new user
        email (EmailStr | None): Email of new user
        full_name (str | None): Full name of new user
    """
    username: str = Field(
        description="Name of the user"
    )
    password: str = Field(
        description="Password of the user"
    )
    email: EmailStr | None = Field(
        default=None,
        description="E-mail of the user"
    )
    full_name: str | None = Field(
        default=None,
        description="Full name of the user"
    )
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "username": "test_user",
                    "password": "ThisIsThePassword1900",
                    "email": "user_email@gmail.com",
                    "full_name": "Billy Joe"
                }
            ]
        }
    )


class UserResponse(BaseModel):
    """
    Pydantic model for sending User as a response

    Attributes:
        username (str): Username of user
        email (EmailStr | None): Email of user
        created_at (datetime): Time of user's creation
    """
    username: str
    email: EmailStr | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class UserResponseUpdate(UserResponse):
    updated_at: datetime


UpdateUser = create_model(
    "UpdateUser",
    **{
        k: (Optional[v], None)
        for k, v in CreateUser.__annotations__.items()
    }
)
