from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings


class PostsSettings(BaseSettings):
    post_upload_dir: str = Field(
        default="uploads/posts",
        validation_alias=AliasChoices("POST_UPLOAD_DIR", "post_upload_dir"),
    )
    post_media_url_prefix: str = Field(
        default="/media/posts",
        validation_alias=AliasChoices("POST_MEDIA_URL_PREFIX", "post_media_url_prefix"),
    )

    @field_validator("post_upload_dir")
    @classmethod
    def normalize_post_upload_dir(cls, value: str) -> str:
        normalized = value.strip()
        return normalized or "uploads/posts"

    @field_validator("post_media_url_prefix")
    @classmethod
    def normalize_post_media_url_prefix(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            return "/media/posts"
        if not normalized.startswith("/"):
            normalized = f"/{normalized}"
        return normalized.rstrip("/") or "/media/posts"
