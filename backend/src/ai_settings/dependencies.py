from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from src.ai_settings.repositories import AISettingsRepository
from src.ai_settings.security import AIKeyEncryptor, build_ai_key_encryptor
from src.ai_settings.services import AdminAIProviderConfigService, UserAISettingsService
from src.database import db_dependency


def get_ai_settings_repository(session: db_dependency) -> AISettingsRepository:
    return AISettingsRepository(session)


def get_ai_key_encryptor() -> AIKeyEncryptor:
    return build_ai_key_encryptor()


def get_user_ai_settings_service(
    repository: Annotated[AISettingsRepository, Depends(get_ai_settings_repository)],
    encryptor: Annotated[AIKeyEncryptor, Depends(get_ai_key_encryptor)],
) -> UserAISettingsService:
    return UserAISettingsService(repository, encryptor)


def get_admin_ai_provider_config_service(
    repository: Annotated[AISettingsRepository, Depends(get_ai_settings_repository)],
) -> AdminAIProviderConfigService:
    return AdminAIProviderConfigService(repository)


user_ai_settings_service_dependency = Annotated[UserAISettingsService, Depends(get_user_ai_settings_service)]
admin_ai_provider_config_service_dependency = Annotated[
    AdminAIProviderConfigService,
    Depends(get_admin_ai_provider_config_service),
]
