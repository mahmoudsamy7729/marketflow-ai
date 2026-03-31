import { apiRequest } from "@/shared/api/http";

import type {
  ChannelConnection,
  DisconnectChannelResult,
  FacebookConnectResult,
  FacebookPage,
  SelectedPage,
} from "@/features/channels/types/channels";

interface SelectedPageDto {
  id: string;
  name: string;
  category: string | null;
  has_access_token: boolean;
  tasks: string[];
}

interface ChannelConnectionDto {
  connection_id: string;
  provider: "facebook";
  status: string;
  expires_at: string | null;
  granted_scopes: string[];
  profile: {
    facebook_user_id: string;
    display_name: string | null;
  };
  selected_page: SelectedPageDto | null;
}

interface MyChannelsResponseDto {
  channels: ChannelConnectionDto[];
}

interface FacebookConnectResponseDto {
  provider: "facebook";
  authorization_url: string;
  state_expires_at: string;
}

interface FacebookPageDto {
  id: string;
  name: string;
  category: string | null;
  has_access_token: boolean;
  tasks: string[];
}

interface FacebookPagesResponseDto {
  provider: "facebook";
  pages: FacebookPageDto[];
}

interface DisconnectChannelResponseDto {
  provider: "facebook";
  status: string;
  message: string;
}

function mapSelectedPage(page: SelectedPageDto): SelectedPage {
  return {
    id: page.id,
    name: page.name,
    category: page.category,
    hasAccessToken: page.has_access_token,
    tasks: page.tasks,
  };
}

function mapConnection(connection: ChannelConnectionDto): ChannelConnection {
  return {
    connectionId: connection.connection_id,
    provider: connection.provider,
    status: connection.status,
    expiresAt: connection.expires_at,
    grantedScopes: connection.granted_scopes,
    profile: {
      facebookUserId: connection.profile.facebook_user_id,
      displayName: connection.profile.display_name,
    },
    selectedPage: connection.selected_page
      ? mapSelectedPage(connection.selected_page)
      : null,
  };
}

function mapFacebookPage(page: FacebookPageDto): FacebookPage {
  return {
    id: page.id,
    name: page.name,
    category: page.category,
    hasAccessToken: page.has_access_token,
    tasks: page.tasks,
  };
}

export async function getMyChannels() {
  const response = await apiRequest<MyChannelsResponseDto>("/api/channels/me", {
    method: "GET",
    auth: true,
  });

  return response.channels.map(mapConnection);
}

export async function getFacebookConnectUrl() {
  const response = await apiRequest<FacebookConnectResponseDto>("/api/channels/facebook/connect", {
    method: "GET",
    auth: true,
  });

  return {
    provider: response.provider,
    authorizationUrl: response.authorization_url,
    stateExpiresAt: response.state_expires_at,
  } satisfies FacebookConnectResult;
}

export async function disconnectFacebook() {
  const response = await apiRequest<DisconnectChannelResponseDto>("/api/channels/facebook/disconnect", {
    method: "POST",
    auth: true,
  });

  return {
    provider: response.provider,
    status: response.status,
    message: response.message,
  } satisfies DisconnectChannelResult;
}

export async function getFacebookPages() {
  const response = await apiRequest<FacebookPagesResponseDto>("/api/channels/facebook/pages", {
    method: "GET",
    auth: true,
  });

  return response.pages.map(mapFacebookPage);
}

export async function selectFacebookPage(pageId: string) {
  const response = await apiRequest<{ page: SelectedPageDto }>("/api/channels/facebook/pages/select", {
    method: "POST",
    auth: true,
    body: {
      page_id: pageId,
    },
  });

  return mapSelectedPage(response.page);
}
