from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, status

from src.campaigns.dependencies import campaign_service_dependency
from src.campaigns.schemas import (
    CampaignBulkScheduleRequest,
    CampaignBulkScheduleResponse,
    CampaignCreateRequest,
    CampaignListResponse,
    CampaignMessageResponse,
    CampaignResponse,
    CampaignUpdateRequest,
)
from src.content_plans.dependencies import content_plan_service_dependency
from src.content_plans.schemas import ContentPlanResponse, GeneratePostsFromPlanResponse
from src.dependencies import current_user_dependency
from src.posts.dependencies import post_generation_service_dependency, post_service_dependency


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


@router.post("/{campaign_id}/generate-plan", response_model=ContentPlanResponse)
async def generate_campaign_plan(
    campaign_id: UUID,
    current_user: current_user_dependency,
    service: content_plan_service_dependency,
) -> ContentPlanResponse:
    return await service.generate_plan(current_user, campaign_id)


@router.get("/{campaign_id}/plan", response_model=ContentPlanResponse)
async def get_campaign_plan(
    campaign_id: UUID,
    current_user: current_user_dependency,
    service: content_plan_service_dependency,
) -> ContentPlanResponse:
    return await service.get_active_plan(current_user, campaign_id)


@router.post("/{campaign_id}/generate-posts-from-plan", response_model=GeneratePostsFromPlanResponse)
async def generate_posts_from_plan(
    campaign_id: UUID,
    current_user: current_user_dependency,
    service: post_generation_service_dependency,
) -> GeneratePostsFromPlanResponse:
    return await service.generate_posts_from_plan(current_user, campaign_id)


@router.post("/{campaign_id}/schedule-posts", response_model=CampaignBulkScheduleResponse)
async def schedule_campaign_posts(
    campaign_id: UUID,
    payload: CampaignBulkScheduleRequest,
    current_user: current_user_dependency,
    service: post_service_dependency,
) -> CampaignBulkScheduleResponse:
    posts = await service.schedule_campaign_posts(
        current_user,
        campaign_id,
        time_of_day=payload.time_of_day,
        timezone_name=payload.timezone,
    )
    return CampaignBulkScheduleResponse(
        campaign_id=campaign_id,
        timezone=payload.timezone,
        posts_scheduled=len(posts),
        posts=[service.to_response(post) for post in posts],
    )
