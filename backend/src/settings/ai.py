from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings


class AISettings(BaseSettings):
    ai_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("AI_API_KEY", "ai_api_key"),
    )
    ai_base_url: str = Field(
        default="https://api.openai.com/v1",
        validation_alias=AliasChoices("AI_BASE_URL", "ai_base_url"),
    )
    ai_model: str = Field(
        default="gpt-5-mini",
        validation_alias=AliasChoices("AI_MODEL", "ai_model"),
    )

    @field_validator("ai_base_url")
    @classmethod
    def normalize_ai_base_url(cls, value: str) -> str:
        normalized = value.strip()
        return normalized.rstrip("/") or "https://api.openai.com/v1"

    @field_validator("ai_model")
    @classmethod
    def normalize_ai_model(cls, value: str) -> str:
        normalized = value.strip()
        return normalized or "gpt-5-mini"
