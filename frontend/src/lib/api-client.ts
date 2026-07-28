/**
 * FlowMind API client.
 *
 * Every error response from the backend follows one envelope (see
 * `app.core.error_handlers._error_envelope`):
 *
 *   { "error": { "code": "...", "message": "...", "request_id": "...", "details"?: ... } }
 *
 * `ApiError` carries that structure through so callers (and the UI) can show
 * the backend's actual message ("Only MP4 files are supported...") instead of
 * a generic "API error 422" string, and can branch on `code` when useful
 * (e.g. "file_too_large" vs "unsupported_file_type").
 */

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    request_id: string | null;
    details?: unknown;
  };
}

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly requestId: string | null;
  readonly details: unknown;

  constructor(status: number, body: ApiErrorBody | null) {
    super(body?.error.message ?? `FlowMind API error ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.code = body?.error.code ?? "unknown_error";
    this.requestId = body?.error.request_id ?? null;
    this.details = body?.error.details;
  }
}

async function toApiError(response: Response): Promise<ApiError> {
  try {
    const body = (await response.json()) as ApiErrorBody;
    return new ApiError(response.status, body);
  } catch {
    return new ApiError(response.status, null);
  }
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const isFormData = typeof FormData !== "undefined" && init?.body instanceof FormData;

  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      ...init?.headers,
    },
  });

  if (!response.ok) {
    throw await toApiError(response);
  }

  return response.json() as Promise<T>;
}

export interface UploadProgress {
  loaded: number;
  total: number;
  percent: number;
}

export function apiUpload<T>(
  path: string,
  formData: FormData,
  options?: {
    onProgress?: (progress: UploadProgress) => void;
    signal?: AbortSignal;
  }
): Promise<T> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${API_URL}${path}`);

    xhr.upload.onprogress = (event) => {
      if (!options?.onProgress) return;
      const total = event.lengthComputable ? event.total : 0;
      const loaded = event.loaded;
      const percent = total > 0 ? Math.min(100, Math.max(0, (loaded / total) * 100)) : 0;
      options.onProgress({ loaded, total, percent });
    };

    xhr.onload = () => {
      let parsedBody: unknown = null;
      try {
        parsedBody = xhr.responseText ? JSON.parse(xhr.responseText) : null;
      } catch {
        parsedBody = null;
      }

      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(parsedBody as T);
      } else {
        reject(new ApiError(xhr.status, parsedBody as ApiErrorBody | null));
      }
    };

    xhr.onerror = () => {
      reject(new ApiError(0, null));
    };

    xhr.onabort = () => {
      const abortError = new Error("Upload aborted");
      abortError.name = "AbortError";
      reject(abortError);
    };

    if (options?.signal) {
      if (options.signal.aborted) {
        xhr.abort();
      } else {
        options.signal.addEventListener("abort", () => xhr.abort());
      }
    }

    xhr.send(formData);
  });
}