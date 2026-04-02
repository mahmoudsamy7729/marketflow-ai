from __future__ import annotations

from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe

from src.auth.models import User
from src.channels import exceptions
from src.channels.providers import FacebookOAuthProvider
from src.channels.repositories import ChannelRepository
from src.channels.repositories.channel_repository import FACEBOOK_PROVIDER, INSTAGRAM_PROVIDER
from src.channels.schemas import (
    ChannelSummaryResponse,
    DisconnectChannelResponse,
    FacebookCallbackResponse,
    FacebookConnectResponse,
    FacebookPageResponse,
    FacebookPagesResponse,
    FacebookProfileResponse,
    InstagramProfileResponse,
    MyChannelsResponse,
    N8NFacebookPageResponse,
    ResolveFacebookPageRequest,
    ResolveFacebookPageResponse,
    SelectFacebookPageRequest,
    SelectFacebookPageResponse,
    SelectedFacebookPageResponse,
)


class ChannelService:
    def __init__(
        self,
        repository: ChannelRepository,
        facebook_provider: FacebookOAuthProvider,
    ) -> None:
        self.repository = repository
        self.facebook_provider = facebook_provider

    async def create_facebook_connect_url(self, user: User) -> FacebookConnectResponse:
        state = token_urlsafe(32)
        authorization_url, expires_at = self.facebook_provider.build_authorization_url(state)
        await self.repository.create_oauth_state(
            user_id=user.id,
            provider=FACEBOOK_PROVIDER,
            state=state,
            expires_at=expires_at,
        )
        return FacebookConnectResponse(
            provider=FACEBOOK_PROVIDER,
            authorization_url=authorization_url,
            state_expires_at=expires_at,
        )

    async def get_my_channels(self, user: User) -> MyChannelsResponse:
        connections = await self.repository.list_active_connections_by_user(user.id)
        channels: list[ChannelSummaryResponse] = []

        for connection in connections:
            if connection.provider != FACEBOOK_PROVIDER or connection.facebook_details is None:
                continue

            channels.append(self._build_facebook_channel_summary(connection))
            if (
                connection.selected_facebook_page is not None
                and connection.selected_facebook_page.instagram_account_id
            ):
                channels.append(self._build_instagram_channel_summary(connection))

        return MyChannelsResponse(channels=channels)

    async def get_facebook_pages(self, user: User) -> FacebookPagesResponse:
        connection = await self.repository.get_connection_by_user_and_provider(
            user_id=user.id,
            provider=FACEBOOK_PROVIDER,
        )
        if connection is None or connection.facebook_details is None:
            raise exceptions.ChannelConnectionNotFound(FACEBOOK_PROVIDER)

        pages_payload = await self.facebook_provider.fetch_pages(
            connection.facebook_details.access_token,
        )
        pages: list[FacebookPageResponse] = []
        for page in pages_payload:
            tasks = page.get("tasks")
            pages.append(
                FacebookPageResponse(
                    id=str(page.get("id", "")),
                    name=str(page.get("name", "")),
                    category=page.get("category"),
                    has_access_token=bool(page.get("access_token")),
                    tasks=[str(task) for task in tasks] if isinstance(tasks, list) else [],
                    instagram_profile=self._build_instagram_profile_from_page(page),
                )
            )

        return FacebookPagesResponse(provider=FACEBOOK_PROVIDER, pages=pages)

    async def select_facebook_page(
        self,
        user: User,
        payload: SelectFacebookPageRequest,
    ) -> SelectFacebookPageResponse:
        connection = await self.repository.get_connection_by_user_and_provider(
            user_id=user.id,
            provider=FACEBOOK_PROVIDER,
        )
        if connection is None or connection.facebook_details is None:
            raise exceptions.ChannelConnectionNotFound(FACEBOOK_PROVIDER)

        pages_payload = await self.facebook_provider.fetch_pages(
            connection.facebook_details.access_token,
        )
        matched_page = next(
            (
                page
                for page in pages_payload
                if str(page.get("id", "")).strip() == payload.page_id
            ),
            None,
        )
        if matched_page is None:
            raise exceptions.FacebookPageNotFound(payload.page_id)

        page_access_token = matched_page.get("access_token")
        if not page_access_token:
            raise exceptions.FacebookPageNotFound(payload.page_id)

        tasks = matched_page.get("tasks")
        tasks_list = [str(task) for task in tasks] if isinstance(tasks, list) else []
        instagram_profile = self._build_instagram_profile_from_page(matched_page)
        await self.repository.upsert_selected_facebook_page(
            connection_id=connection.id,
            facebook_page_id=str(matched_page.get("id", "")),
            page_name=str(matched_page.get("name", "")),
            category=matched_page.get("category"),
            page_access_token=str(page_access_token),
            tasks=",".join(tasks_list) if tasks_list else None,
            instagram_account_id=instagram_profile.instagram_user_id if instagram_profile else None,
            instagram_username=instagram_profile.username if instagram_profile else None,
            instagram_name=instagram_profile.name if instagram_profile else None,
            instagram_profile_picture_url=(
                instagram_profile.profile_picture_url if instagram_profile else None
            ),
        )

        return SelectFacebookPageResponse(
            provider=FACEBOOK_PROVIDER,
            connection_id=connection.id,
            page=SelectedFacebookPageResponse(
                id=str(matched_page.get("id", "")),
                name=str(matched_page.get("name", "")),
                category=matched_page.get("category"),
                has_access_token=True,
                tasks=tasks_list,
                instagram_profile=instagram_profile,
            ),
        )

    async def resolve_facebook_page_for_n8n(
        self,
        payload: ResolveFacebookPageRequest,
    ) -> ResolveFacebookPageResponse:
        connection = await self.repository.get_connection_by_user_and_provider(
            user_id=payload.user_id,
            provider=FACEBOOK_PROVIDER,
        )
        if connection is None or connection.facebook_details is None:
            raise exceptions.ChannelConnectionNotFound(FACEBOOK_PROVIDER)

        selected_page = connection.selected_facebook_page
        if selected_page is None:
            raise exceptions.FacebookSelectedPageNotFound(FACEBOOK_PROVIDER)

        tasks = []
        if selected_page.tasks:
            tasks = [
                task.strip()
                for task in selected_page.tasks.split(",")
                if task.strip()
            ]

        return ResolveFacebookPageResponse(
            provider=FACEBOOK_PROVIDER,
            user_id=payload.user_id,
            connection_id=connection.id,
            page=N8NFacebookPageResponse(
                id=selected_page.facebook_page_id,
                name=selected_page.page_name,
                category=selected_page.category,
                access_token=selected_page.page_access_token,
                tasks=tasks,
            ),
        )

    async def handle_facebook_callback(
        self,
        code: str,
        state: str,
    ) -> FacebookCallbackResponse:
        oauth_state = await self.repository.get_oauth_state(state=state, provider=FACEBOOK_PROVIDER)
        if oauth_state is None:
            raise exceptions.OAuthStateInvalid()
        if oauth_state.consumed:
            raise exceptions.OAuthStateConsumed()
        if oauth_state.expires_at < datetime.now(timezone.utc):
            raise exceptions.OAuthStateExpired()

        token_payload = await self.facebook_provider.exchange_code_for_token(code)
        access_token = token_payload.get("access_token")
        if not access_token:
            raise exceptions.FacebookTokenExchangeFailed()

        profile_payload = await self.facebook_provider.fetch_profile(str(access_token))
        facebook_user_id = profile_payload.get("id")
        if not facebook_user_id:
            raise exceptions.FacebookProfileFetchFailed()

        expires_in = token_payload.get("expires_in")
        expires_at = None
        if isinstance(expires_in, int):
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        granted_scopes_value = token_payload.get("granted_scopes")
        granted_scopes: list[str] = []
        granted_scopes_serialized = None
        if isinstance(granted_scopes_value, list):
            granted_scopes = [str(scope) for scope in granted_scopes_value]
            granted_scopes_serialized = ",".join(granted_scopes)

        connection = await self.repository.upsert_facebook_connection(
            user_id=oauth_state.user_id,
            facebook_user_id=str(facebook_user_id),
            access_token=str(access_token),
            token_type=token_payload.get("token_type"),
            expires_at=expires_at,
            granted_scopes=granted_scopes_serialized,
            display_name=profile_payload.get("name"),
        )
        await self.repository.consume_oauth_state(oauth_state)

        details = connection.facebook_details
        return FacebookCallbackResponse(
            provider=FACEBOOK_PROVIDER,
            status=connection.status,
            connection_id=connection.id,
            user_id=connection.user_id,
            profile=FacebookProfileResponse(
                facebook_user_id=details.facebook_user_id,
                display_name=details.display_name,
            ),
            expires_at=details.expires_at,
            granted_scopes=granted_scopes,
        )

    async def disconnect_facebook(self, user: User) -> DisconnectChannelResponse:
        connection = await self.repository.get_connection_by_user_and_provider(
            user_id=user.id,
            provider=FACEBOOK_PROVIDER,
        )
        if connection is None:
            raise exceptions.ChannelConnectionNotFound(FACEBOOK_PROVIDER)

        await self.repository.disconnect_connection(connection)
        return DisconnectChannelResponse(
            provider=FACEBOOK_PROVIDER,
            status="disconnected",
            message="Facebook channel disconnected successfully.",
        )

    def _build_facebook_channel_summary(self, connection) -> ChannelSummaryResponse:
        details = connection.facebook_details
        granted_scopes = []
        if details.granted_scopes:
            granted_scopes = [
                scope.strip()
                for scope in details.granted_scopes.split(",")
                if scope.strip()
            ]

        return ChannelSummaryResponse(
            connection_id=connection.id,
            provider=FACEBOOK_PROVIDER,
            status=connection.status,
            expires_at=details.expires_at,
            granted_scopes=granted_scopes,
            profile=FacebookProfileResponse(
                facebook_user_id=details.facebook_user_id,
                display_name=details.display_name,
            ),
            selected_target_id=(
                connection.selected_facebook_page.facebook_page_id
                if connection.selected_facebook_page is not None
                else None
            ),
            selected_target_name=(
                connection.selected_facebook_page.page_name
                if connection.selected_facebook_page is not None
                else None
            ),
        )

    def _build_instagram_channel_summary(self, connection) -> ChannelSummaryResponse:
        details = connection.facebook_details
        selected_page = connection.selected_facebook_page
        granted_scopes = []
        if details.granted_scopes:
            granted_scopes = [
                scope.strip()
                for scope in details.granted_scopes.split(",")
                if scope.strip()
            ]

        return ChannelSummaryResponse(
            connection_id=connection.id,
            provider=INSTAGRAM_PROVIDER,
            status="connected",
            expires_at=details.expires_at,
            granted_scopes=granted_scopes,
            instagram_profile=InstagramProfileResponse(
                instagram_user_id=selected_page.instagram_account_id,
                username=selected_page.instagram_username,
                name=selected_page.instagram_name,
                profile_picture_url=selected_page.instagram_profile_picture_url,
            ),
            selected_target_id=selected_page.instagram_account_id,
            selected_target_name=selected_page.instagram_name or selected_page.instagram_username,
        )

    def _build_instagram_profile_from_page(self, page: dict) -> InstagramProfileResponse | None:
        instagram_account = page.get("instagram_business_account")
        if not isinstance(instagram_account, dict):
            return None

        instagram_user_id = str(instagram_account.get("id", "")).strip()
        if not instagram_user_id:
            return None

        username = instagram_account.get("username")
        return InstagramProfileResponse(
            instagram_user_id=instagram_user_id,
            username=str(username).strip() if username is not None else None,
            name=instagram_account.get("name"),
            profile_picture_url=instagram_account.get("profile_picture_url"),
        )
