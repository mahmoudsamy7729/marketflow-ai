from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings


class MediaGenerationSettings(BaseSettings):
    kie_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("KIE_API_KEY", "kie_api_key"),
    )
    kie_base_url: str = Field(
        default="https://api.kie.ai",
        validation_alias=AliasChoices("KIE_BASE_URL", "kie_base_url"),
    )
    kie_image_model: str = Field(
        default="nano-banana-2",
        validation_alias=AliasChoices("KIE_IMAGE_MODEL", "kie_image_model"),
    )
    kie_callback_url: str = Field(
        default="",
        validation_alias=AliasChoices("KIE_CALLBACK_URL", "kie_callback_url"),
    )

    @field_validator("kie_base_url")
    @classmethod
    def normalize_kie_base_url(cls, value: str) -> str:
        normalized = value.strip()
        return normalized.rstrip("/") or "https://api.kie.ai"

    @field_validator("kie_image_model")
    @classmethod
    def normalize_kie_image_model(cls, value: str) -> str:
        normalized = value.strip()
        return normalized or "nano-banana-2"

    @field_validator("kie_callback_url")
    @classmethod
    def normalize_kie_callback_url(cls, value: str) -> str:
        return value.strip()
