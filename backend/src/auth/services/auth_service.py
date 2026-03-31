from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import Response

from src.auth import exceptions
from src.auth.jwt import (
    generate_access_token,
    generate_refresh_token,
    verify_access_token,
    verify_refresh_token,
)
from src.auth.models import User
from src.auth.repositories import UserRepository
from src.auth.schemas import (
    AuthSessionResponse,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    UserResponse,
)
from src.config import settings
from src.hashing import hash_password, verify_password


class AuthService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def register(
        self,
        payload: RegisterRequest,
        response: Response,
    ) -> AuthSessionResponse:
        existing_user = await self.repository.get_by_email(
            payload.email,
            include_deleted=True,
        )
        if existing_user is not None:
            raise exceptions.UserAlreadyExists(payload.email)

        hashed_password = await hash_password(payload.password)
        user = await self.repository.create_user(
            email=payload.email,
            company_name=payload.company_name,
            hashed_password=hashed_password,
        )
        return self._create_auth_session_response(response, user)

    async def login(
        self,
        payload: LoginRequest,
        response: Response,
    ) -> AuthSessionResponse:
        user = await self.repository.get_by_email(payload.email, include_deleted=True)
        if user is None or user.deleted_at is not None:
            raise exceptions.InvalidCredentials()

        password_is_valid = await verify_password(
            payload.password,
            user.hashed_password,
        )
        if not password_is_valid:
            raise exceptions.InvalidCredentials()

        return self._create_auth_session_response(response, user)

    async def refresh_session(
        self,
        refresh_token: str,
        response: Response,
    ) -> AuthSessionResponse:
        payload = verify_refresh_token(refresh_token)
        user = await self._get_active_user_from_subject(payload.get("sub"))
        return self._create_auth_session_response(response, user)

    async def logout(self, response: Response) -> MessageResponse:
        self._clear_auth_cookies(response)
        return MessageResponse(message="Logout successful.")

    async def resolve_user_from_access_token(self, access_token: str) -> User:
        payload = verify_access_token(access_token)
        return await self._get_active_user_from_subject(payload.get("sub"))

    async def _get_active_user_from_subject(self, subject: Any) -> User:
        try:
            user_id = UUID(str(subject))
        except (TypeError, ValueError) as exc:
            raise exceptions.InvalidTokenPayload() from exc

        user = await self.repository.get_by_id(user_id, include_deleted=True)
        if user is None:
            raise exceptions.UserNotFound()
        if user.deleted_at is not None:
            raise exceptions.UserDeleted()

        return user

    def _create_auth_session_response(
        self,
        response: Response,
        user: User,
    ) -> AuthSessionResponse:
        access_token, _ = generate_access_token(user.id)
        self._set_refresh_cookie(response, user.id)
        return AuthSessionResponse(
            access_token=access_token,
            user=UserResponse.model_validate(user),
        )

    def _set_refresh_cookie(self, response: Response, user_id: UUID) -> None:
        refresh_token, _ = generate_refresh_token(user_id)
        response.set_cookie(
            key=settings.refresh_token_cookie_name,
            value=refresh_token,
            max_age=settings.refresh_token_expire_minutes * 60,
            **self._cookie_kwargs(),
        )

    def _clear_auth_cookies(self, response: Response) -> None:
        response.delete_cookie(
            key=settings.access_token_cookie_name,
            path="/",
            domain=settings.cookie_domain,
        )
        response.delete_cookie(
            key=settings.refresh_token_cookie_name,
            path="/",
            domain=settings.cookie_domain,
        )

    def _cookie_kwargs(self) -> dict[str, Any]:
        return {
            "httponly": True,
            "secure": settings.cookie_secure,
            "samesite": settings.cookie_samesite,
            "domain": settings.cookie_domain,
            "path": "/",
        }
