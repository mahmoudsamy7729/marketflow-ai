from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class PostCreateRequest(BaseModel):
    campaign_id: UUID
    channel: str
    body: str = Field(min_length=1)
    image_urls: list[HttpUrl] | None = None
    scheduled_for: datetime | None = None

    @field_validator("channel", "body")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        return value.strip()


class PostUpdateRequest(BaseModel):
    body: str | None = Field(default=None, min_length=1)
    image_urls: list[HttpUrl] | None = None
    scheduled_for: datetime | None = None
    status: str | None = None

    @field_validator("body", "status")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()


class AttachImageUrlsRequest(BaseModel):
    image_urls: list[HttpUrl] = Field(min_length=1)


class PostImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    storage_type: str
    url: str
    original_filename: str | None
    mime_type: str | None
    sort_order: int


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    campaign_id: UUID
    channel: str
    body: str
    status: str
    scheduled_for: datetime | None
    published_at: datetime | None
    external_post_id: str | None
    error_message: str | None
    images: list[PostImageResponse]
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class PostListResponse(BaseModel):
    posts: list[PostResponse]


class PostMessageResponse(BaseModel):
    message: str
