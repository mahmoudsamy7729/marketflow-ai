export interface UserAISettings {
  provider: string;
  provider_display_name: string | null;
  has_api_key: boolean;
  api_key_last4: string | null;
  is_active: boolean;
}

export interface UpdateUserAISettingsRequest {
  provider: string;
  api_key: string;
}

export interface AISettingsMessageResponse {
  message: string;
}

export interface AIProviderConfig {
  provider: string;
  display_name: string;
  base_url: string;
  model: string;
  is_enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface AIProviderConfigListResponse {
  providers: AIProviderConfig[];
}

export interface UpsertAIProviderConfigRequest {
  display_name: string;
  base_url: string;
  model: string;
  is_enabled: boolean;
}
