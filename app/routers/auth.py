# FastAPI modules
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
# models
from app.models.user import User
from app.schemas.user import UserResponse, CreateUser, UpdateUser, UserResponseUpdate
# db
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database.database import motor_db
# logs
from app.logs.logging_config import auth_logger
# utils
import app.utils.utils as utils
# other modules
from datetime import timedelta, datetime
from os import getenv
from typing import Any, Annotated

router = APIRouter()

"""
Authentication Management Endpoints

    The purpose of this docstring is following a DRY principle (don't repeat yourself)
    by documenting common parameters and dependencies for endpoints in this file

Common dependencies:
    1. get_database: Provides an instance of AsyncIOMotorDatabase for database operations
    2. get_current_user: Extracts and validates JWT token, retrieves user's details from the database

Common Parameters:
    1. db (AsyncIOMotorDatabase): Database connection instance
    2. current_user (User): User that is performing this request with his JWT token
"""


@router.post("/token", response_model=utils.Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Annotated[AsyncIOMotorDatabase, Depends(motor_db.get_database)]
) -> Any:
    """Endpoint for user loging to receive an access token

    Args:
        form_data (OAuth2PasswordRequestForm): The client login credentials containing `username` and `password`
        db (see module-level docstring on top)

    Returns:
        Token(*): Access token containing `access_token` and `token_type` fields
        (*)`Any` as a response type of the function is specified only for
            the purpose of avodining IDE warnings

    Raises:
        HTTPException (status_code=401): if user cannot be authenticated

    Dependency Functions:
        see module-level docstring on top

    Examples:
        Request Body
        {
            "username": "newuser",
            "password": "securepassword"
        }
        Response Body
        {
            "access_token": "your_access_token",
            "token_type": "bearer"
        }
    """
    user = await utils.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        auth_logger.warning(f"Failed login attempt for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "bearer"}
        )
    access_token_expires = timedelta(minutes=int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
    access_token = utils.create_access_token(data={'sub': user.username}, expires_delta=access_token_expires)

    auth_logger.info(f"New access token was successfully created for user: {form_data.username}")

    return utils.Token(
        access_token=access_token,
        token_type="bearer"
    )


@router.post("/register", response_model=UserResponse)
async def create_user(
        user: CreateUser,
        db: Annotated[AsyncIOMotorDatabase, Depends(motor_db.get_database)]
) -> Any:
    # TODO: Check if user with the same `username` field already exist
    #   if so, don't add user and throw an Exception
    """Endpoint for creating new user

    Args:
        user (CreateUser): The user information for creating a new user
        db (see module-level docstring on top)

    Returns:
        UserResponse(*): The user's information, not including password field
        (*)`Any` as a response type of the function is specified only for
            the purpose of avodining IDE warnings

    Raises:
        HTTPException (status_code=500): If new user cannot be inserted into the database

    Dependency functions:
        see module-level docsting on top

    Examples:
        Request Body:
        {
            "username": "newuser",
            "email": "newuser@example.com",
            "full_name": "New User",
            "password": "securepassword"
        }
        Response Body:
        {
            "username": "newuser",
            "email": "newuser@example.com",
            "full_name": "New User",
            "created_at": "2024-08-08T12:22:54Z"
        }
    """
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=utils.get_hashed_password(user.password),
        created_at=datetime.utcnow()
    )
    try:
        collection = db.get_collection("users")
        await collection.insert_one(db_user.model_dump())
        auth_logger.info(f"New user: {db_user.username} was successfully registered")
    except Exception as e:
        auth_logger.exception(f"Failed to register new user: {db_user.username}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error inserting new user in the database: {e}")

    return db_user


@router.post("/users/me", response_model=UserResponseUpdate)
async def update_user(
        update_user_data: UpdateUser,
        current_user: Annotated[User, Depends(utils.get_current_user)],
        db: AsyncIOMotorDatabase = Depends(motor_db.get_database)
) -> Any:
    # TODO:
    #  FIX: User's info updating works only when all fields are passed, otherwise, doesn't work

    """Endpoint for updating existing user's information

    Args:
        update_user_data (UpdateUser): Inherited class from the CreateUser with all the optional fields
        current_user (User): Currently authenticated user
        db (see module-level docstring on top)

    Returns:
        UserResponseUpdate(*): Inherited class from the UserResponse, has 1 more specific field: updated_at
        (*)`Any` as a response type of the function is specified only for
            the purpose of avodining IDE warnings

    Raises:
         HTTPException (status_code=404): If the user update fails or the user is not found

    Dependency Functions:
        see module-level docstring on top

    Examples:
        Request Body
        {
            "username": "newuser",
            "email": "newuser@example.com",
            "full_name": "New User",
            "password" "securepassword"
        }
        Response Body
        {
            "username": "newuser",
            "email": "newuser@example.com",
            "created_at": "2024-08-08T12:22:54Z",
            "updated_at": "2024-08-09T11:15:16Z"
        }
    """
    # users collection in database
    collection = db.get_collection("users")

    # exclude unset fields
    update_data = update_user_data.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data['hashed_password'] = utils.myctx.hash(update_data.pop("password"))

    try:
        result = await collection.update_one({"username": current_user.username}, {"$set": update_data})
    except Exception as e:
        auth_logger.exception(f"Failed updating user: {current_user.username}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error updating given user: {e}")

    if result.matched_count == 0:
        auth_logger.exception(f"Failed to find user: {current_user.username} for update")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # find user by the new username if was passed
    # otherwise find user by the already containing in the database username
    updated_user = await collection.find_one(
        {"username": update_user_data.username if "username" in update_data else current_user.username}
    )
    # if user updated username
    # all the dependencies in the `tasks` collection need to be updated to the new username
    if update_user_data.username is not None:
        try:
            await utils.update_username_dependencies(old_username=current_user.username,
                                                     new_username=update_user_data.username,
                                                     db=db)
            auth_logger.info(f"Existing tasks dependencies were successfully updated to work with new username: "
                             f"{current_user.username} --> {update_user_data.username}")
        except Exception as e:
            auth_logger.exception(f"Failed to update tasks dependencies for user: "
                                  f"{current_user.username}(old) --> {update_user_data.username}(new)")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Dependencies in tasks collection cannot be updated: {e}")

    if updated_user:
        auth_logger.info(f"Information for user: {current_user.username} was successfully updated")
        return UserResponseUpdate(
            username=updated_user.get("username"),
            email=updated_user.get("email"),
            created_at=updated_user.get("created_at"),
            updated_at=datetime.utcnow()
        )
    else:
        auth_logger.exception(f"Failed to find user: {current_user.username} for update")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.get("/users/me", response_model=UserResponse)
async def read_my_user(
        current_user: Annotated[User, Depends(utils.get_current_user)]
) -> Any:
    """Endpoint for getting currently authenticated user information

    Args:
        current_user (User): Currently authenticated user

    Returns:
        UserResponse(*): The user's information, not including password field
        (*)`Any` as a response type of the function is specified only for
            the purpose of avodining IDE warnings

    Dependency Functions:
       see module-level docstring on top

    Examples:
        Response Body
        {
            "username": "newuser",
            "email": "newuser@example.com",
            "created_at": "2024-08-08T12:22:54Z"
        }
    """
    return UserResponse(
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at
    )
