from app.logs.logging_config import auth_logger


class RegisterUserException(Exception):
    def __init__(self, username: str):
        auth_logger.exception(f"Error inserting new user in the database: {username}")
        super().__init__(f"Failed to register new user: {username}")


class FindUserException(Exception):
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
        super().__init__(
            f"Some dependencies were not properly updated for new username: {updated_username}."
            f"Your username stays the same: {current_username}"
        )
