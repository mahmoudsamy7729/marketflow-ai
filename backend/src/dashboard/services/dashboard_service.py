from __future__ import annotations

from datetime import datetime, timezone

from src.auth.models import User
from src.dashboard.repositories import DashboardRepository
from src.dashboard.schemas import (
    DashboardCampaignHealthResponse,
    DashboardConnectedChannelResponse,
    DashboardOverviewResponse,
    DashboardRecentActivityResponse,
    DashboardResponse,
    DashboardUpcomingPostResponse,
)


class DashboardService:
    def __init__(self, repository: DashboardRepository) -> None:
        self.repository = repository

    async def get_dashboard(self, user: User) -> DashboardResponse:
        now = datetime.now(timezone.utc)
        overview_counts = await self.repository.get_overview_counts(user.id)
        connected_channels = await self.repository.list_connected_channels(user.id)
        upcoming_posts = await self.repository.list_upcoming_posts(user.id, now)
        recent_activity = await self.repository.list_recent_activity(user.id)
        campaigns = await self.repository.list_campaigns_for_health(user.id)
        active_plan_campaign_ids = await self.repository.get_active_plan_campaign_ids(user.id)
        planned_item_counts = await self.repository.get_planned_item_counts_for_active_plans(user.id)
        post_counts_by_campaign = await self.repository.get_post_counts_by_campaign(user.id)

        return DashboardResponse(
            overview=DashboardOverviewResponse(**overview_counts.__dict__),
            connected_channels=[
                DashboardConnectedChannelResponse(
                    channel=connection.provider,
                    status=connection.status,
                    connected_at=connection.created_at,
                    account_display_name=(
                        connection.facebook_details.display_name
                        if connection.provider == "facebook" and connection.facebook_details is not None
                        else None
                    ),
                    selected_target_name=(
                        connection.selected_facebook_page.page_name
                        if connection.provider == "facebook" and connection.selected_facebook_page is not None
                        else None
                    ),
                )
                for connection in connected_channels
            ],
            upcoming_posts=[
                DashboardUpcomingPostResponse(
                    id=post.id,
                    campaign_id=post.campaign_id,
                    campaign_name=campaign_name,
                    channel=post.channel,
                    scheduled_for=post.scheduled_for,
                    status=post.status,
                    body_preview=self._body_preview(post.body),
                )
                for post, campaign_name in upcoming_posts
                if post.scheduled_for is not None
            ],
            recent_activity=[
                DashboardRecentActivityResponse(
                    post_id=post.id,
                    campaign_id=post.campaign_id,
                    campaign_name=campaign_name,
                    channel=post.channel,
                    activity_type=activity_type,
                    occurred_at=occurred_at,
                    body_preview=self._body_preview(post.body),
                )
                for post, campaign_name, activity_type, occurred_at in recent_activity
                if occurred_at is not None
            ],
            campaign_health=[
                DashboardCampaignHealthResponse(
                    campaign_id=campaign.id,
                    name=campaign.name,
                    status=campaign.status,
                    start_date=campaign.start_date,
                    end_date=campaign.end_date,
                    channels=[channel.channel for channel in campaign.channels],
                    has_active_plan=campaign.id in active_plan_campaign_ids,
                    planned_items_count=planned_item_counts.get(campaign.id, 0),
                    generated_posts_count=post_counts_by_campaign.get(campaign.id, {}).get("generated_posts_count", 0),
                    draft_posts_count=post_counts_by_campaign.get(campaign.id, {}).get("draft_posts_count", 0),
                    scheduled_posts_count=post_counts_by_campaign.get(campaign.id, {}).get("scheduled_posts_count", 0),
                    published_posts_count=post_counts_by_campaign.get(campaign.id, {}).get("published_posts_count", 0),
                    failed_posts_count=post_counts_by_campaign.get(campaign.id, {}).get("failed_posts_count", 0),
                )
                for campaign in campaigns
            ],
        )

    def _body_preview(self, body: str) -> str:
        compact_body = " ".join(body.split())
        if len(compact_body) <= 120:
            return compact_body
        return f"{compact_body[:117]}..."
