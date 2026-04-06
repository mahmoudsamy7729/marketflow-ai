from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai_settings.models import AIProviderConfig, UserAISettings


class AISettingsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_settings(self, user_id: UUID) -> UserAISettings | None:
        statement = select(UserAISettings).where(UserAISettings.user_id == user_id)
        return await self.session.scalar(statement)

    async def upsert_user_settings(
        self,
        user_id: UUID,
        provider: str,
        encrypted_api_key: str,
        api_key_last4: str,
    ) -> UserAISettings:
        settings = await self.get_user_settings(user_id)
        if settings is None:
            settings = UserAISettings(
                user_id=user_id,
                provider=provider,
                encrypted_api_key=encrypted_api_key,
                api_key_last4=api_key_last4,
                is_active=True,
            )
            self.session.add(settings)
        else:
            settings.provider = provider
            settings.encrypted_api_key = encrypted_api_key
            settings.api_key_last4 = api_key_last4
            settings.is_active = True

        await self.session.commit()
        await self.session.refresh(settings)
        return settings

    async def deactivate_user_settings(self, settings: UserAISettings) -> UserAISettings:
        settings.encrypted_api_key = None
        settings.api_key_last4 = None
        settings.is_active = False
        await self.session.commit()
        await self.session.refresh(settings)
        return settings

    async def get_provider_config(self, provider: str) -> AIProviderConfig | None:
        statement = select(AIProviderConfig).where(AIProviderConfig.provider == provider)
        return await self.session.scalar(statement)

    async def list_provider_configs(self) -> list[AIProviderConfig]:
        statement = select(AIProviderConfig).order_by(AIProviderConfig.provider.asc())
        result = await self.session.scalars(statement)
        return list(result.all())

    async def upsert_provider_config(
        self,
        provider: str,
        display_name: str,
        base_url: str,
        model: str,
        is_enabled: bool,
    ) -> AIProviderConfig:
        config = await self.get_provider_config(provider)
        if config is None:
            config = AIProviderConfig(
                provider=provider,
                display_name=display_name,
                base_url=base_url,
                model=model,
                is_enabled=is_enabled,
            )
            self.session.add(config)
        else:
            config.display_name = display_name
            config.base_url = base_url
            config.model = model
            config.is_enabled = is_enabled

        await self.session.commit()
        await self.session.refresh(config)
        return config
