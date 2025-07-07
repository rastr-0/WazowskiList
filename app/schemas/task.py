from pydantic import BaseModel, Field, ConfigDict, create_model
from typing import Optional
from app.models.task import Task
from datetime import datetime, date


class CreateTask(BaseModel):
    """
    Pydantic model for creating a new task

    Attributes:
        title (str): Title of the task
        description (str | None): Description of the task, by default is None
        status (str): Status of the task
    """
    title: str = Field(
        description="Name of the task"
    )
    description: str | None = Field(
        default=None,
        description="Description of the task"
    )
    status: str = Field(
        default="not done",
        description="Status of the task"
    )
    label: str = Field(
        description="Label of the task"
    )
    deadline: datetime | None = Field(
        default=None,
        description="Deadline of the task"
    )
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "Buy groceries",
                    "description": "Milk, Bread, Cheese, Diet Coke",
                    "status": "not done",
                    "label": "shopping",
                    "deadline": "2024-12-11"
                }
            ]
        }
    )


# Pydantic model for updating task information. All the fields are optional
UpdateTask = create_model(
    "UpdateTask",
    **{
        k: (Optional[v], None)
        for k, v in CreateTask.__annotations__.items()
    }
)


class TaskResponse(Task):
    deadline: date | None = Field(
        default=None,
        description="Deadline of the task"
    )


class TaskCollection(BaseModel):
    """
    Pydantic model holding a list of tasks of `TaskResponse` instances
    """
    tasks: list[TaskResponse]
