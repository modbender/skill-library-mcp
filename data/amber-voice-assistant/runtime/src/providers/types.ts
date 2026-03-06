/**
 * Voice provider adapter interface.
 *
 * All telephony providers (Twilio, Telnyx, etc.) must implement this interface
 * so index.ts can remain provider-agnostic.
 *
 * The goal is a thin adapter layer — each method maps 1:1 to what index.ts already does,
 * so the refactor is mechanical and doesn't change call behaviour.
 */

import type { Request } from 'express';

// ─── Result / param types ───────────────────────────────────────────────────

export interface CallResult {
  /** Provider-assigned call identifier (e.g. Twilio CallSid, Telnyx call_control_id) */
  sid: string;
  /** Initial status string returned by the provider (e.g. 'queued', 'initiated') */
  status: string;
}

export interface OutboundCallParams {
  /** E.164 destination phone number, e.g. '+14165551234' */
  to: string;
  /** E.164 caller-ID / from number */
  from: string;
  /**
   * URL the provider POSTs to when the callee answers.
   * Should return TwiML / TeXML that bridges the call.
   */
  webhookUrl: string;
  /** URL for call status-event callbacks */
  statusCallbackUrl?: string;
  /** HTTP method for the status callback (default: 'POST') */
  statusCallbackMethod?: string;
  /** Which call-lifecycle events to subscribe to (e.g. ['initiated','answered','completed']) */
  statusCallbackEvents?: string[];
  /** HTTP method for the webhook URL (default: 'POST') */
  webhookMethod?: string;
}

export interface SipBridgeParams {
  /** Provider's call ID to embed in SIP URI parameters for correlation */
  callSid?: string;
  /** Internal bridge-correlation ID (our own, set when initiating outbound calls) */
  bridgeId?: string;
  /**
   * Short objective string. NOTE: keep this empty / omit for now — long SIP URIs
   * can break the SIP INVITE. The full objective is resolved via bridgeId.
   */
  objective?: string;
}

// ─── Core interface ─────────────────────────────────────────────────────────

/**
 * Every voice provider adapter must implement this interface.
 *
 * Methods are kept minimal: they cover exactly what index.ts needs from Twilio today.
 * Adding more provider-specific functionality (e.g. conference, recording) should be
 * done by extending this interface rather than importing the provider SDK directly.
 */
export interface IVoiceProvider {
  /**
   * MIME type returned in provider webhook responses (e.g. 'text/xml').
   * index.ts passes this to `res.type(...)`.
   */
  responseContentType: string;

  /**
   * The HTTP header that carries the provider's webhook signature.
   * Used by the validation middleware in index.ts to locate the signature.
   *
   * Examples:
   * - Twilio:  'x-twilio-signature'
   * - Telnyx:  'telnyx-signature-ed25519'
   */
  webhookSignatureHeader: string;

  /**
   * Validate an inbound webhook request's signature.
   *
   * Called by the webhook validation middleware before processing any
   * provider webhook (inbound call, status callback, etc.).
   *
   * @param secret    Auth secret for this provider (e.g. Twilio auth token,
   *                  Telnyx webhook signing key).
   * @param signature Value of the provider's signature header.
   * @param url       Full URL the provider posted to (reconstructed from the request).
   * @param params    Parsed URL-encoded body fields (key → value map).
   * @returns         true if the signature is cryptographically valid.
   */
  validateRequest(
    secret: string,
    signature: string,
    url: string,
    params: Record<string, string>
  ): boolean;

  /**
   * Build a response body (TwiML / TeXML / JSON) that instructs the provider
   * to bridge this call leg to an OpenAI Realtime SIP endpoint.
   *
   * Returns a string to send as the HTTP response body to the provider webhook.
   */
  buildSipBridgeResponse(params?: SipBridgeParams): string;

  /**
   * Initiate an outbound phone call via the provider's REST API.
   *
   * @returns A promise that resolves to the call's provider-assigned ID and
   *          initial status once the API request succeeds.
   */
  createOutboundCall(params: OutboundCallParams): Promise<CallResult>;
}

/**
 * Loose config bag passed to `createProvider()`.
 * Each concrete provider casts this to its own typed config interface.
 */
export type ProviderConfig = Record<string, unknown>;
