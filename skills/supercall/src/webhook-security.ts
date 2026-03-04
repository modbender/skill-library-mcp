import crypto from "node:crypto";

import type { WebhookContext } from "./types.js";

/**
 * Validate Twilio webhook signature using HMAC-SHA1.
 *
 * Twilio signs requests by concatenating the URL with sorted POST params,
 * then computing HMAC-SHA1 with the auth token.
 *
 * @see https://www.twilio.com/docs/usage/webhooks/webhooks-security
 */
export function validateTwilioSignature(
  authToken: string,
  signature: string | undefined,
  url: string,
  params: URLSearchParams,
): boolean {
  if (!signature) {
    return false;
  }

  // Build the string to sign: URL + sorted params (key+value pairs)
  let dataToSign = url;

  // Sort params alphabetically and append key+value
  const sortedParams = Array.from(params.entries()).toSorted((a, b) =>
    a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0,
  );

  for (const [key, value] of sortedParams) {
    dataToSign += key + value;
  }

  // HMAC-SHA1 with auth token, then base64 encode
  const expectedSignature = crypto
    .createHmac("sha1", authToken)
    .update(dataToSign)
    .digest("base64");

  // Use timing-safe comparison to prevent timing attacks
  return timingSafeEqual(signature, expectedSignature);
}

/**
 * Timing-safe string comparison to prevent timing attacks.
 */
function timingSafeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) {
    // Still do comparison to maintain constant time
    const dummy = Buffer.from(a);
    crypto.timingSafeEqual(dummy, dummy);
    return false;
  }

  const bufA = Buffer.from(a);
  const bufB = Buffer.from(b);
  return crypto.timingSafeEqual(bufA, bufB);
}

/**
 * Reconstruct the public webhook URL from request headers.
 *
 * When behind a reverse proxy (Tailscale, nginx, ngrok), the original URL
 * used by Twilio differs from the local request URL. We use standard
 * forwarding headers to reconstruct it.
 *
 * Priority order:
 * 1. X-Forwarded-Proto + X-Forwarded-Host (standard proxy headers)
 * 2. X-Original-Host (nginx)
 * 3. Ngrok-Forwarded-Host (ngrok specific)
 * 4. Host header (direct connection)
 */
export function reconstructWebhookUrl(ctx: WebhookContext): string {
  const { headers } = ctx;

  const proto = getHeader(headers, "x-forwarded-proto") || "https";

  const forwardedHost =
    getHeader(headers, "x-forwarded-host") ||
    getHeader(headers, "x-original-host") ||
    getHeader(headers, "ngrok-forwarded-host") ||
    getHeader(headers, "host") ||
    "";

  // Extract path from the context URL (fallback to "/" on parse failure)
  let path = "/";
  try {
    const parsed = new URL(ctx.url);
    path = parsed.pathname + parsed.search;
  } catch {
    // URL parsing failed
  }

  // Remove port from host (ngrok URLs don't have ports)
  const host = forwardedHost.split(":")[0] || forwardedHost;

  return `${proto}://${host}${path}`;
}

function buildTwilioVerificationUrl(
  ctx: WebhookContext,
  publicUrl?: string,
): string {
  if (!publicUrl) {
    return reconstructWebhookUrl(ctx);
  }

  try {
    const base = new URL(publicUrl);
    const requestUrl = new URL(ctx.url);
    base.pathname = requestUrl.pathname;
    base.search = requestUrl.search;
    return base.toString();
  } catch {
    return publicUrl;
  }
}

/**
 * Get a header value, handling both string and string[] types.
 */
function getHeader(
  headers: Record<string, string | string[] | undefined>,
  name: string,
): string | undefined {
  const value = headers[name.toLowerCase()];
  if (Array.isArray(value)) {
    return value[0];
  }
  return value;
}

/**
 * Result of Twilio webhook verification with detailed info.
 */
export interface TwilioVerificationResult {
  ok: boolean;
  reason?: string;
  /** The URL that was used for verification (for debugging) */
  verificationUrl?: string;
  /** Whether we're running behind ngrok free tier */
  isNgrokFreeTier?: boolean;
}

/**
 * Verify Twilio webhook with full context and detailed result.
 *
 * Signature verification is always enforced. When verification fails on
 * ngrok free-tier domains, the result includes isNgrokFreeTier for
 * diagnostic purposes, but the request is still rejected.
 */
export function verifyTwilioWebhook(
  ctx: WebhookContext,
  authToken: string,
  options?: {
    /** Override the public URL (e.g., from config) */
    publicUrl?: string;
  },
): TwilioVerificationResult {
  const signature = getHeader(ctx.headers, "x-twilio-signature");

  if (!signature) {
    return { ok: false, reason: "Missing X-Twilio-Signature header" };
  }

  // Reconstruct the URL Twilio used
  const verificationUrl = buildTwilioVerificationUrl(ctx, options?.publicUrl);

  // Parse the body as URL-encoded params
  const params = new URLSearchParams(ctx.rawBody);

  // Validate signature — always required, no bypass
  const isValid = validateTwilioSignature(authToken, signature, verificationUrl, params);

  if (isValid) {
    return { ok: true, verificationUrl };
  }

  // Check if this is ngrok free tier for diagnostic info
  const isNgrokFreeTier =
    verificationUrl.includes(".ngrok-free.app") || verificationUrl.includes(".ngrok.io");

  return {
    ok: false,
    reason: `Invalid signature for URL: ${verificationUrl}`,
    verificationUrl,
    isNgrokFreeTier,
  };
}
