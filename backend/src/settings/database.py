from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    database_url: str = Field(
        validation_alias=AliasChoices("DATABASE_URL", "database_url"),
    )
    sync_database_url: str = Field(
        validation_alias=AliasChoices("SYNC_DATABASE_URL", "sync_database_url"),
    )
    test_database_url: str = Field(
        validation_alias=AliasChoices("TEST_DATABASE_URL", "test_database_url"),
    )
