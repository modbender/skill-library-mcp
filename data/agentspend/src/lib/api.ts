import type {
  CheckRequest,
  CheckResponse,
  ConfigureClaimResponse,
  ConfigureStatusResponse,
  PayRequest,
  PayResponse,
  SearchResponse,
  StatusResponse,
} from "../types.js";

const API_URL = "https://api.agentspend.co";

export class ApiError extends Error {
  readonly status: number;
  readonly body: unknown;

  constructor(message: string, status: number, body: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

async function parseBody(response: Response): Promise<unknown> {
  const contentType = response.headers.get("content-type") ?? "";

  if (contentType.includes("application/json")) {
    try {
      return await response.json();
    } catch {
      return null;
    }
  }

  return response.text();
}

function errorMessageFromBody(body: unknown, fallback: string): string {
  if (body && typeof body === "object" && "error" in body && typeof body.error === "string") {
    return body.error;
  }

  if (typeof body === "string" && body.length > 0) {
    return body;
  }

  return fallback;
}

export class AgentspendApiClient {
  constructor(private readonly baseUrl = API_URL) {}

  private async request<T>(path: string, init: RequestInit = {}, apiKey?: string): Promise<T> {
    const headers: Record<string, string> = {
      ...(init.headers as Record<string, string> | undefined),
    };

    if (apiKey) {
      headers.Authorization = `Bearer ${apiKey}`;
    }

    if (init.body && !headers["content-type"] && !headers["Content-Type"]) {
      headers["content-type"] = "application/json";
    }

    const response = await fetch(`${this.baseUrl}${path}`, {
      ...init,
      headers,
    });

    const body = await parseBody(response);

    if (!response.ok) {
      throw new ApiError(errorMessageFromBody(body, `Request failed (${response.status})`), response.status, body);
    }

    return body as T;
  }

  pay(apiKey: string, payload: PayRequest): Promise<PayResponse> {
    return this.request<PayResponse>("/pay", {
      method: "POST",
      body: JSON.stringify(payload),
    }, apiKey);
  }

  check(apiKey: string, payload: CheckRequest): Promise<CheckResponse> {
    return this.request<CheckResponse>("/check", {
      method: "POST",
      body: JSON.stringify(payload),
    }, apiKey);
  }

  status(apiKey: string): Promise<StatusResponse> {
    return this.request<StatusResponse>("/status", {
      method: "GET",
    }, apiKey);
  }

  configure(payload?: { weekly_limit_usd?: number }, apiKey?: string): Promise<ConfigureStatusResponse> {
    return this.request<ConfigureStatusResponse>("/configure", {
      method: "POST",
      body: payload ? JSON.stringify(payload) : undefined,
    }, apiKey);
  }

  configureStatus(token: string): Promise<ConfigureStatusResponse> {
    return this.request<ConfigureStatusResponse>(`/configure/${encodeURIComponent(token)}/status`, {
      method: "GET",
    });
  }

  claimConfigure(token: string, apiKeyHash: string): Promise<ConfigureClaimResponse> {
    return this.request<ConfigureClaimResponse>(`/configure/${encodeURIComponent(token)}/claim`, {
      method: "POST",
      body: JSON.stringify({ api_key_hash: apiKeyHash }),
    });
  }

  search(apiKey: string, query: string): Promise<SearchResponse> {
    const params = new URLSearchParams({ q: query });
    return this.request<SearchResponse>(`/search?${params.toString()}`, {
      method: "GET",
    }, apiKey);
  }
}
