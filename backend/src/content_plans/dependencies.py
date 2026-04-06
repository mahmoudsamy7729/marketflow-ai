from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from src.ai_settings.dependencies import user_ai_settings_service_dependency
from src.content_plans.repositories import ContentPlanRepository
from src.content_plans.services import ContentPlanService
from src.dependencies import current_user_dependency
from src.database import db_dependency


def get_content_plan_repository(session: db_dependency) -> ContentPlanRepository:
    return ContentPlanRepository(session)


async def get_content_plan_service(
    repository: Annotated[ContentPlanRepository, Depends(get_content_plan_repository)],
    current_user: current_user_dependency,
    ai_settings_service: user_ai_settings_service_dependency,
) -> ContentPlanService:
    resolved_config = await ai_settings_service.resolve_generation_config(current_user)
    return ContentPlanService(repository, resolved_config.client, resolved_config.model)


content_plan_service_dependency = Annotated[ContentPlanService, Depends(get_content_plan_service)]
