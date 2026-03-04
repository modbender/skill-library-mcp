/**
 * Twilio voice provider adapter.
 *
 * This is the default (and currently only production-ready) provider.
 * Wraps the Twilio Node.js SDK for webhook validation, TwiML generation,
 * and outbound call initiation.
 *
 * All Twilio-specific SDK calls that were previously inline in index.ts
 * live here. index.ts stays provider-agnostic and talks to IVoiceProvider.
 */

import twilio from 'twilio';
import type { IVoiceProvider, OutboundCallParams, SipBridgeParams, CallResult } from './types.js';

// ─── Config ─────────────────────────────────────────────────────────────────

export interface TwilioProviderConfig {
  /** Twilio Account SID (TWILIO_ACCOUNT_SID env var) */
  accountSid: string;
  /** Twilio Auth Token (TWILIO_AUTH_TOKEN env var) */
  authToken: string;
  /**
   * OpenAI Project ID used to construct the SIP URI.
   * Format: sip:<projectId>@sip.api.openai.com
   */
  openAiProjectId: string;
}

// ─── Provider implementation ─────────────────────────────────────────────────

export class TwilioProvider implements IVoiceProvider {
  readonly responseContentType = 'text/xml';
  readonly webhookSignatureHeader = 'x-twilio-signature';

  private readonly authToken: string;
  private readonly openAiProjectId: string;
  private readonly client: ReturnType<typeof twilio>;

  constructor(config: TwilioProviderConfig) {
    if (!config.accountSid) throw new Error('TwilioProvider: missing accountSid');
    if (!config.authToken) throw new Error('TwilioProvider: missing authToken');
    if (!config.openAiProjectId) throw new Error('TwilioProvider: missing openAiProjectId');

    this.authToken = config.authToken;
    this.openAiProjectId = config.openAiProjectId;
    this.client = twilio(config.accountSid, config.authToken);
  }

  // ── Webhook validation ───────────────────────────────────────────────────

  /**
   * Validates the X-Twilio-Signature header using Twilio's HMAC-SHA1 scheme.
   *
   * Twilio docs: https://www.twilio.com/docs/usage/webhooks/webhooks-security
   */
  validateRequest(
    secret: string,
    signature: string,
    url: string,
    params: Record<string, string>
  ): boolean {
    return twilio.validateRequest(secret, signature, url, params);
  }

  // ── SIP bridge response ──────────────────────────────────────────────────

  /**
   * Generates TwiML that dials the OpenAI Realtime SIP endpoint.
   *
   * Correlation fields (callSid, bridgeId) are embedded as SIP URI parameters
   * rather than query-string parameters because query params are not reliably
   * surfaced as SIP headers by Twilio.
   *
   * NOTE: Do NOT embed the full objective in the SIP URI — long URIs break the
   * INVITE. The objective is resolved from the in-memory map via bridgeId in
   * the OpenAI webhook handler.
   */
  buildSipBridgeResponse(params?: SipBridgeParams): string {
    const twiml = new twilio.twiml.VoiceResponse();
    const dial = twiml.dial({ answerOnBridge: true });

    const uriParams: string[] = ['transport=tls'];
    if (params?.callSid) {
      uriParams.push(`x_twilio_callsid=${encodeURIComponent(params.callSid)}`);
    }
    if (params?.bridgeId) {
      uriParams.push(`x_bridge_id=${encodeURIComponent(params.bridgeId)}`);
    }

    const uri = `sip:${this.openAiProjectId}@sip.api.openai.com;${uriParams.join(';')}`;
    dial.sip(uri);
    return twiml.toString();
  }

  // ── Outbound call ────────────────────────────────────────────────────────

  /**
   * Creates an outbound PSTN call via Twilio's Calls API.
   * When the callee answers, Twilio POSTs to `webhookUrl` to fetch TwiML.
   */
  async createOutboundCall(params: OutboundCallParams): Promise<CallResult> {
    const call = await this.client.calls.create({
      to: params.to,
      from: params.from,
      url: params.webhookUrl,
      method: ((params.webhookMethod ?? 'POST') as 'GET' | 'POST'),
      statusCallback: params.statusCallbackUrl,
      statusCallbackMethod: ((params.statusCallbackMethod ?? 'POST') as 'GET' | 'POST'),
      statusCallbackEvent: params.statusCallbackEvents,
    });

    return { sid: call.sid, status: call.status };
  }
}

export default TwilioProvider;
