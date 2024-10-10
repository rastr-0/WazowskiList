from app.logs.logging_config import auth_logger
from app.logs.logging_config import tasks_logger


# authentication related exceptions
class RegisterUserException(Exception):
    def __init__(self, username: str):
        auth_logger.exception(f"Error inserting new user in the database: {username}")
        super().__init__(f"Failed to register new user: {username}")


class UserExistsException(Exception):
    def __init__(self, username: str):
        auth_logger.exception(f"User with the same username: {username} already exists in the database")
        super().__init__(f"User with the same username already registered")


class UserNotFoundException(Exception):
    def __init__(self, username: str, operation_type: str):
        auth_logger.exception(f"Failed to find user: {username} for the given operation: {operation_type}")
        super().__init__(f"Failed to find user: {username}")


class UpdateUserException(Exception):
    def __init__(self, username: str):
        auth_logger.exception(f"Failed updating user: {username}")
        super().__init__(f"Failed updating user: {username}")


class UpdateUserDependenciesException(Exception):
    def __init__(self, current_username: str, updated_username: str):
        auth_logger.info(f"Failed to update tasks dependencies for user: "
                         f"{current_username}(old) --> {updated_username}(new)")
        super().__init__("Some dependencies were not properly updated for new username")


# tasks related exceptions
class AddTaskException(Exception):
    def __init__(self, user_triggered_operation, task_name: str):
        tasks_logger.exception(f"Error inserting new task in the database by user: {user_triggered_operation}")
        super().__init__(f"Failed adding new task")


class InvalidUUIDException(Exception):
    def __init__(self, user_triggered_operation: str, task_id: str):
        tasks_logger.error(f"Invalid UUID format for task_id: {task_id} by user: {user_triggered_operation}")
        super().__init__(f"Invalid id provided for the task")


class BadUpdateRequestException(Exception):
    def __init__(self, user_triggered_operation: str, task_id: str):
        tasks_logger.warning(
            f"No fields to update provided for task_id: {task_id} by user: {user_triggered_operation}"
        )
        super().__init__("No fields to update provided")


class TaskNotFoundException(Exception):
    def __init__(self, user_triggered_operation: str, task_id: str):
        tasks_logger.warning(
            f"Task not found (task_id: {task_id}; user: {user_triggered_operation})"
        )
        super().__init__("Task not found")


class UpdateTaskException(Exception):
    def __init__(self, user_triggered_operation: str, task_id: str):
        tasks_logger.logger(
            f"Task not updated (task_id: {task_id}; user: {user_triggered_operation})"
        )
        super().__init__("Task was not updated")
