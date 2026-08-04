"use client";

import { AlertTriangle, CheckCircle2, Loader2, Workflow } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";

import { useUploadStatus } from "@/hooks/use-upload-status";
import { formatBytes } from "@/lib/utils";

const PIPELINE_STEPS = [
  { label: "Upload", active: false, built: true },
  { label: "Processing", active: true, built: true },
  { label: "Results", active: false, built: true },
  { label: "Dashboard", active: false, built: true },
];

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.round(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

function StatBox({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border/15 bg-white/[0.03] p-4 text-left">
      <p className="font-mono text-[10px] uppercase tracking-wider text-muted/70">{label}</p>
      <p className="mt-1 text-sm text-foreground">{value}</p>
    </div>
  );
}

export default function ProcessingPage() {
  const params = useParams<{ uploadId: string }>();
  const uploadId = params.uploadId;

  const { data, isLoading, isError, error } = useUploadStatus(uploadId);

  const hasMetadata = data && (data.duration || data.width || data.codec);

  return (
    <main className="relative min-h-screen overflow-hidden overflow-x-hidden">
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
              Step 2 of {PIPELINE_STEPS.length}
            </span>
            <span className="text-muted/30">·</span>
            <span className="font-mono text-[11px] uppercase tracking-wider text-muted/70">
              Processing
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
          Step 2
        </span>
        <h1 className="mt-4 max-w-xl text-balance font-display text-3xl font-semibold tracking-tight md:text-4xl">
          Processing your recording
        </h1>

        <div className="mt-12 w-full max-w-xl">
          {isLoading && (
            <div className="glass-panel flex flex-col items-center gap-4 rounded-2xl p-8">
              <Loader2 className="h-6 w-6 animate-spin text-indigo" />
              <p className="text-sm text-muted">Looking up this upload…</p>
            </div>
          )}

          {isError && (
            <div className="flex flex-col items-center gap-4 rounded-2xl border border-red-500/25 bg-red-500/[0.05] p-8">
              <AlertTriangle className="h-6 w-6 text-red-400" />
              <div>
                <p className="text-sm font-medium text-foreground">Couldn&apos;t find this upload</p>
                <p className="mt-1 max-w-xs text-xs text-muted">
                  {error instanceof Error ? error.message : "It may not exist, or the id is invalid."}
                </p>
              </div>
              <Link href="/upload" className="text-sm text-indigo hover:underline">
                Start a new upload
              </Link>
            </div>
          )}

          {data && (
            <div className="glass-panel flex flex-col items-center gap-6 rounded-2xl p-8 text-center">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-indigo/25 bg-indigo/[0.08]">
                {data.status === "completed" ? (
                  <CheckCircle2 className="h-6 w-6 text-teal" />
                ) : data.status === "failed" ? (
                  <AlertTriangle className="h-6 w-6 text-red-400" />
                ) : (
                  <Loader2 className="h-6 w-6 animate-spin text-indigo" />
                )}
              </div>

              <div>
                <p className="max-w-xs truncate text-sm font-medium text-foreground">
                  {data.original_filename}
                </p>
                <p className="mt-1 font-mono text-[11px] uppercase tracking-wider text-muted/60">
                  status: {data.status}
                </p>
              </div>

              {data.status === "uploaded" && (
                <p className="max-w-sm text-xs text-muted/70">
                  Stored and validated. Queued for processing — this will move to
                  &ldquo;processing&rdquo; shortly.
                </p>
              )}

              {data.status === "processing" && (
                <p className="max-w-sm text-xs text-muted/70">
                  Extracting audio, transcribing, and generating documentation now. This can take
                  a minute or two depending on recording length.
                </p>
              )}

              {data.status === "completed" && (
                <>
                  <p className="max-w-sm text-xs text-muted/70">
                    Documentation, SOP, FAQ, and summary have been generated.
                  </p>
                  <Link
                    href={`/results/${uploadId}`}
                    className="rounded-lg bg-gradient-to-r from-indigo to-teal px-4 py-2 text-sm font-medium text-background"
                  >
                    View results
                  </Link>
                </>
              )}

              {data.status === "failed" && (
                <p className="max-w-sm text-xs text-red-400">
                  {data.processing_error ?? "Processing failed for an unknown reason."}
                </p>
              )}

              {hasMetadata && (
                <div className="grid w-full grid-cols-2 gap-3 sm:grid-cols-3">
                  {typeof data.duration === "number" && (
                    <StatBox label="Duration" value={formatDuration(data.duration)} />
                  )}
                  {typeof data.width === "number" && typeof data.height === "number" && (
                    <StatBox label="Resolution" value={`${data.width}×${data.height}`} />
                  )}
                  {typeof data.fps === "number" && (
                    <StatBox label="Frame rate" value={`${Math.round(data.fps)} fps`} />
                  )}
                  {data.codec && <StatBox label="Codec" value={data.codec} />}
                  <StatBox label="File size" value={formatBytes(data.file_size)} />
                  <StatBox label="Uploaded" value={new Date(data.created_at).toLocaleString()} />
                </div>
              )}

              {data.thumbnail_path && (
                <p className="max-w-sm text-[11px] text-muted/50">
                  A thumbnail was generated server-side, but there&apos;s no backend route yet to
                  serve it as an image — not shown here until that exists.
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}