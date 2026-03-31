from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from openai import AsyncOpenAI

from src.channels.dependencies import get_channel_repository, get_facebook_provider
from src.channels.providers import FacebookOAuthProvider
from src.channels.repositories import ChannelRepository
from src.config import settings
from src.content_plans.dependencies import get_content_plan_repository
from src.content_plans.repositories import ContentPlanRepository
from src.database import db_dependency
from src.posts import exceptions
from src.posts.repositories import PostRepository
from src.posts.services import PostGenerationService, PostService


def get_post_repository(session: db_dependency) -> PostRepository:
    return PostRepository(session)


def get_openai_client() -> AsyncOpenAI:
    if not settings.ai_api_key or not settings.ai_model or not settings.ai_base_url:
        raise exceptions.PostsGenerationConfigurationError()
    return AsyncOpenAI(
        api_key=settings.ai_api_key,
        base_url=settings.ai_base_url,
    )


def get_post_service(
    repository: Annotated[PostRepository, Depends(get_post_repository)],
    channel_repository: Annotated[ChannelRepository, Depends(get_channel_repository)],
    facebook_provider: Annotated[FacebookOAuthProvider, Depends(get_facebook_provider)],
) -> PostService:
    return PostService(repository, channel_repository, facebook_provider)


def get_post_generation_service(
    post_repository: Annotated[PostRepository, Depends(get_post_repository)],
    content_plan_repository: Annotated[ContentPlanRepository, Depends(get_content_plan_repository)],
    client: Annotated[AsyncOpenAI, Depends(get_openai_client)],
) -> PostGenerationService:
    return PostGenerationService(post_repository, content_plan_repository, client, settings.ai_model)


post_service_dependency = Annotated[PostService, Depends(get_post_service)]
post_generation_service_dependency = Annotated[
    PostGenerationService,
    Depends(get_post_generation_service),
]
