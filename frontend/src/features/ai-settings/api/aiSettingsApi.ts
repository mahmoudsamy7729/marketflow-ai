import { http } from "@/shared/api/http";
import type {
  AIProviderConfig,
  AIProviderConfigListResponse,
  AISettingsMessageResponse,
  UpdateUserAISettingsRequest,
  UpsertAIProviderConfigRequest,
  UserAISettings,
} from "@/features/ai-settings/types/aiSettings";

export async function getMyAISettings(): Promise<UserAISettings> {
  return http.get<UserAISettings>("/auth/me/ai-settings");
}

export async function updateMyAISettings(payload: UpdateUserAISettingsRequest): Promise<UserAISettings> {
  return http.put<UserAISettings>("/auth/me/ai-settings", payload);
}

export async function deleteMyAISettings(): Promise<AISettingsMessageResponse> {
  return http.delete<AISettingsMessageResponse>("/auth/me/ai-settings");
}

export async function listAIProviderConfigs(): Promise<AIProviderConfigListResponse> {
  return http.get<AIProviderConfigListResponse>("/admin/ai-providers");
}

export async function upsertAIProviderConfig(
  provider: string,
  payload: UpsertAIProviderConfigRequest,
): Promise<AIProviderConfig> {
  return http.put<AIProviderConfig>(`/admin/ai-providers/${provider}`, payload);
}
