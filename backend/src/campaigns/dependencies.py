from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from src.channels.dependencies import get_channel_repository
from src.channels.repositories import ChannelRepository
from src.campaigns.repositories import CampaignRepository
from src.campaigns.services import CampaignService
from src.database import db_dependency


def get_campaign_repository(session: db_dependency) -> CampaignRepository:
    return CampaignRepository(session)


def get_campaign_service(
    repository: Annotated[CampaignRepository, Depends(get_campaign_repository)],
    channel_repository: Annotated[ChannelRepository, Depends(get_channel_repository)],
) -> CampaignService:
    return CampaignService(repository, channel_repository)


campaign_service_dependency = Annotated[CampaignService, Depends(get_campaign_service)]
