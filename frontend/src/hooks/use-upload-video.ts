import { useMutation } from "@tanstack/react-query";
import { useCallback, useRef, useState } from "react";

import { ApiError, apiUpload, type UploadProgress } from "@/lib/api-client";
import {
  ACCEPTED_UPLOAD_EXTENSIONS,
  ACCEPTED_UPLOAD_MIME_TYPES,
  MAX_UPLOAD_SIZE_BYTES,
  MAX_UPLOAD_SIZE_MB,
  type UploadCreateResponse,
} from "@/types/upload";

export class FileValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "FileValidationError";
  }
}

export const UPLOAD_ACCEPT_ATTRIBUTE = [
  ...ACCEPTED_UPLOAD_EXTENSIONS,
  ...ACCEPTED_UPLOAD_MIME_TYPES,
].join(",");

function validateFile(file: File): void {
  const extension = `.${file.name.split(".").pop()?.toLowerCase() ?? ""}`;
  const extensionAllowed = (ACCEPTED_UPLOAD_EXTENSIONS as readonly string[]).includes(extension);
  const mimeAllowed = (ACCEPTED_UPLOAD_MIME_TYPES as readonly string[]).includes(
    file.type.toLowerCase()
  );

  if (!extensionAllowed || !mimeAllowed) {
    throw new FileValidationError(
      `Only MP4 files are supported. Allowed extensions: ${ACCEPTED_UPLOAD_EXTENSIONS.join(", ")}`
    );
  }

  if (file.size > MAX_UPLOAD_SIZE_BYTES) {
    throw new FileValidationError(
      `File exceeds the maximum allowed size of ${MAX_UPLOAD_SIZE_MB}MB`
    );
  }
}

export function getUploadErrorMessage(error: unknown): string {
  if (error instanceof FileValidationError) return error.message;
  if (error instanceof ApiError) {
    if (error.status === 0) return "Couldn't reach the FlowMind API. Check your connection and try again.";
    return error.message;
  }
  if (error instanceof Error && error.name === "AbortError") return "Upload cancelled.";
  return "Something went wrong while uploading. Please try again.";
}

export function useUploadVideo() {
  const [progress, setProgress] = useState<UploadProgress | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const mutation = useMutation<UploadCreateResponse, Error, File>({
    mutationFn: async (file) => {
      validateFile(file);

      const controller = new AbortController();
      abortControllerRef.current = controller;
      setProgress({ loaded: 0, total: file.size, percent: 0 });

      const formData = new FormData();
      formData.append("file", file);

      return apiUpload<UploadCreateResponse>("/api/v1/uploads", formData, {
        signal: controller.signal,
        onProgress: setProgress,
      });
    },
    onSettled: () => {
      abortControllerRef.current = null;
    },
  });

  const cancel = useCallback(() => {
    abortControllerRef.current?.abort();
  }, []);

  const reset = useCallback(() => {
    setProgress(null);
    mutation.reset();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return {
    upload: mutation.mutate,
    uploadAsync: mutation.mutateAsync,
    cancel,
    reset,
    progress,
    status: mutation.status,
    isIdle: mutation.status === "idle",
    isUploading: mutation.status === "pending",
    isSuccess: mutation.status === "success",
    isError: mutation.status === "error",
    data: mutation.data,
    error: mutation.error,
    errorMessage: mutation.error ? getUploadErrorMessage(mutation.error) : null,
  };
}