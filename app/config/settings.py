from email.policy import default

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class CelerySettings(BaseSettings):
    """
    Class representing basic Celery settings

    Attributes:
        CELERY_BROKER_URL: Address of the broker (reddis)
        CELERY_RESULT_BACKEND: Address of the result back (information about execution process of the tasks)
    """
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Celery configuration
    CELERY_BROKER_URL: str = Field(default="celery_broker_url")
    CELERY_RESULT_BACKEND: str = Field(default="celery_result_backend")


class SMTPSettings(BaseSettings):
    """
    Class representing basic SMTP settings

    Attributes:
        SMTP_SERVER: Ip address of the SMTP server
        SMTP_PORT: Port of the SMTP server
        SMTP_USER: username from which account will be sent emails
        SMTP_PASSWORD: Password of user from which account will be sent emails
    """
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SMTP_SERVER: str = Field(default="smtp")
    SMTP_PORT: str = Field(default="smtp_port")
    SMTP_USER: str = Field(default="smtp_user")
    SMTP_PASSWORD: str = Field(default="smtp_password")


class ServerSettings(BaseSettings):
    """
    Class representing 2 basic server settings. Inherits from Pydantic BaseSettings.

    Attributes:
        SERVER_HOST: Ip address of the server, default is 127.0.0.1
        PRODUCTION_SERVER_PORT:
            Specific port number.
            Development port is 7000, production port is 8000
    """
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SERVER_HOST: str = Field(default="server_host")
    PRODUCTION_SERVER_PORT: str = Field(default="server_port")


class DatabaseSettings(BaseSettings):
    """
    Class representing database settings

    Attributes:
        MONGO_HOST: Ip address of the MongoDB client
        MONGO_PORT: Port of the MongoDB client
        MONGO_DB: Name of the database
        MONGO_USERNAME: Username for the MongoDB client
        MONGO_PASSWORD: Password for the MongoDB client
    """
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    MONGO_HOST: str = Field("mongo_host")
    MONGO_PORT: int = Field(27017)
    MONGO_DB: str = Field("mongo_db_name")
    MONGO_USERNAME: str = Field("mongo_username")
    MONGO_PASSWORD: str = Field("mongo_password")

    @property
    def mongo_url(self) -> str:
        return (f"mongodb://{self.MONGO_USERNAME}:{self.MONGO_PASSWORD}@"
                f"{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB}")


class Settings(ServerSettings, DatabaseSettings, CelerySettings, SMTPSettings):
    pass


settings = Settings(env_file=".env")
