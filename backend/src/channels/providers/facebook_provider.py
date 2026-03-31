from __future__ import annotations

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
                        "fields": "id,name,category,access_token,tasks",
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
