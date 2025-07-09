from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Celery
    CELERY_BROKER_URL: str = Field(default="redis://redis:6379/0")
    CELERY_RESULT_BACKEND: str = Field(default="redis://redis:6379/0")

    # SMTP
    SMTP_SERVER: str = Field(default="smtp")
    SMTP_PORT: str = Field(default="587")
    SMTP_USER: str = Field(default="user@example.com")
    SMTP_PASSWORD: str = Field(default="password")

    # Server
    SERVER_HOST: str = Field(default="127.0.0.1")
    PRODUCTION_SERVER_PORT: str = Field(default="8000")

    # Mongo
    MONGO_HOST: str = Field(default="localhost")
    MONGO_PORT: int = Field(default=27017)
    MONGO_DB: str = Field(default="mydb")
    MONGO_USERNAME: str = Field(default="user")
    MONGO_PASSWORD: str = Field(default="pass")

    @property
    def mongo_url(self) -> str:
        return (f"mongodb://{self.MONGO_USERNAME}:{self.MONGO_PASSWORD}@"
                f"{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB}")


settings = Settings()
