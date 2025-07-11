# fastAPI
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
# db
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database.database import motor_db
# pydantic models
from app.schemas.task import TaskResponse
# models
from app.models.user import User
from app.models.reminder import Reminder
# for JWT token encoding/decoding
from jose import jwt
from jose.exceptions import JWEInvalidAuth
# pydantic
from pydantic import BaseModel
# password hashing
from passlib.context import CryptContext
# other modules
import uuid
from datetime import timedelta, datetime, timezone
from dotenv import load_dotenv
from os import getenv
from typing import Annotated
import json

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
myctx = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(password: str, hashed_password: str) -> bool:
    return myctx.verify(password, hashed_password)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


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


async def get_user_by_username(username: str, db: AsyncIOMotorDatabase) -> User | None:
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
                email=user.get("email"),
                full_name=user.get("full_name"),
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
    user = await get_user_by_username(username, db)
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
    user = await get_user_by_username(username=token_data.username, db=db)
    if user is None:
        raise credential_excepttion
    return user


async def update_username_dependencies(
        old_username: str,
        new_username: str,
        db: Annotated[AsyncIOMotorDatabase, Depends(motor_db.get_database)]
):
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
    return TaskResponse(
        id=task['id'],
        title=task['title'],
        description=task['description'],
        status=task['status'],
        owner=task['owner'],
        label=task['label'],
        deadline=task['deadline'],
        created_at=task['created_at'],
        updated_at=task['updated_at']
    )


async def get_task_by_id(
        task_id: uuid.UUID,
        current_user: User,
        db: Annotated[AsyncIOMotorDatabase, Depends(motor_db.get_database)]
) -> TaskResponse | None:
    """
    Get full task information by its ID

    Args:
        task_id (UUID4): ID of the task
        current_user (User): user data for validating tasks owners name with actual user performing request
        db (AsyncIOMotorDatabase): The database connection instance
    Returns:
        str | None: Name of the task if task was found, otherwise, None
    """
    collection = db.get_collection("tasks")
    try:
        task = await collection.find_one({"id": task_id})
        # validating if user performing task is actually owning the task
        if task.get("owner") == current_user.username:
            return convert_to_task_response(task)
    except Exception as e:
        raise ValueError(f"Error finding object by given id: {task_id} | Error description: {e}")


def make_date_humanitic(ugly_date: datetime) -> str:
    return ugly_date.strftime("%m/%d/%Y, %H:%M")


async def prepare_email_body(
        reminder: Reminder,
        current_user: User,
        db: AsyncIOMotorDatabase
) -> str:
    task = await get_task_by_id(reminder.task_id, current_user, db)
    body = f"""\
    <html>
      <body style="background-color: #f4f4f4; padding: 30px; font-family: Arial, sans-serif;">
        <div style="
            max-width: 600px;
            margin: auto;
            background-color: #ffffff;
            padding: 20px 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        ">
          <h2 style="color: #2c3e50;">Task Reminder</h2>
          <p><strong>Task:</strong> {task.title}</p>
          <p><strong>Description:</strong> {task.description}</p>
          <p><strong>Deadline:</strong> {make_date_humanitic(reminder.reminder_time)}</p>
          <p><strong>Your message:</strong> {reminder.message}</p>
          <hr style="margin: 20px 0;">
          <p style="font-size: 0.9em; color: #999;">🧠 Stay focused and good luck!<br>– The WazowskiList Team</p>
        </div>
      </body>
    </html>
    """
    return body
