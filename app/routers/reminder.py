# FastAPI models
import time
from fastapi import APIRouter, Depends, HTTPException, status
# models
from app.models.user import User
# db
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database.database import motor_db
# logs
from app.logs.logging_config import reminder_logger
# pydantic models
from app.models.reminder import Reminder
from app.schemas.reminder import CreateReminder, ReminderResponse, UpdateReminder
# uitls
from app.utils.utils_models import get_current_user, get_task_by_id
from app.utils.utils_models import prepare_email_body
# scheduler
from app.services.scheduler import schedule_reminder
from aioredis import Redis
# other modules
from typing import Any, Annotated
import uuid
from datetime import timedelta

router = APIRouter(prefix="/api/schedule", tags=["reminders"])

"""
Reminder Management Endpoints

    The purpose of this docstring is following a DRY principle (don't repeat yourself)
    by documenting common parameters and dependencies for endpoints in this file

Common dependencies:
    1. get_database: Provides an instance of AsyncIOMotorDatabase for database operations
    2. get_current_user: Extracts and validates JWT token, retrieves user's details from the database

Common Parameters:
    1. db (AsyncIOMotorDatabase): Database connection instance
    2. current_user (User): User that is performing this request with his JWT token
"""


@router.post("/reminder", response_model=ReminderResponse)
async def create_reminder(
        reminder: CreateReminder,
        task_id: str,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Annotated[AsyncIOMotorDatabase, Depends(motor_db.get_database)]
) -> Any:
    """Endpoint for creating a reminder for existing task

    Args:
        reminder (CreateReminder): Data for the new reminder
        task_id (str): Task ID for which reminder will be created
        current_user (User): User that is performing this request with his JWT token
        db (AsyncIOMotorDatabase): Database connection instance

    Returns:
        ReminderResponse: Pydantic model with data added to Redis
        (*)`Any` as a response type of the function is specified only for
            the purpose of avoiding IDE warnings

    Raises:
        HTTPException (status_code=500): if new reminder cannot be processed by Celery
        HTTPException(status_code=1001): if construction of the reminder fails

    Dependency Functions:
        see module-level docstring on top

    Examples:
        Request Body
        {
            "reminder_time": "2024-10-11:12:30",
            "message": "Extremely important reminder, cannot be skipped"
        }
        Response Body
        {
            "reminder_time": "2024-10-11:12:30",
            "message": "Extremely important reminder, cannot be skipped"
        }
    """

    if current_user.email is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"For setting reminders is necessary to have an email address in the profile! Try adding it",
            headers={"Details": "No email to send reminder"}
        )

    try:
        task_in_reminder = await get_task_by_id(uuid.UUID(task_id), current_user, db)
        task_deadline = task_in_reminder.deadline
        reminder_data = Reminder(
            task_id=uuid.UUID(task_id),
            user_id=current_user.id,
            user_email=current_user.email,
            # if reminder time is not explicitly given, then it is deadline - 1 hour
            reminder_time=(
                reminder.reminder_time
                if reminder.reminder_time is not None
                else task_deadline - timedelta(hours=1)
            ),
            message=reminder.message
        )
        reminder_logger.info(f"Reminder was successfully formed: {reminder_data.reminder_time}"
                             f"...{reminder.reminder_time} AND {task_deadline}")
    except Exception as e:
        reminder_logger.error(
            f"Error constructing reminder for user: {current_user.username}. Error: {e}"
        )
        raise HTTPException(
            status_code=status.WS_1011_INTERNAL_ERROR,
            detail=f"Unexpected error occured while processing your reminder. Try again later!",
            headers={"Details": "Reminder construction error"}
        )

    try:
        email_body = await prepare_email_body(reminder_data, current_user, db)
        # schedule reminder at a specific time
        schedule_reminder.apply_async(
            args=[
                str(reminder_data.user_email), email_body
            ],
            eta=reminder_data.reminder_time
        )

        reminder_logger.info(
            f"New reminder was successfully inserted in Reddis by user: {current_user.username}"
        )
    except Exception as e:
        reminder_logger.error(
            f"Error processing task by Celery for user: {current_user.username}. Error: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error occured while processing your reminder. Try again later!",
            headers={"Details": "Celery task failure"}
        )

    return reminder_data


@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
        reminder_id: str,
        reminder: UpdateReminder,
        current_user: Annotated[User, Depends(get_current_user)]
) -> Any:
    """Endpoint for updating an existing reminder

    Args:
        reminder_id (uuid.UUID): Reminder ID
        reminder (CreateReminder): Data for updating reminder
        current_user (User): User that is performing this request with his JWT token

    Returns:
        ReminderResponse: Pydantic model with updated data
        (*)`Any` as a response type of the function is specified only for
            the purpose of avoiding IDE warnings

    Raises:
        HTTPException (status_code=404): if reminder with given ID was not found
    """
    pass


@router.delete("/{reminder_id}", response_model=dict)
async def delete_reminder(
        reminder_id: uuid.UUID
):
    pass
