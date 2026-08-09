import { useMutation, useQueryClient } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api-client";
import type { UploadRead } from "@/types/upload";

/** Retries processing for a failed upload via `POST /uploads/{id}/retry`.
 * Only valid on uploads currently in `failed` state — the backend rejects
 * (409) anything else. On success, invalidates the upload-status query so
 * the Processing page immediately reflects the reset `uploaded` state
 * instead of waiting for its next poll. */
export function useRetryUpload(uploadId: string | undefined) {
  const queryClient = useQueryClient();

  return useMutation<UploadRead, Error, void>({
    mutationFn: () => apiFetch<UploadRead>(`/api/v1/uploads/${uploadId}/retry`, { method: "POST" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["upload-status", uploadId] });
    },
  });
}