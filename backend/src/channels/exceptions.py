from __future__ import annotations

from src.common.exceptions import AppException


class FacebookConfigurationError(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="facebook_configuration_error",
            message="Facebook OAuth is not configured correctly.",
            status_code=500,
        )


class OAuthStateInvalid(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="oauth_state_invalid",
            message="The OAuth state is invalid.",
            status_code=400,
        )


class OAuthStateExpired(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="oauth_state_expired",
            message="The OAuth state has expired.",
            status_code=400,
        )


class OAuthStateConsumed(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="oauth_state_consumed",
            message="The OAuth state has already been used.",
            status_code=400,
        )


class FacebookTokenExchangeFailed(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="facebook_token_exchange_failed",
            message="Facebook token exchange failed.",
            status_code=502,
        )


class FacebookProfileFetchFailed(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="facebook_profile_fetch_failed",
            message="Facebook profile fetch failed.",
            status_code=502,
        )


class FacebookPagesFetchFailed(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="facebook_pages_fetch_failed",
            message="Facebook pages fetch failed.",
            status_code=502,
        )


class FacebookPublishFailed(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="facebook_publish_failed",
            message="Facebook publish failed.",
            status_code=502,
        )


class ChannelConnectionNotFound(AppException):
    def __init__(self, provider: str) -> None:
        super().__init__(
            code="channel_connection_not_found",
            message=f"No active {provider} connection was found.",
            status_code=404,
            extra={"provider": provider},
        )


class FacebookPageNotFound(AppException):
    def __init__(self, page_id: str) -> None:
        super().__init__(
            code="facebook_page_not_found",
            message="The requested Facebook page was not found or is not accessible.",
            status_code=404,
            extra={"page_id": page_id},
        )


class FacebookSelectedPageNotFound(AppException):
    def __init__(self, provider: str) -> None:
        super().__init__(
            code="facebook_selected_page_not_found",
            message=f"No selected {provider} page was found.",
            status_code=404,
            extra={"provider": provider},
        )


class N8NConfigurationError(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="n8n_configuration_error",
            message="N8N integration is not configured correctly.",
            status_code=500,
        )


class N8NAuthenticationFailed(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="n8n_authentication_failed",
            message="N8N authentication failed.",
            status_code=401,
        )
