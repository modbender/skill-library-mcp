import twilio from "twilio";
import type { PluginConfig } from "./config.ts";

export interface InitiateCallOptions {
  to: string;
  callId: string;
  publicUrl: string;
  timeoutSeconds: number;
  enableAmd: boolean;
  maxDurationSeconds: number;
}

export interface TwilioCallResult {
  callSid: string;
  status: string;
}

export interface TwilioCallDetails {
  sid: string;
  status: string;
  direction?: string;
  from?: string;
  to?: string;
  startTime?: string | null;
  endTime?: string | null;
  dateCreated?: string | null;
  dateUpdated?: string | null;
  duration?: string | null;
  answeredBy?: string | null;
  price?: string | null;
  priceUnit?: string | null;
}

export interface TwilioCallEvent {
  requestMethod?: string;
  requestUrl?: string;
  callStatus?: string | null;
  answeredBy?: string | null;
  timestamp?: string | null;
  sequenceNumber?: string | null;
  responseCode?: number | null;
  requestDurationMs?: number | null;
}

export class TwilioClient {
  private client: twilio.Twilio;
  private config: PluginConfig;

  constructor(config: PluginConfig) {
    this.config = config;
    this.client = twilio(config.twilio.accountSid, config.twilio.authToken);
  }

  async initiateCall(opts: InitiateCallOptions): Promise<TwilioCallResult> {
    const twimlUrl = `${opts.publicUrl}/voice/answer?callId=${encodeURIComponent(opts.callId)}`;
    const statusUrl = `${opts.publicUrl}/voice/status?callId=${encodeURIComponent(opts.callId)}`;

    const callParams: Record<string, unknown> = {
      to: opts.to,
      from: this.config.fromNumber,
      url: twimlUrl,
      statusCallback: statusUrl,
      statusCallbackEvent: ["initiated", "ringing", "answered", "completed"],
      statusCallbackMethod: "POST",
      timeout: opts.timeoutSeconds,
      timeLimit: opts.maxDurationSeconds,
    };

    if (opts.enableAmd) {
      // Use synchronous AMD so /voice/answer receives AnsweredBy before we bridge audio.
      callParams.machineDetection = "Enable";
      callParams.machineDetectionTimeout = 8;
    }

    const call = await this.client.calls.create(callParams as unknown as Parameters<typeof this.client.calls.create>[0]);

    return {
      callSid: call.sid,
      status: call.status,
    };
  }

  async hangup(callSid: string): Promise<void> {
    await this.client.calls(callSid).update({ status: "completed" });
  }

  async getCallDetails(callSid: string): Promise<TwilioCallDetails> {
    const call = await this.client.calls(callSid).fetch();
    const raw = call as unknown as Record<string, unknown>;

    return {
      sid: call.sid,
      status: call.status,
      direction: call.direction,
      from: call.from || undefined,
      to: call.to || undefined,
      startTime: call.startTime?.toISOString() ?? null,
      endTime: call.endTime?.toISOString() ?? null,
      dateCreated: call.dateCreated?.toISOString() ?? null,
      dateUpdated: call.dateUpdated?.toISOString() ?? null,
      duration: call.duration,
      answeredBy: (raw.answeredBy as string | undefined) ?? null,
      price: call.price ?? null,
      priceUnit: call.priceUnit ?? null,
    };
  }

  async getCallEvents(callSid: string, limit = 30): Promise<TwilioCallEvent[]> {
    const events = await this.client.calls(callSid).events.list({ limit });

    return events.map((event) => {
      const params = (event.request?.parameters || {}) as Record<string, string | undefined>;

      return {
        requestMethod: event.request?.method,
        requestUrl: event.request?.url,
        callStatus: params.call_status ?? null,
        answeredBy: params.answered_by ?? null,
        timestamp: params.timestamp ?? null,
        sequenceNumber: params.sequence_number ?? null,
        responseCode: event.response?.response_code ?? null,
        requestDurationMs: event.response?.request_duration ?? null,
      };
    });
  }

  async verifyAccount(): Promise<{
    ok: boolean;
    accountSid: string;
    friendlyName?: string;
    error?: string;
  }> {
    try {
      const account = await this.client.api.accounts(this.config.twilio.accountSid).fetch();
      return {
        ok: true,
        accountSid: this.maskSid(account.sid),
        friendlyName: account.friendlyName,
      };
    } catch (err) {
      return {
        ok: false,
        accountSid: this.maskSid(this.config.twilio.accountSid),
        error: err instanceof Error ? err.message : String(err),
      };
    }
  }

  async verifyPhoneNumber(): Promise<{
    ok: boolean;
    number: string;
    capabilities?: { voice: boolean; sms: boolean };
    error?: string;
  }> {
    try {
      const numbers = await this.client.incomingPhoneNumbers.list({
        phoneNumber: this.config.fromNumber,
        limit: 1,
      });

      if (numbers.length === 0) {
        return {
          ok: false,
          number: this.config.fromNumber,
          error: "Phone number not found in your Twilio account",
        };
      }

      const num = numbers[0];
      return {
        ok: true,
        number: this.config.fromNumber,
        capabilities: {
          voice: num.capabilities?.voice ?? false,
          sms: num.capabilities?.sms ?? false,
        },
      };
    } catch (err) {
      return {
        ok: false,
        number: this.config.fromNumber,
        error: err instanceof Error ? err.message : String(err),
      };
    }
  }

  private maskSid(sid: string): string {
    if (sid.length <= 6) return sid;
    return sid.slice(0, 4) + "..." + sid.slice(-4);
  }
}
