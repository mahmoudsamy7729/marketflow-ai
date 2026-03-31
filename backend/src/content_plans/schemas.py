from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.posts.schemas import PostResponse


class ContentPlanItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    content_plan_id: UUID
    campaign_id: UUID
    user_id: UUID
    channel: str
    sequence_order: int
    day_number: int
    planned_for: date
    content_type: str
    topic: str
    angle: str
    goal: str
    funnel_stage: str
    status: str
    created_at: datetime
    updated_at: datetime


class ContentPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    campaign_id: UUID
    user_id: UUID
    status: str
    items: list[ContentPlanItemResponse]
    created_at: datetime
    updated_at: datetime


class UpdateContentPlanItemRequest(BaseModel):
    planned_for: date | None = None
    content_type: str | None = Field(default=None, min_length=1)
    topic: str | None = Field(default=None, min_length=1)
    angle: str | None = Field(default=None, min_length=1)
    goal: str | None = Field(default=None, min_length=1)
    funnel_stage: str | None = Field(default=None, min_length=1)
    status: str | None = None

    @field_validator("content_type", "topic", "angle", "goal", "funnel_stage", "status")
    @classmethod
    def strip_optional_text_fields(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()


class GeneratePostsFromPlanResponse(BaseModel):
    campaign_id: UUID
    posts_created: int
    posts: list[PostResponse]
