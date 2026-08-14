import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-full text-sm font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo/50 focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        primary:
          "bg-gradient-to-r from-indigo to-teal text-background font-semibold shadow-[0_0_30px_-8px_hsl(var(--accent-indigo)/0.7)] hover:shadow-[0_0_40px_-6px_hsl(var(--accent-indigo)/0.9)] hover:-translate-y-0.5",
        outline:
          "border border-border/20 bg-white/[0.02] text-foreground hover:bg-white/[0.06] hover:border-indigo/40",
        ghost: "text-muted hover:text-foreground hover:bg-white/[0.04]",
        /* Claymorphism — reserved for the one or two most important
           tactile actions per screen (Upload, Retry). See
           `.clay-action` in globals.css for the puffy shadow recipe. */
        clay: "clay-action text-background font-semibold",
      },
      size: {
        default: "h-11 px-6",
        sm: "h-9 px-4 text-[13px]",
        lg: "h-12 px-8 text-base",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "default",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };