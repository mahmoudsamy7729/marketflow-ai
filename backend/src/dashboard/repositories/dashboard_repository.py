from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.campaigns.models import Campaign
from src.channels.models import ChannelConnection
from src.content_plans.models import ContentPlan, ContentPlanItem
from src.posts.models import Post


@dataclass
class DashboardOverviewCounts:
    total_campaigns: int
    active_campaigns: int
    total_posts: int
    draft_posts: int
    scheduled_posts: int
    published_posts: int
    failed_posts: int


class DashboardRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_overview_counts(self, user_id: UUID) -> DashboardOverviewCounts:
        campaign_counts_statement = select(
            func.count(Campaign.id),
            func.count(case((Campaign.status == "active", 1))),
        ).where(
            Campaign.user_id == user_id,
            Campaign.deleted_at.is_(None),
        )
        total_campaigns, active_campaigns = (await self.session.execute(campaign_counts_statement)).one()

        post_counts_statement = select(
            func.count(Post.id),
            func.count(case((Post.status == "draft", 1))),
            func.count(case((Post.status == "scheduled", 1))),
            func.count(case((Post.status == "published", 1))),
            func.count(case((Post.status == "failed", 1))),
        ).where(
            Post.user_id == user_id,
            Post.deleted_at.is_(None),
        )
        total_posts, draft_posts, scheduled_posts, published_posts, failed_posts = (
            await self.session.execute(post_counts_statement)
        ).one()

        return DashboardOverviewCounts(
            total_campaigns=int(total_campaigns or 0),
            active_campaigns=int(active_campaigns or 0),
            total_posts=int(total_posts or 0),
            draft_posts=int(draft_posts or 0),
            scheduled_posts=int(scheduled_posts or 0),
            published_posts=int(published_posts or 0),
            failed_posts=int(failed_posts or 0),
        )

    async def list_connected_channels(self, user_id: UUID) -> list[ChannelConnection]:
        statement = (
            select(ChannelConnection)
            .options(
                selectinload(ChannelConnection.facebook_details),
                selectinload(ChannelConnection.selected_facebook_page),
            )
            .where(
                ChannelConnection.user_id == user_id,
                ChannelConnection.status == "connected",
                ChannelConnection.deleted_at.is_(None),
            )
            .order_by(ChannelConnection.created_at.asc())
        )
        result = await self.session.scalars(statement)
        return list(result.all())

    async def list_upcoming_posts(self, user_id: UUID, now: datetime) -> list[tuple[Post, str]]:
        statement = (
            select(Post, Campaign.name)
            .join(Campaign, Campaign.id == Post.campaign_id)
            .where(
                Post.user_id == user_id,
                Post.deleted_at.is_(None),
                Campaign.deleted_at.is_(None),
                Post.status == "scheduled",
                Post.scheduled_for.is_not(None),
                Post.scheduled_for >= now,
            )
            .order_by(Post.scheduled_for.asc(), Post.created_at.asc())
            .limit(5)
        )
        result = await self.session.execute(statement)
        return list(result.all())

    async def list_recent_activity(self, user_id: UUID) -> list[tuple[Post, str, str, datetime]]:
        activity_type_expr = case(
            (Post.published_at.is_not(None), "published"),
            (Post.status == "failed", "failed"),
            else_="generated",
        )
        occurred_at_expr = case(
            (Post.published_at.is_not(None), Post.published_at),
            (Post.status == "failed", Post.updated_at),
            else_=Post.created_at,
        )
        statement = (
            select(Post, Campaign.name, activity_type_expr.label("activity_type"), occurred_at_expr.label("occurred_at"))
            .join(Campaign, Campaign.id == Post.campaign_id)
            .where(
                Post.user_id == user_id,
                Post.deleted_at.is_(None),
                Campaign.deleted_at.is_(None),
            )
            .order_by(occurred_at_expr.desc(), Post.created_at.desc())
            .limit(10)
        )
        result = await self.session.execute(statement)
        return list(result.all())

    async def list_campaigns_for_health(self, user_id: UUID) -> list[Campaign]:
        statement = (
            select(Campaign)
            .options(selectinload(Campaign.channels))
            .where(
                Campaign.user_id == user_id,
                Campaign.deleted_at.is_(None),
            )
            .order_by(Campaign.updated_at.desc())
        )
        result = await self.session.scalars(statement)
        return list(result.unique().all())

    async def get_active_plan_campaign_ids(self, user_id: UUID) -> set[UUID]:
        statement = select(ContentPlan.campaign_id).where(
            ContentPlan.user_id == user_id,
            ContentPlan.status == "active",
        )
        result = await self.session.scalars(statement)
        return set(result.all())

    async def get_planned_item_counts_for_active_plans(self, user_id: UUID) -> dict[UUID, int]:
        statement = (
            select(ContentPlan.campaign_id, func.count(ContentPlanItem.id))
            .join(ContentPlanItem, ContentPlanItem.content_plan_id == ContentPlan.id)
            .where(
                ContentPlan.user_id == user_id,
                ContentPlan.status == "active",
            )
            .group_by(ContentPlan.campaign_id)
        )
        rows = await self.session.execute(statement)
        return {campaign_id: int(count or 0) for campaign_id, count in rows.all()}

    async def get_post_counts_by_campaign(self, user_id: UUID) -> dict[UUID, dict[str, int]]:
        generated_posts_count = func.count(case((Post.content_plan_item_id.is_not(None), 1)))
        statement = (
            select(
                Post.campaign_id,
                generated_posts_count.label("generated_posts_count"),
                func.count(case((Post.status == "draft", 1))).label("draft_posts_count"),
                func.count(case((Post.status == "scheduled", 1))).label("scheduled_posts_count"),
                func.count(case((Post.status == "published", 1))).label("published_posts_count"),
                func.count(case((Post.status == "failed", 1))).label("failed_posts_count"),
            )
            .where(
                Post.user_id == user_id,
                Post.deleted_at.is_(None),
            )
            .group_by(Post.campaign_id)
        )
        rows = await self.session.execute(statement)
        return {
            campaign_id: {
                "generated_posts_count": int(generated_count or 0),
                "draft_posts_count": int(draft_count or 0),
                "scheduled_posts_count": int(scheduled_count or 0),
                "published_posts_count": int(published_count or 0),
                "failed_posts_count": int(failed_count or 0),
            }
            for (
                campaign_id,
                generated_count,
                draft_count,
                scheduled_count,
                published_count,
                failed_count,
            ) in rows.all()
        }
