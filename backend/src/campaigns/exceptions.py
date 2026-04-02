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


class CampaignCadenceInvalid(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="campaign_cadence_invalid",
            message="Campaign cadence values must be greater than or equal to 1.",
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


class CampaignChannelNotConnected(AppException):
    def __init__(self, channel: str) -> None:
        super().__init__(
            code="campaign_channel_not_connected",
            message="The selected campaign channel is not connected for this user.",
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


class CampaignScheduleTimeInvalid(AppException):
    def __init__(self, value: str) -> None:
        super().__init__(
            code="campaign_schedule_time_invalid",
            message="Bulk scheduling requires a valid local time in HH:MM or HH:MM:SS format.",
            status_code=400,
            extra={"time_of_day": value},
        )


class CampaignScheduleTimezoneInvalid(AppException):
    def __init__(self, value: str) -> None:
        super().__init__(
            code="campaign_schedule_timezone_invalid",
            message="Bulk scheduling requires a valid IANA timezone.",
            status_code=400,
            extra={"timezone": value},
        )
