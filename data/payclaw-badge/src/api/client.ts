import type { AgentIdentityResponse } from "../types.js";

class PayClawApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number
  ) {
    super(message);
    this.name = "PayClawApiError";
  }
}

const REQUEST_TIMEOUT_MS = 30_000;

function getConfig() {
  const baseUrl = process.env.PAYCLAW_API_URL;
  const apiKey = process.env.PAYCLAW_API_KEY;
  if (!baseUrl) throw new PayClawApiError("PayClaw API URL is not configured.");
  if (!apiKey) throw new PayClawApiError("PayClaw API key is not configured.");
  if (
    !baseUrl.startsWith("https://") &&
    !baseUrl.startsWith("http://localhost")
  ) {
    throw new PayClawApiError("PayClaw API URL must use HTTPS.");
  }
  return { baseUrl: baseUrl.replace(/\/+$/, ""), apiKey };
}

function authHeaders(apiKey: string): Record<string, string> {
  return {
    Authorization: `Bearer ${apiKey}`,
    "Content-Type": "application/json",
  };
}

async function request<T>(url: string, init: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  let res: Response;
  try {
    res = await fetch(url, { ...init, signal: controller.signal });
  } catch (err) {
    clearTimeout(timeout);
    if (err instanceof Error && err.name === "AbortError") {
      throw new PayClawApiError("Request timed out.");
    }
    throw new PayClawApiError("Could not reach the PayClaw API.");
  } finally {
    clearTimeout(timeout);
  }

  if (res.status === 401) {
    throw new PayClawApiError(
      "Authentication failed. Check your API key.",
      401
    );
  }

  if (!res.ok) {
    let body: string;
    try {
      const json = (await res.json()) as { error?: string };
      body = json.error ?? JSON.stringify(json);
    } catch {
      body = await res.text();
    }
    throw new PayClawApiError(body, res.status);
  }

  return (await res.json()) as T;
}

export async function getAgentIdentity(
  sessionId?: string,
  merchant?: string
): Promise<AgentIdentityResponse> {
  const { baseUrl, apiKey } = getConfig();
  return request<AgentIdentityResponse>(`${baseUrl}/api/agent-identity`, {
    method: "POST",
    headers: authHeaders(apiKey),
    body: JSON.stringify({
      session_id: sessionId,
      ...(merchant ? { merchant } : {}),
    }),
  });
}

export function isApiMode(): boolean {
  return !!process.env.PAYCLAW_API_URL;
}
