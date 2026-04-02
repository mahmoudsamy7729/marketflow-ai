from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from src.database import db_dependency
from src.media_generation.providers import KieProvider
from src.media_generation.repositories import MediaGenerationRepository
from src.media_generation.services import MediaGenerationService
from src.posts.dependencies import get_post_repository
from src.posts.repositories import PostRepository


def get_media_generation_repository(session: db_dependency) -> MediaGenerationRepository:
    return MediaGenerationRepository(session)


def get_kie_provider() -> KieProvider:
    return KieProvider()


def get_media_generation_service(
    repository: Annotated[MediaGenerationRepository, Depends(get_media_generation_repository)],
    post_repository: Annotated[PostRepository, Depends(get_post_repository)],
    kie_provider: Annotated[KieProvider, Depends(get_kie_provider)],
) -> MediaGenerationService:
    return MediaGenerationService(repository, post_repository, kie_provider)


media_generation_service_dependency = Annotated[
    MediaGenerationService,
    Depends(get_media_generation_service),
]
