"use client";

import {
  AlertTriangle,
  Download,
  FileText,
  Loader2,
  Workflow,
} from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { Button } from "@/components/ui/button";
import { CopyButton } from "@/components/ui/copy-button";
import { useUploadResults } from "@/hooks/use-upload-results";
import { API_URL } from "@/lib/api-client";

const PIPELINE_STEPS = [
  { label: "Upload", active: false, built: true },
  { label: "Processing", active: false, built: true },
  { label: "Results", active: true, built: true },
  { label: "Dashboard", active: false, built: true },
];

type TabId = "summary" | "documentation" | "sop" | "faq" | "transcript";

function Prose({ content }: { content: string }) {
  return (
    <div className="prose prose-invert prose-sm max-w-none prose-headings:font-display prose-a:text-indigo prose-code:text-teal">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
    </div>
  );
}

export default function ResultsPage() {
  const params = useParams<{ uploadId: string }>();
  const uploadId = params.uploadId;
  const [activeTab, setActiveTab] = useState<TabId>("summary");

  const { data, isLoading, isError, error } = useUploadResults(uploadId);

  const TABS: { id: TabId; label: string; content: string | null | undefined }[] = data
    ? [
        { id: "summary", label: "Summary", content: data.summary },
        { id: "documentation", label: "Documentation", content: data.documentation },
        { id: "sop", label: "SOP", content: data.sop },
        { id: "faq", label: "FAQ", content: data.faq },
        { id: "transcript", label: "Transcript", content: data.transcript },
      ]
    : [];

  const availableTabs = TABS.filter((tab) => tab.content);
  const effectiveActiveTab = availableTabs.some((tab) => tab.id === activeTab)
    ? activeTab
    : availableTabs[0]?.id;
  const activeContent = TABS.find((tab) => tab.id === effectiveActiveTab)?.content;

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
          <Link href="/upload" className="text-sm text-muted transition-colors hover:text-foreground">
            Upload another
          </Link>
        </div>
      </header>

      <div className="container flex flex-col items-center pb-24 pt-12 text-center">
        <nav aria-label="Pipeline progress" className="mb-12">
          <div className="flex items-center gap-2 sm:hidden">
            <span className="font-mono text-[11px] uppercase tracking-wider text-teal">
              Step 3 of {PIPELINE_STEPS.length}
            </span>
            <span className="text-muted/30">·</span>
            <span className="font-mono text-[11px] uppercase tracking-wider text-muted/70">
              Results
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
          Step 3
        </span>
        <h1 className="mt-4 max-w-xl text-balance font-display text-3xl font-semibold tracking-tight md:text-4xl">
          Results
        </h1>

        <div className="mt-12 w-full max-w-3xl text-left">
          {isLoading && (
            <div className="glass-panel flex flex-col items-center gap-4 rounded-2xl p-12 text-center">
              <Loader2 className="h-6 w-6 animate-spin text-indigo" />
              <p className="text-sm text-muted">Loading results…</p>
            </div>
          )}

          {isError && (
            <div className="flex flex-col items-center gap-4 rounded-2xl border border-red-500/25 bg-red-500/[0.05] p-12 text-center">
              <AlertTriangle className="h-6 w-6 text-red-400" />
              <div>
                <p className="text-sm font-medium text-foreground">Couldn&apos;t load results</p>
                <p className="mt-1 max-w-xs text-xs text-muted">
                  {error instanceof Error ? error.message : "It may not exist, or the id is invalid."}
                </p>
              </div>
              <Link href="/dashboard" className="text-sm text-indigo hover:underline">
                Back to Dashboard
              </Link>
            </div>
          )}

          {data && data.status !== "completed" && data.status !== "failed" && (
            <div className="glass-panel flex flex-col items-center gap-4 rounded-2xl p-12 text-center">
              <Loader2 className="h-6 w-6 animate-spin text-indigo" />
              <div>
                <p className="text-sm font-medium text-foreground">Still processing</p>
                <p className="mt-1 max-w-sm text-xs text-muted">
                  This recording hasn&apos;t finished processing yet (status: {data.status}).
                  Check the Processing page for live status.
                </p>
              </div>
              <Link href={`/processing/${uploadId}`} className="text-sm text-indigo hover:underline">
                View processing status
              </Link>
            </div>
          )}

          {data && data.status === "failed" && (
            <div className="flex flex-col items-center gap-4 rounded-2xl border border-red-500/25 bg-red-500/[0.05] p-12 text-center">
              <AlertTriangle className="h-6 w-6 text-red-400" />
              <div>
                <p className="text-sm font-medium text-foreground">Processing failed</p>
                <p className="mt-1 max-w-sm text-xs text-muted">
                  {data.error ?? "The pipeline failed for an unknown reason."}
                </p>
              </div>
              <Link href="/upload" className="text-sm text-indigo hover:underline">
                Try a new upload
              </Link>
            </div>
          )}

          {data && data.status === "completed" && availableTabs.length === 0 && (
            <div className="glass-panel flex flex-col items-center gap-4 rounded-2xl p-12 text-center">
              <FileText className="h-6 w-6 text-muted" />
              <p className="text-sm text-muted">
                Processing completed, but no documents were generated.
              </p>
            </div>
          )}

          {data && data.status === "completed" && availableTabs.length > 0 && (
            <div className="glass-panel rounded-2xl p-2">
              <div className="flex flex-col gap-3 border-b border-border/10 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
                <p className="truncate text-sm font-medium text-foreground">
                  {data.original_filename}
                </p>
                <div className="flex shrink-0 gap-2">
                  <Button variant="outline" size="sm" asChild>
                    <a href={`${API_URL}/api/v1/uploads/${uploadId}/export/markdown`} download>
                      <Download className="h-3.5 w-3.5" /> Markdown
                    </a>
                  </Button>
                  <Button variant="outline" size="sm" asChild>
                    <a href={`${API_URL}/api/v1/uploads/${uploadId}/export/pdf`} download>
                      <Download className="h-3.5 w-3.5" /> PDF
                    </a>
                  </Button>
                </div>
              </div>

              <div
                className="flex gap-1 overflow-x-auto px-4 py-3 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
              >
                {availableTabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`shrink-0 whitespace-nowrap rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
                      effectiveActiveTab === tab.id
                        ? "bg-white/[0.06] text-foreground"
                        : "text-muted hover:text-foreground"
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              <div className="p-4">
                {activeContent ? (
                  <div className="rounded-xl border border-border/10 bg-white/[0.02] p-6">
                    <div className="mb-3 flex justify-end">
                      <CopyButton text={activeContent} />
                    </div>
                    <Prose content={activeContent} />
                  </div>
                ) : (
                  <p className="p-6 text-sm text-muted">
                    This section wasn&apos;t generated for this recording.
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}