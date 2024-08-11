from pydantic import BaseModel, Field, ConfigDict
from app.models.task import Task


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
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "Buy groceries",
                    "description": "Milk, Bread, Cheese, Diet Coke",
                    "status": "not done"
                }
            ]
        }
    )


def convert_to_optional(schema):
    from typing import Optional
    return {k: Optional[v] for k, v in schema.__annotations__.items()}


class UpdateTask(CreateTask):
    """Pydantic model for updating task information. All the fields are optional

    Attributes:
        title: New title of the task
        description: New description of the task
        status: New status of the task
    """
    # convert_to_optional converts all the fields of CreateTask to optional
    # and set them to __annotations__ of UpdateTask class
    # by using this approach we don't duplicate code
    __annotations__ = convert_to_optional(CreateTask)


class TaskResponse(Task):
    pass


class TaskCollection(BaseModel):
    """
    Pydantic model holding a list of tasks of `TaskResponse` instances
    """
    tasks: list[TaskResponse]
