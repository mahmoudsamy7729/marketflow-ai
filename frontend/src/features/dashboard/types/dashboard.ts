export interface DashboardOverview {
  total_campaigns: number;
  active_campaigns: number;
  total_posts: number;
  draft_posts: number;
  scheduled_posts: number;
  published_posts: number;
  failed_posts: number;
}

export interface DashboardConnectedChannel {
  channel: string;
  status: string;
  connected_at: string;
  account_display_name: string | null;
  selected_target_name: string | null;
}

export interface DashboardUpcomingPost {
  id: string;
  campaign_id: string;
  campaign_name: string;
  channel: string;
  scheduled_for: string;
  status: string;
  body_preview: string;
}

export interface DashboardRecentActivity {
  post_id: string;
  campaign_id: string;
  campaign_name: string;
  channel: string;
  activity_type: string;
  occurred_at: string;
  body_preview: string;
}

export interface DashboardCampaignHealth {
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

export interface DashboardResponse {
  overview: DashboardOverview;
  connected_channels: DashboardConnectedChannel[];
  upcoming_posts: DashboardUpcomingPost[];
  recent_activity: DashboardRecentActivity[];
  campaign_health: DashboardCampaignHealth[];
}
