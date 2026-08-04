import { useQuery } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api-client";
import type { ResultsResponse } from "@/types/upload";

/** Fetches `GET /api/v1/uploads/{uploadId}/results`. No polling — the caller
 * decides when to refetch (e.g. after confirming status is "completed" via
 * `useUploadStatus`). */
export function useUploadResults(uploadId: string | undefined) {
  return useQuery<ResultsResponse>({
    queryKey: ["upload-results", uploadId],
    queryFn: () => apiFetch<ResultsResponse>(`/api/v1/uploads/${uploadId}/results`),
    enabled: Boolean(uploadId),
    retry: 1,
  });
}