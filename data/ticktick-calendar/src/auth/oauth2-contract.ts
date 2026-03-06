import {
  ContractValidationError,
  ensureRecord,
  readOptionalString,
  readRequiredString,
  UnknownRecord,
} from "../common/contract-validation.js";

const CALLBACK_CONTRACT = "oauth2-callback";
const TOKEN_CONTRACT = "oauth2-token-response";

export type TickTickOAuthGrantType = "authorization_code" | "refresh_token";

export interface TickTickAuthorizationRequest {
  clientId: string;
  redirectUri: string;
  state: string;
  scope?: string;
  responseType?: "code";
  codeChallenge?: string;
  codeChallengeMethod?: "S256";
}

export interface TickTickTokenExchangeRequest {
  grantType: "authorization_code";
  code: string;
  redirectUri: string;
  clientId: string;
  clientSecret: string;
  codeVerifier?: string;
}

export interface TickTickRefreshTokenRequest {
  grantType: "refresh_token";
  refreshToken: string;
  clientId: string;
  clientSecret: string;
}

export type TickTickTokenRequest = TickTickTokenExchangeRequest | TickTickRefreshTokenRequest;

export interface TickTickAuthorizationCallbackSuccess {
  code: string;
  state?: string;
}

export interface TickTickAuthorizationCallbackFailure {
  error: string;
  errorDescription?: string;
  state?: string;
}

export type TickTickAuthorizationCallback =
  | { ok: true; value: TickTickAuthorizationCallbackSuccess }
  | { ok: false; value: TickTickAuthorizationCallbackFailure };

export interface TickTickAccessToken {
  accessToken: string;
  tokenType: string;
  refreshToken?: string;
  scope?: string;
  expiresIn?: number;
}

export type TickTickAuthErrorCode =
  | "access_denied"
  | "invalid_grant"
  | "invalid_request"
  | "invalid_client"
  | "invalid_scope"
  | "unsupported_grant_type"
  | "network_error"
  | "timeout"
  | "unknown";

export interface TickTickAuthFlowError {
  code: TickTickAuthErrorCode;
  message: string;
  retriable: boolean;
  cause?: unknown;
}

export function buildAuthorizationUrl(baseUrl: string, request: TickTickAuthorizationRequest): string {
  if (request.state.trim().length === 0) {
    throw new ContractValidationError("oauth2-authorization-request", "State must be a non-empty string.");
  }

  const url = new URL(baseUrl);
  url.searchParams.set("client_id", request.clientId);
  url.searchParams.set("redirect_uri", request.redirectUri);
  url.searchParams.set("response_type", request.responseType ?? "code");
  url.searchParams.set("state", request.state);

  if (request.scope !== undefined) {
    url.searchParams.set("scope", request.scope);
  }
  if (request.codeChallenge !== undefined) {
    url.searchParams.set("code_challenge", request.codeChallenge);
    url.searchParams.set("code_challenge_method", request.codeChallengeMethod ?? "S256");
  }

  return url.toString();
}

export function parseAuthorizationCallback(payload: unknown): TickTickAuthorizationCallback {
  const record = ensureRecord(payload, CALLBACK_CONTRACT);

  const code = readOptionalString(record, "code", CALLBACK_CONTRACT);
  const error = readOptionalString(record, "error", CALLBACK_CONTRACT);
  const state = readOptionalString(record, "state", CALLBACK_CONTRACT);

  if (code !== undefined && error !== undefined) {
    throw new ContractValidationError(CALLBACK_CONTRACT, "Callback payload cannot contain both 'code' and 'error'.");
  }
  if (code === undefined && error === undefined) {
    throw new ContractValidationError(CALLBACK_CONTRACT, "Callback payload must contain either 'code' or 'error'.");
  }

  if (error !== undefined) {
    const errorDescription = readOptionalString(record, "error_description", CALLBACK_CONTRACT);
    const failure: TickTickAuthorizationCallbackFailure = {
      error,
    };
    if (errorDescription !== undefined) {
      failure.errorDescription = errorDescription;
    }
    if (state !== undefined) {
      failure.state = state;
    }

    return {
      ok: false,
      value: failure,
    };
  }

  if (code === undefined) {
    throw new ContractValidationError(CALLBACK_CONTRACT, "Missing authorization code.");
  }

  const success: TickTickAuthorizationCallbackSuccess = {
    code,
  };
  if (state !== undefined) {
    success.state = state;
  }

  return {
    ok: true,
    value: success,
  };
}

export function parseTokenResponse(payload: unknown): TickTickAccessToken {
  const record = ensureRecord(payload, TOKEN_CONTRACT);

  const accessToken = readStringFromAliases(record, ["access_token", "accessToken"], TOKEN_CONTRACT);
  const tokenType = readStringFromAliases(record, ["token_type", "tokenType"], TOKEN_CONTRACT);
  const refreshToken = readOptionalStringFromAliases(record, ["refresh_token", "refreshToken"], TOKEN_CONTRACT);
  const scope = readOptionalString(record, "scope", TOKEN_CONTRACT);

  const expiresInRaw = readOptionalValueFromAliases(record, ["expires_in", "expiresIn"]);
  let expiresIn: number | undefined;
  if (expiresInRaw !== undefined) {
    expiresIn = parseExpiresIn(expiresInRaw);
  }

  const token: TickTickAccessToken = {
    accessToken,
    tokenType,
  };

  if (refreshToken !== undefined) {
    token.refreshToken = refreshToken;
  }
  if (scope !== undefined) {
    token.scope = scope;
  }
  if (expiresIn !== undefined) {
    token.expiresIn = expiresIn;
  }

  return token;
}

