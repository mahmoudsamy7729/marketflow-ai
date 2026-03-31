from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from src.content_plans.dependencies import content_plan_service_dependency
from src.content_plans.schemas import ContentPlanItemResponse, UpdateContentPlanItemRequest
from src.dependencies import current_user_dependency


router = APIRouter(tags=["content-plans"])


@router.patch("/content-plan-items/{item_id}", response_model=ContentPlanItemResponse)
async def update_content_plan_item(
    item_id: UUID,
    payload: UpdateContentPlanItemRequest,
    current_user: current_user_dependency,
    service: content_plan_service_dependency,
) -> ContentPlanItemResponse:
    return await service.update_plan_item(current_user, item_id, payload)
