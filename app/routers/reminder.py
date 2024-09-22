# FastAPI models
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
from app.schemas.reminder import CreateReminder, ReminderResponse
# uitls
from app.utils.utils import get_current_user
# scheduler
from app.services.scheduler import schedule_reminder
# other modules
from typing import Any, Annotated
import uuid

router = APIRouter(prefix="/api/schedule", tags=["reminders"])


@router.post("/reminder", response_model=ReminderResponse)
async def create_reminder(
        reminder: CreateReminder,
        task_id: uuid.UUID,
        db: Annotated[AsyncIOMotorDatabase, Depends(motor_db.get_database)],
        current_user: Annotated[User, Depends(get_current_user)]
) -> Any:
    collection = db.get_collection("reminders")

    reminder_db = Reminder(
        task_id=task_id,
        user_id=current_user.id,
        user_email=current_user.email,
        reminder_time=reminder.reminder_time,
        message=reminder.message
    )
    try:
        await collection.insert_one(reminder_db.model_dump())
        reminder_logger.info(
            f"New reminder was successfully inserted in the database by user: {current_user.username}"
        )
    except Exception as e:
        reminder_logger.error(
            f"Error inserting new reminder in the database by user: {current_user.username}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inserting new reminder in the database: {e}"
        )

    # Schedule the reminder logic
    await schedule_reminder(reminder.task_id, reminder.reminder_time)

    reminder_logger.info("New reminder was successfully created")

    return reminder_db


@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
        reminder_id: uuid.UUID,
        db: Annotated[AsyncIOMotorDatabase, Depends(motor_db.get_database)]
) -> Any:
    collection = db.get_collection("reminders")
    reminder = await collection.find_one({"_id": reminder_id})
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return Reminder(**reminder)


@router.delete("/{reminder_id}")
async def delete_reminder(
        reminder_id: uuid.UUID,
        db: Annotated[AsyncIOMotorDatabase, Depends(motor_db.get_database)]
) -> dict:
    collection = db.get_collection("reminders")
    result = await collection.delete_one({"_id": reminder_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Reminder not found")

    return {"detail": f"Reminder (id: {reminder_id}) was successfully deleted"}
