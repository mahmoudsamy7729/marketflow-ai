import { useEffect, useState } from "react";
import { Link, Navigate } from "react-router-dom";

import {
  DashboardShell,
  dashboardSidebarLiveDescription,
  dashboardSidebarLiveRoute,
  dashboardSidebarNavItems,
} from "@/app/DashboardShell";
import { getDashboard } from "@/features/dashboard/api/dashboardApi";
import { useAuth } from "@/features/auth/hooks/useAuth";
import { HttpError } from "@/shared/api/http";
import type {
  DashboardCampaignHealth,
  DashboardConnectedChannel,
  DashboardRecentActivity,
  DashboardResponse,
  DashboardUpcomingPost,
} from "@/features/dashboard/types/dashboard";

const overviewMeta = [
  { key: "total_campaigns", label: "Total campaigns" },
  { key: "active_campaigns", label: "Active campaigns" },
  { key: "total_posts", label: "Total posts" },
  { key: "draft_posts", label: "Draft posts" },
  { key: "scheduled_posts", label: "Scheduled posts" },
  { key: "published_posts", label: "Published posts" },
  { key: "failed_posts", label: "Failed posts" },
] as const;

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
  }).format(new Date(value));
}

function formatChannelName(value: string): string {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function EmptyMessage({ body, title }: { body: string; title: string }) {
  return (
    <div className="dashboard-empty">
      <strong>{title}</strong>
      <p>{body}</p>
    </div>
  );
}

function ChannelSection({ channels }: { channels: DashboardConnectedChannel[] }) {
  return (
    <section className="dashboard-panel">
      <div className="dashboard-section-heading">
        <div>
          <p className="dashboard-kicker">Channels</p>
          <h2>Connected channels</h2>
        </div>
        <span className="dashboard-section-meta">{channels.length} active links</span>
      </div>

      {channels.length === 0 ? (
        <EmptyMessage
          body="No publishing channels are connected yet. Connect a channel to start campaign execution."
          title="No connected channels"
        />
      ) : (
        <div className="dashboard-channel-list">
          {channels.map((channel) => (
            <article className="dashboard-channel-row" key={`${channel.channel}-${channel.connected_at}`}>
              <div className="dashboard-channel-main">
                <div className="dashboard-channel-name">
                  <span className="dashboard-dot" />
                  <strong>{formatChannelName(channel.channel)}</strong>
                </div>
                <p>
                  {channel.account_display_name ?? "Unknown account"}
                  {" · "}
                  {channel.selected_target_name ?? "No selected target"}
                </p>
              </div>
              <div className="dashboard-channel-meta">
                <span>{channel.status}</span>
                <time dateTime={channel.connected_at}>{formatDateTime(channel.connected_at)}</time>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

function UpcomingSection({ posts }: { posts: DashboardUpcomingPost[] }) {
  return (
    <section className="dashboard-panel">
      <div className="dashboard-section-heading">
        <div>
          <p className="dashboard-kicker">Queue</p>
          <h2>Upcoming posts</h2>
        </div>
        <span className="dashboard-section-meta">Next {posts.length} items</span>
      </div>

      {posts.length === 0 ? (
        <EmptyMessage
          body="No scheduled posts are in the queue right now."
          title="Queue is empty"
        />
      ) : (
        <div className="dashboard-list">
          {posts.map((post) => (
            <article className="dashboard-list-row" key={post.id}>
              <div className="dashboard-list-main">
                <div className="dashboard-list-topline">
                  <strong>{post.campaign_name}</strong>
                  <span>{formatChannelName(post.channel)}</span>
                </div>
                <p>{post.body_preview}</p>
              </div>
              <div className="dashboard-list-side">
                <span className="dashboard-status">{post.status}</span>
                <time dateTime={post.scheduled_for}>{formatDateTime(post.scheduled_for)}</time>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

function ActivitySection({ items }: { items: DashboardRecentActivity[] }) {
  return (
    <section className="dashboard-panel">
      <div className="dashboard-section-heading">
        <div>
          <p className="dashboard-kicker">Activity</p>
          <h2>Recent activity</h2>
        </div>
        <span className="dashboard-section-meta">Latest execution log</span>
      </div>

      {items.length === 0 ? (
        <EmptyMessage
          body="Activity will appear here as posts are published, scheduled, or updated."
          title="No recent activity"
        />
      ) : (
        <div className="dashboard-list">
          {items.map((item) => (
            <article className="dashboard-list-row" key={item.post_id}>
              <div className="dashboard-list-main">
                <div className="dashboard-list-topline">
                  <strong>{item.campaign_name}</strong>
                  <span>{formatChannelName(item.channel)}</span>
                </div>
                <p>{item.body_preview}</p>
              </div>
              <div className="dashboard-list-side">
                <span className="dashboard-status">{item.activity_type}</span>
                <time dateTime={item.occurred_at}>{formatDateTime(item.occurred_at)}</time>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

function HealthSection({ campaigns }: { campaigns: DashboardCampaignHealth[] }) {
  return (
    <section className="dashboard-panel dashboard-panel-wide">
      <div className="dashboard-section-heading">
        <div>
          <p className="dashboard-kicker">Campaigns</p>
          <h2>Campaign health</h2>
        </div>
        <span className="dashboard-section-meta">{campaigns.length} tracked campaigns</span>
      </div>

      {campaigns.length === 0 ? (
        <EmptyMessage
          body="Create a campaign to start tracking plan depth, output, and publishing status."
          title="No campaign health data"
        />
      ) : (
        <div className="dashboard-health-table">
          <div className="dashboard-health-head">
            <span>Campaign</span>
            <span>Window</span>
            <span>Channels</span>
            <span>Plan</span>
            <span>Output</span>
            <span>Status</span>
          </div>

          {campaigns.map((campaign) => (
            <article className="dashboard-health-row" key={campaign.campaign_id}>
              <div className="dashboard-health-cell">
                <strong>{campaign.name}</strong>
                <span>{campaign.has_active_plan ? "Active plan attached" : "No active plan"}</span>
              </div>
              <div className="dashboard-health-cell">
                <strong>
                  {formatDate(campaign.start_date)} - {formatDate(campaign.end_date)}
                </strong>
                <span>{campaign.status}</span>
              </div>
              <div className="dashboard-health-cell">
                <strong>{campaign.channels.map(formatChannelName).join(", ")}</strong>
                <span>{campaign.channels.length} selected</span>
              </div>
              <div className="dashboard-health-cell">
                <strong>{campaign.planned_items_count} planned</strong>
                <span>{campaign.generated_posts_count} generated</span>
              </div>
              <div className="dashboard-health-cell">
                <strong>{campaign.scheduled_posts_count} scheduled</strong>
                <span>{campaign.published_posts_count} published</span>
              </div>
              <div className="dashboard-health-cell">
                <strong>{campaign.failed_posts_count} failed</strong>
                <span>{campaign.draft_posts_count} drafts</span>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

export function DashboardPage() {
  const { isAuthenticated, isLoading: isAuthLoading } = useAuth();
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }

    let isMounted = true;

    async function loadDashboard(refresh = false) {
      if (refresh) {
        setIsRefreshing(true);
      } else {
        setIsLoading(true);
      }

      setError(null);

      try {
        const response = await getDashboard();

        if (isMounted) {
          setDashboard(response);
        }
      } catch (requestError) {
        if (!isMounted) {
          return;
        }

        if (requestError instanceof HttpError && requestError.status === 401) {
          setError("Your session is no longer valid. Sign in again to load the dashboard.");
          return;
        }

        if (requestError instanceof Error) {
          setError(requestError.message);
        } else {
          setError("Unable to load dashboard data right now.");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
          setIsRefreshing(false);
        }
      }
    }

    void loadDashboard();

    return () => {
      isMounted = false;
    };
  }, [isAuthenticated]);

  if (isAuthLoading) {
    return <div className="dashboard-boot">Restoring your workspace...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate replace to="/login" />;
  }

  async function handleRefresh() {
    try {
      setIsRefreshing(true);
      setError(null);
      const response = await getDashboard();
      setDashboard(response);
    } catch (requestError) {
      if (requestError instanceof Error) {
        setError(requestError.message);
      } else {
        setError("Unable to refresh dashboard data.");
      }
    } finally {
      setIsRefreshing(false);
    }
  }

  return (
    <DashboardShell
      liveDescription={dashboardSidebarLiveDescription}
      liveRoute={dashboardSidebarLiveRoute}
      navAriaLabel="Dashboard sections"
      navItems={dashboardSidebarNavItems}
    >
        <header className="dashboard-header">
          <div>
            <p className="dashboard-kicker">Operations</p>
            <h1>Campaign command center</h1>
            <p className="dashboard-header-copy">
              Full-width visibility into campaign volume, channel state, queued posts,
              recent execution, and campaign health.
            </p>
          </div>

          <div className="dashboard-header-actions">
            <Link className="button button-secondary" to="/">
              Back to site
            </Link>
            <button
              className="button button-primary"
              onClick={() => void handleRefresh()}
              type="button"
            >
              {isRefreshing ? "Refreshing..." : "Refresh data"}
            </button>
          </div>
        </header>

        {error ? <div className="dashboard-error">{error}</div> : null}

        {isLoading ? (
          <div className="dashboard-loading">Loading dashboard data...</div>
        ) : dashboard ? (
          <>
            <section className="dashboard-overview" id="overview">
              {overviewMeta.map((item) => (
                <article className="dashboard-stat" key={item.key}>
                  <span>{item.label}</span>
                  <strong>{dashboard.overview[item.key]}</strong>
                </article>
              ))}
            </section>

            <div className="dashboard-grid">
              <div className="dashboard-column">
                <div id="channels">
                  <ChannelSection channels={dashboard.connected_channels} />
                </div>
                <div id="queue">
                  <UpcomingSection posts={dashboard.upcoming_posts} />
                </div>
              </div>

              <div className="dashboard-column">
                <div id="activity">
                  <ActivitySection items={dashboard.recent_activity} />
                </div>
              </div>
            </div>

            <div id="health">
              <HealthSection campaigns={dashboard.campaign_health} />
            </div>
          </>
        ) : (
          <div className="dashboard-loading">No dashboard data returned.</div>
        )}
    </DashboardShell>
  );
}
