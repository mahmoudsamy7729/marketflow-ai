from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter

from src.dependencies import current_user_dependency
from src.media_generation.dependencies import media_generation_service_dependency
from src.media_generation.schemas import MediaGenerationCallbackResponse, MediaGenerationJobResponse


router = APIRouter(prefix="/media-generation", tags=["media-generation"])


@router.get("/jobs/{job_id}", response_model=MediaGenerationJobResponse)
async def get_media_generation_job(
    job_id: UUID,
    current_user: current_user_dependency,
    service: media_generation_service_dependency,
) -> MediaGenerationJobResponse:
    return await service.get_job(current_user, job_id)


@router.post("/kie/callback", response_model=MediaGenerationCallbackResponse)
async def handle_kie_callback(
    payload: dict[str, Any],
    service: media_generation_service_dependency,
) -> MediaGenerationCallbackResponse:
    return await service.handle_kie_callback(payload)
