import type { Dashboard } from "@/features/dashboard/types/dashboard";
import { formatCount, formatDate, formatDateTime } from "@/shared/lib/format";
import { Card } from "@/shared/ui/Card";
import { SectionState } from "@/shared/ui/SectionState";
import { StatusBadge } from "@/shared/ui/StatusBadge";

interface DashboardViewProps {
  dashboard: Dashboard;
}

function OverviewMetric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/[0.45] p-5">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-3 text-3xl font-semibold text-white">{value.toLocaleString()}</p>
    </div>
  );
}

export function DashboardView({ dashboard }: DashboardViewProps) {
  return (
    <div className="space-y-6">
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <OverviewMetric label="Total campaigns" value={dashboard.overview.totalCampaigns} />
        <OverviewMetric label="Active campaigns" value={dashboard.overview.activeCampaigns} />
        <OverviewMetric label="Total posts" value={dashboard.overview.totalPosts} />
        <OverviewMetric label="Published posts" value={dashboard.overview.publishedPosts} />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-xl font-semibold text-white">Channel connectivity</h2>
              <p className="mt-1 text-sm text-slate-400">
                Current connections and selected publishing targets.
              </p>
            </div>
            <StatusBadge status={`${dashboard.connectedChannels.length} connected`} />
          </div>

          <div className="mt-6 space-y-3">
            {dashboard.connectedChannels.length > 0 ? (
              dashboard.connectedChannels.map((channel) => (
                <div
                  className="rounded-2xl border border-white/10 bg-slate-950/[0.45] p-4"
                  key={`${channel.channel}-${channel.connectedAt}`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-base font-medium capitalize text-white">{channel.channel}</p>
                      <p className="text-sm text-slate-400">
                        {channel.accountDisplayName ?? "No account name available"}
                      </p>
                    </div>
                    <StatusBadge status={channel.status} />
                  </div>
                  <p className="mt-3 text-sm text-slate-400">
                    Target: {channel.selectedTargetName ?? "Not selected yet"}
                  </p>
                  <p className="mt-1 text-xs uppercase tracking-[0.2em] text-slate-500">
                    Connected {formatDateTime(channel.connectedAt)}
                  </p>
                </div>
              ))
            ) : (
              <SectionState
                description="No channels are connected yet. This layout is ready for channel onboarding next."
                title="No connected channels"
              />
            )}
          </div>
        </Card>

        <Card>
          <h2 className="text-xl font-semibold text-white">Post pipeline</h2>
          <p className="mt-1 text-sm text-slate-400">
            Draft, scheduled, and failed counts from the current dashboard snapshot.
          </p>

          <div className="mt-6 grid gap-3 sm:grid-cols-3">
            <OverviewMetric label="Draft" value={dashboard.overview.draftPosts} />
            <OverviewMetric label="Scheduled" value={dashboard.overview.scheduledPosts} />
            <OverviewMetric label="Failed" value={dashboard.overview.failedPosts} />
          </div>
        </Card>
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <Card>
          <h2 className="text-xl font-semibold text-white">Upcoming posts</h2>
          <p className="mt-1 text-sm text-slate-400">
            Scheduled content queued for publishing.
          </p>

          <div className="mt-6 space-y-3">
            {dashboard.upcomingPosts.length > 0 ? (
              dashboard.upcomingPosts.map((post) => (
                <div className="rounded-2xl border border-white/10 bg-slate-950/[0.45] p-4" key={post.id}>
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-base font-medium text-white">{post.campaignName}</p>
                      <p className="mt-1 text-sm text-slate-400">{post.bodyPreview}</p>
                    </div>
                    <StatusBadge status={post.status} />
                  </div>
                  <div className="mt-3 flex flex-wrap gap-4 text-sm text-slate-400">
                    <span className="capitalize">{post.channel}</span>
                    <span>{formatDateTime(post.scheduledFor)}</span>
                  </div>
                </div>
              ))
            ) : (
              <SectionState
                description="Scheduled posts will appear here once campaigns start generating content."
                title="No upcoming posts"
              />
            )}
          </div>
        </Card>

        <Card>
          <h2 className="text-xl font-semibold text-white">Recent activity</h2>
          <p className="mt-1 text-sm text-slate-400">
            The latest publishing-related events returned by the backend.
          </p>

          <div className="mt-6 space-y-3">
            {dashboard.recentActivity.length > 0 ? (
              dashboard.recentActivity.map((activity) => (
                <div
                  className="rounded-2xl border border-white/10 bg-slate-950/[0.45] p-4"
                  key={`${activity.postId}-${activity.occurredAt}`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-base font-medium text-white">{activity.campaignName}</p>
                      <p className="mt-1 text-sm capitalize text-cyan-100">
                        {activity.activityType.replaceAll("_", " ")}
                      </p>
                    </div>
                    <span className="text-xs uppercase tracking-[0.2em] text-slate-500">
                      {formatDateTime(activity.occurredAt)}
                    </span>
                  </div>
                  <p className="mt-3 text-sm text-slate-400">{activity.bodyPreview}</p>
                </div>
              ))
            ) : (
              <SectionState
                description="Recent publish and scheduling events will render here once the system is active."
                title="No recent activity"
              />
            )}
          </div>
        </Card>
      </section>

      <Card>
        <h2 className="text-xl font-semibold text-white">Campaign health</h2>
        <p className="mt-1 text-sm text-slate-400">
          Delivery coverage, plan presence, and output volume by campaign.
        </p>

        <div className="mt-6 space-y-3">
          {dashboard.campaignHealth.length > 0 ? (
            dashboard.campaignHealth.map((campaign) => (
              <div className="rounded-2xl border border-white/10 bg-slate-950/[0.45] p-5" key={campaign.campaignId}>
                <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                  <div>
                    <div className="flex flex-wrap items-center gap-3">
                      <p className="text-base font-medium text-white">{campaign.name}</p>
                      <StatusBadge status={campaign.status} />
                      {campaign.hasActivePlan ? (
                        <span className="rounded-full bg-cyan-500/15 px-2.5 py-1 text-xs font-medium text-cyan-100 ring-1 ring-cyan-400/20">
                          Active plan
                        </span>
                      ) : null}
                    </div>
                    <p className="mt-2 text-sm text-slate-400">
                      {formatDate(campaign.startDate)} to {formatDate(campaign.endDate)}
                    </p>
                    <p className="mt-1 text-sm text-slate-500">
                      Channels: {campaign.channels.length > 0 ? campaign.channels.join(", ") : "No channels"}
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-3 text-sm text-slate-300 sm:grid-cols-3">
                    <span>{formatCount(campaign.plannedItemsCount, "planned")}</span>
                    <span>{formatCount(campaign.generatedPostsCount, "generated")}</span>
                    <span>{formatCount(campaign.draftPostsCount, "draft")}</span>
                    <span>{formatCount(campaign.scheduledPostsCount, "scheduled")}</span>
                    <span>{formatCount(campaign.publishedPostsCount, "published")}</span>
                    <span>{formatCount(campaign.failedPostsCount, "failed")}</span>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <SectionState
              description="Campaign health will populate after the first campaign is created."
              title="No campaigns yet"
            />
          )}
        </div>
      </Card>
    </div>
  );
}

