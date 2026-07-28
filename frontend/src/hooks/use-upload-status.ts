import { useQuery } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api-client";
import type { UploadRead } from "@/types/upload";

const POLL_INTERVAL_MS = 4000;

/** Statuses that mean "nothing further will change" — polling stops here.
 * Neither ever actually occurs today (see `use-upload-status.ts` module
 * doc), since the backend has no pipeline that transitions a status past
 * "uploaded" yet. Written correctly now so nothing here needs to change
 * once it does. */
const TERMINAL_STATUSES = new Set<UploadRead["status"]>(["completed", "failed"]);

/**
 * Polls `GET /api/v1/uploads/{uploadId}` for the real, current status of an
 * upload. Today every upload's status will read "uploaded" indefinitely —
 * the backend's processing pipeline (transcription, doc generation,
 * embedding) isn't implemented yet, so this intentionally does not simulate
 * progress. It reflects exactly what the API returns.
 */
export function useUploadStatus(uploadId: string | undefined) {
  return useQuery<UploadRead>({
    queryKey: ["upload-status", uploadId],
    queryFn: () => apiFetch<UploadRead>(`/api/v1/uploads/${uploadId}`),
    enabled: Boolean(uploadId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status && TERMINAL_STATUSES.has(status)) return false;
      return POLL_INTERVAL_MS;
    },
    retry: 1,
  });
}