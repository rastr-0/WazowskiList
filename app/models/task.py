from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
import uuid


class Task(BaseModel):
    """
    Pydantic model representing a task

    Attributes:
        id (uuid.UUID): ID of the task
        title (str): Title of the task
        description (str): Description of the task
        status (str): Status of the task
        owner (str): Creator of the task
        label (str): Label of the task
        created_at (datetime): Timestamp when task was created
        updated_at (datetime): Timestamp when task was updated
        model_config (ConfigDict):
            TypedDict for configuring Pydantic behaviour,
            including usage example for OpenAPI
    """

    id: uuid.UUID = Field(
        alias="_id",
        default_factory=uuid.uuid4,
        description="Identification of the task"
    )
    title: str = Field(
        description="Name of the task"
    )
    description: str | None = Field(
        default=None,
        description="Description of the task"
    )
    status: str = Field(
        description="Status of the task, e.g. pending, done, ..."
    )
    owner: str = Field(
        description="Owner of the task"
    )
    label: str = Field(
        description="Label of the task"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when task was created"
    )
    updated_at: datetime | None = Field(
        default=None,
        description="Timestamp when task was updated"
    )

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "9a94f0dd-27e6-4e98-9474-174c7117703d",
                    "title": "German language",
                    "description": "Learn new words from the previous class",
                    "status": "pending",
                    "owner": "rastr",
                    "label": "important",
                    "created_at": "2024, 7, 18, 14, 35, 6, 789754",
                    "updated_at": "2024, 9, 3, 17, 13, 5, 426102"
                }
            ]
        }
    )
