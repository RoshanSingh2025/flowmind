import { useQuery } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api-client";

interface HealthResponse {
  status: string;
  environment: string;
}

/**
 * Polls the FastAPI `/health` endpoint. Used by the live "system status"
 * indicator in the demo section so the landing page reflects a real backend
 * rather than a hardcoded badge.
 */
export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: () => apiFetch<HealthResponse>("/api/v1/health"),
    retry: 0,
    refetchInterval: 30_000,
  });
}