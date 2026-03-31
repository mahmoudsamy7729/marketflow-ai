from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    app_name: str = Field(
        default="FastAPI Auth System",
        validation_alias=AliasChoices("APP_NAME", "app_name"),
    )
    app_env: str = Field(
        default="development",
        validation_alias=AliasChoices("APP_ENV", "app_env"),
    )
    app_debug: bool = Field(
        default=True,
        validation_alias=AliasChoices("APP_DEBUG", "app_debug"),
    )
    app_url: str = Field(
        default="http://localhost:8000",
        validation_alias=AliasChoices("APP_URL", "app_url"),
    )
    frontend_url: str = Field(
        default="http://localhost:3000",
        validation_alias=AliasChoices("FRONTEND_URL", "frontend_url"),
    )
