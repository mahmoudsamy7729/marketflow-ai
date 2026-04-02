from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from src.auth.models import User
from src.media_generation import exceptions
from src.media_generation.providers import KieProvider
from src.media_generation.repositories import MediaGenerationRepository
from src.media_generation.schemas import MediaGenerationCallbackResponse, MediaGenerationJobResponse
from src.posts import exceptions as post_exceptions
from src.posts.models import REMOTE_URL_STORAGE_TYPE
from src.posts.repositories import PostRepository


class MediaGenerationService:
    def __init__(
        self,
        repository: MediaGenerationRepository,
        post_repository: PostRepository,
        kie_provider: KieProvider,
    ) -> None:
        self.repository = repository
        self.post_repository = post_repository
        self.kie_provider = kie_provider

    async def generate_image_for_post(self, user: User, post_id: UUID) -> MediaGenerationJobResponse:
        post = await self.post_repository.get_post_by_id_for_user(post_id, user.id)
        if post is None:
            raise post_exceptions.PostNotFound()

        prompt = (post.image_prompt or "").strip()
        if not prompt:
            raise exceptions.MediaGenerationPromptMissing()

        job = await self.repository.create_image_job(
            user_id=user.id,
            post_id=post.id,
            prompt=prompt,
        )
        try:
            external_job_id = await self.kie_provider.create_image_task(
                prompt=prompt,
                channel=post.channel,
            )
        except exceptions.MediaGenerationConfigurationError as exc:
            await self.repository.mark_job_failed(job, error_message=exc.message)
            raise
        except exceptions.MediaGenerationSubmissionFailed as exc:
            await self.repository.mark_job_failed(job, error_message=exc.message)
            raise

        job = await self.repository.mark_job_submitted(job, external_job_id=external_job_id)
        return self._to_response(job)

    async def get_job(self, user: User, job_id: UUID) -> MediaGenerationJobResponse:
        job = await self.repository.get_job_by_id_for_user(job_id, user.id)
        if job is None:
            raise exceptions.MediaGenerationJobNotFound()
        return self._to_response(job)

    async def handle_kie_callback(self, payload: dict) -> MediaGenerationCallbackResponse:
        external_job_id = self.kie_provider.extract_callback_task_id(payload)
        if not external_job_id:
            raise exceptions.MediaGenerationCallbackTaskMissing()

        job = await self.repository.get_job_by_external_job_id(external_job_id)
        if job is None:
            raise exceptions.MediaGenerationJobNotFound()

        if job.status == "completed":
            return MediaGenerationCallbackResponse(message="Callback already processed.")

        task_details = await self.kie_provider.get_task_details(task_id=external_job_id)

        if self.kie_provider.is_success_task_details(task_details):
            result_url = self.kie_provider.extract_task_result_url(task_details)
            if not result_url:
                error_message = self.kie_provider.extract_task_error_message(task_details) or "Kie task details did not include a result image URL."
                await self.repository.mark_job_failed(job, error_message=error_message)
                return MediaGenerationCallbackResponse(message="Callback processed as failed.")

            post = await self.post_repository.get_post_by_id(job.post_id)
            if post is not None:
                await self.post_repository.append_post_images_if_missing(
                    post,
                    [
                        {
                            "storage_type": REMOTE_URL_STORAGE_TYPE,
                            "file_url": result_url,
                            "file_path": None,
                            "original_filename": None,
                            "mime_type": None,
                        }
                    ],
                )
            await self.repository.mark_job_completed(
                job,
                result_url=result_url,
                completed_at=datetime.now(timezone.utc),
            )
            return MediaGenerationCallbackResponse(message="Callback processed successfully.")

        error_message = self.kie_provider.extract_task_error_message(task_details) or self.kie_provider.extract_callback_error_message(payload) or "Kie media generation failed."
        await self.repository.mark_job_failed(job, error_message=error_message)
        return MediaGenerationCallbackResponse(message="Callback processed as failed.")

    def _to_response(self, job) -> MediaGenerationJobResponse:
        return MediaGenerationJobResponse.model_validate(job)
