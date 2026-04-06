import { useEffect, useState } from "react";
import { Link, Navigate } from "react-router-dom";

import {
  DashboardShell,
  dashboardSidebarNavItems,
} from "@/app/DashboardShell";
import {
  listAIProviderConfigs,
  upsertAIProviderConfig,
} from "@/features/ai-settings/api/aiSettingsApi";
import type { AIProviderConfig } from "@/features/ai-settings/types/aiSettings";
import { useAuth } from "@/features/auth/hooks/useAuth";
import { HttpError } from "@/shared/api/http";

const adminLiveRoute = "GET /api/admin/ai-providers";
const adminLiveDescription = "Admin-managed AI provider routing config";

const defaultProviderConfig: AIProviderConfig = {
  provider: "openai",
  display_name: "OpenAI",
  base_url: "https://api.openai.com/v1",
  model: "gpt-5-mini",
  is_enabled: true,
  created_at: "",
  updated_at: "",
};

export function AdminAIProvidersPage() {
  const { isAuthenticated, isLoading: isAuthLoading, user } = useAuth();
  const [config, setConfig] = useState<AIProviderConfig>(defaultProviderConfig);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated || !user?.is_admin) {
      return;
    }

    let isMounted = true;

    async function loadConfigs() {
      setIsLoading(true);
      setError(null);

      try {
        const response = await listAIProviderConfigs();
        if (!isMounted) {
          return;
        }
        const openaiConfig =
          response.providers.find((item) => item.provider === "openai") ?? defaultProviderConfig;
        setConfig(openaiConfig);
      } catch (requestError) {
        if (!isMounted) {
          return;
        }
        if (requestError instanceof Error) {
          setError(requestError.message);
        } else {
          setError("Unable to load provider configuration.");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    void loadConfigs();

    return () => {
      isMounted = false;
    };
  }, [isAuthenticated, user?.is_admin]);

  if (isAuthLoading) {
    return <div className="dashboard-boot">Restoring your workspace...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate replace to="/login" />;
  }

  if (!user?.is_admin) {
    return <Navigate replace to="/dashboard" />;
  }

  async function handleSave() {
    setIsSaving(true);
    setError(null);
    setStatusMessage(null);

    try {
      const response = await upsertAIProviderConfig("openai", {
        display_name: config.display_name,
        base_url: config.base_url,
        model: config.model,
        is_enabled: config.is_enabled,
      });
      setConfig(response);
      setStatusMessage("Provider configuration saved.");
    } catch (requestError) {
      if (requestError instanceof HttpError && requestError.error?.message) {
        setError(requestError.error.message);
      } else if (requestError instanceof Error) {
        setError(requestError.message);
      } else {
        setError("Unable to save provider configuration.");
      }
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <DashboardShell
      liveDescription={adminLiveDescription}
      liveRoute={adminLiveRoute}
      navAriaLabel="Admin provider settings"
      navItems={dashboardSidebarNavItems}
    >
      <header className="dashboard-header">
        <div>
          <p className="dashboard-kicker">Admin</p>
          <h1>AI provider control</h1>
          <p className="dashboard-header-copy">
            Configure the shared endpoint and model used when authenticated users supply their own API keys.
          </p>
        </div>

        <div className="dashboard-header-actions">
          <Link className="button button-secondary" to="/settings">
            User settings
          </Link>
        </div>
      </header>

      {error ? <div className="dashboard-error">{error}</div> : null}
      {statusMessage ? <div className="channels-status">{statusMessage}</div> : null}

      {isLoading ? (
        <div className="dashboard-loading">Loading provider configuration...</div>
      ) : (
        <div className="settings-grid">
          <section className="dashboard-panel">
            <div className="dashboard-section-heading">
              <div>
                <p className="dashboard-kicker">Provider</p>
                <h2>OpenAI configuration</h2>
              </div>
              <span className="dashboard-section-meta">{config.is_enabled ? "Enabled" : "Disabled"}</span>
            </div>

            <div className="settings-form">
              <label className="settings-label" htmlFor="provider-display-name">
                Display name
              </label>
              <input
                className="settings-input"
                id="provider-display-name"
                onChange={(event) => setConfig((currentValue) => ({ ...currentValue, display_name: event.target.value }))}
                type="text"
                value={config.display_name}
              />

              <label className="settings-label" htmlFor="provider-base-url">
                Base URL
              </label>
              <input
                className="settings-input"
                id="provider-base-url"
                onChange={(event) => setConfig((currentValue) => ({ ...currentValue, base_url: event.target.value }))}
                type="text"
                value={config.base_url}
              />

              <label className="settings-label" htmlFor="provider-model">
                Model
              </label>
              <input
                className="settings-input"
                id="provider-model"
                onChange={(event) => setConfig((currentValue) => ({ ...currentValue, model: event.target.value }))}
                type="text"
                value={config.model}
              />

              <label className="settings-toggle">
                <input
                  checked={config.is_enabled}
                  onChange={(event) => setConfig((currentValue) => ({ ...currentValue, is_enabled: event.target.checked }))}
                  type="checkbox"
                />
                <span>Provider is enabled for user BYOK validation and generation</span>
              </label>

              <div className="settings-actions">
                <button className="button button-primary" disabled={isSaving} onClick={() => void handleSave()} type="button">
                  {isSaving ? "Saving..." : "Save provider config"}
                </button>
              </div>
            </div>
          </section>
        </div>
      )}
    </DashboardShell>
  );
}
