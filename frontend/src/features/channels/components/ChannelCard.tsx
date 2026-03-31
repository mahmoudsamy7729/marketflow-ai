import { useMemo } from "react";

import type { ChannelConnection, FacebookPage, SupportedChannel } from "@/features/channels/types/channels";
import { Button } from "@/shared/ui/Button";
import { Card } from "@/shared/ui/Card";
import { StatusBadge } from "@/shared/ui/StatusBadge";

interface ChannelCardProps {
  channel: SupportedChannel;
  connection: ChannelConnection | null;
  connectDisabled?: boolean;
  disconnectDisabled?: boolean;
  isPagesLoading?: boolean;
  onConnect: () => void;
  onDisconnect: () => void;
  onSelectPage: (pageId: string) => void;
  pages: FacebookPage[];
  selectDisabled?: boolean;
}

export function ChannelCard({
  channel,
  connection,
  connectDisabled = false,
  disconnectDisabled = false,
  isPagesLoading = false,
  onConnect,
  onDisconnect,
  onSelectPage,
  pages,
  selectDisabled = false,
}: ChannelCardProps) {
  const selectedPageId = connection?.selectedPage?.id ?? "";
  const pageOptions = useMemo(
    () => pages.map((page) => ({ value: page.id, label: page.name })),
    [pages],
  );

  const isConnected = connection?.status === "connected";

  return (
    <Card className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-3">
            <h2 className="text-2xl font-semibold text-white">{channel.name}</h2>
            <StatusBadge status={isConnected ? connection.status : "not_connected"} />
          </div>
          <p className="mt-3 max-w-2xl text-sm text-slate-400">{channel.description}</p>
        </div>

        {isConnected ? (
          <Button disabled={disconnectDisabled} onClick={onDisconnect} variant="secondary">
            Disconnect
          </Button>
        ) : (
          <Button disabled={connectDisabled} onClick={onConnect}>
            Connect
          </Button>
        )}
      </div>

      {isConnected && connection ? (
        <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
          <section className="rounded-2xl border border-white/10 bg-slate-950/[0.45] p-5">
            <h3 className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-300">
              Connection details
            </h3>
            <dl className="mt-4 space-y-3 text-sm text-slate-300">
              <div>
                <dt className="text-slate-500">Account</dt>
                <dd className="mt-1 text-white">{connection.profile.displayName ?? "Unnamed Facebook account"}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Facebook user ID</dt>
                <dd className="mt-1 break-all text-white">{connection.profile.facebookUserId}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Granted scopes</dt>
                <dd className="mt-1 text-white">
                  {connection.grantedScopes.length > 0 ? connection.grantedScopes.join(", ") : "No scopes reported"}
                </dd>
              </div>
            </dl>
          </section>

          <section className="rounded-2xl border border-white/10 bg-slate-950/[0.45] p-5">
            <h3 className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-300">
              Publishing page
            </h3>
            <p className="mt-2 text-sm text-slate-400">
              Choose the Facebook page this workspace should publish to.
            </p>

            <div className="mt-5 space-y-4">
              {connection.selectedPage ? (
                <div className="rounded-2xl border border-emerald-400/15 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-100">
                  Selected page: <span className="font-semibold">{connection.selectedPage.name}</span>
                </div>
              ) : (
                <div className="rounded-2xl border border-dashed border-white/[0.12] bg-slate-950/40 px-4 py-3 text-sm text-slate-400">
                  No Facebook page selected yet.
                </div>
              )}

              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-200" htmlFor="facebook-page-select">
                  Facebook page
                </label>
                <select
                  aria-label="Facebook page"
                  className="min-h-11 w-full rounded-xl border border-white/[0.12] bg-slate-950/[0.75] px-4 py-2 text-sm text-white outline-none transition focus:border-cyan-400/70 focus:ring-2 focus:ring-cyan-400/30"
                  disabled={isPagesLoading || selectDisabled || pageOptions.length === 0}
                  id="facebook-page-select"
                  onChange={(event) => {
                    const nextPageId = event.target.value;
                    if (!nextPageId || nextPageId === selectedPageId) {
                      return;
                    }

                    onSelectPage(nextPageId);
                  }}
                  value={selectedPageId}
                >
                  <option value="">
                    {isPagesLoading
                      ? "Loading pages..."
                      : pageOptions.length > 0
                        ? "Choose a page"
                        : "No pages available"}
                  </option>
                  {pageOptions.map((page) => (
                    <option key={page.value} value={page.value}>
                      {page.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </section>
        </div>
      ) : (
        <div className="rounded-2xl border border-dashed border-white/[0.12] bg-slate-950/40 px-5 py-8 text-center">
          <h3 className="text-base font-semibold text-white">No connection yet</h3>
          <p className="mt-2 text-sm text-slate-400">
            Connect Facebook to authorize access and choose the page this workspace should manage.
          </p>
        </div>
      )}
    </Card>
  );
}
