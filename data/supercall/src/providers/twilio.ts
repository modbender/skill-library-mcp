import crypto from "node:crypto";

import type { TwilioConfig } from "../config.js";
import type {
  HangupCallInput,
  InitiateCallInput,
  InitiateCallResult,
  NormalizedEvent,
  ProviderWebhookParseResult,
  WebhookContext,
  WebhookVerificationResult,
} from "../types.js";
import { escapeXml } from "../voice-mapping.js";
import type { VoiceCallProvider } from "./base.js";
import { twilioApiRequest } from "./twilio/api.js";
import { verifyTwilioProviderWebhook } from "./twilio/webhook.js";

/**
 * Twilio Voice API provider implementation.
 *
 * Uses Twilio Programmable Voice API with Media Streams for real-time
 * bidirectional audio streaming.
 *
 * @see https://www.twilio.com/docs/voice
 * @see https://www.twilio.com/docs/voice/media-streams
 */
export interface TwilioProviderOptions {
  /** Override public URL for signature verification */
  publicUrl?: string;
  /** Path for media stream WebSocket (e.g., /voice/stream) */
  streamPath?: string;
}

export class TwilioProvider implements VoiceCallProvider {
  readonly name = "twilio" as const;

  private readonly accountSid: string;
  private readonly authToken: string;
  private readonly baseUrl: string;
  private readonly callWebhookUrls = new Map<string, string>();
  private readonly options: TwilioProviderOptions;

  /** Current public webhook URL (set when tunnel starts or from config) */
  private currentPublicUrl: string | null = null;

  constructor(config: TwilioConfig, options: TwilioProviderOptions = {}) {
    if (!config.accountSid) {
      throw new Error("Twilio Account SID is required");
    }
    if (!config.authToken) {
      throw new Error("Twilio Auth Token is required");
    }

    this.accountSid = config.accountSid;
    this.authToken = config.authToken;
    this.baseUrl = `https://api.twilio.com/2010-04-01/Accounts/${this.accountSid}`;
    this.options = options;

    if (options.publicUrl) {
      this.currentPublicUrl = options.publicUrl;
    }
  }

  setPublicUrl(url: string): void {
    this.currentPublicUrl = url;
  }

  /**
   * Make an authenticated request to the Twilio API.
   */
  private async apiRequest<T = unknown>(
    endpoint: string,
    params: Record<string, string | string[]>,
    options?: { allowNotFound?: boolean },
  ): Promise<T> {
    return await twilioApiRequest<T>({
      baseUrl: this.baseUrl,
      accountSid: this.accountSid,
      authToken: this.authToken,
      endpoint,
      body: params,
      allowNotFound: options?.allowNotFound,
    });
  }

  /**
   * Verify Twilio webhook signature using HMAC-SHA1.
   *
   * Handles reverse proxy scenarios (Tailscale, nginx, ngrok) by reconstructing
   * the public URL from forwarding headers.
   *
   * @see https://www.twilio.com/docs/usage/webhooks/webhooks-security
   */
  verifyWebhook(ctx: WebhookContext): WebhookVerificationResult {
    return verifyTwilioProviderWebhook({
      ctx,
      authToken: this.authToken,
      currentPublicUrl: this.currentPublicUrl,
      options: this.options,
    });
  }

  /**
   * Parse Twilio webhook event into normalized format.
   */
  parseWebhookEvent(ctx: WebhookContext): ProviderWebhookParseResult {
    try {
      const params = new URLSearchParams(ctx.rawBody);
      const callIdFromQuery =
        typeof ctx.query?.callId === "string" && ctx.query.callId.trim()
          ? ctx.query.callId.trim()
          : undefined;
      const event = this.normalizeEvent(params, callIdFromQuery);

      // For Twilio, we must return TwiML. Most actions are driven by Calls API updates,
      // so the webhook response is typically a pause to keep the call alive.
      const twiml = this.generateTwimlResponse(ctx);

      return {
        events: event ? [event] : [],
        providerResponseBody: twiml,
        providerResponseHeaders: { "Content-Type": "application/xml" },
        statusCode: 200,
      };
    } catch {
      return { events: [], statusCode: 400 };
    }
  }

  /**
   * Parse Twilio direction to normalized format.
   */
  private static parseDirection(
    direction: string | null,
  ): "inbound" | "outbound" | undefined {
    if (direction === "inbound") return "inbound";
    if (direction === "outbound-api" || direction === "outbound-dial")
      return "outbound";
    return undefined;
  }

  /**
   * Convert Twilio webhook params to normalized event format.
   */
  private normalizeEvent(
    params: URLSearchParams,
    callIdOverride?: string,
  ): NormalizedEvent | null {
    const callSid = params.get("CallSid") || "";

    const baseEvent = {
      id: crypto.randomUUID(),
      callId: callIdOverride || callSid,
      providerCallId: callSid,
      timestamp: Date.now(),
      direction: TwilioProvider.parseDirection(params.get("Direction")),
      from: params.get("From") || undefined,
      to: params.get("To") || undefined,
    };

    // Handle speech result (from <Gather>)
    const speechResult = params.get("SpeechResult");
    if (speechResult) {
      return {
        ...baseEvent,
        type: "call.speech",
        transcript: speechResult,
        isFinal: true,
        confidence: parseFloat(params.get("Confidence") || "0.9"),
      };
    }

    // Handle DTMF
    const digits = params.get("Digits");
    if (digits) {
      return { ...baseEvent, type: "call.dtmf", digits };
    }

    // Handle call status changes
    const callStatus = params.get("CallStatus");
    switch (callStatus) {
      case "initiated":
        return { ...baseEvent, type: "call.initiated" };
      case "ringing":
        return { ...baseEvent, type: "call.ringing" };
      case "in-progress":
        return { ...baseEvent, type: "call.answered" };
      case "completed":
      case "busy":
      case "no-answer":
      case "failed":
        return { ...baseEvent, type: "call.ended", reason: callStatus };
      case "canceled":
        return { ...baseEvent, type: "call.ended", reason: "hangup-bot" };
      default:
        return null;
    }
  }

