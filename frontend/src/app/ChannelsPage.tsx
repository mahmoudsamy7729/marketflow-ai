import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, Navigate } from "react-router-dom";

import {
  DashboardShell,
  dashboardSidebarLiveDescription,
  dashboardSidebarLiveRoute,
  dashboardSidebarNavItems,
} from "@/app/DashboardShell";
import { useAuth } from "@/features/auth/hooks/useAuth";
import {
  disconnectFacebook,
  getFacebookPages,
  getFacebookConnectUrl,
  getMyChannels,
  selectFacebookPage,
} from "@/features/channels/api/channelsApi";
import type {
  ChannelSummary,
  FacebookPage,
  MyChannelsResponse,
} from "@/features/channels/types/channels";
import { HttpError } from "@/shared/api/http";

interface ChannelCardData {
  provider: "facebook" | "instagram";
  title: string;
  subtitle: string;
  imageSrc: string;
  imageAlt: string;
  summary: ChannelSummary | null;
}

const channelCatalog: Omit<ChannelCardData, "summary">[] = [
  {
    provider: "facebook",
    title: "Facebook",
    subtitle: "Connect a page and publish content through the current live workflow.",
    imageSrc: "/facebook.png",
    imageAlt: "Facebook logo",
  },
  {
    provider: "instagram",
    title: "Instagram",
    subtitle: "Available when your selected Facebook page includes a linked Instagram business account.",
    imageSrc: "/instagram.png",
    imageAlt: "Instagram logo",
  },
] as const;

