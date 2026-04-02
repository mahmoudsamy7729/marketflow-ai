from __future__ import annotations

from src.common.exceptions import AppException


class MediaGenerationConfigurationError(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="media_generation_configuration_error",
            message="Media generation is not configured correctly.",
            status_code=500,
        )


class MediaGenerationJobNotFound(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="media_generation_job_not_found",
            message="Media generation job not found.",
            status_code=404,
        )


class MediaGenerationPromptMissing(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="media_generation_prompt_missing",
            message="This post does not have an image prompt to generate media from.",
            status_code=400,
        )


class MediaGenerationSubmissionFailed(AppException):
    def __init__(self, message: str | None = None, extra: dict | None = None) -> None:
        super().__init__(
            code="media_generation_submission_failed",
            message=message or "Submitting the media generation task failed.",
            status_code=502,
            extra=extra,
        )


class MediaGenerationCallbackTaskMissing(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="media_generation_callback_task_missing",
            message="The media generation callback payload is missing a task identifier.",
            status_code=400,
        )