  private static readonly EMPTY_TWIML =
    '<?xml version="1.0" encoding="UTF-8"?><Response></Response>';

  private static readonly PAUSE_TWIML = `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Pause length="30"/>
</Response>`;

  /**
   * Generate TwiML response for webhook.
   * When a call is answered, connects to media stream for bidirectional audio.
   */
  private generateTwimlResponse(ctx?: WebhookContext): string {
    if (!ctx) return TwilioProvider.EMPTY_TWIML;

    const params = new URLSearchParams(ctx.rawBody);
    const type =
      typeof ctx.query?.type === "string" ? ctx.query.type.trim() : undefined;
    const isStatusCallback = type === "status";
    const callStatus = params.get("CallStatus");
    const direction = params.get("Direction");
    const isOutbound = direction?.startsWith("outbound") ?? false;
    // Handle initial TwiML request (when Twilio first initiates the call)
    // Return streaming TwiML immediately for outbound calls.
    if (!isStatusCallback && isOutbound) {
      const streamUrl = this.getStreamUrl();
      return streamUrl
        ? this.getStreamConnectXml(streamUrl)
        : TwilioProvider.PAUSE_TWIML;
    }

    // Status callbacks should not receive TwiML.
    if (isStatusCallback) {
      return TwilioProvider.EMPTY_TWIML;
    }

    // Handle subsequent webhook requests (status callbacks, etc.)
    // For inbound calls, answer immediately with stream
    if (direction === "inbound") {
      const streamUrl = this.getStreamUrl();
      return streamUrl
        ? this.getStreamConnectXml(streamUrl)
        : TwilioProvider.PAUSE_TWIML;
    }

    // For outbound calls, only connect to stream when call is in-progress
    if (callStatus !== "in-progress") {
      return TwilioProvider.EMPTY_TWIML;
    }

    const streamUrl = this.getStreamUrl();
    return streamUrl
      ? this.getStreamConnectXml(streamUrl)
      : TwilioProvider.PAUSE_TWIML;
  }

  /**
   * Get the WebSocket URL for media streaming.
   * Derives from the public URL origin + stream path.
   */
  private getStreamUrl(): string | null {
    if (!this.currentPublicUrl || !this.options.streamPath) {
      return null;
    }

    // Extract just the origin (host) from the public URL, ignoring any path
    const url = new URL(this.currentPublicUrl);
    const origin = url.origin;

    // Convert https:// to wss:// for WebSocket
    const wsOrigin = origin
      .replace(/^https:\/\//, "wss://")
      .replace(/^http:\/\//, "ws://");

    // Append the stream path
    const path = this.options.streamPath.startsWith("/")
      ? this.options.streamPath
      : `/${this.options.streamPath}`;

    return `${wsOrigin}${path}`;
  }

  /**
   * Generate TwiML to connect a call to a WebSocket media stream.
   * This enables bidirectional audio streaming for real-time STT/TTS.
   *
   * @param streamUrl - WebSocket URL (wss://...) for the media stream
   */
  getStreamConnectXml(streamUrl: string): string {
    return `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Connect>
    <Stream url="${escapeXml(streamUrl)}" />
  </Connect>
</Response>`;
  }

  /**
   * Initiate an outbound call via Twilio API.
   * Uses webhook URL for dynamic TwiML.
   */
  async initiateCall(input: InitiateCallInput): Promise<InitiateCallResult> {
    const url = new URL(input.webhookUrl);
    url.searchParams.set("callId", input.callId);

    // Create separate URL for status callbacks (required by Twilio)
    const statusUrl = new URL(input.webhookUrl);
    statusUrl.searchParams.set("callId", input.callId);
    statusUrl.searchParams.set("type", "status"); // Differentiate from TwiML requests

    // Build request params - always use URL-based TwiML.
    // Twilio silently ignores `StatusCallback` when using the inline `Twiml` parameter.
    const params: Record<string, string | string[]> = {
      To: input.to,
      From: input.from,
      Url: url.toString(), // TwiML serving endpoint
      StatusCallback: statusUrl.toString(), // Separate status callback endpoint
      StatusCallbackEvent: ["initiated", "ringing", "answered", "completed"],
      Record: "true",
      RecordingChannels: "dual",
      Timeout: "30",
    };

    const result = await this.apiRequest<TwilioCallResponse>(
      "/Calls.json",
      params,
    );

    this.callWebhookUrls.set(result.sid, url.toString());

    return {
      providerCallId: result.sid,
      status: result.status === "queued" ? "queued" : "initiated",
    };
  }

  /**
   * Hang up a call via Twilio API.
   */
  async hangupCall(input: HangupCallInput): Promise<void> {
    this.callWebhookUrls.delete(input.providerCallId);

    await this.apiRequest(
      `/Calls/${input.providerCallId}.json`,
      { Status: "completed" },
      { allowNotFound: true },
    );
  }

  // Full realtime does not use TwiML TTS or <Gather> actions.
}

// -----------------------------------------------------------------------------
// Twilio-specific types
// -----------------------------------------------------------------------------

interface TwilioCallResponse {
  sid: string;
  status: string;
  direction: string;
  from: string;
  to: string;
  uri: string;
}
