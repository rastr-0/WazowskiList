from pydantic import BaseModel, Field, ConfigDict, create_model
from typing import Optional
from datetime import datetime


class CreateReminder(BaseModel):
    reminder_time: datetime = Field(
        description="Time when the reminder will be send"
    )
    message: str = Field(
        description="Message in the reminder"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    # format type for 'reminder_time' is not precise
                    "reminder_time": "2024-12-11/12:00",
                    "message": "I should not skip this one, really important"
                }
            ]
        }
    )


class ReminderResponse(CreateReminder):
    pass


UpdateReminder = create_model(
    "UpdateReminder",
    **{
        k: (Optional[v], None)
        for k, v in CreateReminder.__annotations__.items()
    }
)
