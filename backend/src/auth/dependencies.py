from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request

from src.auth.exceptions import AuthenticationRequired
from src.auth.repositories import UserRepository
from src.auth.services import AuthService
from src.config import settings
from src.database import db_dependency


def get_user_repository(session: db_dependency) -> UserRepository:
    return UserRepository(session)


def get_auth_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> AuthService:
    return AuthService(repository)


async def get_refresh_token(
    request: Request,
) -> str:
    refresh_token = request.cookies.get(settings.refresh_token_cookie_name)
    if not refresh_token:
        raise AuthenticationRequired()

    return refresh_token


auth_service_dependency = Annotated[AuthService, Depends(get_auth_service)]
refresh_token_dependency = Annotated[str, Depends(get_refresh_token)]
