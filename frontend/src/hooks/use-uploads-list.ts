import { useQuery } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api-client";
import type { UploadListResponse } from "@/types/upload";

const POLL_INTERVAL_MS = 4000;

/** Fetches `GET /api/v1/uploads` — the real, paginated list of uploads,
 * newest first. Polls automatically while any upload in the current page is
 * still in-flight (`uploaded`/`processing`), so newly-uploaded items
 * visibly flip to "completed"/"failed" without a manual refresh; stops
 * polling once everything on the page has reached a terminal state. */
export function useUploadsList(limit = 20, offset = 0) {
  return useQuery<UploadListResponse>({
    queryKey: ["uploads-list", limit, offset],
    queryFn: () => apiFetch<UploadListResponse>(`/api/v1/uploads?limit=${limit}&offset=${offset}`),
    refetchInterval: (query) => {
      const items = query.state.data?.items;
      if (!items) return false;
      const hasInFlight = items.some(
        (item) => item.status === "uploaded" || item.status === "processing"
      );
      return hasInFlight ? POLL_INTERVAL_MS : false;
    },
  });
}