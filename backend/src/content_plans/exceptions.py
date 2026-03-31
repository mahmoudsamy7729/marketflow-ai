from __future__ import annotations

from src.common.exceptions import AppException


class ContentPlanNotFound(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="content_plan_not_found",
            message="Active content plan not found.",
            status_code=404,
        )


class ContentPlanItemNotFound(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="content_plan_item_not_found",
            message="Content plan item not found.",
            status_code=404,
        )


class ContentPlanItemStatusInvalid(AppException):
    def __init__(self, status: str) -> None:
        super().__init__(
            code="content_plan_item_status_invalid",
            message="The content plan item contains an unsupported status.",
            status_code=400,
            extra={"status": status},
        )


class ContentPlanItemTypeInvalid(AppException):
    def __init__(self, content_type: str) -> None:
        super().__init__(
            code="content_plan_item_type_invalid",
            message="The content plan item contains an unsupported content type.",
            status_code=400,
            extra={"content_type": content_type},
        )


class ContentPlanNotEditable(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="content_plan_not_editable",
            message="Archived content plans cannot be edited.",
            status_code=400,
        )


class ContentPlanItemDateInvalid(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="content_plan_item_date_invalid",
            message="The planned date must be inside the campaign date range.",
            status_code=400,
        )


class ContentPlanGenerationConfigurationError(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="content_plan_generation_configuration_error",
            message="AI content plan generation is not configured correctly.",
            status_code=500,
        )


class ContentPlanGenerationFailed(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="content_plan_generation_failed",
            message="Content plan generation failed.",
            status_code=502,
        )


class ContentPlanGenerationInvalidOutput(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="content_plan_generation_invalid_output",
            message="AI returned an invalid content plan payload.",
            status_code=502,
        )
