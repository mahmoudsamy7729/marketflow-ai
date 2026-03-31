from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.campaigns.models import Campaign, CampaignTargetChannel


class CampaignRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _base_statement(self):
        return select(Campaign).options(selectinload(Campaign.channels))

    async def create_campaign(
        self,
        *,
        user_id: UUID,
        name: str,
        start_date: date,
        end_date: date,
        posts_per_interval: int,
        interval_days: int,
        goal: str,
        hook_style: str,
        tone: str,
        target_audience: str,
        notes: str | None,
        status: str,
        channels: list[str],
    ) -> Campaign:
        campaign = Campaign(
            user_id=user_id,
            name=name,
            start_date=start_date,
            end_date=end_date,
            posts_per_interval=posts_per_interval,
            interval_days=interval_days,
            goal=goal,
            hook_style=hook_style,
            tone=tone,
            target_audience=target_audience,
            notes=notes,
            status=status,
            channels=[CampaignTargetChannel(channel=channel) for channel in channels],
        )
        self.session.add(campaign)
        await self.session.commit()
        return await self.get_campaign_by_id_for_user(campaign.id, user_id)

    async def list_campaigns_by_user(self, user_id: UUID) -> list[Campaign]:
        statement = (
            self._base_statement()
            .where(
                Campaign.user_id == user_id,
                Campaign.deleted_at.is_(None),
            )
            .order_by(Campaign.created_at.desc())
        )
        result = await self.session.scalars(statement)
        return list(result.unique().all())

    async def get_campaign_by_id_for_user(
        self,
        campaign_id: UUID,
        user_id: UUID,
    ) -> Campaign | None:
        statement = self._base_statement().where(
            Campaign.id == campaign_id,
            Campaign.user_id == user_id,
            Campaign.deleted_at.is_(None),
        )
        return await self.session.scalar(statement)

    async def update_campaign(
        self,
        campaign: Campaign,
        *,
        name: str | None,
        start_date: date | None,
        end_date: date | None,
        posts_per_interval: int | None,
        interval_days: int | None,
        goal: str | None,
        hook_style: str | None,
        tone: str | None,
        target_audience: str | None,
        notes: str | None,
        status: str | None,
        channels: list[str] | None,
    ) -> Campaign:
        if name is not None:
            campaign.name = name
        if start_date is not None:
            campaign.start_date = start_date
        if end_date is not None:
            campaign.end_date = end_date
        if posts_per_interval is not None:
            campaign.posts_per_interval = posts_per_interval
        if interval_days is not None:
            campaign.interval_days = interval_days
        if goal is not None:
            campaign.goal = goal
        if hook_style is not None:
            campaign.hook_style = hook_style
        if tone is not None:
            campaign.tone = tone
        if target_audience is not None:
            campaign.target_audience = target_audience
        if notes is not None:
            campaign.notes = notes
        if status is not None:
            campaign.status = status
        if channels is not None:
            campaign.channels.clear()
            campaign.channels.extend(
                CampaignTargetChannel(channel=channel)
                for channel in channels
            )

        await self.session.commit()
        return await self.get_campaign_by_id_for_user(campaign.id, campaign.user_id)

    async def soft_delete_campaign(self, campaign: Campaign) -> Campaign:
        campaign.deleted_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(campaign)
        return campaign
