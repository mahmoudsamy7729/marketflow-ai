import { http } from "@/shared/api/http";

import type {
  DisconnectChannelResponse,
  FacebookConnectResponse,
  FacebookPagesResponse,
  MyChannelsResponse,
  SelectFacebookPageResponse,
} from "@/features/channels/types/channels";

export async function getMyChannels(): Promise<MyChannelsResponse> {
  return http.get<MyChannelsResponse>("/channels/me");
}

export async function getFacebookConnectUrl(): Promise<FacebookConnectResponse> {
  return http.get<FacebookConnectResponse>("/channels/facebook/connect");
}

export async function disconnectFacebook(): Promise<DisconnectChannelResponse> {
  return http.post<DisconnectChannelResponse>("/channels/facebook/disconnect");
}

export async function getFacebookPages(): Promise<FacebookPagesResponse> {
  return http.get<FacebookPagesResponse>("/channels/facebook/pages");
}

export async function selectFacebookPage(pageId: string): Promise<SelectFacebookPageResponse> {
  return http.post<SelectFacebookPageResponse>("/channels/facebook/pages/select", {
    page_id: pageId,
  });
}
