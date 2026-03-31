import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

import * as redirectModule from "@/features/channels/lib/redirect";
import {
  createRouteHandlers,
  jsonResponse,
  renderApp,
} from "@/test/testUtils";

const sessionResponse = {
  access_token: "access-token",
  user: {
    id: "user-1",
    email: "owner@example.com",
    company_name: "Acme Studio",
    created_at: "2026-03-31T12:00:00Z",
    updated_at: "2026-03-31T12:00:00Z",
    deleted_at: null,
  },
};

const dashboardResponse = {
  overview: {
    total_campaigns: 4,
    active_campaigns: 2,
    total_posts: 16,
    draft_posts: 3,
    scheduled_posts: 5,
    published_posts: 7,
    failed_posts: 1,
  },
  connected_channels: [],
  upcoming_posts: [],
  recent_activity: [],
  campaign_health: [],
};

const connectedChannel = {
  connection_id: "connection-1",
  provider: "facebook",
  status: "connected",
  expires_at: null,
  granted_scopes: ["public_profile"],
  profile: {
    facebook_user_id: "fb-user-1",
    display_name: "Acme FB",
  },
  selected_page: {
    id: "page-1",
    name: "Acme Page",
    category: "Business",
    has_access_token: true,
    tasks: ["CREATE_CONTENT"],
  },
};

const facebookPagesResponse = {
  provider: "facebook",
  pages: [
    {
      id: "page-1",
      name: "Acme Page",
      category: "Business",
      has_access_token: true,
      tasks: ["CREATE_CONTENT"],
    },
    {
      id: "page-2",
      name: "Launch Page",
      category: "Brand",
      has_access_token: true,
      tasks: ["CREATE_CONTENT"],
    },
  ],
};

function createUnauthorizedResponse() {
  return jsonResponse(
    {
      error: {
        code: "authentication_required",
        message: "Authentication is required.",
        extra: {},
      },
    },
    { status: 401 },
  );
}

