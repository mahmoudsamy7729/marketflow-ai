from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx

from src.channels import exceptions
from src.config import settings


class FacebookOAuthProvider:
    AUTHORIZE_URL = "https://www.facebook.com/{version}/dialog/oauth"
    TOKEN_URL = "https://graph.facebook.com/{version}/oauth/access_token"
    PROFILE_URL = "https://graph.facebook.com/{version}/me"
    PAGES_URL = "https://graph.facebook.com/{version}/me/accounts"
    FEED_POST_URL = "https://graph.facebook.com/{version}/{page_id}/feed"
    PHOTOS_URL = "https://graph.facebook.com/{version}/{page_id}/photos"
    INSTAGRAM_MEDIA_URL = "https://graph.facebook.com/{version}/{ig_account_id}/media"
    INSTAGRAM_MEDIA_PUBLISH_URL = "https://graph.facebook.com/{version}/{ig_account_id}/media_publish"

    def _ensure_configured(self) -> None:
        if (
            not settings.facebook_app_id
            or not settings.facebook_app_secret
            or not settings.facebook_redirect_uri
        ):
            raise exceptions.FacebookConfigurationError()

    def build_authorization_url(self, state: str) -> tuple[str, datetime]:
        self._ensure_configured()
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.facebook_state_expire_minutes,
        )
        params = {
            "client_id": settings.facebook_app_id,
            "redirect_uri": settings.facebook_redirect_uri,
            "state": state,
            "response_type": "code",
        }
        if settings.facebook_config_id:
            params["config_id"] = settings.facebook_config_id
        else:
            params["scope"] = settings.facebook_oauth_scopes

        query = urlencode(params)
        url = self.AUTHORIZE_URL.format(version=settings.facebook_api_version)
        return f"{url}?{query}", expires_at

    async def exchange_code_for_token(self, code: str) -> dict:
        self._ensure_configured()
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(
                    self.TOKEN_URL.format(version=settings.facebook_api_version),
                    params={
                        "client_id": settings.facebook_app_id,
                        "client_secret": settings.facebook_app_secret,
                        "redirect_uri": settings.facebook_redirect_uri,
                        "code": code,
                    },
                )
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise exceptions.FacebookTokenExchangeFailed() from exc

    async def fetch_profile(self, access_token: str) -> dict:
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(
                    self.PROFILE_URL.format(version=settings.facebook_api_version),
                    params={
                        "fields": "id,name",
                        "access_token": access_token,
                    },
                )
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise exceptions.FacebookProfileFetchFailed() from exc

    async def fetch_pages(self, access_token: str) -> list[dict]:
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(
                    self.PAGES_URL.format(version=settings.facebook_api_version),
                    params={
                        "fields": "id,name,category,access_token,tasks,instagram_business_account{id,username,name,profile_picture_url}",
                        "access_token": access_token,
                    },
                )
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise exceptions.FacebookPagesFetchFailed() from exc

        data = payload.get("data")
        if not isinstance(data, list):
            raise exceptions.FacebookPagesFetchFailed()

        return data

    async def publish_feed_post(
        self,
        page_id: str,
        page_access_token: str,
        message: str,
    ) -> dict:
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    self.FEED_POST_URL.format(
                        version=settings.facebook_api_version,
                        page_id=page_id,
                    ),
                    data={
                        "message": message,
                        "access_token": page_access_token,
                    },
                )
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise exceptions.FacebookPublishFailed() from exc

    async def upload_unpublished_photo_from_url(
        self,
        page_id: str,
        page_access_token: str,
        image_url: str,
    ) -> str:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.PHOTOS_URL.format(
                        version=settings.facebook_api_version,
                        page_id=page_id,
                    ),
                    data={
                        "url": image_url,
                        "published": "false",
                        "access_token": page_access_token,
                    },
                )
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise exceptions.FacebookPublishFailed() from exc

        media_id = str(payload.get("id", "")).strip()
        if not media_id:
            raise exceptions.FacebookPublishFailed()
        return media_id

    async def upload_unpublished_photo_from_bytes(
        self,
        page_id: str,
        page_access_token: str,
        file_bytes: bytes,
        filename: str,
        mime_type: str | None,
    ) -> str:
        try:
            payload = await asyncio.to_thread(
                self._upload_unpublished_photo_from_bytes_sync,
                page_id,
                page_access_token,
                file_bytes,
                filename,
                mime_type,
            )
        except (httpx.HTTPError, ValueError) as exc:
            raise exceptions.FacebookPublishFailed() from exc

        media_id = str(payload.get("id", "")).strip()
        if not media_id:
            raise exceptions.FacebookPublishFailed()
        return media_id

    async def publish_feed_post_with_media(
        self,
        page_id: str,
        page_access_token: str,
        message: str,
        media_ids: list[str],
    ) -> dict:
        form_data: dict[str, str] = {
            "message": message,
            "access_token": page_access_token,
        }
        for index, media_id in enumerate(media_ids):
            form_data[f"attached_media[{index}]"] = json.dumps({"media_fbid": media_id})

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.FEED_POST_URL.format(
                        version=settings.facebook_api_version,
                        page_id=page_id,
                    ),
                    data=form_data,
                )
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise exceptions.FacebookPublishFailed() from exc

    async def create_instagram_image_container(
        self,
        *,
        ig_account_id: str,
        access_token: str,
        image_url: str,
        caption: str | None,
    ) -> str:
        payload: dict[str, str] = {
            "image_url": image_url,
            "access_token": access_token,
        }
        if caption:
            payload["caption"] = caption

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.INSTAGRAM_MEDIA_URL.format(
                        version=settings.facebook_api_version,
                        ig_account_id=ig_account_id,
                    ),
                    data=payload,
                )
                response.raise_for_status()
                result = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise exceptions.InstagramPublishFailed() from exc

        container_id = str(result.get("id", "")).strip()
        if not container_id:
            raise exceptions.InstagramPublishFailed()
        return container_id

    async def publish_instagram_media(
        self,
        *,
        ig_account_id: str,
        access_token: str,
        creation_id: str,
    ) -> dict:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.INSTAGRAM_MEDIA_PUBLISH_URL.format(
                        version=settings.facebook_api_version,
                        ig_account_id=ig_account_id,
                    ),
                    data={
                        "creation_id": creation_id,
                        "access_token": access_token,
                    },
                )
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise exceptions.InstagramPublishFailed() from exc

    def _upload_unpublished_photo_from_bytes_sync(
        self,
        page_id: str,
        page_access_token: str,
        file_bytes: bytes,
        filename: str,
        mime_type: str | None,
    ) -> dict:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                self.PHOTOS_URL.format(
                    version=settings.facebook_api_version,
                    page_id=page_id,
                ),
                data={
                    "published": "false",
                    "access_token": page_access_token,
                },
                files={
                    "source": (
                        filename,
                        file_bytes,
                        mime_type or "application/octet-stream",
                    )
                },
            )
            response.raise_for_status()
            return response.json()
