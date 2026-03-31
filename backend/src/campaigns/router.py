from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, status

from src.campaigns.dependencies import campaign_service_dependency
from src.campaigns.schemas import (
    CampaignCreateRequest,
    CampaignListResponse,
    CampaignMessageResponse,
    CampaignResponse,
    CampaignUpdateRequest,
)
from src.dependencies import current_user_dependency


router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    payload: CampaignCreateRequest,
    current_user: current_user_dependency,
    service: campaign_service_dependency,
) -> CampaignResponse:
    return await service.create_campaign(current_user, payload)


@router.get("", response_model=CampaignListResponse)
async def list_campaigns(
    current_user: current_user_dependency,
    service: campaign_service_dependency,
) -> CampaignListResponse:
    return await service.list_campaigns(current_user)


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: UUID,
    current_user: current_user_dependency,
    service: campaign_service_dependency,
) -> CampaignResponse:
    return await service.get_campaign(current_user, campaign_id)


@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: UUID,
    payload: CampaignUpdateRequest,
    current_user: current_user_dependency,
    service: campaign_service_dependency,
) -> CampaignResponse:
    return await service.update_campaign(current_user, campaign_id, payload)


@router.delete("/{campaign_id}", response_model=CampaignMessageResponse)
async def delete_campaign(
    campaign_id: UUID,
    current_user: current_user_dependency,
    service: campaign_service_dependency,
) -> CampaignMessageResponse:
    return await service.delete_campaign(current_user, campaign_id)
