"use client";

import { Check, Copy } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export interface CopyButtonProps {
  text: string;
  className?: string;
  label?: string;
}

/** Copies `text` to the clipboard, showing a brief checkmark confirmation.
 * Reused by every Results section instead of duplicating clipboard logic. */
export function CopyButton({ text, className, label = "Copy" }: CopyButtonProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // Clipboard API can be unavailable (older browsers, non-HTTPS
      // contexts) — fail silently rather than surfacing a disruptive error
      // for a low-stakes convenience action.
    }
  };

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={handleCopy}
      className={cn("gap-1.5", className)}
    >
      {copied ? (
        <>
          <Check className="h-3.5 w-3.5 text-teal" /> Copied
        </>
      ) : (
        <>
          <Copy className="h-3.5 w-3.5" /> {label}
        </>
      )}
    </Button>
  );
}