from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from src.channels.dependencies import channel_service_dependency, n8n_api_key_dependency
from src.channels.schemas import (
    DisconnectChannelResponse,
    FacebookCallbackResponse,
    FacebookConnectResponse,
    FacebookPagesResponse,
    MyChannelsResponse,
    ResolveFacebookPageRequest,
    ResolveFacebookPageResponse,
    SelectFacebookPageRequest,
    SelectFacebookPageResponse,
)
from src.dependencies import current_user_dependency


router = APIRouter(prefix="/channels", tags=["channels"])


@router.get("/facebook/connect", response_model=FacebookConnectResponse)
async def connect_facebook(
    current_user: current_user_dependency,
    service: channel_service_dependency,
) -> FacebookConnectResponse:
    return await service.create_facebook_connect_url(current_user)


@router.get("/facebook/callback", response_model=FacebookCallbackResponse)
async def facebook_callback(
    code: Annotated[str, Query(min_length=1)],
    state: Annotated[str, Query(min_length=1)],
    service: channel_service_dependency,
) -> FacebookCallbackResponse:
    return await service.handle_facebook_callback(code=code, state=state)


@router.get("/me", response_model=MyChannelsResponse)
async def get_my_channels(
    current_user: current_user_dependency,
    service: channel_service_dependency,
) -> MyChannelsResponse:
    return await service.get_my_channels(current_user)


@router.post("/facebook/disconnect", response_model=DisconnectChannelResponse)
async def disconnect_facebook(
    current_user: current_user_dependency,
    service: channel_service_dependency,
) -> DisconnectChannelResponse:
    return await service.disconnect_facebook(current_user)


@router.get("/facebook/pages", response_model=FacebookPagesResponse)
async def get_facebook_pages(
    current_user: current_user_dependency,
    service: channel_service_dependency,
) -> FacebookPagesResponse:
    return await service.get_facebook_pages(current_user)


@router.post("/facebook/pages/select", response_model=SelectFacebookPageResponse)
async def select_facebook_page(
    payload: SelectFacebookPageRequest,
    current_user: current_user_dependency,
    service: channel_service_dependency,
) -> SelectFacebookPageResponse:
    return await service.select_facebook_page(current_user, payload)


@router.post("/facebook/n8n/resolve-page", response_model=ResolveFacebookPageResponse)
async def resolve_facebook_page_for_n8n(
    payload: ResolveFacebookPageRequest,
    _: n8n_api_key_dependency,
    service: channel_service_dependency,
) -> ResolveFacebookPageResponse:
    return await service.resolve_facebook_page_for_n8n(payload)
