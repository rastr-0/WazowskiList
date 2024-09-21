# FastAPI models
from fastapi import APIRouter, Depends, HTTPException
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
# scheduler
from app.reminder_sending_logic.scheduler import schedule_reminder
# other modules
from typing import Any, Annotated
import uuid

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.post("/", response_model=ReminderResponse)
async def create_reminder(
        reminder: CreateReminder,
        db: Annotated[AsyncIOMotorDatabase, Depends(motor_db.get_database)],
        current_user: Annotated[User, Depends()]
) -> Any:
    collection = db.get_collection("reminders")
    reminder_data = reminder.model_dump()
    result = await collection.insert_one(reminder_data)

    # Schedule the reminder logic
    await schedule_reminder(reminder.task_id, reminder.reminder_time)

    reminder_logger.info("New reminder was successfully created")

    reminder.id = str(result.inserted_id)
    return reminder


@router.get("/{reminder_id}", response_model=Reminder)
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
) -> Any:
    collection = db.get_collection("reminders")
    result = await collection.delete_one({"_id": reminder_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"status": "Reminder deleted"}
