import { request as playwrightRequest, type APIRequestContext } from "playwright";

const DEFAULT_API_BASE = "https://app.prospairrow.com/api/v1";

export type ProspectApiRecord = Record<string, unknown>;

type ApiCallResult = {
  ok: boolean;
  status: number;
  data: Record<string, unknown>;
  error?: string;
};

function asObject(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) return {};
  return value as Record<string, unknown>;
}

function isAllowedApiBase(apiBase: string): boolean {
  try {
    const url = new URL(apiBase);
    return url.protocol === "https:" && url.hostname === "app.prospairrow.com";
  } catch {
    return false;
  }
}

function normalizeApiBase(input?: string): string {
  const raw = String(input || DEFAULT_API_BASE).trim();
  return raw.replace(/\/+$/, "");
}

function normalizePath(path: string): string {
  return path.replace(/^\/+/, "");
}

async function parseResponse(response: Awaited<ReturnType<APIRequestContext["fetch"]>>): Promise<unknown> {
  const text = await response.text();
  if (!text) return {};
  try {
    return JSON.parse(text);
  } catch {
    return { raw: text };
  }
}

function formatError(path: string, method: "GET" | "POST", status: number, payload: Record<string, unknown>): string {
  const msg = String(payload.error || payload.message || `HTTP_${status}`);
  return `${msg} [${method} ${path} status=${status}]`;
}

export class ProspairrowApiClient {
  private constructor(
    private readonly requestContext: APIRequestContext,
    public readonly apiBase: string,
    private readonly apiKey: string
  ) {}

  static async fromEnv(): Promise<{ client?: ProspairrowApiClient; error?: string }> {
    const key = String(process.env.PROSPAIRROW_API_KEY || "").trim();
    if (!key) {
      return { error: "PROSPAIRROW_API_KEY_NOT_SET" };
    }
    return this.fromApiKey(key);
  }

  static async fromApiKey(apiKey: string): Promise<{ client?: ProspairrowApiClient; error?: string }> {
    const key = String(apiKey || "").trim();
    if (!key) {
      return { error: "PROSPAIRROW_API_KEY_NOT_SET" };
    }

    const apiBase = normalizeApiBase(process.env.PROSPAIRROW_API_BASE);
    if (!isAllowedApiBase(apiBase)) {
      return { error: `PROSPAIRROW_API_BASE_INVALID_OR_BLOCKED: ${apiBase}` };
    }

    const requestContext = await playwrightRequest.newContext({
      baseURL: `${apiBase}/`,
      extraHTTPHeaders: {
        Accept: "application/json",
        "Content-Type": "application/json",
        Authorization: `Bearer ${key}`,
        "X-API-Key": key
      }
    });

    return { client: new ProspairrowApiClient(requestContext, apiBase, key) };
  }

  async close(): Promise<void> {
    await this.requestContext.dispose();
  }

  private async call(
    path: string,
    method: "GET" | "POST" = "GET",
    body?: unknown,
    headers?: Record<string, string>
  ): Promise<ApiCallResult> {
    const relativePath = normalizePath(path);
    const response = await this.requestContext.fetch(relativePath, {
      method,
      data: body,
      headers
    });

    const parsed = asObject(await parseResponse(response));
    if (!response.ok()) {
      return {
        ok: false,
        status: response.status(),
        data: parsed,
        error: formatError(relativePath, method, response.status(), parsed)
      };
    }

    return { ok: true, status: response.status(), data: parsed };
  }

  async listProspects(limit = 50): Promise<{ ok: boolean; status: number; prospects: ProspectApiRecord[]; error?: string; raw: Record<string, unknown> }> {
    const res = await this.call(`prospects?limit=${encodeURIComponent(String(limit))}`, "GET");
    const prospects = Array.isArray(res.data.prospects)
      ? (res.data.prospects as ProspectApiRecord[])
      : (Array.isArray(res.data.items) ? (res.data.items as ProspectApiRecord[]) : []);
    return { ok: res.ok, status: res.status, prospects, error: res.error, raw: res.data };
  }

  async searchProspects(companyName: string, limit = 5): Promise<{ ok: boolean; status: number; prospects: ProspectApiRecord[]; error?: string; raw: Record<string, unknown> }> {
    const res = await this.call(`prospects/search?company_name=${encodeURIComponent(companyName)}&limit=${encodeURIComponent(String(limit))}`, "GET");
    const prospects = Array.isArray(res.data.prospects) ? (res.data.prospects as ProspectApiRecord[]) : [];
    return { ok: res.ok, status: res.status, prospects, error: res.error, raw: res.data };
  }

