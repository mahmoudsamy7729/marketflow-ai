import type { HTMLAttributes, PropsWithChildren } from "react";

import { cn } from "@/shared/lib/cn";

export function Card({
  children,
  className,
  ...props
}: PropsWithChildren<HTMLAttributes<HTMLDivElement>>) {
  return (
    <div
      className={cn(
        "rounded-3xl border border-white/10 bg-white/[0.06] p-6 shadow-[0_24px_80px_-32px_rgba(15,23,42,0.75)] backdrop-blur-md",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}

