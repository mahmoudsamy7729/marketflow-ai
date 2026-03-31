export type SupportedChannelProvider = "facebook";

export interface SupportedChannel {
  provider: SupportedChannelProvider;
  name: string;
  description: string;
}

export interface ChannelProfile {
  facebookUserId: string;
  displayName: string | null;
}

export interface SelectedPage {
  id: string;
  name: string;
  category: string | null;
  hasAccessToken: boolean;
  tasks: string[];
}

export interface ChannelConnection {
  connectionId: string;
  provider: SupportedChannelProvider;
  status: string;
  expiresAt: string | null;
  grantedScopes: string[];
  profile: ChannelProfile;
  selectedPage: SelectedPage | null;
}

export interface FacebookConnectResult {
  provider: SupportedChannelProvider;
  authorizationUrl: string;
  stateExpiresAt: string;
}

export interface FacebookPage {
  id: string;
  name: string;
  category: string | null;
  hasAccessToken: boolean;
  tasks: string[];
}

export interface DisconnectChannelResult {
  provider: SupportedChannelProvider;
  status: string;
  message: string;
}

export interface CallbackStatusBanner {
  tone: "success" | "error";
  title: string;
  description: string;
}
