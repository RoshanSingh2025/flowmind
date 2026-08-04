/**
 * Types mirroring the backend's upload contract exactly (see
 * `backend/app/schemas/upload.py`, `backend/app/models/upload.py`, and
 * `backend/app/core/config.py`). Keeping these in one place means the
 * frontend can't silently drift from what the API actually accepts.
 */

/** Mirrors `app.models.upload.UploadStatus`. Only "uploaded" is ever set
 * today — the rest are reserved for pipeline stages not yet implemented. */
export type UploadStatus = "uploaded" | "queued" | "processing" | "completed" | "failed";

/** Response body of `POST /api/v1/uploads` (see `UploadCreateResponse`). */
export interface UploadCreateResponse {
  upload_id: string;
  status: UploadStatus;
}

/** Response body of `GET /api/v1/uploads/{upload_id}` (see `UploadRead`). */
export interface UploadRead {
  upload_id: string;
  original_filename: string;
  stored_filename: string;
  mime_type: string;
  file_size: number;
  checksum: string;
  status: UploadStatus;
  created_at: string;

  /**
   * Technical metadata, populated by ffprobe during upload. All `null`
   * until extraction succeeds, and remain `null` forever for uploads where
   * it failed (the backend logs and continues rather than failing the
   * upload — see `UploadService.create_upload`).
   */
  duration: number | null;
  width: number | null;
  height: number | null;
  fps: number | null;
  codec: string | null;
  bitrate: number | null;
  container_format: string | null;

  /**
   * Raw server-side filesystem path — NOT a loadable URL. There is
   * currently no static mount or route serving this file over HTTP, so this
   * cannot be used directly as an `<img src>` yet.
   */
  thumbnail_path: string | null;

  /**
   * Pipeline outputs, populated by the background processing pipeline.
   * All `null` until `status` reaches "completed" (or forever on "failed").
   */
  transcript: string | null;
  documentation_markdown: string | null;
  sop_markdown: string | null;
  faq_markdown: string | null;
  summary_markdown: string | null;
  processing_error: string | null;
}

/** Response body of `GET /api/v1/uploads` (paginated list, newest first). */
export interface UploadListResponse {
  items: UploadRead[];
  total: number;
  limit: number;
  offset: number;
}

/** The error envelope every FlowMind API error responds with (see
 * `app.core.error_handlers._error_envelope`). */
export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    request_id: string | null;
    details?: unknown;
  };
}

/** Response body of `GET /api/v1/uploads/{upload_id}/results` (see `ResultsResponse`). */
export interface ResultsResponse {
  upload_id: string;
  status: UploadStatus;
  original_filename: string;
  transcript: string | null;
  documentation: string | null;
  sop: string | null;
  faq: string | null;
  summary: string | null;
  error: string | null;
}

/**
 * Mirrors `Settings` defaults in `backend/app/core/config.py`:
 * `allowed_upload_extensions`, `allowed_upload_mime_types`, `max_upload_size_mb`.
 *
 * If those env vars are overridden on the backend, update these to match —
 * client-side validation exists purely to fail fast with a friendly message;
 * the server is still the source of truth and re-validates independently.
 */
export const ACCEPTED_UPLOAD_EXTENSIONS = [".mp4"] as const;
export const ACCEPTED_UPLOAD_MIME_TYPES = ["video/mp4"] as const;
export const MAX_UPLOAD_SIZE_MB = 500;
export const MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024;