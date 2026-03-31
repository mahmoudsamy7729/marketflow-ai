from __future__ import annotations

from fastapi import APIRouter, Response, status

from src.auth.dependencies import auth_service_dependency, refresh_token_dependency
from src.auth.schemas import (
    AuthSessionResponse,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    UserResponse,
)
from src.dependencies import current_user_dependency


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=AuthSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: RegisterRequest,
    response: Response,
    service: auth_service_dependency,
) -> AuthSessionResponse:
    return await service.register(payload, response)


@router.post("/login", response_model=AuthSessionResponse)
async def login(
    payload: LoginRequest,
    response: Response,
    service: auth_service_dependency,
) -> AuthSessionResponse:
    return await service.login(payload, response)


@router.post("/refresh", response_model=AuthSessionResponse)
async def refresh_session(
    response: Response,
    refresh_token: refresh_token_dependency,
    service: auth_service_dependency,
) -> AuthSessionResponse:
    return await service.refresh_session(refresh_token, response)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    response: Response,
    service: auth_service_dependency,
) -> MessageResponse:
    return await service.logout(response)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: current_user_dependency) -> UserResponse:
    return UserResponse.model_validate(current_user)
