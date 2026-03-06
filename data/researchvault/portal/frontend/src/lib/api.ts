import { API_BASE } from '@/config';

export type VaultRunResult = {
  argv: string[];
  exit_code: number;
  stdout: string;
  stderr: string;
  truncated: boolean;
  ok: boolean;
  db_path?: string;
  db_source?: string;
  db_note?: string;
};

export type Project = {
  id: string;
  name: string;
  objective: string;
  status: string;
  created_at: string;
  priority: number;
};

export type VaultEvent = {
  type: string;
  step: number;
  payload: string;
  confidence: number;
  source: string;
  timestamp: string;
  tags: string;
};

export type Insight = {
  title: string;
  content: string;
  evidence: string;
  tags: string;
  timestamp: string;
  confidence: number;
};

export type StatusData = {
  project: Project;
  recent_events: VaultEvent[];
  insights: Insight[];
};

export type Branch = {
  id: string;
  name: string;
  parent_id: string | null;
  hypothesis: string;
  status: string;
  created_at: string;
};

export type VerificationMission = {
  id: string;
  status: string;
  priority: number;
  query: string;
  finding_title: string;
  finding_conf: number;
  created_at: string;
  completed_at: string | null;
  last_error: string | null;
};

export type DbCandidate = {
  path: string;
  exists: boolean;
  size_bytes: number | null;
  mtime_s: number | null;
  schema_version: number | null;
  counts: Record<string, number> | null;
  last_finding_at: string | null;
  last_event_at: string | null;
  error: string | null;
};

export type ResolvedDb = Omit<DbCandidate, 'error'> & {
  source: 'selected' | 'env' | 'auto';
  note: string;
};

export type SystemDbsResponse = {
  now_ms: number;
  current: ResolvedDb;
  candidates: DbCandidate[];
};

export type DiagnosticsHint = {
  type: string;
  severity: 'low' | 'medium' | 'high';
  title: string;
  detail: string;
  recommend_db_path?: string;
  [k: string]: unknown;
};

export type DiagnosticsResponse = {
  now_ms: number;
  backend: { python: string; platform: string; pid: number };
  env: {
    RESEARCHVAULT_DB: string | null;
    RESEARCHVAULT_SEARCH_PROVIDERS?: string | null;
    RESEARCHVAULT_WATCHDOG_INGEST_TOP?: string | null;
    RESEARCHVAULT_VERIFY_INGEST_TOP?: string | null;
    RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS?: string | null;
    RESEARCHVAULT_PORTAL_TOKEN_set: boolean;
    BRAVE_API_KEY_set: boolean;
    SERPER_API_KEY_set?: boolean;
    SEARXNG_BASE_URL_set?: boolean;
    effective_allowed_db_roots?: string[];
  };
  providers: {
    brave: { configured: boolean; source: 'env' | 'portal' | 'none' | string };
    serper?: { configured: boolean; source: 'env' | 'portal' | 'none' | string };
    searxng?: { configured: boolean; source: 'env' | 'portal' | 'none' | string; base_url?: string | null };
    duckduckgo?: { configured: boolean; source: string };
    wikipedia?: { configured: boolean; source: string };
  };
  db: { current: ResolvedDb; candidates: DbCandidate[] };
  cli: {
    ok: boolean;
    exit_code: number;
    stderr: string;
    truncated: boolean;
    projects_parsed: number | null;
    parse_error: string | null;
  };
  hints: DiagnosticsHint[];
  snapshot: { current_projects: number | null; current_findings: number | null };
};

export type SecretsStatusResponse = {
  brave_api_key_configured: boolean;
  brave_api_key_source: 'env' | 'portal' | 'none' | string;
  serper_api_key_configured?: boolean;
  serper_api_key_source?: 'env' | 'portal' | 'none' | string;
  searxng_base_url_configured?: boolean;
  searxng_base_url_source?: 'env' | 'portal' | 'none' | string;
  searxng_base_url?: string | null;
};

export type GraphNode = {
  id: string;
  type: 'finding' | 'artifact';
  label: string;
  confidence?: number;
  tags?: string;
  created_at?: string;
  subtype?: string;
  path?: string;
  metadata?: string;
};

export type GraphEdge = {
  id: string | number;
  source: string;
  target: string;
  type: string;
  metadata?: string;
  created_at?: string;
};

export type GraphResponse = {
  ok: boolean;
  reason?: string;
  db: ResolvedDb;
  project_id: string;
  branch: string;
  branch_id?: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
};

export async function apiJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {}),
    },
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status}: ${text}`);
  }

  return res.json();
}

export async function runVaultGet(endpoint: string): Promise<VaultRunResult> {
  return apiJson<VaultRunResult>(endpoint, { method: 'GET' });
}

export async function runVaultPost(endpoint: string, payload?: unknown): Promise<VaultRunResult> {
  return apiJson<VaultRunResult>(endpoint, {
    method: 'POST',
    body: JSON.stringify(payload ?? {}),
  });
}

export async function systemGet<T>(path: string): Promise<T> {
  return apiJson<T>(`/system${path}`, { method: 'GET' });
}

export async function systemPost<T>(path: string, payload?: unknown): Promise<T> {
  return apiJson<T>(`/system${path}`, {
    method: 'POST',
    body: JSON.stringify(payload ?? {}),
  });
}

export function systemStreamUrl(intervalS: number): string {
  const url = new URL(`${API_BASE}/system/stream`);
  url.searchParams.set('interval_s', String(intervalS));
  return url.toString();
}
