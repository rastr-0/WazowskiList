import uuid
from datetime import datetime

from pydantic import BaseModel, Field, EmailStr


class Reminder(BaseModel):
    id: uuid.UUID = Field(
        alias="_id",
        default_factory=uuid.uuid4,
        description="Identefication of the reminder"
    )
    task_id: str = Field(
        description="Task ID"
    )
    celery_id: str | None = Field(
        default=None,
        description="Reminder ID"
    )
    user_id: uuid.UUID = Field(
        description="User ID"
    )
    user_email: EmailStr = Field(
        description="User email"
    )
    reminder_time: datetime | None = Field(
        default=None,
        description="Reminder time"
    )
    message: str = Field(
        description="Message in the reminder"
    )
