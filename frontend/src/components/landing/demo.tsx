"use client";

import { motion } from "framer-motion";
import { CheckCircle2, Loader2, Upload, XCircle } from "lucide-react";

import { useHealth } from "@/hooks/use-health";
import { useAppStore, type DemoView } from "@/store/use-app-store";

const TABS: { id: DemoView; label: string }[] = [
  { id: "upload", label: "Upload" },
  { id: "docs", label: "Generated doc" },
  { id: "chat", label: "Ask the knowledge base" },
];

function StatusIndicator() {
  const { data, isLoading, isError } = useHealth();

  if (isLoading) {
    return (
      <span className="flex items-center gap-1.5 font-mono text-[11px] text-muted">
        <Loader2 className="h-3 w-3 animate-spin" /> checking api…
      </span>
    );
  }

  if (isError || !data) {
    return (
      <span className="flex items-center gap-1.5 font-mono text-[11px] text-muted">
        <XCircle className="h-3 w-3" /> api offline (start the backend to see live status)
      </span>
    );
  }

  return (
    <span className="flex items-center gap-1.5 font-mono text-[11px] text-teal">
      <CheckCircle2 className="h-3 w-3" /> api {data.status} · {data.environment}
    </span>
  );
}

function DemoContent({ view }: { view: DemoView }) {
  if (view === "upload") {
    return (
      <div className="flex h-72 flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-border/20 bg-white/[0.02]">
        <Upload className="h-8 w-8 text-indigo" strokeWidth={1.5} />
        <p className="text-sm text-muted">Drop a screen recording, or click to browse</p>
        <p className="font-mono text-[11px] text-muted/70">.mp4 · .mov · .webm · .mkv</p>
      </div>
    );
  }

  if (view === "docs") {
    return (
      <div className="h-72 space-y-4 overflow-hidden rounded-xl border border-border/10 bg-white/[0.02] p-6">
        <div className="h-3 w-1/2 rounded-full bg-foreground/20" />
        <div className="space-y-2 pt-2">
          {[1, 2, 3].map((step) => (
            <div key={step} className="flex items-start gap-3">
              <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-teal/15 font-mono text-[10px] text-teal">
                {step}
              </span>
              <div className="flex-1 space-y-1.5 pt-0.5">
                <div className="h-2 w-full rounded-full bg-white/10" />
                <div className="h-2 w-4/5 rounded-full bg-white/5" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-72 flex-col justify-end gap-3 rounded-xl border border-border/10 bg-white/[0.02] p-6">
      <div className="self-end rounded-2xl rounded-br-sm bg-indigo/15 px-4 py-2 text-sm text-foreground">
        How do I reset a user's password?
      </div>
      <div className="self-start rounded-2xl rounded-bl-sm bg-white/5 px-4 py-2 text-sm text-muted">
        Open <span className="text-foreground">Settings → Members</span>, select the user, and
        choose <span className="text-foreground">"Send reset link."</span> Sourced from the
        onboarding recording, step 4.
      </div>
    </div>
  );
}

export function Demo() {
  const activeDemoView = useAppStore((s) => s.activeDemoView);
  const setActiveDemoView = useAppStore((s) => s.setActiveDemoView);

  return (
    <section id="demo" className="relative py-28">
      <div className="container">
        <div className="mx-auto mb-16 max-w-2xl text-center">
          <span className="font-mono text-xs uppercase tracking-[0.2em] text-indigo/70">
            See it in motion
          </span>
          <h2 className="mt-4 font-display text-3xl font-semibold tracking-tight md:text-4xl">
            One recording, three outputs
          </h2>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6 }}
          className="glass-panel mx-auto max-w-3xl rounded-2xl p-2"
        >
          {/* window chrome */}
          <div className="flex items-center justify-between px-4 py-3">
            <div className="flex gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-white/10" />
              <span className="h-2.5 w-2.5 rounded-full bg-white/10" />
              <span className="h-2.5 w-2.5 rounded-full bg-white/10" />
            </div>
            <StatusIndicator />
          </div>

          <div className="flex gap-1 border-b border-border/10 px-4 pb-3">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveDemoView(tab.id)}
                className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
                  activeDemoView === tab.id
                    ? "bg-white/[0.06] text-foreground"
                    : "text-muted hover:text-foreground"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="p-4">
            <DemoContent view={activeDemoView} />
          </div>
        </motion.div>
      </div>
    </section>
  );
}
