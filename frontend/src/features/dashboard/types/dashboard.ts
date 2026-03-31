export interface DashboardOverview {
  totalCampaigns: number;
  activeCampaigns: number;
  totalPosts: number;
  draftPosts: number;
  scheduledPosts: number;
  publishedPosts: number;
  failedPosts: number;
}

export interface DashboardConnectedChannel {
  channel: string;
  status: string;
  connectedAt: string;
  accountDisplayName: string | null;
  selectedTargetName: string | null;
}

export interface DashboardUpcomingPost {
  id: string;
  campaignId: string;
  campaignName: string;
  channel: string;
  scheduledFor: string;
  status: string;
  bodyPreview: string;
}

export interface DashboardRecentActivity {
  postId: string;
  campaignId: string;
  campaignName: string;
  channel: string;
  activityType: string;
  occurredAt: string;
  bodyPreview: string;
}

export interface DashboardCampaignHealth {
  campaignId: string;
  name: string;
  status: string;
  startDate: string;
  endDate: string;
  channels: string[];
  hasActivePlan: boolean;
  plannedItemsCount: number;
  generatedPostsCount: number;
  draftPostsCount: number;
  scheduledPostsCount: number;
  publishedPostsCount: number;
  failedPostsCount: number;
}

export interface Dashboard {
  overview: DashboardOverview;
  connectedChannels: DashboardConnectedChannel[];
  upcomingPosts: DashboardUpcomingPost[];
  recentActivity: DashboardRecentActivity[];
  campaignHealth: DashboardCampaignHealth[];
}

