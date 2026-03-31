from __future__ import annotations

import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient

import main as main_module
from src.channels import exceptions
from src.channels.dependencies import get_channel_service
from src.channels.schemas import (
    ChannelSummaryResponse,
    FacebookCallbackResponse,
    FacebookProfileResponse,
    MyChannelsResponse,
    SelectedFacebookPageResponse,
)
from src.channels.services.channel_service import ChannelService
from src.dependencies import get_current_user


class CallbackServiceSuccessStub:
    async def handle_facebook_callback(self, code: str, state: str) -> FacebookCallbackResponse:
        return FacebookCallbackResponse(
            provider="facebook",
            status="connected",
            connection_id=uuid4(),
            user_id=uuid4(),
            profile=FacebookProfileResponse(
                facebook_user_id="fb-user-1",
                display_name="Acme FB",
            ),
            expires_at=None,
            granted_scopes=["public_profile"],
        )


class CallbackServiceErrorStub:
    async def handle_facebook_callback(self, code: str, state: str) -> FacebookCallbackResponse:
        raise exceptions.OAuthStateInvalid()


class ChannelsServiceStub:
    async def get_my_channels(self, user) -> MyChannelsResponse:
        return MyChannelsResponse(
            channels=[
                ChannelSummaryResponse(
                    connection_id=uuid4(),
                    provider="facebook",
                    status="connected",
                    expires_at=None,
                    granted_scopes=["public_profile"],
                    profile=FacebookProfileResponse(
                        facebook_user_id="fb-user-1",
                        display_name="Acme FB",
                    ),
                    selected_page=SelectedFacebookPageResponse(
                        id="page-1",
                        name="Acme Page",
                        category="Business",
                        has_access_token=True,
                        tasks=["CREATE_CONTENT"],
                    ),
                )
            ]
        )


class ChannelsRouterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = main_module.app
        self.app.dependency_overrides.clear()
        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        self.app.dependency_overrides.clear()

    def test_callback_success_redirects_to_frontend_channels(self) -> None:
        self.app.dependency_overrides[get_channel_service] = lambda: CallbackServiceSuccessStub()

        response = self.client.get(
            "/api/channels/facebook/callback",
            params={"code": "facebook-code", "state": "oauth-state"},
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["location"],
            f"{main_module.settings.frontend_url}/channels?provider=facebook&status=connected",
        )

    def test_callback_error_redirects_to_frontend_channels_with_error_code(self) -> None:
        self.app.dependency_overrides[get_channel_service] = lambda: CallbackServiceErrorStub()

        response = self.client.get(
            "/api/channels/facebook/callback",
            params={"code": "facebook-code", "state": "oauth-state"},
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["location"],
            f"{main_module.settings.frontend_url}/channels?provider=facebook&status=error&code=oauth_state_invalid",
        )

    def test_my_channels_includes_selected_page_summary(self) -> None:
        self.app.dependency_overrides[get_channel_service] = lambda: ChannelsServiceStub()
        self.app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=uuid4())

        response = self.client.get("/api/channels/me")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["channels"][0]["selected_page"]["name"], "Acme Page")
        self.assertEqual(payload["channels"][0]["profile"]["display_name"], "Acme FB")


class FakeRepository:
    def __init__(self) -> None:
        self.connection = SimpleNamespace(
            id=uuid4(),
            user_id=uuid4(),
            provider="facebook",
            status="connected",
            deleted_at=None,
            facebook_details=SimpleNamespace(
                facebook_user_id="fb-user-1",
                display_name="Acme FB",
                expires_at=None,
                granted_scopes="public_profile",
            ),
            selected_facebook_page=SimpleNamespace(
                facebook_page_id="page-1",
                page_name="Acme Page",
                category="Business",
                page_access_token="token",
                tasks="CREATE_CONTENT,MANAGE",
            ),
        )

    async def list_active_connections_by_user(self, user_id):
        if self.connection.deleted_at is None:
            return [self.connection]
        return []

    async def get_connection_by_user_and_provider(self, user_id, provider):
        if self.connection.deleted_at is None and self.connection.provider == provider:
            return self.connection
        return None

    async def disconnect_connection(self, connection):
        connection.status = "disconnected"
        connection.deleted_at = datetime.now(timezone.utc)
        return connection


class ChannelServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_disconnect_removes_connection_from_my_channels(self) -> None:
        repository = FakeRepository()
        service = ChannelService(repository=repository, facebook_provider=SimpleNamespace())
        user = SimpleNamespace(id=repository.connection.user_id)

        connected_channels = await service.get_my_channels(user)
        self.assertEqual(len(connected_channels.channels), 1)
        self.assertEqual(connected_channels.channels[0].selected_page.name, "Acme Page")
        self.assertEqual(connected_channels.channels[0].selected_page.tasks, ["CREATE_CONTENT", "MANAGE"])

        disconnect_response = await service.disconnect_facebook(user)
        self.assertEqual(disconnect_response.status, "disconnected")

        disconnected_channels = await service.get_my_channels(user)
        self.assertEqual(disconnected_channels.channels, [])


if __name__ == "__main__":
    unittest.main()
