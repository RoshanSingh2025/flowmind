export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/**
 * Thin fetch wrapper for the FlowMind API. Kept dependency-free (no axios)
 * since the surface area today is a couple of read-only endpoints; this is
 * the single seam to extend (auth headers, retries) as the API grows.
 */
export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`FlowMind API error ${response.status}: ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}
