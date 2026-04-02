from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.channels.models import (
    ChannelConnection,
    FacebookConnectionDetails,
    FacebookSelectedPage,
    OAuthState,
)


FACEBOOK_PROVIDER = "facebook"
INSTAGRAM_PROVIDER = "instagram"
CONNECTED_STATUS = "connected"
DISCONNECTED_STATUS = "disconnected"


class ChannelRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_oauth_state(
        self,
        user_id: UUID,
        provider: str,
        state: str,
        expires_at: datetime,
    ) -> OAuthState:
        oauth_state = OAuthState(
            user_id=user_id,
            provider=provider,
            state=state,
            expires_at=expires_at,
            consumed=False,
        )
        self.session.add(oauth_state)
        await self.session.commit()
        await self.session.refresh(oauth_state)
        return oauth_state

    async def get_oauth_state(self, state: str, provider: str) -> OAuthState | None:
        statement = select(OAuthState).where(
            OAuthState.state == state,
            OAuthState.provider == provider,
        )
        return await self.session.scalar(statement)

    async def consume_oauth_state(self, oauth_state: OAuthState) -> OAuthState:
        oauth_state.consumed = True
        oauth_state.consumed_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(oauth_state)
        return oauth_state

    async def get_connection_by_user_and_provider(
        self,
        user_id: UUID,
        provider: str,
    ) -> ChannelConnection | None:
        statement = (
            select(ChannelConnection)
            .options(
                selectinload(ChannelConnection.facebook_details),
                selectinload(ChannelConnection.selected_facebook_page),
            )
            .where(
                ChannelConnection.user_id == user_id,
                ChannelConnection.provider == provider,
                ChannelConnection.deleted_at.is_(None),
            )
        )
        return await self.session.scalar(statement)

    async def list_active_connections_by_user(
        self,
        user_id: UUID,
    ) -> list[ChannelConnection]:
        statement = (
            select(ChannelConnection)
            .options(
                selectinload(ChannelConnection.facebook_details),
                selectinload(ChannelConnection.selected_facebook_page),
            )
            .where(
                ChannelConnection.user_id == user_id,
                ChannelConnection.deleted_at.is_(None),
            )
            .order_by(ChannelConnection.created_at.asc())
        )
        result = await self.session.scalars(statement)
        return list(result.all())

    async def list_connected_providers_by_user(self, user_id: UUID) -> set[str]:
        statement = (
            select(ChannelConnection)
            .options(selectinload(ChannelConnection.selected_facebook_page))
            .where(
                ChannelConnection.user_id == user_id,
                ChannelConnection.status == CONNECTED_STATUS,
                ChannelConnection.deleted_at.is_(None),
            )
        )
        result = await self.session.scalars(statement)
        connections = list(result.all())
        providers = {connection.provider for connection in connections}
        if any(
            connection.provider == FACEBOOK_PROVIDER
            and connection.selected_facebook_page is not None
            and connection.selected_facebook_page.instagram_account_id
            for connection in connections
        ):
            providers.add(INSTAGRAM_PROVIDER)
        return providers

    async def upsert_facebook_connection(
        self,
        user_id: UUID,
        facebook_user_id: str,
        access_token: str,
        token_type: str | None,
        expires_at: datetime | None,
        granted_scopes: str | None,
        display_name: str | None,
    ) -> ChannelConnection:
        connection = await self.get_connection_by_user_and_provider(user_id, FACEBOOK_PROVIDER)

        if connection is None:
            connection = ChannelConnection(
                user_id=user_id,
                provider=FACEBOOK_PROVIDER,
                status=CONNECTED_STATUS,
            )
            self.session.add(connection)
            await self.session.flush()
            self.session.add(
                FacebookConnectionDetails(
                    connection_id=connection.id,
                    facebook_user_id=facebook_user_id,
                    access_token=access_token,
                    token_type=token_type,
                    expires_at=expires_at,
                    granted_scopes=granted_scopes,
                    display_name=display_name,
                )
            )
        else:
            connection.status = CONNECTED_STATUS
            connection.deleted_at = None
            details = connection.facebook_details
            if details is None:
                self.session.add(
                    FacebookConnectionDetails(
                        connection_id=connection.id,
                        facebook_user_id=facebook_user_id,
                        access_token=access_token,
                        token_type=token_type,
                        expires_at=expires_at,
                        granted_scopes=granted_scopes,
                        display_name=display_name,
                    )
                )
            else:
                details.facebook_user_id = facebook_user_id
                details.access_token = access_token
                details.token_type = token_type
                details.expires_at = expires_at
                details.granted_scopes = granted_scopes
                details.display_name = display_name

        await self.session.commit()
        statement = (
            select(ChannelConnection)
            .options(
                selectinload(ChannelConnection.facebook_details),
                selectinload(ChannelConnection.selected_facebook_page),
            )
            .where(ChannelConnection.id == connection.id)
        )
        return await self.session.scalar(statement)

    async def disconnect_connection(self, connection: ChannelConnection) -> ChannelConnection:
        connection.status = DISCONNECTED_STATUS
        connection.deleted_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(connection)
        return connection

    async def upsert_selected_facebook_page(
        self,
        connection_id: UUID,
        facebook_page_id: str,
        page_name: str,
        category: str | None,
        page_access_token: str,
        tasks: str | None,
        instagram_account_id: str | None,
        instagram_username: str | None,
        instagram_name: str | None,
        instagram_profile_picture_url: str | None,
    ) -> FacebookSelectedPage:
        selected_page = await self.session.get(FacebookSelectedPage, connection_id)
        if selected_page is None:
            selected_page = FacebookSelectedPage(
                connection_id=connection_id,
                facebook_page_id=facebook_page_id,
                page_name=page_name,
                category=category,
                page_access_token=page_access_token,
                tasks=tasks,
                instagram_account_id=instagram_account_id,
                instagram_username=instagram_username,
                instagram_name=instagram_name,
                instagram_profile_picture_url=instagram_profile_picture_url,
            )
            self.session.add(selected_page)
        else:
            selected_page.facebook_page_id = facebook_page_id
            selected_page.page_name = page_name
            selected_page.category = category
            selected_page.page_access_token = page_access_token
            selected_page.tasks = tasks
            selected_page.instagram_account_id = instagram_account_id
            selected_page.instagram_username = instagram_username
            selected_page.instagram_name = instagram_name
            selected_page.instagram_profile_picture_url = instagram_profile_picture_url

        await self.session.commit()
        await self.session.refresh(selected_page)
        return selected_page

    async def get_selected_facebook_page(
        self,
        connection_id: UUID,
    ) -> FacebookSelectedPage | None:
        return await self.session.get(FacebookSelectedPage, connection_id)
