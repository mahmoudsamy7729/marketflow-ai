from __future__ import annotations

from src.common.exceptions import AppException


class PostNotFound(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="post_not_found",
            message="Post not found.",
            status_code=404,
        )


class PostCampaignNotFound(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="post_campaign_not_found",
            message="Campaign not found for this post.",
            status_code=404,
        )


class PostChannelInvalid(AppException):
    def __init__(self, channel: str) -> None:
        super().__init__(
            code="post_channel_invalid",
            message="The post contains an unsupported channel.",
            status_code=400,
            extra={"channel": channel},
        )


class PostChannelNotAllowedForCampaign(AppException):
    def __init__(self, channel: str) -> None:
        super().__init__(
            code="post_channel_not_allowed_for_campaign",
            message="The selected channel is not targeted by the campaign.",
            status_code=400,
            extra={"channel": channel},
        )


class PostStatusInvalid(AppException):
    def __init__(self, status: str) -> None:
        super().__init__(
            code="post_status_invalid",
            message="The post contains an unsupported status.",
            status_code=400,
            extra={"status": status},
        )


class PostStatusNotEditable(AppException):
    def __init__(self, status: str) -> None:
        super().__init__(
            code="post_status_not_editable",
            message="Only draft and scheduled statuses can be set manually.",
            status_code=400,
            extra={"status": status},
        )


class PostPublishNowStatusInvalid(AppException):
    def __init__(self, status: str) -> None:
        super().__init__(
            code="post_publish_now_status_invalid",
            message="Only draft and scheduled posts can be published immediately.",
            status_code=400,
            extra={"status": status},
        )


class PostPublishNowChannelUnsupported(AppException):
    def __init__(self, channel: str) -> None:
        super().__init__(
            code="post_publish_now_channel_unsupported",
            message="Publish now is not supported for this post channel.",
            status_code=400,
            extra={"channel": channel},
        )


class PostPublishNowFailed(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="post_publish_now_failed",
            message="Publishing the post now failed.",
            status_code=502,
        )


class PostInstagramTargetNotConfigured(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="post_instagram_target_not_configured",
            message="No linked Instagram professional account was found on the selected Facebook page.",
            status_code=400,
        )


class PostInstagramMediaRequired(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="post_instagram_media_required",
            message="Instagram posts require media.",
            status_code=400,
        )


class PostInstagramMediaCountUnsupported(AppException):
    def __init__(self, count: int) -> None:
        super().__init__(
            code="post_instagram_media_count_unsupported",
            message="Instagram publish now supports exactly one image in v1.",
            status_code=400,
            extra={"image_count": count},
        )


class PostInstagramMediaSourceUnsupported(AppException):
    def __init__(self, storage_type: str) -> None:
        super().__init__(
            code="post_instagram_media_source_unsupported",
            message="Instagram publish now only supports remote image URLs in v1.",
            status_code=400,
            extra={"storage_type": storage_type},
        )


class PostImageNotFound(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="post_image_not_found",
            message="Post image not found.",
            status_code=404,
        )


class PostsGenerationConfigurationError(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="posts_generation_configuration_error",
            message="AI post generation is not configured correctly.",
            status_code=500,
        )


class PostsGenerationFailed(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="posts_generation_failed",
            message="Post generation failed.",
            status_code=502,
        )


class PostsGenerationInvalidOutput(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="posts_generation_invalid_output",
            message="AI returned an invalid posts payload.",
            status_code=502,
        )
