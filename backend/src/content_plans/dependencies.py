from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from openai import AsyncOpenAI

from src.config import settings
from src.content_plans import exceptions
from src.content_plans.repositories import ContentPlanRepository
from src.content_plans.services import ContentPlanService
from src.database import db_dependency


def get_content_plan_repository(session: db_dependency) -> ContentPlanRepository:
    return ContentPlanRepository(session)


def get_content_plan_openai_client() -> AsyncOpenAI:
    if not settings.ai_api_key or not settings.ai_model or not settings.ai_base_url:
        raise exceptions.ContentPlanGenerationConfigurationError()
    return AsyncOpenAI(api_key=settings.ai_api_key, base_url=settings.ai_base_url)


def get_content_plan_service(
    repository: Annotated[ContentPlanRepository, Depends(get_content_plan_repository)],
    client: Annotated[AsyncOpenAI, Depends(get_content_plan_openai_client)],
) -> ContentPlanService:
    return ContentPlanService(repository, client, settings.ai_model)


content_plan_service_dependency = Annotated[ContentPlanService, Depends(get_content_plan_service)]
