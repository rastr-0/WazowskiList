# FastAPI models
from fastapi import APIRouter, Depends, HTTPException, Query, status
# pydantic models
from app.models.task import Task
from app.models.user import User
from app.schemas.task import CreateTask, UpdateTask, TaskResponse, TaskCollection
# db
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database.database import motor_db
# utils
from app.utils.utils import get_current_user
# logs
from app.logs.logging_config import tasks_logger
# other modules
from typing import Any, Annotated
import uuid
from datetime import datetime

router = APIRouter()

"""
Task Management Endpoints

    The purpose of this docstring is following a DRY principle (don't repeat yourself)
    by documenting common parameters and dependencies for endpoints in this file

Common Dependencies:
    1. get_database: Provides an instance of AsyncIOMotorDatabase for database operations
    2. get_current_user: Extracts and validates JWT token, retrieves user's details from the database

Common Parameters:
    1. db (AsyncIOMotorDatabase): Database connection instance
    2. current_user (User): User that is performing this request with his JWT token
"""


@router.post("/tasks", response_model=TaskResponse)
async def create_task(
        task: CreateTask,
        db: Annotated[AsyncIOMotorDatabase, Depends(motor_db.get_database)],
        current_user: Annotated[User, Depends(get_current_user)]
) -> Any:
    """Endpoint for creating new task in the database

    Args:
        task (CreateTask): Data for the new task
        db (see module-level docstring on top)
        current_user (see module-level docstring on top)

    Returns:
        TaskResponse(*): Pydantic model with new added data to the database
        (*)`Any` as a response type of the function is specified only for
            the purpose of avodining IDE warnings

    Raises:
        HTTPException (status_code=500): if new task cannot be inserted into the database

    Dependency Functions:
        see module-level docstring on top

    Examples:
        Request Body
        {
            "title": "new task title",
            "description": "new task description",
            "status": "status of new task"
        }
        Response Body
        {
            "id": "cff06f70-d6fa-43b3-a7e6-9a130169f7c6",
            "title": "new task title",
            "description": "new task description",
            "status": "status of new task",
            "owner": "newuser",
            "created_at": "2024-09-08T17:17:10Z",
            "updated_at": None
        }

    """
    db_task = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        owner=current_user.username,
        created_at=datetime.utcnow()
    )
    try:
        collection = db.get_collection("tasks")
        await collection.insert_one(db_task.model_dump())
        tasks_logger.info(f"New task was successfully inserted by user: {current_user.username}")
    except Exception as e:
        tasks_logger.exception(f"Error inserting new task in the database by user: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inserting new task in the database: {e}"
        )
    return db_task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
        task_id: str,
        task_update: UpdateTask,
        db: AsyncIOMotorDatabase = Depends(motor_db.get_database),
        current_user: User = Depends(get_current_user)
) -> Any:
    """Endpoint for updating an existing task in the database based on its title.

    Args:
        task_id (str): ID of the task.
        task_update (UpdateTask): Updated data for the task.
        db (see module-level docstring on top)
        current_user (see module-level docstring on top)

    Returns:
        TaskResponse: Pydantic model with updated data.

    Raises:
        HTTPException (status_code=400): If task_update is empty.

    Dependency Functions:
        documented in `common management endpoints->common dependencies (1 and 2)` on top of the file

    Examples:
        Request Body (all fields are optional):
        {
            "title": "new task title",
            "description": "new task description",
            "status": "status of new task"
        }
        Response Body:
        {
            "id": "cff06f70-d6fa-43b3-a7e6-9a130169f7c6",
            "title": "new task title",
            "description": "new task description",
            "status": "status of new task",
            "owner": "newuser",
            "created_at": "2024-09-08T17:17:10Z",
            "updated_at": "2024-09-10T20:20:50Z"
        }
    """
    tasks_logger.info(
        f"Attempting to update task (task_id: {task_id}) by user: {current_user.username}"
    )

    # Get only non-None fields
    update_data = {k: v for k, v in task_update.model_dump().items() if v is not None}

    if not update_data:
        tasks_logger.warning(
            f"No fields to update provided for task_id: {task_id} by user: {current_user.username}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update provided"
        )

    # Tasks collection in the database
    collection = db.get_collection("tasks")

    # Update task by task_id and owner
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError as e:
        tasks_logger.error(
            f"Invalid UUID format for task_id: {task_id} by user: {current_user.username}. Error: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid UUID format: {e}"
        )

    # Update the updated_at field
    update_data["updated_at"] = datetime.now()

    tasks_logger.info(
        f"Attempting to update task_id: {task_id} by user: {current_user.username} with data: {update_data}"
    )

    result = await collection.update_one(
        {"id": task_uuid, "owner": current_user.username},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        tasks_logger.warning(
            f"Task not found for update (task_id: {task_id}; user: {current_user.username})"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if result.modified_count == 0:
        tasks_logger.error(
            f"Failed to update task data (task_id: {task_id}; user: {current_user.username})"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task data"
        )

    updated_task = await collection.find_one({"id": task_uuid})

    if not updated_task:
        tasks_logger.error(
            f"Updated task not found in the database (task_id: {task_id}; user: {current_user.username})"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Updated task not found"
        )

    tasks_logger.info(
        f"Task successfully updated (task_id: {task_id}; user: {current_user.username})"
    )

    # TODO: rewrite with using utils.convert_to_task_response
    return TaskResponse(
        id=updated_task["id"],
        title=updated_task["title"],
        description=updated_task["description"],
        status=updated_task["status"],
        owner=updated_task["owner"],
        created_at=updated_task["created_at"],
        updated_at=updated_task["updated_at"]
    )


@router.delete("/tasks/{task_id}")
async def delete_task(
        task_id: str,
        db: Annotated[AsyncIOMotorDatabase, Depends(motor_db.get_database)],
        current_user: Annotated[User, Depends(get_current_user)]
) -> dict:
    """Endpoint for deleting task specified by its id

    Args:
        task_id (str): Auto-generated ID of the task
        db (see module-level docstring on top)
        current_user (see module-level docstring on top)

    Returns:
        dict: Message about successful deleting the task

    Raises:
        HTTPException (status_code=404): if task was failed to be deleted

    Dependency Functions:
        see module-level docstring on top
    """
    tasks_logger.info(
        f"Attempting to delete task (task_id: {task_id}) by user: {current_user.username}"
    )

    collection = db.get_collection("tasks")
    result = await collection.delete_one(
        {
            "id": uuid.UUID(task_id),
            "owner": current_user.username
        }
    )
    if result.deleted_count == 0:
        tasks_logger.warning(
            f"Failed to delete task (task_id: {task_id}) by user: {current_user.username}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Failed to delete task with following id: {task_id}"
        )

    tasks_logger.info(
        f"Task successfully deleted (task_id: {task_id}) by user: {current_user.username}"
    )
    return {"detail": "Task was successfully deleted"}


@router.get("/tasks", response_model=TaskCollection)
async def get_task(
        db: Annotated[AsyncIOMotorDatabase, Depends(motor_db.get_database)],
        current_user: Annotated[User, Depends(get_current_user)],
        task_status: Annotated[str | None, Query(
            # default=None,
            title="Status of the tasks",
            description="Provide your status for getting only tasks with it"
        )] = None,
        sort_by: Annotated[str | None, Query(
            # default=None,
            title="Sort tasks by specific fields",
            description="Available fields: `created_at`, `updated_at`",
            # regex checks that given string is one of the available fields
            pattern="^(created_at|updated_at)$"
        )] = None,
        sort_order: Annotated[str | None, Query(
            # default=None,
            title="Sorting order",
            description="Available orders: `asc`, `desc`",
            # regex checks that given string is one of the available fields
            pattern="^(asc|desc)$"
        )] = None,
        skip: Annotated[int, Query(
            # default=0,
            title="Skip pagination",
            ge=0
        )] = 0,
        limit: Annotated[int, Query(
            # default=100,
            # to prevent server abuse
            title="Limit pagination",
            le=500
        )] = 100
) -> TaskCollection:
    """Endpoint for fetching tasks from the database and sort them based on given order and criteria.

    By default, `sort_by` and `sort_order` are None.
    If you provide `sort_by` and NOT provide `sort_order`, by default, it's ascending.
    If you privde `sort_order` and NOT provide `sort_by` program will raise an exception.

    Args:
        db (see module-level docstring on top)
        current_user (see module-level docstring on top)
        task_status (str - optional): Status of the tasks
        sort_by (str - optional): Field based on which tasks will be sorted
        sort_order (str - optional): Order in which tasks will be sorted (ascending or descending)
        skip (str - ptional): Number of tasks to skip (for pagination)
        limit (str - optional): Maximum number of tasks to return (for pagination)

    Returns:
        TaskCollection: list of Task instances

    Raises:
        HTTPException (status_code=400):
            If `sort_order` is provided and `sort_by` is not. This scenario follows to the exception
        HTTPException (status_code=500): If tasks cannot be fetched from the database

    Dependency Functions:
        see module-level docstring on top

    Examples:
        Response Body
        {
            [
                {
                    id": "cff06f70-d6fa-43b3-a7e6-9a130169f7c6",
                    "title": "new task title 1",
                    "description": "new task description 1",
                    "status": "status of new task 1",
                    "owner": "newuser1",
                    "created_at": "2024-10-08T17:20:13Z",
                    "updated_at": date or None
                },
                {
                    id": "3193f773-e077-412b-b6df-2be4d92493ea",
                    "title": "new task title 2",
                    "description": "new task description 2",
                    "status": "status of new task 2",
                    "owner": "newuser2",
                    "created_at": "2024-11-03T15:01:53Z",
                    "updated_at": date or None
                }
            ]
        }
    """
    tasks_logger.info(
        f"Fetching tasks for user: {current_user.username} with params - "
        f"status: {task_status}, sort_by: {sort_by}, sort_order: {sort_order}, "
        f"skip: {skip}, limit: {limit}"
    )

    if sort_order is not None and sort_by is None:
        tasks_logger.error(f"Sort order provided without sort_by for user: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="`sort_order` criteria is provided, but `sort_by` is not. Error sorting tasks"
        )

    sort_order_value = 1 if sort_order == 'asc' else -1 if sort_order == 'desc' else None
    sort_criteria = [(sort_by, sort_order_value)] if sort_by and sort_order_value else None

    try:
        query = {'owner': current_user.username}
        if task_status:
            query['status'] = task_status

        collection = db.get_collection("tasks")
        cursor = collection.find(query).skip(skip).limit(limit)
        if sort_criteria:
            cursor = cursor.sort(sort_criteria)
        tasks = await cursor.to_list(length=limit)
        tasks_logger.info(f"Tasks fetched successfully for user: {current_user.username}")
    except Exception as e:
        tasks_logger.error(f"Failed to fetch tasks from the database for user: {current_user.username}. Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch tasks from the database: {e}"
        )
    # TODO: rewrite with using utils.convert_to_task_response
    task_models = list(
        TaskResponse(
            id=task['id'],
            title=task['title'],
            description=task['description'],
            status=task['status'],
            owner=task['owner'],
            created_at=task['created_at'],
            updated_at=task['updated_at']
        )
        for task in tasks
    )

    return TaskCollection(tasks=task_models)
