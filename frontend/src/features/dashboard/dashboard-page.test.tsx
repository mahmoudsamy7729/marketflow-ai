import { screen } from "@testing-library/react";

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

function renderDashboardWithResponse(body: unknown, init: ResponseInit = {}) {
  createRouteHandlers([
    {
      method: "POST",
      path: "/api/auth/refresh",
      response: jsonResponse(sessionResponse),
    },
    {
      method: "GET",
      path: "/dashboard",
      response: jsonResponse(body, init),
    },
  ]);

  renderApp(["/dashboard"]);
}

describe("dashboard page", () => {
  it("renders populated dashboard data", async () => {
    renderDashboardWithResponse({
      overview: {
        total_campaigns: 6,
        active_campaigns: 4,
        total_posts: 32,
        draft_posts: 8,
        scheduled_posts: 10,
        published_posts: 12,
        failed_posts: 2,
      },
      connected_channels: [
        {
          channel: "facebook",
          status: "connected",
          connected_at: "2026-03-31T12:00:00Z",
          account_display_name: "Acme FB",
          selected_target_name: "Acme Page",
        },
      ],
      upcoming_posts: [
        {
          id: "post-1",
          campaign_id: "campaign-1",
          campaign_name: "Spring Launch",
          channel: "facebook",
          scheduled_for: "2026-04-01T09:00:00Z",
          status: "scheduled",
          body_preview: "New seasonal offer.",
        },
      ],
      recent_activity: [
        {
          post_id: "post-2",
          campaign_id: "campaign-1",
          campaign_name: "Spring Launch",
          channel: "facebook",
          activity_type: "published",
          occurred_at: "2026-03-31T10:00:00Z",
          body_preview: "Published yesterday.",
        },
      ],
      campaign_health: [
        {
          campaign_id: "campaign-1",
          name: "Spring Launch",
          status: "active",
          start_date: "2026-03-01",
          end_date: "2026-04-30",
          channels: ["facebook"],
          has_active_plan: true,
          planned_items_count: 12,
          generated_posts_count: 8,
          draft_posts_count: 2,
          scheduled_posts_count: 4,
          published_posts_count: 2,
          failed_posts_count: 0,
        },
      ],
    });

    expect(await screen.findByText(/channel connectivity/i)).toBeInTheDocument();
    expect(screen.getByText(/acme fb/i)).toBeInTheDocument();
    expect(screen.getByText(/new seasonal offer\./i)).toBeInTheDocument();
    expect(screen.getAllByText(/spring launch/i).length).toBeGreaterThan(0);
  });

  it("renders empty states when the dashboard lists are empty", async () => {
    renderDashboardWithResponse({
      overview: {
        total_campaigns: 0,
        active_campaigns: 0,
        total_posts: 0,
        draft_posts: 0,
        scheduled_posts: 0,
        published_posts: 0,
        failed_posts: 0,
      },
      connected_channels: [],
      upcoming_posts: [],
      recent_activity: [],
      campaign_health: [],
    });

    expect(await screen.findByText(/no connected channels/i)).toBeInTheDocument();
    expect(screen.getByText(/no upcoming posts/i)).toBeInTheDocument();
    expect(screen.getByText(/no recent activity/i)).toBeInTheDocument();
    expect(screen.getByText(/no campaigns yet/i)).toBeInTheDocument();
  });

  it("renders an error state when the dashboard request fails", async () => {
    renderDashboardWithResponse(
      {
        error: {
          code: "dashboard_failed",
          message: "Dashboard failed.",
          extra: {},
        },
      },
      { status: 500 },
    );

    expect(await screen.findByText(/unable to load dashboard/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /retry request/i })).toBeInTheDocument();
  });
});


