from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from src.campaigns.repositories import CampaignRepository
from src.campaigns.services import CampaignService
from src.database import db_dependency


def get_campaign_repository(session: db_dependency) -> CampaignRepository:
    return CampaignRepository(session)


def get_campaign_service(
    repository: Annotated[CampaignRepository, Depends(get_campaign_repository)],
) -> CampaignService:
    return CampaignService(repository)


campaign_service_dependency = Annotated[CampaignService, Depends(get_campaign_service)]
