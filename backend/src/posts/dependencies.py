from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from src.ai_settings.dependencies import user_ai_settings_service_dependency
from src.channels.dependencies import get_channel_repository, get_facebook_provider
from src.channels.providers import FacebookOAuthProvider
from src.channels.repositories import ChannelRepository
from src.content_plans.dependencies import get_content_plan_repository
from src.content_plans.repositories import ContentPlanRepository
from src.database import db_dependency
from src.dependencies import current_user_dependency
from src.posts.publishers import FacebookPostPublisher, InstagramPostPublisher
from src.posts.repositories import PostRepository
from src.posts.services import PostGenerationService, PostService


def get_post_repository(session: db_dependency) -> PostRepository:
    return PostRepository(session)


def get_post_service(
    repository: Annotated[PostRepository, Depends(get_post_repository)],
    channel_repository: Annotated[ChannelRepository, Depends(get_channel_repository)],
    facebook_provider: Annotated[FacebookOAuthProvider, Depends(get_facebook_provider)],
) -> PostService:
    return PostService(
        repository,
        channel_repository,
        facebook_provider,
        publishers={
            "facebook": FacebookPostPublisher(facebook_provider),
            "instagram": InstagramPostPublisher(facebook_provider),
        },
    )


async def get_post_generation_service(
    post_repository: Annotated[PostRepository, Depends(get_post_repository)],
    content_plan_repository: Annotated[ContentPlanRepository, Depends(get_content_plan_repository)],
    current_user: current_user_dependency,
    ai_settings_service: user_ai_settings_service_dependency,
) -> PostGenerationService:
    resolved_config = await ai_settings_service.resolve_generation_config(current_user)
    return PostGenerationService(
        post_repository,
        content_plan_repository,
        resolved_config.client,
        resolved_config.model,
    )


post_service_dependency = Annotated[PostService, Depends(get_post_service)]
post_generation_service_dependency = Annotated[
    PostGenerationService,
    Depends(get_post_generation_service),
]
