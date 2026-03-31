from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class DashboardOverviewResponse(BaseModel):
    total_campaigns: int
    active_campaigns: int
    total_posts: int
    draft_posts: int
    scheduled_posts: int
    published_posts: int
    failed_posts: int


class DashboardConnectedChannelResponse(BaseModel):
    channel: str
    status: str
    connected_at: datetime
    account_display_name: str | None
    selected_target_name: str | None


class DashboardUpcomingPostResponse(BaseModel):
    id: UUID
    campaign_id: UUID
    campaign_name: str
    channel: str
    scheduled_for: datetime
    status: str
    body_preview: str


class DashboardRecentActivityResponse(BaseModel):
    post_id: UUID
    campaign_id: UUID
    campaign_name: str
    channel: str
    activity_type: str
    occurred_at: datetime
    body_preview: str


class DashboardCampaignHealthResponse(BaseModel):
    campaign_id: UUID
    name: str
    status: str
    start_date: date
    end_date: date
    channels: list[str]
    has_active_plan: bool
    planned_items_count: int
    generated_posts_count: int
    draft_posts_count: int
    scheduled_posts_count: int
    published_posts_count: int
    failed_posts_count: int


class DashboardResponse(BaseModel):
    overview: DashboardOverviewResponse
    connected_channels: list[DashboardConnectedChannelResponse]
    upcoming_posts: list[DashboardUpcomingPostResponse]
    recent_activity: list[DashboardRecentActivityResponse]
    campaign_health: list[DashboardCampaignHealthResponse]
