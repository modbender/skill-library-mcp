import { ContractValidationError } from "../common/contract-validation.js";
import {
  classifyAuthError,
  parseTokenResponse,
  toTokenRequestFormData,
  type TickTickAccessToken,
  type TickTickAuthFlowError,
  type TickTickRefreshTokenRequest,
  type TickTickTokenExchangeRequest,
} from "./oauth2-contract.js";

export interface TickTickOAuth2ClientConfig {
  tokenUrl: string;
  clientId: string;
  clientSecret: string;
  timeoutMs?: number;
  userAgent?: string;
  fetchImplementation?: TickTickFetchLike;
}

export interface ExchangeAuthorizationCodeInput {
  code: string;
  redirectUri: string;
  codeVerifier?: string;
}

export class TickTickOAuth2Error extends Error {
  readonly flowError: TickTickAuthFlowError;
  readonly status?: number;
  readonly responseBody?: unknown;

  constructor(flowError: TickTickAuthFlowError, status?: number, responseBody?: unknown) {
    super(flowError.message);
    this.name = "TickTickOAuth2Error";
    this.flowError = flowError;
    if (status !== undefined) {
      this.status = status;
    }
    if (responseBody !== undefined) {
      this.responseBody = responseBody;
    }
  }
}

export class TickTickOAuth2Client {
  private readonly config: ResolvedTickTickOAuth2ClientConfig;

  constructor(config: TickTickOAuth2ClientConfig) {
    this.config = resolveConfig(config);
  }

  async exchangeAuthorizationCode(input: ExchangeAuthorizationCodeInput): Promise<TickTickAccessToken> {
    assertNonEmpty(input.code, "code");
    assertNonEmpty(input.redirectUri, "redirectUri");

    const request: TickTickTokenExchangeRequest = {
      grantType: "authorization_code",
      code: input.code,
      redirectUri: input.redirectUri,
      clientId: this.config.clientId,
      clientSecret: this.config.clientSecret,
    };
    if (input.codeVerifier !== undefined) {
      request.codeVerifier = input.codeVerifier;
    }

    return this.executeTokenRequest(request);
  }

  async refreshAccessToken(refreshToken: string): Promise<TickTickAccessToken> {
    assertNonEmpty(refreshToken, "refreshToken");

    const request: TickTickRefreshTokenRequest = {
      grantType: "refresh_token",
      refreshToken,
      clientId: this.config.clientId,
      clientSecret: this.config.clientSecret,
    };

    return this.executeTokenRequest(request);
  }

  private async executeTokenRequest(
    request: TickTickTokenExchangeRequest | TickTickRefreshTokenRequest
  ): Promise<TickTickAccessToken> {
    try {
      const form = toTokenRequestFormData(request);
      const response = await runWithTimeout(
        () =>
          this.config.fetchImplementation(this.config.tokenUrl, {
            method: "POST",
            headers: buildTokenHeaders(this.config.userAgent),
            body: form.toString(),
          }),
        this.config.timeoutMs
      );

      const body = await readResponseBody(response);

      if (!response.ok) {
        const flowError = classifyAuthError(body);
        throw new TickTickOAuth2Error(flowError, response.status, body);
      }

      return parseTokenResponse(body);
    } catch (error) {
      if (error instanceof TickTickOAuth2Error) {
        throw error;
      }

      const flowError = classifyAuthError(error);
      throw new TickTickOAuth2Error(flowError);
    }
  }
}

interface TickTickFetchResponse {
  ok: boolean;
  status: number;
  headers: {
    get(name: string): string | null;
  };
  json(): Promise<unknown>;
  text(): Promise<string>;
}

interface TickTickFetchInit {
  method: "POST";
  headers: Record<string, string>;
  body: string;
}

type TickTickFetchLike = (url: string, init: TickTickFetchInit) => Promise<TickTickFetchResponse>;

interface ResolvedTickTickOAuth2ClientConfig {
  tokenUrl: string;
  clientId: string;
  clientSecret: string;
  timeoutMs: number;
  userAgent?: string;
  fetchImplementation: TickTickFetchLike;
}

function resolveConfig(config: TickTickOAuth2ClientConfig): ResolvedTickTickOAuth2ClientConfig {
  assertNonEmpty(config.clientId, "clientId");
  assertNonEmpty(config.clientSecret, "clientSecret");

  const tokenUrl = validateAbsoluteUrl(config.tokenUrl, "tokenUrl");
  const timeoutMs = config.timeoutMs ?? 10_000;
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) {
    throw new ContractValidationError("ticktick-oauth2-client", "timeoutMs must be a positive number.");
  }

  const fetchImplementation = config.fetchImplementation ?? resolveDefaultFetch();

  const resolved: ResolvedTickTickOAuth2ClientConfig = {
    tokenUrl,
    clientId: config.clientId,
    clientSecret: config.clientSecret,
    timeoutMs,
    fetchImplementation,
  };

  if (config.userAgent !== undefined) {
    resolved.userAgent = config.userAgent;
  }

  return resolved;
}

function resolveDefaultFetch(): TickTickFetchLike {
  const fetchImpl = (globalThis as { fetch?: unknown }).fetch;
  if (typeof fetchImpl !== "function") {
    throw new ContractValidationError("ticktick-oauth2-client", "fetch is not available in this runtime.");
  }

  return fetchImpl as TickTickFetchLike;
}

function validateAbsoluteUrl(value: string, field: string): string {
  assertNonEmpty(value, field);

  let parsed: URL;
  try {
    parsed = new URL(value);
  } catch {
    throw new ContractValidationError("ticktick-oauth2-client", `${field} must be an absolute URL.`);
  }

  return parsed.toString();
}

function assertNonEmpty(value: string, field: string): void {
  if (value.trim().length === 0) {
    throw new ContractValidationError("ticktick-oauth2-client", `${field} must be a non-empty string.`);
  }
}

function buildTokenHeaders(userAgent: string | undefined): Record<string, string> {
  const headers: Record<string, string> = {
    accept: "application/json",
    "content-type": "application/x-www-form-urlencoded",
  };

  if (userAgent !== undefined && userAgent.trim().length > 0) {
    headers["user-agent"] = userAgent;
  }

  return headers;
}

async function readResponseBody(response: TickTickFetchResponse): Promise<unknown> {
  const contentType = response.headers.get("content-type")?.toLowerCase() ?? "";
  if (contentType.includes("application/json")) {
    try {
      return await response.json();
    } catch {
      return undefined;
    }
  }

  const text = await response.text();
  return text.length === 0 ? undefined : text;
}

async function runWithTimeout<T>(run: () => Promise<T>, timeoutMs: number): Promise<T> {
  let timeoutHandle: ReturnType<typeof setTimeout> | undefined;

  const timeoutPromise = new Promise<never>((_, reject) => {
    timeoutHandle = setTimeout(() => {
      reject(new Error(`OAuth token request timeout after ${timeoutMs}ms`));
    }, timeoutMs);
  });

  try {
    return await Promise.race([run(), timeoutPromise]);
  } finally {
    if (timeoutHandle !== undefined) {
      clearTimeout(timeoutHandle);
    }
  }
}
