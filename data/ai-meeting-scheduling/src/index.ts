// SkipUp Meeting Scheduler — OpenClaw Skill
// Client-side wrapper for SkipUp's public Meeting Requests API

const BASE_URL = "https://api.skipup.ai/api/v1";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface Participant {
  email: string;
  name?: string;
  timezone?: string;
}

export interface Timeframe {
  start?: string; // ISO 8601 datetime
  end?: string;   // ISO 8601 datetime
}

export interface MeetingContext {
  title?: string;
  purpose?: string;
  description?: string;    // Free-text instructions for the AI
  duration_minutes?: number;
  timeframe?: Timeframe;
}

export interface CreateMeetingRequestParams {
  organizer_email: string;
  organizer_name?: string;
  organizer_timezone?: string;
  participant_emails?: string[];
  participants?: Participant[];
  include_introduction?: boolean;
  context?: MeetingContext;
  idempotency_key?: string;
}

export interface CancelMeetingRequestParams {
  id: string;
  notify?: boolean;
}

export interface MeetingRequest {
  id: string;
  organizer_email: string;
  participant_emails: string[];
  status: "active" | "booked" | "cancelled" | "paused";
  title?: string;
  purpose?: string;
  description?: string;
  include_introduction?: boolean;
  duration_minutes?: number;
  timeframe?: Timeframe;
  created_at: string;
  updated_at: string;
  booked_at?: string;
  cancelled_at?: string;
  paused_at?: string;
}

export interface WorkspaceMember {
  id: string;
  email: string;
  name: string;
  role: string;
  deactivated_at: string | null;
  created_at: string;
}

export interface PaginationMeta {
  limit: number;
  has_more: boolean;
  next_cursor?: string;
}

export interface ListMeetingRequestsParams {
  participant_email?: string;
  organizer_email?: string;
  status?: "active" | "paused" | "booked" | "cancelled";
  created_after?: string;
  created_before?: string;
  limit?: number;
  cursor?: string;
}

export interface ListWorkspaceMembersParams {
  email?: string;
  role?: string;
  limit?: number;
  cursor?: string;
}

export interface SkipUpError {
  error: {
    type: string;
    message: string;
  };
}

export type SkipUpResult<T> =
  | { ok: true; data: T; status: number }
  | { ok: false; error: SkipUpError["error"]; status: number };

export type SkipUpPaginatedResult<T> =
  | { ok: true; data: T[]; meta: PaginationMeta; status: number }
  | { ok: false; error: SkipUpError["error"]; status: number };

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

function getApiKey(): string {
  const key = process.env.SKIPUP_API_KEY;
  if (!key) {
    throw new Error(
      "SKIPUP_API_KEY environment variable is not set. " +
      "Get your API key from your SkipUp workspace settings."
    );
  }
  return key;
}

function buildHeaders(method: string, idempotencyKey?: string): Record<string, string> {
  const h: Record<string, string> = {
    "Authorization": `Bearer ${getApiKey()}`,
    "Accept": "application/json",
  };
  if (method !== "GET") {
    h["Content-Type"] = "application/json";
  }
  if (idempotencyKey) {
    h["Idempotency-Key"] = idempotencyKey;
  }
  return h;
}

async function request<T>(
  method: string,
  path: string,
  body?: Record<string, unknown>,
  idempotencyKey?: string
): Promise<SkipUpResult<T>> {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    method,
    headers: buildHeaders(method, idempotencyKey),
    body: body ? JSON.stringify(body) : undefined,
  });

  const json = await res.json();

  if (!res.ok) {
    return {
      ok: false,
      error: (json as SkipUpError).error ?? { type: "unknown", message: res.statusText },
      status: res.status,
    };
  }

  return { ok: true, data: (json as { data: T }).data, status: res.status };
}

