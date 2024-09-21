import uuid
from datetime import datetime

from pydantic import BaseModel, Field, EmailStr


class Reminder(BaseModel):
    id: uuid.UUID = Field(
        alias="_id",
        default_factory=uuid.uuid4,
        description="Identefication of the reminder"
    )
    task_id: uuid.UUID = Field(
        description="Task ID"
    )
    user_id: uuid.UUID = Field(
        description="User ID"
    )
    user_email: EmailStr = Field(
        description="User email"
    )
    reminder_time: datetime = Field(
        description="Reminder time"
    )
    message: str = Field(
        description="Message in the reminder"
    )