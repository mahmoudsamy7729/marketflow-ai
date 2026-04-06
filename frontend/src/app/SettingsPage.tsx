import { useEffect, useState } from "react";
import { Link, Navigate } from "react-router-dom";

import {
  DashboardShell,
  dashboardSidebarNavItems,
} from "@/app/DashboardShell";
import {
  deleteMyAISettings,
  getMyAISettings,
  updateMyAISettings,
} from "@/features/ai-settings/api/aiSettingsApi";
import type { UserAISettings } from "@/features/ai-settings/types/aiSettings";
import { useAuth } from "@/features/auth/hooks/useAuth";
import { HttpError } from "@/shared/api/http";

const settingsLiveRoute = "GET /api/auth/me/ai-settings";
const settingsLiveDescription = "Authenticated BYOK settings state";

export function SettingsPage() {
  const { isAuthenticated, isLoading: isAuthLoading } = useAuth();
  const [settings, setSettings] = useState<UserAISettings | null>(null);
  const [provider, setProvider] = useState("openai");
  const [apiKey, setApiKey] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }

    let isMounted = true;

    async function loadSettings() {
      setIsLoading(true);
      setError(null);

      try {
        const response = await getMyAISettings();
        if (!isMounted) {
          return;
        }
        setSettings(response);
        setProvider(response.provider);
      } catch (requestError) {
        if (!isMounted) {
          return;
        }
        if (requestError instanceof Error) {
          setError(requestError.message);
        } else {
          setError("Unable to load AI settings.");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    void loadSettings();

    return () => {
      isMounted = false;
    };
  }, [isAuthenticated]);

  if (isAuthLoading) {
    return <div className="dashboard-boot">Restoring your workspace...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate replace to="/login" />;
  }

  async function handleSave() {
    setIsSaving(true);
    setError(null);
    setStatusMessage(null);

    try {
      const response = await updateMyAISettings({ provider, api_key: apiKey });
      setSettings(response);
      setApiKey("");
      setStatusMessage("API key validated and saved.");
    } catch (requestError) {
      if (requestError instanceof HttpError && requestError.error?.message) {
        setError(requestError.error.message);
      } else if (requestError instanceof Error) {
        setError(requestError.message);
      } else {
        setError("Unable to save AI settings.");
      }
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDelete() {
    setIsDeleting(true);
    setError(null);
    setStatusMessage(null);

    try {
      const response = await deleteMyAISettings();
      setSettings((currentValue) =>
        currentValue
          ? { ...currentValue, has_api_key: false, api_key_last4: null, is_active: false }
          : {
              provider: "openai",
              provider_display_name: "OpenAI",
              has_api_key: false,
              api_key_last4: null,
              is_active: false,
            },
      );
      setApiKey("");
      setStatusMessage(response.message);
    } catch (requestError) {
      if (requestError instanceof HttpError && requestError.error?.message) {
        setError(requestError.error.message);
      } else if (requestError instanceof Error) {
        setError(requestError.message);
      } else {
        setError("Unable to remove AI settings.");
      }
    } finally {
      setIsDeleting(false);
    }
  }

  return (
    <DashboardShell
      liveDescription={settingsLiveDescription}
      liveRoute={settingsLiveRoute}
      navAriaLabel="Settings sections"
      navItems={dashboardSidebarNavItems}
    >
      <header className="dashboard-header">
        <div>
          <p className="dashboard-kicker">Account</p>
          <h1>AI settings</h1>
          <p className="dashboard-header-copy">
            Connect your own provider key for content generation. Model selection and endpoint routing are managed by the admin workspace configuration.
          </p>
        </div>

        <div className="dashboard-header-actions">
          <Link className="button button-secondary" to="/dashboard">
            Back to dashboard
          </Link>
        </div>
      </header>

      {error ? <div className="dashboard-error">{error}</div> : null}
      {statusMessage ? <div className="channels-status">{statusMessage}</div> : null}

      {isLoading ? (
        <div className="dashboard-loading">Loading AI settings...</div>
      ) : (
        <div className="settings-grid">
          <section className="dashboard-panel">
            <div className="dashboard-section-heading">
              <div>
                <p className="dashboard-kicker">Provider</p>
                <h2>Bring your own key</h2>
              </div>
              <span className="dashboard-section-meta">
                {settings?.has_api_key ? "Configured" : "Not configured"}
              </span>
            </div>

            <div className="settings-summary">
              <div className="settings-summary-row">
                <span>Provider</span>
                <strong>{settings?.provider_display_name ?? "OpenAI"}</strong>
              </div>
              <div className="settings-summary-row">
                <span>Stored key</span>
                  <strong>
                    {settings?.has_api_key && settings.api_key_last4
                    ? `****${settings.api_key_last4}`
                    : "No key saved"}
                  </strong>
              </div>
              <div className="settings-summary-row">
                <span>Status</span>
                <strong>{settings?.is_active ? "Active" : "Missing key"}</strong>
              </div>
            </div>

            <div className="settings-form">
              <label className="settings-label" htmlFor="ai-provider">
                Provider
              </label>
              <select
                className="settings-input"
                id="ai-provider"
                onChange={(event) => setProvider(event.target.value)}
                value={provider}
              >
                <option value="openai">OpenAI</option>
              </select>

              <label className="settings-label" htmlFor="ai-api-key">
                API key
              </label>
              <input
                autoComplete="off"
                className="settings-input"
                id="ai-api-key"
                onChange={(event) => setApiKey(event.target.value)}
                placeholder="Paste your OpenAI API key"
                type="password"
                value={apiKey}
              />

              <p className="settings-note">
                The backend validates this key immediately against the admin-managed provider endpoint before it is stored.
              </p>

              <div className="settings-actions">
                <button
                  className="button button-primary"
                  disabled={isSaving || apiKey.trim().length === 0}
                  onClick={() => void handleSave()}
                  type="button"
                >
                  {isSaving ? "Saving..." : settings?.has_api_key ? "Replace key" : "Save key"}
                </button>
                <button
                  className="button button-secondary"
                  disabled={isDeleting || !settings?.has_api_key}
                  onClick={() => void handleDelete()}
                  type="button"
                >
                  {isDeleting ? "Removing..." : "Remove key"}
                </button>
              </div>
            </div>
          </section>
        </div>
      )}
    </DashboardShell>
  );
}