async function requestPaginated<T>(
  path: string,
  params?: Record<string, string | number | undefined>
): Promise<SkipUpPaginatedResult<T>> {
  const query = new URLSearchParams();
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined) {
        query.set(key, String(value));
      }
    }
  }
  const qs = query.toString();
  const url = `${BASE_URL}${path}${qs ? `?${qs}` : ""}`;
  const res = await fetch(url, {
    method: "GET",
    headers: buildHeaders("GET"),
  });

  const json = await res.json();

  if (!res.ok) {
    return {
      ok: false,
      error: (json as SkipUpError).error ?? { type: "unknown", message: res.statusText },
      status: res.status,
    };
  }

  const parsed = json as { data: T[]; meta: PaginationMeta };
  return { ok: true, data: parsed.data, meta: parsed.meta, status: res.status };
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Create a new meeting request.
 *
 * SkipUp will asynchronously reach out to all participants via email to
 * coordinate availability, negotiate across timezones, and book a meeting.
 * Returns 202 Accepted — the meeting is NOT instantly booked.
 */
export async function createMeetingRequest(
  params: CreateMeetingRequestParams
): Promise<SkipUpResult<MeetingRequest>> {
  const body: Record<string, unknown> = {
    organizer_email: params.organizer_email,
  };

  if (params.organizer_name) body.organizer_name = params.organizer_name;
  if (params.organizer_timezone) body.organizer_timezone = params.organizer_timezone;
  if (params.include_introduction !== undefined) body.include_introduction = params.include_introduction;

  // Exactly one of participants or participant_emails must be provided
  if (params.participants) {
    body.participants = params.participants;
  } else if (params.participant_emails) {
    body.participant_emails = params.participant_emails;
  }

  if (params.context) body.context = params.context;

  return request<MeetingRequest>(
    "POST",
    "/meeting_requests",
    body,
    params.idempotency_key
  );
}

/**
 * Cancel an active or paused meeting request.
 *
 * Only requests with status "active" or "paused" can be cancelled.
 * Set `notify: true` to send cancellation emails to participants.
 */
export async function cancelMeetingRequest(
  params: CancelMeetingRequestParams
): Promise<SkipUpResult<MeetingRequest>> {
  const body: Record<string, unknown> = {};
  if (params.notify !== undefined) body.notify = params.notify;

  return request<MeetingRequest>(
    "POST",
    `/meeting_requests/${encodeURIComponent(params.id)}/cancel`,
    body
  );
}

/**
 * Pause an active meeting request.
 *
 * Only requests with status "active" can be paused. Pausing is silent —
 * participants are not notified. While paused, SkipUp stops processing
 * messages and sending follow-ups. Incoming messages are still recorded.
 */
export async function pauseMeetingRequest(
  id: string
): Promise<SkipUpResult<MeetingRequest>> {
  return request<MeetingRequest>(
    "POST",
    `/meeting_requests/${encodeURIComponent(id)}/pause`
  );
}

/**
 * Resume a paused meeting request.
 *
 * Only requests with status "paused" can be resumed. SkipUp returns to
 * active status and picks up scheduling where it left off, including
 * reviewing any messages that arrived while paused.
 */
export async function resumeMeetingRequest(
  id: string
): Promise<SkipUpResult<MeetingRequest>> {
  return request<MeetingRequest>(
    "POST",
    `/meeting_requests/${encodeURIComponent(id)}/resume`
  );
}

/**
 * List meeting requests in the workspace.
 *
 * Returns a paginated list sorted by creation date (newest first).
 * Filter by participant, organizer, status, or date range.
 */
export async function listMeetingRequests(
  params?: ListMeetingRequestsParams
): Promise<SkipUpPaginatedResult<MeetingRequest>> {
  return requestPaginated<MeetingRequest>("/meeting_requests", params);
}

/**
 * Get a single meeting request by ID.
 */
export async function getMeetingRequest(
  id: string
): Promise<SkipUpResult<MeetingRequest>> {
  return request<MeetingRequest>(
    "GET",
    `/meeting_requests/${encodeURIComponent(id)}`
  );
}

/**
 * List workspace members.
 *
 * Returns a paginated list of active members, ordered by most recently added.
 * Filter by email or role.
 */
export async function listWorkspaceMembers(
  params?: ListWorkspaceMembersParams
): Promise<SkipUpPaginatedResult<WorkspaceMember>> {
  return requestPaginated<WorkspaceMember>("/workspace_members", params);
}
