/**
 * Telnyx voice provider adapter — STUB (not yet implemented).
 *
 * ─── Why Telnyx? ───────────────────────────────────────────────────────────
 * Telnyx is ~40–60% cheaper than Twilio for PSTN calling, with a very similar
 * API surface. Their markup language is TeXML, which is nearly identical to
 * TwiML — most XML responses can be reused with minor edits.
 *
 * ─── How to implement this provider ────────────────────────────────────────
 * 1. Create a Telnyx account: https://portal.telnyx.com/
 * 2. Buy a phone number and create a SIP Connection / TeXML Application.
 * 3. Install the Telnyx SDK:
 *      npm install telnyx
 * 4. Replace every stub below with a real implementation (see inline TODOs).
 * 5. Set VOICE_PROVIDER=telnyx in your .env and add TELNYX_API_KEY +
 *    TELNYX_SIP_CONNECTION_ID.
 *
 * ─── References ─────────────────────────────────────────────────────────────
 * - Telnyx Node SDK:  https://github.com/team-telnyx/telnyx-node
 * - TeXML reference:  https://developers.telnyx.com/docs/voice/programmable-voice/texml-translator
 * - Webhook security: https://developers.telnyx.com/docs/api/v2/overview#webhook-security
 * - Call Control API: https://developers.telnyx.com/docs/api/v2/call-control/Call
 */

import type { IVoiceProvider, OutboundCallParams, SipBridgeParams, CallResult } from './types.js';

// ─── Config ─────────────────────────────────────────────────────────────────

export interface TelnyxProviderConfig {
  /** Telnyx API v2 key from the portal (TELNYX_API_KEY env var) */
  apiKey: string;
  /**
   * Telnyx SIP Connection ID or TeXML Application ID used for outbound calls.
   * Found in the Telnyx portal under Voice → SIP Connections.
   * (TELNYX_SIP_CONNECTION_ID env var)
   */
  sipConnectionId: string;
  /**
   * OpenAI Project ID used to construct the SIP URI.
   * Same value as OPENAI_PROJECT_ID used by the Twilio adapter.
   */
  openAiProjectId: string;
}

// ─── Provider stub ───────────────────────────────────────────────────────────

export class TelnyxProvider implements IVoiceProvider {
  // TeXML responses use the same content type as TwiML.
  readonly responseContentType = 'text/xml';

  /**
   * Telnyx uses Ed25519-signed webhook payloads.
   * Header: 'telnyx-signature-ed25519' (base64 encoded)
   * Companion header: 'telnyx-timestamp' (Unix epoch seconds)
   *
   * See: https://developers.telnyx.com/docs/api/v2/overview#webhook-security
   */
  readonly webhookSignatureHeader = 'telnyx-signature-ed25519';

  constructor(_config: TelnyxProviderConfig) {
    // TODO: Initialize the Telnyx SDK client here once you install it.
    //
    //   import Telnyx from 'telnyx';
    //   this.telnyx = new Telnyx(_config.apiKey);
    //   this.sipConnectionId = _config.sipConnectionId;
    //   this.openAiProjectId = _config.openAiProjectId;
  }

  // ── Webhook validation ───────────────────────────────────────────────────

  /**
   * Validates an inbound Telnyx webhook using Ed25519 signature verification.
   *
   * Telnyx sends two headers:
   *   telnyx-signature-ed25519 — base64-encoded Ed25519 signature
   *   telnyx-timestamp         — Unix epoch timestamp (must not be too old)
   *
   * TODO: Implement using the Telnyx SDK's helper or verify manually:
   *
   *   import { verifyWebhookSignature } from 'telnyx';
   *   return verifyWebhookSignature(rawBody, signature, timestamp, publicKey);
   *
   * Note: `secret` here should be the public key from the Telnyx portal
   * (Telnyx uses asymmetric signing, not HMAC like Twilio).
   */
  validateRequest(
    _secret: string,
    _signature: string,
    _url: string,
    _params: Record<string, string>
  ): boolean {
    // Stub: always reject — prevents any webhook from being accepted until
    // this provider is fully implemented. Returns false rather than throwing
    // to avoid unhandled exceptions in the request pipeline.
    return false;
  }

  // ── SIP bridge response ──────────────────────────────────────────────────

  /**
   * Builds a TeXML response that bridges the call to OpenAI Realtime SIP.
   *
   * TeXML is nearly identical to TwiML. A minimal bridging response looks like:
   *
   *   <?xml version="1.0" encoding="UTF-8"?>
   *   <Response>
   *     <Dial answerOnBridge="true">
   *       <Sip>sip:PROJ_ID@sip.api.openai.com;transport=tls;x_bridge_id=...</Sip>
   *     </Dial>
   *   </Response>
   *
   * The SIP URI format and correlation parameters are the same as Twilio.
   * However, Telnyx routes outbound SIP through its own carrier infrastructure —
   * verify that direct sip.api.openai.com routing is supported by your trunk.
   *
   * TODO: Build the TeXML string. You can reuse the same XML template as Twilio
   * or use a TeXML builder library.
   */
  buildSipBridgeResponse(_params?: SipBridgeParams): string {
    throw new Error('Telnyx provider not yet implemented: buildSipBridgeResponse');
  }

  // ── Outbound call ────────────────────────────────────────────────────────

  /**
   * Initiates an outbound call via Telnyx's Call Control API.
   *
   * Telnyx returns a `call_control_id` (analogous to Twilio's CallSid).
   *
   * TODO: Implement with the Telnyx SDK or a direct REST call:
   *
   *   const response = await fetch('https://api.telnyx.com/v2/calls', {
   *     method: 'POST',
   *     headers: {
   *       Authorization: `Bearer ${this.apiKey}`,
   *       'Content-Type': 'application/json',
   *     },
   *     body: JSON.stringify({
   *       connection_id: this.sipConnectionId,
   *       to: params.to,
   *       from: params.from,
   *       webhook_url: params.webhookUrl,
   *       webhook_url_method: params.webhookMethod ?? 'POST',
   *     }),
   *   });
   *   const data = await response.json();
   *   return { sid: data.data.call_control_id, status: data.data.state };
   */
  async createOutboundCall(_params: OutboundCallParams): Promise<CallResult> {
    throw new Error('Telnyx provider not yet implemented: createOutboundCall');
  }
}

export default TelnyxProvider;
