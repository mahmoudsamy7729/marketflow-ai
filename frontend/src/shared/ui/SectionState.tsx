import { Button } from "@/shared/ui/Button";

interface SectionStateProps {
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}

export function SectionState({
  title,
  description,
  actionLabel,
  onAction,
}: SectionStateProps) {
  return (
    <div className="rounded-2xl border border-dashed border-white/[0.12] bg-slate-950/40 px-5 py-8 text-center">
      <h3 className="text-base font-semibold text-white">{title}</h3>
      <p className="mt-2 text-sm text-slate-400">{description}</p>
      {actionLabel && onAction ? (
        <div className="mt-4">
          <Button onClick={onAction} variant="secondary">
            {actionLabel}
          </Button>
        </div>
      ) : null}
    </div>
  );
}