function formatDateTime(value: string | null): string {
  if (!value) {
    return "No expiry";
  }

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

function ChannelDetailList({ channel }: { channel: ChannelSummary }) {
  const rows =
    channel.provider === "facebook"
      ? [
          {
            label: "Profile",
            value: channel.profile?.display_name ?? "Connected account",
          },
          {
            label: "Selected target",
            value: channel.selected_target_name ?? "No page selected yet",
          },
          {
            label: "Scopes",
            value: channel.granted_scopes.length > 0 ? channel.granted_scopes.join(", ") : "No scopes recorded",
          },
          {
            label: "Token expiry",
            value: formatDateTime(channel.expires_at),
          },
        ]
      : [
          {
            label: "Profile",
            value:
              channel.instagram_profile?.name ??
              channel.instagram_profile?.username ??
              "Instagram profile",
          },
          {
            label: "Username",
            value: channel.instagram_profile?.username ?? "Unavailable",
          },
          {
            label: "Selected target",
            value: channel.selected_target_name ?? "Linked through Facebook page",
          },
          {
            label: "Token expiry",
            value: formatDateTime(channel.expires_at),
          },
        ];

  return (
    <div className="channels-details">
      {rows.map((row) => (
        <div className="channels-detail-row" key={row.label}>
          <span>{row.label}</span>
          <strong>{row.value}</strong>
        </div>
      ))}
    </div>
  );
}

export function ChannelsPage() {
  const { isAuthenticated, isLoading: isAuthLoading } = useAuth();
  const [channelsResponse, setChannelsResponse] = useState<MyChannelsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isConnecting, setIsConnecting] = useState<"facebook" | "instagram" | null>(null);
  const [isDisconnecting, setIsDisconnecting] = useState<"facebook" | "instagram" | null>(null);
  const [isCompletingConnection, setIsCompletingConnection] = useState(false);
  const [facebookPages, setFacebookPages] = useState<FacebookPage[]>([]);
  const [isPageChooserOpen, setIsPageChooserOpen] = useState(false);
  const [isLoadingPages, setIsLoadingPages] = useState(false);
  const [isSelectingPage, setIsSelectingPage] = useState(false);
  const [selectedPageId, setSelectedPageId] = useState("");
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const popupRef = useRef<Window | null>(null);
  const popupPollRef = useRef<number | null>(null);

  const loadChannels = useCallback(async (mode: "initial" | "refresh" = "initial") => {
    if (mode === "initial") {
      setIsLoading(true);
    } else {
      setIsCompletingConnection(true);
    }

    setError(null);

    try {
      const response = await getMyChannels();
      setChannelsResponse(response);
    } catch (requestError) {
      if (requestError instanceof HttpError && requestError.status === 401) {
        setError("Your session expired. Sign in again to load your channels.");
      } else if (requestError instanceof Error) {
        setError(requestError.message);
      } else {
        setError("Unable to load channels right now.");
      }
    } finally {
      setIsLoading(false);
      setIsCompletingConnection(false);
    }
  }, []);

  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }

    void loadChannels();
  }, [isAuthenticated, loadChannels]);

  useEffect(() => {
    function clearPopupState() {
      setIsConnecting(null);
      setIsCompletingConnection(false);

      if (popupPollRef.current !== null) {
        window.clearInterval(popupPollRef.current);
        popupPollRef.current = null;
      }
    }

    function handleMessage(event: MessageEvent) {
      if (event.origin !== window.location.origin) {
        return;
      }

      const payload = event.data as {
        code: string | null;
        message: string;
        provider: string;
        source?: string;
        status: "success" | "error";
      };

      if (payload?.source !== "channels-oauth-callback") {
        return;
      }

      if (popupRef.current && !popupRef.current.closed) {
        popupRef.current.close();
      }

      if (payload.status === "success") {
        setIsConnecting(payload.provider as "facebook" | "instagram");
        setIsCompletingConnection(true);
        void loadChannels("refresh");
      } else {
        setError(payload.message || "Channel connection failed.");
        clearPopupState();
      }
    }

    window.addEventListener("message", handleMessage);

    return () => {
      window.removeEventListener("message", handleMessage);
      clearPopupState();
    };
  }, [loadChannels]);

  const channelCards = useMemo<ChannelCardData[]>(() => {
    const channels = channelsResponse?.channels ?? [];

    return channelCatalog.map((channel) => ({
      ...channel,
      summary: channels.find((item) => item.provider === channel.provider) ?? null,
    }));
  }, [channelsResponse]);

  const facebookChannel = useMemo(
    () => channelCards.find((channel) => channel.provider === "facebook")?.summary ?? null,
    [channelCards],
  );

  const selectedFacebookPage = useMemo(
    () => facebookPages.find((page) => page.id === selectedPageId) ?? null,
    [facebookPages, selectedPageId],
  );

  useEffect(() => {
    if (!facebookChannel) {
      setIsPageChooserOpen(false);
      setFacebookPages([]);
      setSelectedPageId("");
      return;
    }

    if (!selectedPageId && facebookChannel.selected_target_id) {
      setSelectedPageId(facebookChannel.selected_target_id);
    }
  }, [facebookChannel, selectedPageId]);

  if (isAuthLoading) {
    return <div className="dashboard-boot">Restoring your workspace...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate replace to="/login" />;
  }

  async function handleConnect(provider: "facebook" | "instagram") {
    setIsConnecting(provider);
    setError(null);
    setStatusMessage(null);

    try {
      const response = await getFacebookConnectUrl();
      const popup = window.open(
        response.authorization_url,
        "channel-connect-popup",
        "width=720,height=820,menubar=no,toolbar=no,location=yes,status=no,resizable=yes,scrollbars=yes",
      );

      if (!popup) {
        throw new Error("Popup blocked. Please allow popups and try again.");
      }

      popupRef.current = popup;

      if (popupPollRef.current !== null) {
        window.clearInterval(popupPollRef.current);
      }

      popupPollRef.current = window.setInterval(() => {
        if (popupRef.current?.closed) {
          window.clearInterval(popupPollRef.current ?? undefined);
          popupPollRef.current = null;
          popupRef.current = null;
          setIsConnecting(null);
        }
      }, 400);
    } catch (requestError) {
      if (requestError instanceof Error) {
        setError(requestError.message);
      } else {
        setError("Unable to start the connection flow.");
      }
      setIsConnecting(null);
    }
  }

  async function handleDisconnect(provider: "facebook" | "instagram") {
    setIsDisconnecting(provider);
    setError(null);
    setStatusMessage(null);

    try {
      const response = await disconnectFacebook();
      setStatusMessage(response.message);
      await loadChannels("refresh");
    } catch (requestError) {
      if (requestError instanceof Error) {
        setError(requestError.message);
      } else {
        setError("Unable to disconnect the channel right now.");
      }
    } finally {
      setIsDisconnecting(null);
    }
  }

  async function handleTogglePageChooser() {
    if (isPageChooserOpen) {
      setIsPageChooserOpen(false);
      return;
    }

    setIsPageChooserOpen(true);
    setIsLoadingPages(true);
    setError(null);
    setStatusMessage(null);

    try {
      const response = await getFacebookPages();
      setFacebookPages(response.pages);

      const defaultPageId =
        facebookChannel?.selected_target_id ??
        response.pages.find((page) => page.has_access_token)?.id ??
        response.pages[0]?.id ??
        "";

      setSelectedPageId((currentValue) => {
        if (currentValue && response.pages.some((page) => page.id === currentValue)) {
          return currentValue;
        }

        return defaultPageId;
      });
    } catch (requestError) {
      setIsPageChooserOpen(false);

      if (requestError instanceof Error) {
        setError(requestError.message);
      } else {
        setError("Unable to load Facebook pages right now.");
      }
    } finally {
      setIsLoadingPages(false);
    }
  }

  async function handleSelectPage() {
    if (!selectedPageId) {
      setError("Choose a Facebook page first.");
      return;
    }

    setIsSelectingPage(true);
    setError(null);
    setStatusMessage(null);

    try {
      const response = await selectFacebookPage(selectedPageId);
      setStatusMessage(`Publishing page updated to ${response.page.name}.`);
      await loadChannels("refresh");
      setIsPageChooserOpen(false);
    } catch (requestError) {
      if (requestError instanceof Error) {
        setError(requestError.message);
      } else {
        setError("Unable to save the selected Facebook page.");
      }
    } finally {
      setIsSelectingPage(false);
    }
  }

  return (
    <DashboardShell
      liveDescription={dashboardSidebarLiveDescription}
      liveRoute={dashboardSidebarLiveRoute}
      navAriaLabel="Channels sections"
      navItems={dashboardSidebarNavItems}
    >
        <header className="dashboard-header">
          <div>
            <p className="dashboard-kicker">Channels</p>
            <h1>Publishing channels</h1>
            <p className="dashboard-header-copy">
              View the channels currently supported in the system and see whether each one is connected, linked, or still waiting for activation.
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

        {isCompletingConnection ? (
          <div className="channels-syncing">
            Refreshing channel workspace data...
          </div>
        ) : null}

        {isLoading ? (
          <div className="dashboard-loading">Loading channels...</div>
        ) : (
          <section className="channels-grid" id="available-channels">
            {channelCards.map((channel) => {
              const isConnected = channel.summary?.status === "connected";
              const actionLabel =
                channel.provider === "instagram" && !isConnected
                  ? "Connect through Facebook"
                  : "Connect";

              return (
                <article className="channels-card" key={channel.provider}>
                  <div className="channels-card-top">
                    <img
                      alt={channel.imageAlt}
                      className="channels-logo"
                      src={channel.imageSrc}
                    />

                    <div className="channels-copy">
                      <div className="channels-heading-row">
                        <h2>{channel.title}</h2>
                        <span className={`channels-badge ${isConnected ? "is-connected" : "is-idle"}`}>
                          {isConnected ? "Connected" : "Not connected"}
                        </span>
                      </div>
                      <p>{channel.subtitle}</p>
                    </div>
                  </div>

                  {isConnected && channel.summary ? (
                    <ChannelDetailList channel={channel.summary} />
                  ) : (
                    <div className="channels-empty-state">
                      <strong>
                        {channel.provider === "instagram"
                          ? "Instagram is activated by selecting a Facebook page with a linked Instagram business account."
                          : "Facebook connection is required before channel publishing can begin."}
                      </strong>
                      <p>
                        {channel.provider === "instagram"
                          ? "Start with Facebook OAuth, then select the page that owns the Instagram business profile."
                          : "Run the Facebook OAuth flow to store the channel connection and selected publishing target."}
                      </p>
                    </div>
                  )}

                  {isConnected && channel.provider === "facebook" ? (
                    <div className="channels-page-picker">
                      <div className="channels-page-picker-header">
                        <div>
                          <strong>
                            {channel.summary?.selected_target_name ? "Publishing page selected" : "Choose your publishing page"}
                          </strong>
                          <p>
                            Pick the Facebook page this workspace should post to. Instagram availability depends on the selected page.
                          </p>
                        </div>

                        <button
                          className="button button-secondary"
                          disabled={isConnecting !== null || isDisconnecting !== null || isSelectingPage}
                          onClick={() => void handleTogglePageChooser()}
                          type="button"
                        >
                          {isPageChooserOpen
                            ? "Hide pages"
                            : channel.summary?.selected_target_id
                              ? "Change page"
                              : "Choose page"}
                        </button>
                      </div>

                      {isPageChooserOpen ? (
                        isLoadingPages ? (
                          <div className="channels-page-picker-state">Loading available Facebook pages...</div>
                        ) : facebookPages.length > 0 ? (
                          <div className="channels-page-picker-form">
                            <label className="channels-page-picker-label" htmlFor="facebook-page-select">
                              Available pages
                            </label>
                            <select
                              className="channels-page-select"
                              id="facebook-page-select"
                              onChange={(event) => setSelectedPageId(event.target.value)}
                              value={selectedPageId}
                            >
                              <option disabled value="">
                                Select a Facebook page
                              </option>
                              {facebookPages.map((page) => (
                                <option key={page.id} value={page.id}>
                                  {page.name}
                                  {page.instagram_profile ? " • Instagram linked" : ""}
                                </option>
                              ))}
                            </select>

                            {selectedFacebookPage ? (
                              <div className="channels-page-meta">
                                <div className="channels-page-meta-row">
                                  <span>Category</span>
                                  <strong>{selectedFacebookPage.category ?? "Uncategorized"}</strong>
                                </div>
                                <div className="channels-page-meta-row">
                                  <span>Linked Instagram</span>
                                  <strong>
                                    {selectedFacebookPage.instagram_profile?.username ??
                                      selectedFacebookPage.instagram_profile?.name ??
                                      "Not linked"}
                                  </strong>
                                </div>
                                <div className="channels-page-meta-row">
                                  <span>Tasks</span>
                                  <strong>
                                    {selectedFacebookPage.tasks.length > 0
                                      ? selectedFacebookPage.tasks.join(", ")
                                      : "No tasks returned"}
                                  </strong>
                                </div>
                              </div>
                            ) : null}

                            <div className="channels-page-picker-actions">
                              <button
                                className="button button-primary"
                                disabled={!selectedPageId || isSelectingPage}
                                onClick={() => void handleSelectPage()}
                                type="button"
                              >
                                {isSelectingPage ? "Saving..." : "Save page"}
                              </button>
                            </div>
                          </div>
                        ) : (
                          <div className="channels-page-picker-state">
                            No Facebook pages were returned for this account.
                          </div>
                        )
                      ) : null}
                    </div>
                  ) : null}

                  <div className="channels-actions">
                    {!isConnected ? (
                      <button
                        className="button button-primary"
                        disabled={isConnecting !== null || isDisconnecting !== null}
                        onClick={() => void handleConnect(channel.provider)}
                        type="button"
                      >
                        {isConnecting === channel.provider ? "Connecting..." : actionLabel}
                      </button>
                    ) : (
                      <>
                        <span className="channels-footnote">
                          {channel.provider === "facebook"
                            ? "Facebook page and publish target are available."
                            : "Instagram is linked through your selected Facebook page. Disconnecting here removes the Facebook connection too."}
                        </span>
                        <button
                          className="button button-secondary"
                          disabled={isConnecting !== null || isDisconnecting !== null}
                          onClick={() => void handleDisconnect(channel.provider)}
                          type="button"
                        >
                          {isDisconnecting === channel.provider ? "Disconnecting..." : "Disconnect"}
                        </button>
                      </>
                    )}
                  </div>
                </article>
              );
            })}
          </section>
        )}
    </DashboardShell>
  );
}
