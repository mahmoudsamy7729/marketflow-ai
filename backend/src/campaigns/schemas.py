from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator
from src.posts.schemas import PostResponse


class CampaignCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    start_date: date
    end_date: date
    posts_per_interval: int = Field(ge=1)
    interval_days: int = Field(ge=1)
    goal: str = Field(min_length=1)
    hook_style: str = Field(min_length=1)
    tone: str = Field(min_length=1)
    target_audience: str = Field(min_length=1)
    notes: str | None = None
    channels: list[str]

    @field_validator("name", "goal", "hook_style", "tone", "target_audience", "notes")
    @classmethod
    def strip_text_fields(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()


class CampaignUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    start_date: date | None = None
    end_date: date | None = None
    posts_per_interval: int | None = Field(default=None, ge=1)
    interval_days: int | None = Field(default=None, ge=1)
    goal: str | None = Field(default=None, min_length=1)
    hook_style: str | None = Field(default=None, min_length=1)
    tone: str | None = Field(default=None, min_length=1)
    target_audience: str | None = Field(default=None, min_length=1)
    notes: str | None = None
    status: str | None = None
    channels: list[str] | None = None

    @field_validator("name", "goal", "hook_style", "tone", "target_audience", "notes", "status")
    @classmethod
    def strip_optional_text_fields(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()


class CampaignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    start_date: date
    end_date: date
    posts_per_interval: int
    interval_days: int
    goal: str
    hook_style: str
    tone: str
    target_audience: str
    notes: str | None
    status: str
    channels: list[str]
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class CampaignListResponse(BaseModel):
    campaigns: list[CampaignResponse]


class CampaignMessageResponse(BaseModel):
    message: str


class CampaignBulkScheduleRequest(BaseModel):
    time_of_day: str = Field(min_length=4, max_length=8)
    timezone: str = Field(min_length=1, max_length=128)

    @field_validator("time_of_day", "timezone")
    @classmethod
    def strip_schedule_fields(cls, value: str) -> str:
        return value.strip()


class CampaignBulkScheduleResponse(BaseModel):
    campaign_id: UUID
    timezone: str
    posts_scheduled: int
    posts: list[PostResponse]
