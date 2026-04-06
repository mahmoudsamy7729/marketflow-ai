from __future__ import annotations

from fastapi import APIRouter

from src.ai_settings.dependencies import (
    admin_ai_provider_config_service_dependency,
    user_ai_settings_service_dependency,
)
from src.ai_settings.schemas import (
    AIProviderConfigListResponse,
    AIProviderConfigResponse,
    AISettingsMessageResponse,
    UpdateUserAISettingsRequest,
    UpsertAIProviderConfigRequest,
    UserAISettingsResponse,
)
from src.dependencies import current_admin_dependency, current_user_dependency


user_router = APIRouter(prefix="/auth/me/ai-settings", tags=["ai-settings"])
admin_router = APIRouter(prefix="/admin/ai-providers", tags=["admin-ai-providers"])


@user_router.get("", response_model=UserAISettingsResponse)
async def get_my_ai_settings(
    current_user: current_user_dependency,
    service: user_ai_settings_service_dependency,
) -> UserAISettingsResponse:
    return await service.get_settings(current_user)


@user_router.put("", response_model=UserAISettingsResponse)
async def update_my_ai_settings(
    payload: UpdateUserAISettingsRequest,
    current_user: current_user_dependency,
    service: user_ai_settings_service_dependency,
) -> UserAISettingsResponse:
    return await service.update_settings(current_user, payload)


@user_router.delete("", response_model=AISettingsMessageResponse)
async def delete_my_ai_settings(
    current_user: current_user_dependency,
    service: user_ai_settings_service_dependency,
) -> AISettingsMessageResponse:
    return await service.delete_settings(current_user)


@admin_router.get("", response_model=AIProviderConfigListResponse)
async def list_ai_provider_configs(
    _: current_admin_dependency,
    service: admin_ai_provider_config_service_dependency,
) -> AIProviderConfigListResponse:
    return await service.list_provider_configs()


@admin_router.put("/{provider}", response_model=AIProviderConfigResponse)
async def upsert_ai_provider_config(
    provider: str,
    payload: UpsertAIProviderConfigRequest,
    _: current_admin_dependency,
    service: admin_ai_provider_config_service_dependency,
) -> AIProviderConfigResponse:
    return await service.upsert_provider_config(provider, payload)
