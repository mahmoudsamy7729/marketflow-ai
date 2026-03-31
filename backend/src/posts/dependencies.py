from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from src.database import db_dependency
from src.posts.repositories import PostRepository
from src.posts.services import PostService


def get_post_repository(session: db_dependency) -> PostRepository:
    return PostRepository(session)


def get_post_service(
    repository: Annotated[PostRepository, Depends(get_post_repository)],
) -> PostService:
    return PostService(repository)


post_service_dependency = Annotated[PostService, Depends(get_post_service)]
