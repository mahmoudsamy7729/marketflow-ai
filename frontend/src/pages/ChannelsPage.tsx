import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { getCallbackStatusBanner } from "@/features/channels/lib/callbackStatus";
import { redirectToExternalUrl } from "@/features/channels/lib/redirect";
import { supportedChannels } from "@/features/channels/lib/supportedChannels";
import {
  useChannelsQuery,
  useConnectFacebookMutation,
  useDisconnectFacebookMutation,
  useFacebookPagesQuery,
  useSelectFacebookPageMutation,
} from "@/features/channels/hooks/useChannelsData";
import type { CallbackStatusBanner } from "@/features/channels/types/channels";
import { ChannelCard } from "@/features/channels/components/ChannelCard";
import { ChannelsStatusBanner } from "@/features/channels/components/ChannelsStatusBanner";
import { ApiError } from "@/shared/api/http";
import { Card } from "@/shared/ui/Card";
import { SectionState } from "@/shared/ui/SectionState";

export function ChannelsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [banner, setBanner] = useState<CallbackStatusBanner | null>(null);
  const [pageActionError, setPageActionError] = useState<string | null>(null);
  const channelsQuery = useChannelsQuery();
  const connectFacebookMutation = useConnectFacebookMutation();
  const disconnectFacebookMutation = useDisconnectFacebookMutation();
  const facebookConnection = useMemo(
    () => channelsQuery.data?.find((channel) => channel.provider === "facebook") ?? null,
    [channelsQuery.data],
  );
  const facebookPagesQuery = useFacebookPagesQuery(facebookConnection?.status === "connected");
  const selectFacebookPageMutation = useSelectFacebookPageMutation();

  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    const nextBanner = getCallbackStatusBanner(
      searchParams.get("provider"),
      searchParams.get("status"),
      searchParams.get("code"),
    );

    if (!nextBanner) {
      return;
    }

    setBanner(nextBanner);
    void navigate(location.pathname, { replace: true });
  }, [location.pathname, location.search, navigate]);

  async function handleConnectFacebook() {
    setPageActionError(null);

    try {
      const response = await connectFacebookMutation.mutateAsync();
      redirectToExternalUrl(response.authorizationUrl);
    } catch (error) {
      setPageActionError(
        error instanceof ApiError ? error.message : "Unable to start the Facebook authorization flow.",
      );
    }
  }

  async function handleDisconnectFacebook() {
    setPageActionError(null);

    try {
      await disconnectFacebookMutation.mutateAsync();
    } catch (error) {
      setPageActionError(
        error instanceof ApiError ? error.message : "Unable to disconnect Facebook right now.",
      );
    }
  }

  async function handleSelectFacebookPage(pageId: string) {
    setPageActionError(null);

    try {
      await selectFacebookPageMutation.mutateAsync(pageId);
    } catch (error) {
      setPageActionError(
        error instanceof ApiError ? error.message : "Unable to save the Facebook page selection.",
      );
    }
  }

  return (
    <div className="space-y-6">
      <section className="rounded-[2rem] border border-white/10 bg-[linear-gradient(135deg,rgba(22,78,99,0.78),rgba(15,23,42,0.94))] px-6 py-8 shadow-[0_35px_100px_-45px_rgba(8,47,73,0.75)]">
        <p className="text-sm uppercase tracking-[0.28em] text-cyan-200/80">Integrations</p>
        <h1 className="mt-4 text-4xl font-semibold text-white">Channels</h1>
        <p className="mt-3 max-w-2xl text-sm text-slate-300">
          Connect supported publishing channels, review account state, and select the page each workspace should target.
        </p>
      </section>

      {banner ? <ChannelsStatusBanner banner={banner} /> : null}

      {pageActionError ? (
        <Card>
          <SectionState
            description={pageActionError}
            title="Channel action failed"
          />
        </Card>
      ) : null}

      {channelsQuery.isLoading ? (
        <Card>
          <SectionState
            description="Loading current channel connections and Facebook account state."
            title="Fetching channels"
          />
        </Card>
      ) : null}

      {channelsQuery.isError ? (
        <Card>
          <SectionState
            actionLabel="Retry"
            description="The channels page could not load connection state from the backend."
            onAction={() => void channelsQuery.refetch()}
            title="Unable to load channels"
          />
        </Card>
      ) : null}

      {channelsQuery.data ? (
        <div className="space-y-6">
          {supportedChannels.map((channel) => (
            <ChannelCard
              channel={channel}
              connectDisabled={connectFacebookMutation.isPending}
              connection={channel.provider === "facebook" ? facebookConnection : null}
              disconnectDisabled={disconnectFacebookMutation.isPending}
              isPagesLoading={facebookPagesQuery.isLoading}
              key={channel.provider}
              onConnect={() => {
                void handleConnectFacebook();
              }}
              onDisconnect={() => {
                void handleDisconnectFacebook();
              }}
              onSelectPage={(pageId) => {
                void handleSelectFacebookPage(pageId);
              }}
              pages={channel.provider === "facebook" ? facebookPagesQuery.data ?? [] : []}
              selectDisabled={selectFacebookPageMutation.isPending}
            />
          ))}

          {facebookConnection?.status === "connected" && facebookPagesQuery.isError ? (
            <Card>
              <SectionState
                actionLabel="Retry"
                description="Facebook is connected, but the available pages could not be loaded."
                onAction={() => void facebookPagesQuery.refetch()}
                title="Unable to load Facebook pages"
              />
            </Card>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
