from __future__ import annotations

from src.common.exceptions import AppException


class UnsupportedAIProvider(AppException):
    def __init__(self, provider: str) -> None:
        super().__init__(
            code="unsupported_ai_provider",
            message="The selected AI provider is not supported.",
            status_code=400,
            extra={"provider": provider},
        )


class UserAISettingsNotConfigured(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="user_ai_settings_not_configured",
            message="AI provider is not configured for this account.",
            status_code=400,
        )


class AIProviderConfigUnavailable(AppException):
    def __init__(self, provider: str) -> None:
        super().__init__(
            code="ai_provider_config_unavailable",
            message="The selected AI provider is not available right now.",
            status_code=503,
            extra={"provider": provider},
        )


class AIAPIKeyInvalid(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="ai_api_key_invalid",
            message="The provided API key could not be validated.",
            status_code=400,
        )


class AIEncryptionConfigurationError(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="ai_encryption_configuration_error",
            message="AI encryption is not configured correctly.",
            status_code=500,
        )
