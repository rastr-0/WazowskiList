from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


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

    SERVER_HOST: str
    PRODUCTION_SERVER_PORT: str


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

    MONGO_HOST: str
    MONGO_PORT: str
    MONGO_DB: str
    MONGO_USERNAME: str
    MONGO_PASSWORD: str

    @property
    def mongo_url(self) -> str:
        return (f"mongodb://{self.MONGO_USERNAME}:{self.MONGO_PASSWORD}@"
                f"{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB}")


class Settings(ServerSettings, DatabaseSettings):
    pass


settings = Settings(_env_file=".env")
