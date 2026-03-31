import { apiRequest } from "@/shared/api/http";

import type {
  Dashboard,
  DashboardCampaignHealth,
  DashboardConnectedChannel,
  DashboardRecentActivity,
  DashboardUpcomingPost,
} from "@/features/dashboard/types/dashboard";

interface DashboardOverviewDto {
  total_campaigns: number;
  active_campaigns: number;
  total_posts: number;
  draft_posts: number;
  scheduled_posts: number;
  published_posts: number;
  failed_posts: number;
}

interface DashboardConnectedChannelDto {
  channel: string;
  status: string;
  connected_at: string;
  account_display_name: string | null;
  selected_target_name: string | null;
}

interface DashboardUpcomingPostDto {
  id: string;
  campaign_id: string;
  campaign_name: string;
  channel: string;
  scheduled_for: string;
  status: string;
  body_preview: string;
}

interface DashboardRecentActivityDto {
  post_id: string;
  campaign_id: string;
  campaign_name: string;
  channel: string;
  activity_type: string;
  occurred_at: string;
  body_preview: string;
}

interface DashboardCampaignHealthDto {
  campaign_id: string;
  name: string;
  status: string;
  start_date: string;
  end_date: string;
  channels: string[];
  has_active_plan: boolean;
  planned_items_count: number;
  generated_posts_count: number;
  draft_posts_count: number;
  scheduled_posts_count: number;
  published_posts_count: number;
  failed_posts_count: number;
}

interface DashboardDto {
  overview: DashboardOverviewDto;
  connected_channels: DashboardConnectedChannelDto[];
  upcoming_posts: DashboardUpcomingPostDto[];
  recent_activity: DashboardRecentActivityDto[];
  campaign_health: DashboardCampaignHealthDto[];
}

function mapConnectedChannel(channel: DashboardConnectedChannelDto): DashboardConnectedChannel {
  return {
    channel: channel.channel,
    status: channel.status,
    connectedAt: channel.connected_at,
    accountDisplayName: channel.account_display_name,
    selectedTargetName: channel.selected_target_name,
  };
}

function mapUpcomingPost(post: DashboardUpcomingPostDto): DashboardUpcomingPost {
  return {
    id: post.id,
    campaignId: post.campaign_id,
    campaignName: post.campaign_name,
    channel: post.channel,
    scheduledFor: post.scheduled_for,
    status: post.status,
    bodyPreview: post.body_preview,
  };
}

function mapRecentActivity(activity: DashboardRecentActivityDto): DashboardRecentActivity {
  return {
    postId: activity.post_id,
    campaignId: activity.campaign_id,
    campaignName: activity.campaign_name,
    channel: activity.channel,
    activityType: activity.activity_type,
    occurredAt: activity.occurred_at,
    bodyPreview: activity.body_preview,
  };
}

function mapCampaignHealth(campaign: DashboardCampaignHealthDto): DashboardCampaignHealth {
  return {
    campaignId: campaign.campaign_id,
    name: campaign.name,
    status: campaign.status,
    startDate: campaign.start_date,
    endDate: campaign.end_date,
    channels: campaign.channels,
    hasActivePlan: campaign.has_active_plan,
    plannedItemsCount: campaign.planned_items_count,
    generatedPostsCount: campaign.generated_posts_count,
    draftPostsCount: campaign.draft_posts_count,
    scheduledPostsCount: campaign.scheduled_posts_count,
    publishedPostsCount: campaign.published_posts_count,
    failedPostsCount: campaign.failed_posts_count,
  };
}

export async function getDashboard() {
  const response = await apiRequest<DashboardDto>("/dashboard", {
    method: "GET",
    auth: true,
  });

  return {
    overview: {
      totalCampaigns: response.overview.total_campaigns,
      activeCampaigns: response.overview.active_campaigns,
      totalPosts: response.overview.total_posts,
      draftPosts: response.overview.draft_posts,
      scheduledPosts: response.overview.scheduled_posts,
      publishedPosts: response.overview.published_posts,
      failedPosts: response.overview.failed_posts,
    },
    connectedChannels: response.connected_channels.map(mapConnectedChannel),
    upcomingPosts: response.upcoming_posts.map(mapUpcomingPost),
    recentActivity: response.recent_activity.map(mapRecentActivity),
    campaignHealth: response.campaign_health.map(mapCampaignHealth),
  } satisfies Dashboard;
}

