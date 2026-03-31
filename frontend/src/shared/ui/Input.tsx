import { forwardRef } from "react";
import type { InputHTMLAttributes } from "react";

import { cn } from "@/shared/lib/cn";

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  function Input({ className, ...props }, ref) {
    return (
      <input
        className={cn(
          "min-h-11 w-full rounded-xl border border-white/[0.12] bg-slate-950/70 px-4 py-2 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-400/70 focus:ring-2 focus:ring-cyan-400/30",
          className,
        )}
        ref={ref}
        {...props}
      />
    );
  },
);

