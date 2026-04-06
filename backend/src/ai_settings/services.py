from __future__ import annotations

from dataclasses import dataclass

from openai import AsyncOpenAI

from src.ai_settings import exceptions
from src.ai_settings.models import AIProviderConfig, OPENAI_PROVIDER, SUPPORTED_AI_PROVIDERS
from src.ai_settings.repositories import AISettingsRepository
from src.ai_settings.schemas import (
    AIProviderConfigListResponse,
    AIProviderConfigResponse,
    AISettingsMessageResponse,
    UpdateUserAISettingsRequest,
    UpsertAIProviderConfigRequest,
    UserAISettingsResponse,
)
from src.ai_settings.security import AIKeyEncryptor
from src.auth.models import User


@dataclass
class ResolvedAIClientConfig:
    client: AsyncOpenAI
    model: str
    provider: str


class UserAISettingsService:
    def __init__(
        self,
        repository: AISettingsRepository,
        encryptor: AIKeyEncryptor,
    ) -> None:
        self.repository = repository
        self.encryptor = encryptor

    async def get_settings(self, user: User) -> UserAISettingsResponse:
        provider_config = await self.repository.get_provider_config(OPENAI_PROVIDER)
        settings = await self.repository.get_user_settings(user.id)
        provider = settings.provider if settings is not None else OPENAI_PROVIDER
        has_api_key = bool(settings and settings.is_active and settings.encrypted_api_key)
        return UserAISettingsResponse(
            provider=provider,
            provider_display_name=provider_config.display_name if provider_config is not None else "OpenAI",
            has_api_key=has_api_key,
            api_key_last4=settings.api_key_last4 if has_api_key else None,
            is_active=bool(settings and settings.is_active),
        )

    async def update_settings(
        self,
        user: User,
        payload: UpdateUserAISettingsRequest,
    ) -> UserAISettingsResponse:
        provider = payload.provider.strip().lower()
        if provider not in SUPPORTED_AI_PROVIDERS:
            raise exceptions.UnsupportedAIProvider(provider)

        provider_config = await self._get_enabled_provider_config(provider)
        await self._validate_api_key(provider_config, payload.api_key)
        encrypted_api_key = self.encryptor.encrypt(payload.api_key)
        settings = await self.repository.upsert_user_settings(
            user_id=user.id,
            provider=provider,
            encrypted_api_key=encrypted_api_key,
            api_key_last4=payload.api_key[-4:],
        )
        return UserAISettingsResponse(
            provider=settings.provider,
            provider_display_name=provider_config.display_name,
            has_api_key=True,
            api_key_last4=settings.api_key_last4,
            is_active=settings.is_active,
        )

    async def delete_settings(self, user: User) -> AISettingsMessageResponse:
        settings = await self.repository.get_user_settings(user.id)
        if settings is not None:
            await self.repository.deactivate_user_settings(settings)
        return AISettingsMessageResponse(message="AI provider settings cleared successfully.")

    async def resolve_generation_config(self, user: User) -> ResolvedAIClientConfig:
        user_settings = await self.repository.get_user_settings(user.id)
        if user_settings is None or not user_settings.is_active or not user_settings.encrypted_api_key:
            raise exceptions.UserAISettingsNotConfigured()

        provider_config = await self._get_enabled_provider_config(user_settings.provider)
        api_key = self.encryptor.decrypt(user_settings.encrypted_api_key)
        client = AsyncOpenAI(api_key=api_key, base_url=provider_config.base_url)
        return ResolvedAIClientConfig(
            client=client,
            model=provider_config.model,
            provider=provider_config.provider,
        )

    async def _validate_api_key(self, provider_config: AIProviderConfig, api_key: str) -> None:
        client = AsyncOpenAI(api_key=api_key, base_url=provider_config.base_url)
        try:
            await client.models.list()
        except Exception as exc:
            raise exceptions.AIAPIKeyInvalid() from exc

    async def _get_enabled_provider_config(self, provider: str) -> AIProviderConfig:
        config = await self.repository.get_provider_config(provider)
        if config is None or not config.is_enabled:
            raise exceptions.AIProviderConfigUnavailable(provider)
        return config


class AdminAIProviderConfigService:
    def __init__(self, repository: AISettingsRepository) -> None:
        self.repository = repository

    async def list_provider_configs(self) -> AIProviderConfigListResponse:
        providers = await self.repository.list_provider_configs()
        return AIProviderConfigListResponse(
            providers=[AIProviderConfigResponse.model_validate(provider) for provider in providers],
        )

    async def upsert_provider_config(
        self,
        provider: str,
        payload: UpsertAIProviderConfigRequest,
    ) -> AIProviderConfigResponse:
        normalized_provider = provider.strip().lower()
        if normalized_provider not in SUPPORTED_AI_PROVIDERS:
            raise exceptions.UnsupportedAIProvider(normalized_provider)

        config = await self.repository.upsert_provider_config(
            provider=normalized_provider,
            display_name=payload.display_name,
            base_url=payload.base_url,
            model=payload.model,
            is_enabled=payload.is_enabled,
        )
        return AIProviderConfigResponse.model_validate(config)
