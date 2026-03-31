import { cn } from "@/shared/lib/cn";

interface StatusBadgeProps {
  status: string;
}

const statusClasses: Record<string, string> = {
  active: "bg-emerald-500/15 text-emerald-200 ring-1 ring-emerald-400/20",
  connected: "bg-emerald-500/15 text-emerald-200 ring-1 ring-emerald-400/20",
  scheduled: "bg-cyan-500/15 text-cyan-100 ring-1 ring-cyan-400/20",
  published: "bg-indigo-500/15 text-indigo-100 ring-1 ring-indigo-400/20",
  draft: "bg-amber-500/15 text-amber-100 ring-1 ring-amber-400/20",
  failed: "bg-rose-500/15 text-rose-100 ring-1 ring-rose-400/20",
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const normalizedStatus = status.trim().toLowerCase();

  return (
    <span
      className={cn(
        "inline-flex rounded-full px-2.5 py-1 text-xs font-medium capitalize",
        statusClasses[normalizedStatus] ??
          "bg-white/10 text-slate-200 ring-1 ring-white/[0.12]",
      )}
    >
      {normalizedStatus.replaceAll("_", " ")}
    </span>
  );
}

