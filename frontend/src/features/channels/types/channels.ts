export interface FacebookProfile {
  facebook_user_id: string;
  display_name: string | null;
}

export interface InstagramProfile {
  instagram_user_id: string;
  username: string | null;
  name: string | null;
  profile_picture_url: string | null;
}

export interface ChannelSummary {
  connection_id: string;
  provider: string;
  status: string;
  expires_at: string | null;
  granted_scopes: string[];
  profile: FacebookProfile | null;
  instagram_profile: InstagramProfile | null;
  selected_target_id: string | null;
  selected_target_name: string | null;
}

export interface MyChannelsResponse {
  channels: ChannelSummary[];
}

export interface FacebookConnectResponse {
  provider: string;
  authorization_url: string;
  state_expires_at: string;
}

export interface DisconnectChannelResponse {
  provider: string;
  status: string;
  message: string;
}

export interface FacebookPage {
  id: string;
  name: string;
  category: string | null;
  has_access_token: boolean;
  tasks: string[];
  instagram_profile: InstagramProfile | null;
}

export interface FacebookPagesResponse {
  provider: string;
  pages: FacebookPage[];
}

export interface SelectFacebookPageResponse {
  provider: string;
  connection_id: string;
  page: FacebookPage;
}
