from pathlib import Path

from pydantic_settings import SettingsConfigDict

from src.settings.app import AppSettings
from src.settings.auth import AuthSettings
from src.settings.database import DatabaseSettings
from src.settings.facebook import FacebookSettings
from src.settings.n8n import N8NSettings
from src.settings.posts import PostsSettings


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(
    AppSettings,
    DatabaseSettings,
    AuthSettings,
    FacebookSettings,
    N8NSettings,
    PostsSettings,
):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
