from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header

from src.channels.providers import FacebookOAuthProvider
from src.channels.repositories import ChannelRepository
from src.channels.services import ChannelService
from src.config import settings
from src.channels import exceptions
from src.database import db_dependency


def get_channel_repository(session: db_dependency) -> ChannelRepository:
    return ChannelRepository(session)


def get_facebook_provider() -> FacebookOAuthProvider:
    return FacebookOAuthProvider()


def get_channel_service(
    repository: Annotated[ChannelRepository, Depends(get_channel_repository)],
    facebook_provider: Annotated[FacebookOAuthProvider, Depends(get_facebook_provider)],
) -> ChannelService:
    return ChannelService(repository, facebook_provider)


channel_service_dependency = Annotated[ChannelService, Depends(get_channel_service)]


def verify_n8n_api_key(
    x_n8n_api_key: Annotated[str | None, Header(alias="X-N8N-API-Key")] = None,
) -> None:
    if not settings.n8n_api_key:
        raise exceptions.N8NConfigurationError()
    if x_n8n_api_key != settings.n8n_api_key:
        raise exceptions.N8NAuthenticationFailed()


n8n_api_key_dependency = Annotated[None, Depends(verify_n8n_api_key)]
