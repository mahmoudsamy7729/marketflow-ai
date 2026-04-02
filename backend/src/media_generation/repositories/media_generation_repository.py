from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.media_generation.models import (
    MEDIA_GENERATION_PROVIDER_KIE,
    MEDIA_GENERATION_TYPE_IMAGE,
    MediaGenerationJob,
)


class MediaGenerationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_image_job(
        self,
        *,
        user_id: UUID,
        post_id: UUID,
        prompt: str,
    ) -> MediaGenerationJob:
        job = MediaGenerationJob(
            user_id=user_id,
            post_id=post_id,
            provider=MEDIA_GENERATION_PROVIDER_KIE,
            media_type=MEDIA_GENERATION_TYPE_IMAGE,
            status="queued",
            prompt=prompt,
        )
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def get_job_by_id_for_user(self, job_id: UUID, user_id: UUID) -> MediaGenerationJob | None:
        statement = select(MediaGenerationJob).where(
            MediaGenerationJob.id == job_id,
            MediaGenerationJob.user_id == user_id,
        )
        return await self.session.scalar(statement)

    async def get_job_by_external_job_id(self, external_job_id: str) -> MediaGenerationJob | None:
        statement = select(MediaGenerationJob).where(MediaGenerationJob.external_job_id == external_job_id)
        return await self.session.scalar(statement)

    async def mark_job_submitted(self, job: MediaGenerationJob, *, external_job_id: str) -> MediaGenerationJob:
        job.status = "submitted"
        job.external_job_id = external_job_id
        job.error_message = None
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def mark_job_completed(
        self,
        job: MediaGenerationJob,
        *,
        result_url: str,
        completed_at: datetime,
    ) -> MediaGenerationJob:
        job.status = "completed"
        job.result_url = result_url
        job.error_message = None
        job.completed_at = completed_at
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def mark_job_failed(self, job: MediaGenerationJob, *, error_message: str) -> MediaGenerationJob:
        job.status = "failed"
        job.error_message = error_message
        await self.session.commit()
        await self.session.refresh(job)
        return job