function readStringFromAliases(record: UnknownRecord, keys: string[], contract: string): string {
  for (const key of keys) {
    const value = record[key];
    if (typeof value === "string" && value.trim().length > 0) {
      return value;
    }
  }

  throw new ContractValidationError(contract, `Missing required string in aliases: ${keys.join(", ")}.`);
}

function readOptionalStringFromAliases(record: UnknownRecord, keys: string[], contract: string): string | undefined {
  for (const key of keys) {
    const value = record[key];
    if (value === undefined || value === null) {
      continue;
    }
    if (typeof value !== "string") {
      throw new ContractValidationError(contract, `Expected '${key}' to be a string.`);
    }
    return value;
  }
  return undefined;
}

function readOptionalValueFromAliases(record: UnknownRecord, keys: string[]): unknown {
  for (const key of keys) {
    if (record[key] !== undefined && record[key] !== null) {
      return record[key];
    }
  }
  return undefined;
}

function parseExpiresIn(value: unknown): number {
  if (typeof value === "number" && Number.isFinite(value) && value >= 0) {
    return value;
  }
  if (typeof value === "string" && value.trim().length > 0) {
    const parsed = Number.parseInt(value, 10);
    if (Number.isFinite(parsed) && parsed >= 0) {
      return parsed;
    }
  }

  throw new ContractValidationError(TOKEN_CONTRACT, "Expected 'expires_in' to be a non-negative integer.");
}

export function toTokenRequestFormData(request: TickTickTokenRequest): URLSearchParams {
  const form = new URLSearchParams();
  form.set("grant_type", request.grantType);
  form.set("client_id", request.clientId);
  form.set("client_secret", request.clientSecret);

  if (request.grantType === "authorization_code") {
    form.set("code", request.code);
    form.set("redirect_uri", request.redirectUri);
    if (request.codeVerifier !== undefined) {
      form.set("code_verifier", request.codeVerifier);
    }
    return form;
  }

  form.set("refresh_token", request.refreshToken);
  return form;
}

export function classifyAuthError(error: unknown): TickTickAuthFlowError {
  if (isObjectWithStringField(error, "error")) {
    const errorRecord = error as Record<string, unknown>;
    const oauthError = errorRecord.error;
    if (typeof oauthError !== "string") {
      return {
        code: "unknown",
        message: "OAuth2 error payload is malformed.",
        retriable: false,
        cause: error,
      };
    }

    const code = mapAuthCode(oauthError);
    const description = typeof errorRecord.error_description === "string" ? errorRecord.error_description : undefined;

    return {
      code,
      message: description ?? oauthError,
      retriable: code === "network_error" || code === "timeout" || code === "unknown",
      cause: error,
    };
  }

  if (error instanceof Error) {
    const lowered = error.message.toLowerCase();
    if (lowered.includes("timeout")) {
      return {
        code: "timeout",
        message: error.message,
        retriable: true,
        cause: error,
      };
    }

    return {
      code: "network_error",
      message: error.message,
      retriable: true,
      cause: error,
    };
  }

  return {
    code: "unknown",
    message: "Unknown OAuth2 auth error",
    retriable: false,
    cause: error,
  };
}

function isObjectWithStringField(value: unknown, field: string): value is Record<string, string> {
  return typeof value === "object" && value !== null && typeof (value as Record<string, unknown>)[field] === "string";
}

function mapAuthCode(code: string): TickTickAuthErrorCode {
  const known: TickTickAuthErrorCode[] = [
    "access_denied",
    "invalid_grant",
    "invalid_request",
    "invalid_client",
    "invalid_scope",
    "unsupported_grant_type",
  ];

  return known.includes(code as TickTickAuthErrorCode) ? (code as TickTickAuthErrorCode) : "unknown";
}

export function assertValidTokenRequestPayload(value: unknown): TickTickTokenRequest {
  const record = ensureRecord(value, "oauth2-token-request");
  const grantType = readRequiredString(record, "grantType", "oauth2-token-request");
  const clientId = readRequiredString(record, "clientId", "oauth2-token-request");
  const clientSecret = readRequiredString(record, "clientSecret", "oauth2-token-request");

  if (grantType === "authorization_code") {
    const codeVerifier = readOptionalString(record, "codeVerifier", "oauth2-token-request");
    const exchangeRequest: TickTickTokenExchangeRequest = {
      grantType,
      code: readRequiredString(record, "code", "oauth2-token-request"),
      redirectUri: readRequiredString(record, "redirectUri", "oauth2-token-request"),
      clientId,
      clientSecret,
    };
    if (codeVerifier !== undefined) {
      exchangeRequest.codeVerifier = codeVerifier;
    }

    return exchangeRequest;
  }

  if (grantType === "refresh_token") {
    return {
      grantType,
      refreshToken: readRequiredString(record, "refreshToken", "oauth2-token-request"),
      clientId,
      clientSecret,
    };
  }

  throw new ContractValidationError(
    "oauth2-token-request",
    "Expected grantType to be 'authorization_code' or 'refresh_token'."
  );
}
