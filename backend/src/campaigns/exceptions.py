from __future__ import annotations

from src.common.exceptions import AppException


class CampaignNotFound(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="campaign_not_found",
            message="Campaign not found.",
            status_code=404,
        )


class CampaignDateRangeInvalid(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="campaign_date_range_invalid",
            message="Campaign start date must be before or equal to the end date.",
            status_code=400,
        )


class CampaignChannelsRequired(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="campaign_channels_required",
            message="At least one campaign channel is required.",
            status_code=400,
        )


class CampaignChannelInvalid(AppException):
    def __init__(self, channel: str) -> None:
        super().__init__(
            code="campaign_channel_invalid",
            message="The campaign contains an unsupported channel.",
            status_code=400,
            extra={"channel": channel},
        )


class CampaignStatusInvalid(AppException):
    def __init__(self, status: str) -> None:
        super().__init__(
            code="campaign_status_invalid",
            message="The campaign contains an unsupported status.",
            status_code=400,
            extra={"status": status},
        )
