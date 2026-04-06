from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.ai_settings.models import OPENAI_PROVIDER


class UserAISettingsResponse(BaseModel):
    provider: str
    provider_display_name: str | None = None
    has_api_key: bool
    api_key_last4: str | None = None
    is_active: bool


class UpdateUserAISettingsRequest(BaseModel):
    provider: str = Field(default=OPENAI_PROVIDER)
    api_key: str = Field(min_length=1, max_length=512)

    @field_validator("provider")
    @classmethod
    def normalize_provider(cls, value: str) -> str:
        normalized = value.strip().lower()
        return normalized or OPENAI_PROVIDER

    @field_validator("api_key")
    @classmethod
    def normalize_api_key(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("API key is required.")
        return normalized


class AISettingsMessageResponse(BaseModel):
    message: str


class AIProviderConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    provider: str
    display_name: str
    base_url: str
    model: str
    is_enabled: bool
    created_at: datetime
    updated_at: datetime


class AIProviderConfigListResponse(BaseModel):
    providers: list[AIProviderConfigResponse]


class UpsertAIProviderConfigRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=100)
    base_url: str = Field(min_length=1, max_length=500)
    model: str = Field(min_length=1, max_length=255)
    is_enabled: bool = True

    @field_validator("display_name", "model")
    @classmethod
    def normalize_trimmed_fields(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("This field is required.")
        return normalized

    @field_validator("base_url")
    @classmethod
    def normalize_base_url(cls, value: str) -> str:
        normalized = value.strip().rstrip("/")
        if not normalized:
            raise ValueError("Base URL is required.")
        return normalized
