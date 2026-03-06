import type {
  HangupCallInput,
  InitiateCallInput,
  InitiateCallResult,
  ProviderName,
  ProviderWebhookParseResult,
  WebhookContext,
  WebhookVerificationResult,
} from "../types.js";

/**
 * Abstract base interface for voice call providers.
 *
 * Each provider (Twilio, mock) implements this interface to provide
 * a consistent API for the call manager.
 *
 * Responsibilities:
 * - Webhook verification and event parsing
 * - Outbound call initiation and hangup
 * - Media control (TTS playback, STT listening)
 */
export interface VoiceCallProvider {
  /** Provider identifier */
  readonly name: ProviderName;

  /**
   * Verify webhook signature/HMAC before processing.
   * Must be called before parseWebhookEvent.
   */
  verifyWebhook(ctx: WebhookContext): WebhookVerificationResult;

  /**
   * Parse provider-specific webhook payload into normalized events.
   * Returns events and optional response to send back to provider.
   */
  parseWebhookEvent(ctx: WebhookContext): ProviderWebhookParseResult;

  /**
   * Initiate an outbound call.
   * @returns Provider call ID and status
   */
  initiateCall(input: InitiateCallInput): Promise<InitiateCallResult>;

  /**
   * Hang up an active call.
   */
  hangupCall(input: HangupCallInput): Promise<void>;

  // Full realtime handles speech directly via media streams.
}
