import type { CallbackStatusBanner } from "@/features/channels/types/channels";
import { cn } from "@/shared/lib/cn";

interface ChannelsStatusBannerProps {
  banner: CallbackStatusBanner;
}

export function ChannelsStatusBanner({ banner }: ChannelsStatusBannerProps) {
  return (
    <div
      className={cn(
        "rounded-2xl border px-5 py-4",
        banner.tone === "success"
          ? "border-emerald-400/20 bg-emerald-500/12 text-emerald-100"
          : "border-rose-400/20 bg-rose-500/12 text-rose-100",
      )}
    >
      <h2 className="text-sm font-semibold uppercase tracking-[0.24em]">{banner.title}</h2>
      <p className="mt-2 text-sm opacity-90">{banner.description}</p>
    </div>
  );
}