  async listIcpQualifiedProspects(input: {
    minCompanyScore: number;
    minIcpScore?: number;
    perPage?: number;
    page?: number;
  }): Promise<{ ok: boolean; status: number; prospects: ProspectApiRecord[]; error?: string; raw: Record<string, unknown> }> {
    const query = new URLSearchParams();
    query.set("min_company_score", String(input.minCompanyScore));
    if (typeof input.minIcpScore === "number") query.set("min_icp_score", String(input.minIcpScore));
    if (typeof input.perPage === "number") query.set("per_page", String(input.perPage));
    if (typeof input.page === "number") query.set("page", String(input.page));

    const res = await this.call(`prospects/icp-qualified?${query.toString()}`, "GET");
    const prospects = Array.isArray(res.data.prospects)
      ? (res.data.prospects as ProspectApiRecord[])
      : (Array.isArray(res.data.items) ? (res.data.items as ProspectApiRecord[]) : []);
    return { ok: res.ok, status: res.status, prospects, error: res.error, raw: res.data };
  }

  async createProspect(payload: Record<string, unknown>): Promise<ApiCallResult> {
    return this.call("prospects", "POST", payload);
  }

  async getProspect(prospectId: string): Promise<ApiCallResult> {
    return this.call(`prospects/${encodeURIComponent(prospectId)}`, "GET");
  }

  async getBusinessIntelligence(prospectId: string): Promise<ApiCallResult> {
    return this.call(`prospects/${encodeURIComponent(prospectId)}/business-intelligence`, "GET");
  }

  async getSalesStrategy(prospectId: string): Promise<ApiCallResult> {
    return this.call(`prospects/${encodeURIComponent(prospectId)}/sales-strategy`, "GET");
  }

  async enrichProspect(prospectId: string): Promise<ApiCallResult> {
    return this.call(`prospects/${encodeURIComponent(prospectId)}/comprehensive-enrich`, "POST");
  }

  async generateContentMarketing(positioningIntensity: number): Promise<ApiCallResult> {
    return this.call(
      "content-marketing/generate",
      "POST",
      {
        positioning_intensity: positioningIntensity
      },
      {
        Authorization: `Bearer ${this.apiKey}`,
        "X-API-Key": this.apiKey
      }
    );
  }

  async generatePositionSolution(prospectId: string): Promise<ApiCallResult> {
    return this.call(`prospects/${encodeURIComponent(prospectId)}/position-solution`, "POST");
  }

  async getCompetitors(prospectId: string): Promise<ApiCallResult> {
    return this.call(`prospects/${encodeURIComponent(prospectId)}/competitors`, "GET");
  }

  async discoverCompetitors(prospectId: string): Promise<ApiCallResult> {
    return this.call(
      `prospects/${encodeURIComponent(prospectId)}/competitors/discover`,
      "POST",
      undefined,
      {
        Authorization: `Bearer ${this.apiKey}`,
        "X-API-Key": this.apiKey
      }
    );
  }

  async apolloIcpRun(
    prospectId: string,
    input: {
      reveal: boolean;
      revealLimit: number;
    }
  ): Promise<ApiCallResult> {
    return this.call(`prospects/${encodeURIComponent(prospectId)}/apollo-icp-run`, "POST", {
      reveal: input.reveal,
      reveal_limit: input.revealLimit
    });
  }

  async getIcpScore(
    prospectId: string,
    input: {
      forceRescore?: boolean;
    }
  ): Promise<ApiCallResult> {
    return this.call(`prospects/${encodeURIComponent(prospectId)}/icp-score`, "POST", {
      force_rescore: Boolean(input.forceRescore)
    });
  }

  async getCompanyScore(prospectId: string): Promise<ApiCallResult> {
    return this.call(`prospects/${encodeURIComponent(prospectId)}/company-score`, "POST");
  }

}

export function pickProspectId(record: Record<string, unknown>): string | null {
  const id = record.id ?? record.prospect_id ?? asObject(record.prospect).id;
  if (!id) return null;
  return String(id);
}

export function pickCompany(record: Record<string, unknown>): string {
  return String(record.company || record.company_name || "").trim();
}

export function pickWebsite(record: Record<string, unknown>): string {
  return String(record.website || record.company_website || "").trim();
}
