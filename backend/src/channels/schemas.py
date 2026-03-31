from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class FacebookConnectResponse(BaseModel):
    provider: str
    authorization_url: str
    state_expires_at: datetime


class FacebookProfileResponse(BaseModel):
    facebook_user_id: str
    display_name: str | None


class FacebookCallbackResponse(BaseModel):
    provider: str
    status: str
    connection_id: UUID
    user_id: UUID
    profile: FacebookProfileResponse
    expires_at: datetime | None
    granted_scopes: list[str]


class SelectedFacebookPageResponse(BaseModel):
    id: str
    name: str
    category: str | None
    has_access_token: bool
    tasks: list[str]


class ChannelSummaryResponse(BaseModel):
    connection_id: UUID
    provider: str
    status: str
    expires_at: datetime | None
    granted_scopes: list[str]
    profile: FacebookProfileResponse
    selected_page: SelectedFacebookPageResponse | None = None


class MyChannelsResponse(BaseModel):
    channels: list[ChannelSummaryResponse]


class DisconnectChannelResponse(BaseModel):
    provider: str
    status: str
    message: str


class FacebookPageResponse(BaseModel):
    id: str
    name: str
    category: str | None
    has_access_token: bool
    tasks: list[str]


class FacebookPagesResponse(BaseModel):
    provider: str
    pages: list[FacebookPageResponse]


class SelectFacebookPageRequest(BaseModel):
    page_id: str


class SelectFacebookPageResponse(BaseModel):
    provider: str
    connection_id: UUID
    page: SelectedFacebookPageResponse


class ResolveFacebookPageRequest(BaseModel):
    user_id: UUID


class N8NFacebookPageResponse(BaseModel):
    id: str
    name: str
    category: str | None
    access_token: str
    tasks: list[str]


class ResolveFacebookPageResponse(BaseModel):
    provider: str
    user_id: UUID
    connection_id: UUID
    page: N8NFacebookPageResponse
