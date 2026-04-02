from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MediaGenerationJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    post_id: UUID
    user_id: UUID
    provider: str
    media_type: str
    status: str
    prompt: str
    external_job_id: str | None
    result_url: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None


class MediaGenerationCallbackResponse(BaseModel):
    message: str


class KieCallbackPayload(BaseModel):
    code: int | None = None
    msg: str | None = None
    taskId: str | None = None
    data: dict[str, Any] | None = None
