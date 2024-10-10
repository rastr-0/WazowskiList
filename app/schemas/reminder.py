from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from app.utils.utils import convert_to_optional


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


class UpdateReminder(CreateReminder):
    # convert_to_optional converts all the fields of CreateReminder to optional
    # and set them to __annotations__ of UpdateReminder class
    # by using this approach we don't duplicate code
    __annotations__ = convert_to_optional(CreateReminder)
