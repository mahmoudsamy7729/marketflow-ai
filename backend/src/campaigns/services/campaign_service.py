from __future__ import annotations

from datetime import date
from uuid import UUID

from src.auth.models import User
from src.campaigns import exceptions
from src.campaigns.models import (
    ALLOWED_CAMPAIGN_CHANNELS,
    ALLOWED_CAMPAIGN_STATUSES,
    Campaign,
)
from src.campaigns.repositories import CampaignRepository
from src.campaigns.schemas import (
    CampaignCreateRequest,
    CampaignListResponse,
    CampaignMessageResponse,
    CampaignResponse,
    CampaignUpdateRequest,
)


DEFAULT_CAMPAIGN_STATUS = "draft"


class CampaignService:
    def __init__(self, repository: CampaignRepository) -> None:
        self.repository = repository

    async def create_campaign(
        self,
        user: User,
        payload: CampaignCreateRequest,
    ) -> CampaignResponse:
        channels = self._normalize_channels(payload.channels)
        self._validate_date_range(payload.start_date, payload.end_date)

        campaign = await self.repository.create_campaign(
            user_id=user.id,
            name=payload.name.strip(),
            start_date=payload.start_date,
            end_date=payload.end_date,
            goal=payload.goal.strip(),
            hook_style=payload.hook_style.strip(),
            tone=payload.tone.strip(),
            target_audience=payload.target_audience.strip(),
            notes=payload.notes.strip() if payload.notes else None,
            status=DEFAULT_CAMPAIGN_STATUS,
            channels=channels,
        )
        return self._to_response(campaign)

    async def list_campaigns(self, user: User) -> CampaignListResponse:
        campaigns = await self.repository.list_campaigns_by_user(user.id)
        return CampaignListResponse(
            campaigns=[self._to_response(campaign) for campaign in campaigns],
        )

    async def get_campaign(self, user: User, campaign_id: UUID) -> CampaignResponse:
        campaign = await self.repository.get_campaign_by_id_for_user(campaign_id, user.id)
        if campaign is None:
            raise exceptions.CampaignNotFound()

        return self._to_response(campaign)

    async def update_campaign(
        self,
        user: User,
        campaign_id: UUID,
        payload: CampaignUpdateRequest,
    ) -> CampaignResponse:
        campaign = await self.repository.get_campaign_by_id_for_user(campaign_id, user.id)
        if campaign is None:
            raise exceptions.CampaignNotFound()

        next_start_date = payload.start_date or campaign.start_date
        next_end_date = payload.end_date or campaign.end_date
        self._validate_date_range(next_start_date, next_end_date)

        channels = None
        if payload.channels is not None:
            channels = self._normalize_channels(payload.channels)

        status = None
        if payload.status is not None:
            status = self._normalize_status(payload.status)

        updated_campaign = await self.repository.update_campaign(
            campaign,
            name=payload.name.strip() if payload.name else None,
            start_date=payload.start_date,
            end_date=payload.end_date,
            goal=payload.goal.strip() if payload.goal else None,
            hook_style=payload.hook_style.strip() if payload.hook_style else None,
            tone=payload.tone.strip() if payload.tone else None,
            target_audience=payload.target_audience.strip() if payload.target_audience else None,
            notes=payload.notes.strip() if payload.notes else None,
            status=status,
            channels=channels,
        )
        return self._to_response(updated_campaign)

    async def delete_campaign(self, user: User, campaign_id: UUID) -> CampaignMessageResponse:
        campaign = await self.repository.get_campaign_by_id_for_user(campaign_id, user.id)
        if campaign is None:
            raise exceptions.CampaignNotFound()

        await self.repository.soft_delete_campaign(campaign)
        return CampaignMessageResponse(message="Campaign deleted successfully.")

    def _normalize_channels(self, channels: list[str]) -> list[str]:
        normalized_channels: list[str] = []
        seen: set[str] = set()

        for channel in channels:
            normalized = channel.strip().lower()
            if not normalized:
                continue
            if normalized not in ALLOWED_CAMPAIGN_CHANNELS:
                raise exceptions.CampaignChannelInvalid(normalized)
            if normalized in seen:
                continue

            seen.add(normalized)
            normalized_channels.append(normalized)

        if not normalized_channels:
            raise exceptions.CampaignChannelsRequired()

        return normalized_channels

    def _normalize_status(self, status: str) -> str:
        normalized = status.strip().lower()
        if normalized not in ALLOWED_CAMPAIGN_STATUSES:
            raise exceptions.CampaignStatusInvalid(normalized)
        return normalized

    def _validate_date_range(self, start_date: date, end_date: date) -> None:
        if start_date > end_date:
            raise exceptions.CampaignDateRangeInvalid()

    def _to_response(self, campaign: Campaign) -> CampaignResponse:
        return CampaignResponse(
            id=campaign.id,
            user_id=campaign.user_id,
            name=campaign.name,
            start_date=campaign.start_date,
            end_date=campaign.end_date,
            goal=campaign.goal,
            hook_style=campaign.hook_style,
            tone=campaign.tone,
            target_audience=campaign.target_audience,
            notes=campaign.notes,
            status=campaign.status,
            channels=[channel.channel for channel in campaign.channels],
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            deleted_at=campaign.deleted_at,
        )
