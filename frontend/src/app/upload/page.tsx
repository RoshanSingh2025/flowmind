import type { Metadata } from "next";
import { Workflow } from "lucide-react";
import Link from "next/link";

import { UploadDropzone } from "@/components/upload/UploadDropzone";

export const metadata: Metadata = {
  title: "Upload a recording — FlowMind",
  description: "Upload a screen recording to start turning it into documentation and a knowledge base.",
};

const PIPELINE_STEPS = [
  { label: "Upload", active: true, built: true },
  { label: "Processing", active: false, built: true },
  { label: "Results", active: false, built: true },
  { label: "Dashboard", active: false, built: true },
];

export default function UploadPage() {
  return (
    <main className="relative min-h-screen overflow-hidden">
      <div className="grid-overlay bg-mesh-glow absolute inset-0 -z-10 [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,black,transparent)]" />

      <header className="container flex items-center justify-between py-6">
        <Link href="/" className="flex items-center gap-2 font-display text-lg font-semibold">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-indigo to-teal text-background">
            <Workflow className="h-4.5 w-4.5" strokeWidth={2.5} />
          </span>
          FlowMind
        </Link>
        <div className="flex items-center gap-6">
          <Link href="/dashboard" className="text-sm text-muted transition-colors hover:text-foreground">
            Dashboard
          </Link>
          <Link href="/" className="text-sm text-muted transition-colors hover:text-foreground">
            Back to home
          </Link>
        </div>
      </header>

      <div className="container flex flex-col items-center pb-24 pt-12 text-center">
        <nav aria-label="Pipeline progress" className="mb-12">
          <div className="flex items-center gap-2 sm:hidden">
            <span className="font-mono text-[11px] uppercase tracking-wider text-teal">
              Step 1 of {PIPELINE_STEPS.length}
            </span>
            <span className="text-muted/30">·</span>
            <span className="font-mono text-[11px] uppercase tracking-wider text-muted/70">
              Upload
            </span>
          </div>

          <div className="hidden items-center gap-2 sm:flex">
            {PIPELINE_STEPS.map((step, index) => (
              <div key={step.label} className="flex items-center gap-2">
                <span
                  className={`font-mono text-[11px] uppercase tracking-wider ${
                    step.active ? "text-teal" : step.built ? "text-muted/60" : "text-muted/30"
                  }`}
                >
                  {step.label}
                </span>
                {index < PIPELINE_STEPS.length - 1 && (
                  <span className="h-px w-6 bg-border/20" aria-hidden="true" />
                )}
              </div>
            ))}
          </div>
        </nav>

        <span className="font-mono text-xs uppercase tracking-[0.2em] text-indigo/70">
          Step 1
        </span>
        <h1 className="mt-4 max-w-xl text-balance font-display text-3xl font-semibold tracking-tight md:text-4xl">
          Upload a screen recording
        </h1>
        <p className="mt-4 max-w-lg text-balance text-muted">
          Drop in a recording of your product being used. FlowMind stores it and prepares it for
          the next pipeline stage.
        </p>

        <div className="mt-12 w-full max-w-xl">
          <UploadDropzone />
        </div>
      </div>
    </main>
  );
}