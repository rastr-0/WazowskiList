from app.logs.logging_config import auth_logger, tasks_logger, database_logger, reminder_logger


# General Exception Base Class
class AppException(Exception):
    def __init__(self, logger, message: str):
        logger.exception(message)
        super().__init__(message)


# Authentication related exceptions
class RegisterUserException(AppException):
    def __init__(self, username: str):
        message = f"Failed to register new user: {username}"
        super().__init__(auth_logger, message)


class UserExistsException(AppException):
    def __init__(self, username: str):
        message = f"User with the same username already registered: {username}"
        super().__init__(auth_logger, message)


class UserNotFoundException(AppException):
    def __init__(self, username: str, operation_type: str):
        message = f"Failed to find user: {username} for operation: {operation_type}"
        super().__init__(auth_logger, message)


class UpdateUserException(AppException):
    def __init__(self, username: str):
        message = f"Failed to update user: {username}"
        super().__init__(auth_logger, message)


class UpdateUserDependenciesException(AppException):
    def __init__(self, current_username: str, updated_username: str):
        message = f"Failed to update task dependencies for user: {current_username} -> {updated_username}"
        super().__init__(auth_logger, message)


# Task related exceptions
class AddTaskException(AppException):
    def __init__(self, user_triggered_operation: str, task_name: str):
        message = f"Failed to add task: {task_name}, triggered by user: {user_triggered_operation}"
        super().__init__(tasks_logger, message)


class InvalidUUIDException(AppException):
    def __init__(self, user_triggered_operation: str, task_id: str):
        message = f"Invalid UUID for task_id: {task_id}, triggered by user: {user_triggered_operation}"
        super().__init__(tasks_logger, message)


class BadUpdateRequestException(AppException):
    def __init__(self, user_triggered_operation: str, task_id: str):
        message = f"No fields to update for task_id: {task_id}, triggered by user: {user_triggered_operation}"
        super().__init__(tasks_logger, message)


class TaskNotFoundException(AppException):
    def __init__(self, user_triggered_operation: str, task_id: str):
        message = f"Task not found (task_id: {task_id}, triggered by user: {user_triggered_operation})"
        super().__init__(tasks_logger, message)


class UpdateTaskException(AppException):
    def __init__(self, user_triggered_operation: str, task_id: str):
        message = f"Failed to update task (task_id: {task_id}, triggered by user: {user_triggered_operation})"
        super().__init__(tasks_logger, message)


# Database and Message-Broker related exceptions
class CreateConnectionException(AppException):
    def __init__(self, msg: str):
        super().__init__(database_logger, msg)


class UpdateReminderException(AppException):
    def __init__(self, user_triggered_operation: str, reminder_id: str):
        message = f"Failed to update reminder (reminder_id: {reminder_id}, triggered by user: {user_triggered_operation})"
        super().__init__(tasks_logger, message)


class ReminderNotFoundException(AppException):
    def __init__(self, user_triggered_operation: str, reminder_id: str):
        message = f"Reminder not found (reminder_id: {reminder_id}, triggered by user: {user_triggered_operation})"
        super().__init__(tasks_logger, message)


class DeleteReminderException(AppException):
    def __init__(self, user_triggered_operation: str, reminder_id: str):
        message = f"Failed to delete remidner (reminder_id: {reminder_id}, triggered by user: {user_triggered_operation})"
        super().__init__(reminder_logger, message)


class AddReminderException(AppException):
    def __init__(self, user_triggered_operation: str, reminder_id):
        message = f"Failed to add remidner (reminder_id: {reminder_id}, triggered by user: {user_triggered_operation})"
        super().__init__(reminder_logger, message)


class LoggingSetupException(Exception):
    pass
