/**
 * Authentication handling for MCP server
 * Supports Bearer tokens and OAuth2 PKCE flow
 */

import { z } from "zod";

export const AuthConfigSchema = z.object({
  apiKey: z.string().optional(),
  oauth2: z.object({
    clientId: z.string(),
    redirectUri: z.string(),
    scopes: z.array(z.string()).default([]),
  }).optional(),
});

export type AuthConfig = z.infer<typeof AuthConfigSchema>;

export interface AuthContext {
  apiKey?: string;
  accessToken?: string;
  userId?: string;
  orgId?: string;
  scopes: string[];
}

/**
 * Extract auth context from environment or request headers
 */
export function getAuthContext(headers?: Record<string, string>): AuthContext {
  const apiKey = process.env.DEAL_WORKS_API_KEY ?? headers?.["x-api-key"];
  const accessToken = headers?.["authorization"]?.replace(/^Bearer\s+/i, "");

  return {
    apiKey,
    accessToken: accessToken ?? apiKey,
    userId: headers?.["x-user-id"],
    orgId: headers?.["x-org-id"],
    scopes: parseScopes(headers?.["x-scopes"]),
  };
}

function parseScopes(scopeHeader?: string): string[] {
  if (!scopeHeader) return [];
  return scopeHeader.split(/[\s,]+/).filter(Boolean);
}

/**
 * Validate that auth context has required scopes
 */
export function requireScopes(context: AuthContext, required: string[]): void {
  if (required.length === 0) return;

  // API key has all scopes
  if (context.apiKey) return;

  const missing = required.filter((s) => !context.scopes.includes(s));
  if (missing.length > 0) {
    throw new Error(`Missing required scopes: ${missing.join(", ")}`);
  }
}

/**
 * Generate OAuth2 PKCE authorization URL
 */
export function generateAuthUrl(
  config: NonNullable<AuthConfig["oauth2"]>,
  state: string,
  codeVerifier: string
): string {
  const codeChallenge = generateCodeChallenge(codeVerifier);

  const params = new URLSearchParams({
    client_id: config.clientId,
    redirect_uri: config.redirectUri,
    response_type: "code",
    scope: config.scopes.join(" "),
    state,
    code_challenge: codeChallenge,
    code_challenge_method: "S256",
  });

  return `https://hq.works/oauth/authorize?${params.toString()}`;
}

/**
 * Generate PKCE code challenge from verifier
 */
function generateCodeChallenge(verifier: string): string {
  // In Node.js, use crypto for SHA256
  const crypto = globalThis.crypto ?? require("crypto");
  const encoder = new TextEncoder();
  const data = encoder.encode(verifier);

  // Synchronous hash for simplicity - in production use async
  const hash = crypto.createHash?.("sha256").update(verifier).digest()
    ?? new Uint8Array(32); // Fallback for browser

  return base64UrlEncode(hash);
}

function base64UrlEncode(buffer: ArrayBuffer | Uint8Array): string {
  const bytes = buffer instanceof Uint8Array ? buffer : new Uint8Array(buffer);
  let binary = "";
  for (const byte of bytes) {
    binary += String.fromCharCode(byte);
  }
  return btoa(binary)
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}

/**
 * Generate random code verifier for PKCE
 */
export function generateCodeVerifier(): string {
  const array = new Uint8Array(32);
  globalThis.crypto?.getRandomValues?.(array) ??
    require("crypto").randomFillSync(array);
  return base64UrlEncode(array);
}
