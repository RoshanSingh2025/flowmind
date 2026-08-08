"use client";

import { AlertTriangle, FileVideo, Loader2, Upload, Workflow } from "lucide-react";
import Image from "next/image";
import Link from "next/link";

import { useUploadsList } from "@/hooks/use-uploads-list";
import { API_URL } from "@/lib/api-client";
import { formatBytes } from "@/lib/utils";

export default function DashboardPage() {
  const { data, isLoading, isError } = useUploadsList();

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
        <Link
          href="/upload"
          className="text-sm text-muted transition-colors hover:text-foreground"
        >
          New upload
        </Link>
      </header>

      <div className="container pb-24 pt-12">
        <div className="mb-10">
          <span className="font-mono text-xs uppercase tracking-[0.2em] text-indigo/70">
            Dashboard
          </span>
          <h1 className="mt-4 font-display text-3xl font-semibold tracking-tight md:text-4xl">
            Your uploads
          </h1>
          {data && (
            <p className="mt-2 text-sm text-muted">
              {data.total} upload{data.total === 1 ? "" : "s"} total
            </p>
          )}
        </div>

        {isLoading && (
          <div className="glass-panel flex flex-col items-center gap-4 rounded-2xl p-12">
            <Loader2 className="h-6 w-6 animate-spin text-indigo" />
            <p className="text-sm text-muted">Loading uploads…</p>
          </div>
        )}

        {isError && (
          <div className="flex flex-col items-center gap-4 rounded-2xl border border-red-500/25 bg-red-500/[0.05] p-12 text-center">
            <AlertTriangle className="h-6 w-6 text-red-400" />
            <p className="text-sm text-muted">
              Couldn&apos;t reach the FlowMind API. Check that the backend is running.
            </p>
          </div>
        )}

        {data && data.items.length === 0 && (
          <div className="glass-panel flex flex-col items-center gap-4 rounded-2xl p-12 text-center">
            <Upload className="h-8 w-8 text-indigo" strokeWidth={1.5} />
            <div>
              <p className="text-sm font-medium text-foreground">No uploads yet</p>
              <p className="mt-1 text-xs text-muted">
                Upload a screen recording to see it appear here.
              </p>
            </div>
            <Link
              href="/upload"
              className="rounded-lg bg-gradient-to-r from-indigo to-teal px-4 py-2 text-sm font-medium text-background"
            >
              Upload a recording
            </Link>
          </div>
        )}

        {data && data.items.length > 0 && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {data.items.map((item) => (
              <Link
                key={item.upload_id}
                href={
                  item.status === "completed"
                    ? `/results/${item.upload_id}`
                    : `/processing/${item.upload_id}`
                }
                className="glass-panel group flex flex-col gap-3 rounded-2xl p-5 text-left transition-colors hover:border-indigo/30"
              >
                <div className="flex items-center justify-between">
                  {item.thumbnail_path ? (
                    <Image
                      src={`${API_URL}/api/v1/uploads/${item.upload_id}/thumbnail`}
                      alt=""
                      width={56}
                      height={40}
                      className="h-10 w-14 rounded-lg border border-border/15 object-cover"
                    />
                  ) : (
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-indigo/25 bg-indigo/[0.08]">
                      <FileVideo className="h-4.5 w-4.5 text-indigo" strokeWidth={1.75} />
                    </div>
                  )}
                  <span
                    className={`font-mono text-[10px] uppercase tracking-wider ${
                      item.status === "completed"
                        ? "text-teal"
                        : item.status === "failed"
                          ? "text-red-400"
                          : "text-indigo/80"
                    }`}
                  >
                    {item.status}
                  </span>
                </div>
                <div>
                  <p className="truncate text-sm font-medium text-foreground">
                    {item.original_filename}
                  </p>
                  <p className="mt-1 text-xs text-muted">
                    {formatBytes(item.file_size)} ·{" "}
                    {new Date(item.created_at).toLocaleDateString()}
                  </p>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}