"use client";

import { AnimatePresence, motion } from "framer-motion";
import { CheckCircle2, Loader2, Upload, X, XCircle } from "lucide-react";
import Link from "next/link";
import { useCallback, useRef, useState } from "react";
import type { DragEvent, KeyboardEvent } from "react";

import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { UPLOAD_ACCEPT_ATTRIBUTE, useUploadVideo } from "@/hooks/use-upload-video";
import { cn } from "@/lib/utils";
import { MAX_UPLOAD_SIZE_MB, type UploadCreateResponse } from "@/types/upload";

function formatBytes(bytes: number): string {
  if (bytes <= 0) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  let size = bytes;
  let unitIndex = 0;
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex += 1;
  }
  return `${size.toFixed(size < 10 && unitIndex > 0 ? 1 : 0)} ${units[unitIndex]}`;
}

export interface UploadDropzoneProps {
  onUploadSuccess?: (data: UploadCreateResponse, file: File) => void;
  className?: string;
}

export function UploadDropzone({ onUploadSuccess, className }: UploadDropzoneProps) {
  const [isDragActive, setIsDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const dragCounter = useRef(0);

  const { upload, cancel, reset, progress, isUploading, isSuccess, isError, data, errorMessage } =
    useUploadVideo();

  const handleFiles = useCallback(
    (files: FileList | null) => {
      const file = files?.[0];
      if (!file) return;
      setSelectedFile(file);
      upload(file, {
        onSuccess: (response) => onUploadSuccess?.(response, file),
      });
    },
    [upload, onUploadSuccess]
  );

  const openFilePicker = () => inputRef.current?.click();

  const onDrop = useCallback(
    (event: DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      dragCounter.current = 0;
      setIsDragActive(false);
      handleFiles(event.dataTransfer.files);
    },
    [handleFiles]
  );

  const onDragEnter = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    dragCounter.current += 1;
    setIsDragActive(true);
  };

  const onDragLeave = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    dragCounter.current -= 1;
    if (dragCounter.current <= 0) {
      dragCounter.current = 0;
      setIsDragActive(false);
    }
  };

  const onDragOver = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  };

  const onKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      openFilePicker();
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    reset();
  };

  const isIdle = !isUploading && !isSuccess && !isError;

  return (
    <div className={cn("w-full", className)}>
      <input
        ref={inputRef}
        type="file"
        accept={UPLOAD_ACCEPT_ATTRIBUTE}
        className="hidden"
        onChange={(event) => handleFiles(event.target.files)}
      />

      <AnimatePresence mode="wait">
        {isIdle && (
          <motion.div
            key="idle"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            role="button"
            tabIndex={0}
            onClick={openFilePicker}
            onKeyDown={onKeyDown}
            onDrop={onDrop}
            onDragEnter={onDragEnter}
            onDragLeave={onDragLeave}
            onDragOver={onDragOver}
            className={cn(
              "flex h-72 cursor-pointer flex-col items-center justify-center gap-3 rounded-2xl border border-dashed transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo/50",
              isDragActive
                ? "border-indigo/60 bg-indigo/[0.06]"
                : "border-border/20 bg-white/[0.02] hover:border-indigo/35 hover:bg-white/[0.03]"
            )}
          >
            <motion.div
              animate={{ y: isDragActive ? -4 : 0, scale: isDragActive ? 1.08 : 1 }}
              transition={{ duration: 0.2 }}
              className="flex h-14 w-14 items-center justify-center rounded-2xl border border-indigo/25 bg-indigo/[0.08]"
            >
              <Upload className="h-6 w-6 text-indigo" strokeWidth={1.75} />
            </motion.div>
            <p className="text-sm font-medium text-foreground">
              {isDragActive ? "Drop it right here" : "Drop a screen recording, or click to browse"}
            </p>
            <p className="font-mono text-[11px] text-muted/70">
              .mp4 only · up to {MAX_UPLOAD_SIZE_MB}MB
            </p>
          </motion.div>
        )}

        {isUploading && selectedFile && (
          <motion.div
            key="uploading"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="glass-panel flex h-72 flex-col items-center justify-center gap-5 rounded-2xl p-8 text-center"
          >
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-indigo/25 bg-indigo/[0.08]">
              <Loader2 className="h-6 w-6 animate-spin text-indigo" strokeWidth={1.75} />
            </div>
            <div className="w-full max-w-xs space-y-2">
              <div className="flex items-center justify-between font-mono text-[11px] text-muted">
                <span className="max-w-[70%] truncate">{selectedFile.name}</span>
                <span>{Math.round(progress?.percent ?? 0)}%</span>
              </div>
              <Progress value={progress?.percent ?? 0} />
              <p className="text-xs text-muted/70">
                {formatBytes(progress?.loaded ?? 0)} of{" "}
                {formatBytes(progress?.total ?? selectedFile.size)}
              </p>
            </div>
            <Button variant="ghost" size="sm" onClick={cancel}>
              <X className="h-3.5 w-3.5" /> Cancel
            </Button>
          </motion.div>
        )}

        {isSuccess && data && selectedFile && (
          <motion.div
            key="success"
            initial={{ opacity: 0, scale: 0.97 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="glass-panel flex h-72 flex-col items-center justify-center gap-4 rounded-2xl p-8 text-center"
          >
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-teal/25 bg-teal/[0.08]">
              <CheckCircle2 className="h-6 w-6 text-teal" strokeWidth={1.75} />
            </div>
            <div>
              <p className="text-sm font-medium text-foreground">Upload complete</p>
              <p className="mt-1 max-w-xs truncate text-xs text-muted">{selectedFile.name}</p>
              <p className="mt-2 font-mono text-[11px] text-muted/60">{data.upload_id}</p>
            </div>
            <p className="max-w-xs text-xs text-muted/70">
              Stored and ready. Processing (transcription, docs, and the knowledge base) is the
              next pipeline stage — not wired up yet.
            </p>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={handleReset}>
                Upload another
              </Button>
              <Button variant="ghost" size="sm" asChild>
                <Link href={`/processing/${data.upload_id}`}>View status</Link>
              </Button>
            </div>
          </motion.div>
        )}

        {isError && (
          <motion.div
            key="error"
            initial={{ opacity: 0, scale: 0.97 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="flex h-72 flex-col items-center justify-center gap-4 rounded-2xl border border-red-500/25 bg-red-500/[0.05] p-8 text-center"
          >
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-red-500/25 bg-red-500/[0.08]">
              <XCircle className="h-6 w-6 text-red-400" strokeWidth={1.75} />
            </div>
            <div>
              <p className="text-sm font-medium text-foreground">Upload failed</p>
              <p className="mt-1 max-w-xs text-xs text-muted">{errorMessage}</p>
            </div>
            <Button variant="outline" size="sm" onClick={handleReset}>
              Try again
            </Button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}