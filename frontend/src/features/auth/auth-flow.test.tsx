import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

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

describe("auth flow", () => {
  it("logs in and redirects to the dashboard", async () => {
    createRouteHandlers([
      {
        method: "POST",
        path: "/api/auth/refresh",
        response: () => createUnauthorizedResponse(),
      },
      {
        method: "POST",
        path: "/api/auth/login",
        response: jsonResponse(sessionResponse),
      },
      {
        method: "GET",
        path: "/dashboard",
        response: jsonResponse(dashboardResponse),
      },
    ]);

    renderApp(["/login"]);

    const user = userEvent.setup();
    await user.type(await screen.findByLabelText(/email/i), "owner@example.com");
    await user.type(screen.getByLabelText(/password/i), "password123");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    expect(await screen.findByRole("heading", { name: /dashboard/i })).toBeInTheDocument();
    expect(screen.getByText(/acme studio/i)).toBeInTheDocument();
  });

  it("registers a user and lands on the dashboard", async () => {
    createRouteHandlers([
      {
        method: "POST",
        path: "/api/auth/refresh",
        response: () => createUnauthorizedResponse(),
      },
      {
        method: "POST",
        path: "/api/auth/register",
        response: jsonResponse(sessionResponse, { status: 201 }),
      },
      {
        method: "GET",
        path: "/dashboard",
        response: jsonResponse(dashboardResponse),
      },
    ]);

    renderApp(["/register"]);

    const user = userEvent.setup();
    await user.type(await screen.findByLabelText(/company name/i), "Acme Studio");
    await user.type(screen.getByLabelText(/email/i), "owner@example.com");
    await user.type(screen.getByLabelText(/password/i), "password123");
    await user.click(screen.getByRole("button", { name: /create account/i }));

    expect(await screen.findByRole("heading", { name: /dashboard/i })).toBeInTheDocument();
  });

  it("restores the session on page load via refresh cookie", async () => {
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
    ]);

    renderApp(["/dashboard"]);

    expect(await screen.findByRole("heading", { name: /dashboard/i })).toBeInTheDocument();
    expect(screen.getByText(/owner@example.com/i)).toBeInTheDocument();
  });

  it("redirects to login when refresh restoration fails", async () => {
    createRouteHandlers([
      {
        method: "POST",
        path: "/api/auth/refresh",
        response: () => createUnauthorizedResponse(),
      },
    ]);

    renderApp(["/dashboard"]);

    expect(await screen.findByRole("heading", { name: /welcome back/i })).toBeInTheDocument();
  });

  it("clears auth state on logout", async () => {
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
        method: "POST",
        path: "/api/auth/logout",
        response: jsonResponse({ message: "Logout successful." }),
      },
    ]);

    renderApp(["/dashboard"]);

    const user = userEvent.setup();
    await user.click(await screen.findByRole("button", { name: /sign out/i }));

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: /welcome back/i })).toBeInTheDocument();
    });
  });
});