describe("channels page", () => {
  it("protects the channels route like the dashboard", async () => {
    createRouteHandlers([
      {
        method: "POST",
        path: "/api/auth/refresh",
        response: () => createUnauthorizedResponse(),
      },
    ]);

    renderApp(["/channels"]);

    expect(await screen.findByRole("heading", { name: /welcome back/i })).toBeInTheDocument();
  });

  it("renders sidebar navigation and navigates from dashboard to channels", async () => {
    createRouteHandlers([
      {
        method: "POST",
        path: "/api/auth/refresh",
        response: jsonResponse(sessionResponse),
      },
      {
        method: "GET",
        path: "/dashboard",
        response: jsonResponse(dashboardResponse),
      },
      {
        method: "GET",
        path: "/api/channels/me",
        response: jsonResponse({ channels: [] }),
      },
    ]);

    renderApp(["/dashboard"]);

    expect(await screen.findByRole("link", { name: /channels/i })).toBeInTheDocument();

    const user = userEvent.setup();
    await user.click(screen.getByRole("link", { name: /channels/i }));

    expect(await screen.findByRole("heading", { name: /channels/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /dashboard/i })).toBeInTheDocument();
  });

  it("shows connect when Facebook is not connected", async () => {
    createRouteHandlers([
      {
        method: "POST",
        path: "/api/auth/refresh",
        response: jsonResponse(sessionResponse),
      },
      {
        method: "GET",
        path: "/api/channels/me",
        response: jsonResponse({ channels: [] }),
      },
    ]);

    renderApp(["/channels"]);

    expect(await screen.findByRole("button", { name: /connect/i })).toBeInTheDocument();
    expect(screen.getByText(/no connection yet/i)).toBeInTheDocument();
  });

  it("shows disconnect and selected page state when Facebook is connected", async () => {
    createRouteHandlers([
      {
        method: "POST",
        path: "/api/auth/refresh",
        response: jsonResponse(sessionResponse),
      },
      {
        method: "GET",
        path: "/api/channels/me",
        response: jsonResponse({ channels: [connectedChannel] }),
      },
      {
        method: "GET",
        path: "/api/channels/facebook/pages",
        response: jsonResponse(facebookPagesResponse),
      },
    ]);

    renderApp(["/channels"]);

    expect(await screen.findByRole("button", { name: /disconnect/i })).toBeInTheDocument();
    expect(screen.getByText(/acme fb/i)).toBeInTheDocument();
    expect(screen.getByText(/selected page:/i)).toBeInTheDocument();
    expect(screen.getByDisplayValue(/acme page/i)).toBeInTheDocument();
  });

  it("requests the Facebook connect URL and redirects the browser", async () => {
    const redirectSpy = vi
      .spyOn(redirectModule, "redirectToExternalUrl")
      .mockImplementation(() => {});

    createRouteHandlers([
      {
        method: "POST",
        path: "/api/auth/refresh",
        response: jsonResponse(sessionResponse),
      },
      {
        method: "GET",
        path: "/api/channels/me",
        response: jsonResponse({ channels: [] }),
      },
      {
        method: "GET",
        path: "/api/channels/facebook/connect",
        response: jsonResponse({
          provider: "facebook",
          authorization_url: "https://facebook.test/oauth",
          state_expires_at: "2026-03-31T12:10:00Z",
        }),
      },
    ]);

    renderApp(["/channels"]);

    const user = userEvent.setup();
    await user.click(await screen.findByRole("button", { name: /connect/i }));

    await waitFor(() => {
      expect(redirectSpy).toHaveBeenCalledWith("https://facebook.test/oauth");
    });
  });

  it("disconnects Facebook and refreshes the card to disconnected", async () => {
    let isConnected = true;

    createRouteHandlers([
      {
        method: "POST",
        path: "/api/auth/refresh",
        response: jsonResponse(sessionResponse),
      },
      {
        method: "GET",
        path: "/api/channels/me",
        response: () =>
          jsonResponse({
            channels: isConnected ? [connectedChannel] : [],
          }),
      },
      {
        method: "GET",
        path: "/api/channels/facebook/pages",
        response: jsonResponse(facebookPagesResponse),
      },
      {
        method: "POST",
        path: "/api/channels/facebook/disconnect",
        response: () => {
          isConnected = false;
          return jsonResponse({
            provider: "facebook",
            status: "disconnected",
            message: "Facebook channel disconnected successfully.",
          });
        },
      },
    ]);

    renderApp(["/channels"]);

    const user = userEvent.setup();
    await user.click(await screen.findByRole("button", { name: /disconnect/i }));

    expect(await screen.findByRole("button", { name: /connect/i })).toBeInTheDocument();
  });

  it("selects a Facebook page and refreshes the selected page state", async () => {
    let selectedPage = connectedChannel.selected_page;

    createRouteHandlers([
      {
        method: "POST",
        path: "/api/auth/refresh",
        response: jsonResponse(sessionResponse),
      },
      {
        method: "GET",
        path: "/api/channels/me",
        response: () =>
          jsonResponse({
            channels: [
              {
                ...connectedChannel,
                selected_page: selectedPage,
              },
            ],
          }),
      },
      {
        method: "GET",
        path: "/api/channels/facebook/pages",
        response: jsonResponse(facebookPagesResponse),
      },
      {
        method: "POST",
        path: "/api/channels/facebook/pages/select",
        response: () => {
          selectedPage = {
            id: "page-2",
            name: "Launch Page",
            category: "Brand",
            has_access_token: true,
            tasks: ["CREATE_CONTENT"],
          };
          return jsonResponse({
            provider: "facebook",
            connection_id: "connection-1",
            page: selectedPage,
          });
        },
      },
    ]);

    renderApp(["/channels"]);

    const user = userEvent.setup();
    await user.selectOptions(await screen.findByRole("combobox", { name: /facebook page/i }), "page-2");

    expect(await screen.findByDisplayValue(/launch page/i)).toBeInTheDocument();
    expect(screen.getByText(/selected page:/i)).toBeInTheDocument();
  });

  it("shows callback success state from the channels query params", async () => {
    createRouteHandlers([
      {
        method: "POST",
        path: "/api/auth/refresh",
        response: jsonResponse(sessionResponse),
      },
      {
        method: "GET",
        path: "/api/channels/me",
        response: jsonResponse({ channels: [] }),
      },
    ]);

    renderApp(["/channels?provider=facebook&status=connected"]);

    expect(await screen.findByText(/facebook connected/i)).toBeInTheDocument();
  });
});

