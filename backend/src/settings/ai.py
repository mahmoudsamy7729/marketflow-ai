import base64
import hashlib

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings


class AISettings(BaseSettings):
    ai_encryption_key: str = Field(
        default="",
        validation_alias=AliasChoices("AI_ENCRYPTION_KEY", "ai_encryption_key"),
    )

    @field_validator("ai_encryption_key")
    @classmethod
    def normalize_ai_encryption_key(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            return ""

        try:
            base64.urlsafe_b64decode(normalized.encode("utf-8"))
            return normalized
        except Exception:
            digest = hashlib.sha256(normalized.encode("utf-8")).digest()
            return base64.urlsafe_b64encode(digest).decode("utf-8")
