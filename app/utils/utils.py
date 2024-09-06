# fastAPI
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
# db
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database.database import motor_db
# pydantic models
from app.schemas.task import TaskResponse
# password hashing
from passlib.context import CryptContext
# models
from app.models.user import User
# for JWT token encoding/decoding
from jose import jwt
from jose.exceptions import JWEInvalidAuth
# pydantic
from pydantic import BaseModel
# other modules
from datetime import timedelta, datetime, timezone
from dotenv import load_dotenv
from os import getenv
from typing import Annotated
import json

load_dotenv()

myctx = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


def verify_password(password: str, hashed_password: str) -> bool:
    return myctx.verify(password, hashed_password)


def get_hashed_password(password: str) -> str:
    return myctx.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Function for creating an access JWT token with optional expiration time,
        default is 30 minutes

    Args:
        data (dict): Information to be included in the token (in my implementation it's username)
        expires_delta (timedelta | None): Optional expiration time for JWT token, default is 15 minutes

    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"expiration": expire})

    # Serialize datetime object to str
    # because pydantic doesn't know how to handle datetime type
    json_data = json.dumps(to_encode, default=str)

    return jwt.encode(json.loads(json_data), getenv("SECRET_KEY"))


async def get_user(username: str, db: AsyncIOMotorDatabase) -> User | None:
    """Function for getting user by its username from the database

    Args:
        username (str): Username of the user
        db (AsyncIOMotorDatabase): The database connection instance

    Returns:
        User | None: User class instance in case of success and None in case of fail

    Raises:
        HTTTPException (status_code=404): If user cannot be found in the database
    """
    try:
        collection = db.get_collection("users")
        user = await collection.find_one({"username": username})
        if user:
            return User(
                username=user.get("username"),
                hashed_password=user.get("hashed_password")
            )
    except Exception as e:
        HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User cannot be found in the database: {e}"
        )
        return None


async def authenticate_user(username: str, password: str, db: AsyncIOMotorDatabase) -> bool | User:
    """Authenticate user with passed password

    Args:
        username: Username of the user
        password: User password
        db: The database connection instance

    Returns:
        bool | User: An instance of the User class if verified, otherwise False
    """
    user = await get_user(username, db)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Annotated[AsyncIOMotorDatabase, Depends(motor_db.get_database)]
) -> User:
    """Decode JWT token and check if user exists in database

    Args:
        token (str): Encoded JWT token
        db (AsyncIOMotorDatabase): The database connection instance

    Returns:
        User: User class instance

    Raises:
        HTTTPException (status_code=401):
            If username cannot be extracted from the passed token or username doesn't exist in the database
    """
    credential_excepttion = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "bearer"}
    )
    try:
        paylod = jwt.decode(token, getenv("SECRET_KEY"), algorithms=[getenv("ALGORITHM")])
        username: str = paylod.get("sub")
        if username is None:
            raise credential_excepttion
        token_data = TokenData(username=username)
    except JWEInvalidAuth:
        raise credential_excepttion
    user = await get_user(username=token_data.username, db=db)
    if user is None:
        raise credential_excepttion
    return user


async def update_username_dependencies(old_username: str, new_username: str, db: AsyncIOMotorDatabase):
    """Update dependencies in the `tasks` database collection from old owner's username to the new

    Args:
        old_username (str): Old owner's username
        new_username (str): New owner's username
        db (AsyncIOMotorDatabase): The database connection instance

    Raises:
        HTTPException (status_code=500):
            if an old owner's username cannot be updated to the new one
    """
    collection = db.get_collection("tasks")
    try:
        await collection.update_many(
            {"owner": old_username},
            {"$set": {"owner": new_username}}
        )
    except Exception as _:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Old owner username cannot be changed to new owner username"
                   f"{old_username}(old) -> {new_username}(new)"
        )


def convert_to_task_response(task: dict) -> TaskResponse:
    print(task)
    return TaskResponse(
        id=task['id'],
        title=task['title'],
        description=task['description'],
        status=task['status'],
        owner=task['owner'],
        label=task['label'],
        created_at=task['created_at'],
        updated_at=task['updated_at']
    )
