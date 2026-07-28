import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";

import { cn } from "@/lib/utils";

const progressTrackVariants = cva(
  "relative w-full overflow-hidden rounded-full bg-white/[0.06]",
  {
    variants: {
      size: {
        default: "h-2",
        sm: "h-1.5",
        lg: "h-3",
      },
    },
    defaultVariants: { size: "default" },
  }
);

const progressIndicatorVariants = cva(
  "h-full rounded-full transition-[width] duration-300 ease-out",
  {
    variants: {
      variant: {
        default: "bg-gradient-to-r from-indigo to-teal",
        indigo: "bg-indigo",
        teal: "bg-teal",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

export interface ProgressProps
  extends Omit<React.HTMLAttributes<HTMLDivElement>, "value">,
    VariantProps<typeof progressTrackVariants>,
    VariantProps<typeof progressIndicatorVariants> {
  /** Current value, measured against `max`. Defaults to 0. */
  value?: number;
  /** Upper bound `value` is measured against. Defaults to 100. */
  max?: number;
}

/**
 * Dependent-free progress bar (no `@radix-ui/react-progress` install
 * required) with the accessible `role="progressbar"` semantics that
 * primitive would otherwise provide.
 */
const Progress = React.forwardRef<HTMLDivElement, ProgressProps>(
  ({ className, value = 0, max = 100, size, variant, ...props }, ref) => {
    const clamped = Math.min(max, Math.max(0, value));
    const percent = max > 0 ? (clamped / max) * 100 : 0;

    return (
      <div
        ref={ref}
        role="progressbar"
        aria-valuenow={Math.round(clamped)}
        aria-valuemin={0}
        aria-valuemax={max}
        className={cn(progressTrackVariants({ size }), className)}
        {...props}
      >
        <div
          className={cn(progressIndicatorVariants({ variant }))}
          style={{ width: `${percent}%` }}
        />
      </div>
    );
  }
);
Progress.displayName = "Progress";

export { Progress, progressIndicatorVariants, progressTrackVariants };