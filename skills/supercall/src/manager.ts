import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

import WebSocket from "ws";

import { resolveUserPath } from "./utils.js";
import type { VoiceCallConfig } from "./config.js";
import type { VoiceCallProvider } from "./providers/base.js";
import {
  type CallId,
  type CallRecord,
  type CallState,
  type NormalizedEvent,
  type OutboundCallOptions,
  TerminalStates,
  type TranscriptEntry,
} from "./types.js";

/**
 * Manages voice calls: state machine, persistence, and provider coordination.
 */
export class CallManager {
  private activeCalls = new Map<CallId, CallRecord>();
  private providerCallIdMap = new Map<string, CallId>(); // providerCallId -> internal callId
  private processedEventIds = new Set<string>();
  private provider: VoiceCallProvider | null = null;
  private config: VoiceCallConfig;
  private storePath: string;
  private webhookUrl: string | null = null;
  private selfTestSecret: string | null = null;
  private lastPreflightAt: number | null = null;
  private lastPreflightOk = false;
  private transcriptWaiters = new Map<
    CallId,
    {
      resolve: (text: string) => void;
      reject: (err: Error) => void;
      timeout: NodeJS.Timeout;
    }
  >();
  /** Max duration timers to auto-hangup calls after configured timeout */
  private maxDurationTimers = new Map<CallId, NodeJS.Timeout>();
  
  /** Callback for when a call completes */
  private onCallComplete: ((call: CallRecord) => void) | null = null;

  constructor(
    config: VoiceCallConfig,
    storePath?: string,
    options?: { selfTestSecret?: string },
  ) {
    this.config = config;
    // Resolve store path with tilde expansion (like other config values)
    const rawPath =
      storePath ||
      config.store ||
      path.join(process.env.HOME || "~", "clawd", "supercall-logs");
    this.storePath = resolveUserPath(rawPath);
    this.selfTestSecret = options?.selfTestSecret ?? null;
  }

  /**
   * Initialize the call manager with a provider.
   */
  initialize(provider: VoiceCallProvider, webhookUrl: string): void {
    this.provider = provider;
    this.webhookUrl = webhookUrl;

    // Ensure store directory exists
    fs.mkdirSync(this.storePath, { recursive: true });

    // Load any persisted active calls
    this.loadActiveCalls();
  }

  /**
   * Get the current provider.
   */
  getProvider(): VoiceCallProvider | null {
    return this.provider;
  }

  /**
   * Initiate an outbound call.
   */
  async initiateCall(
    to: string,
    sessionKey?: string,
    options?: OutboundCallOptions | string,
  ): Promise<{ callId: CallId; success: boolean; error?: string }> {
    const opts: OutboundCallOptions =
      typeof options === "string" ? { message: options } : (options ?? {});
    const initialMessage = opts.message;
    
    if (!this.provider) {
      return { callId: "", success: false, error: "Provider not initialized" };
    }

    if (!this.webhookUrl) {
      return { callId: "", success: false, error: "Webhook URL not configured" };
    }

    try {
      await this.ensurePublicWebhookReachable();
    } catch (err) {
      return {
        callId: "",
        success: false,
        error: err instanceof Error ? err.message : String(err),
      };
    }

    const activeCalls = this.getActiveCalls();
    if (activeCalls.length >= this.config.maxConcurrentCalls) {
      return {
        callId: "",
        success: false,
        error: `Maximum concurrent calls (${this.config.maxConcurrentCalls}) reached`,
      };
    }

    const callId = crypto.randomUUID();
    const from =
      this.config.fromNumber ||
      (this.provider?.name === "mock" ? "+15550000000" : undefined);
    if (!from) {
      return { callId: "", success: false, error: "fromNumber not configured" };
    }

    const callRecord: CallRecord = {
      callId,
      provider: this.provider.name,
      direction: "outbound",
      state: "initiated",
      from,
      to,
      sessionKey,
      startedAt: Date.now(),
      transcript: [],
      processedEventIds: [],
      metadata: {
        ...(initialMessage && { initialMessage }),
      },
    };

    this.activeCalls.set(callId, callRecord);
    this.persistCallRecord(callRecord);

    try {
      const result = await this.provider.initiateCall({
        callId,
        from,
        to,
        webhookUrl: this.webhookUrl,
      });

      callRecord.providerCallId = result.providerCallId;
      this.providerCallIdMap.set(result.providerCallId, callId);
      this.persistCallRecord(callRecord);

      return { callId, success: true };
    } catch (err) {
      callRecord.state = "failed";
      callRecord.endedAt = Date.now();
      callRecord.endReason = "failed";
      this.persistCallRecord(callRecord);
      this.activeCalls.delete(callId);
      if (callRecord.providerCallId) {
        this.providerCallIdMap.delete(callRecord.providerCallId);
      }

      return {
        callId,
        success: false,
        error: err instanceof Error ? err.message : String(err),
      };
    }
  }

  private async ensurePublicWebhookReachable(): Promise<void> {
    if (!this.webhookUrl) {
      throw new Error("Webhook URL not configured");
    }

    let url: URL;
    try {
      url = new URL(this.webhookUrl);
    } catch {
      return;
    }

    const hostname = url.hostname;
    const isLocal =
      hostname === "localhost" ||
      hostname === "127.0.0.1" ||
      hostname === "0.0.0.0";
    if (isLocal) {
      return;
    }

    const now = Date.now();
    if (this.lastPreflightOk && this.lastPreflightAt && now - this.lastPreflightAt < 30000) {
      return;
    }

    if (!this.selfTestSecret) {
      throw new Error("Webhook self-test secret not initialized");
    }

    // Test 1: HTTP POST to webhook endpoint
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 4000);
    try {
      const response = await fetch(this.webhookUrl, {
        method: "POST",
        headers: {
          "x-supercall-self-test": this.selfTestSecret,
        },
        body: "self-test",
        signal: controller.signal,
      });
      if (!response.ok) {
        throw new Error(`Webhook self-test failed (HTTP ${response.status})`);
      }
    } finally {
      clearTimeout(timeout);
    }

    // Test 2: WebSocket endpoint (critical for media streaming)
    const streamPath = this.config.streaming?.streamPath || "/voice/stream";
    const wsProtocol = url.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${wsProtocol}//${url.host}${streamPath}`;
    
    await this.testWebSocketEndpoint(wsUrl);

    this.lastPreflightOk = true;
    this.lastPreflightAt = now;
  }

  /**
   * Test that the WebSocket endpoint is reachable.
   * Opens a connection and immediately closes it.
   */
  private testWebSocketEndpoint(wsUrl: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const timeoutMs = 4000;
      let resolved = false;

      const timer = setTimeout(() => {
        if (!resolved) {
          resolved = true;
          ws.close();
          reject(new Error(`WebSocket self-test timeout (${wsUrl})`));
        }
      }, timeoutMs);

      const ws = new WebSocket(wsUrl);

      ws.on("open", () => {
        if (!resolved) {
          resolved = true;
          clearTimeout(timer);
          ws.close();
          resolve();
        }
      });

      ws.on("error", (err) => {
        if (!resolved) {
          resolved = true;
          clearTimeout(timer);
          reject(new Error(`WebSocket self-test failed (${wsUrl}): ${err.message}`));
        }
      });

      ws.on("unexpected-response", (_req, res) => {
        if (!resolved) {
          resolved = true;
          clearTimeout(timer);
          reject(new Error(`WebSocket upgrade rejected (${wsUrl}): HTTP ${res.statusCode}`));
        }
      });
    });
  }

  /**
   * End an active call.
   */
  async endCall(callId: CallId): Promise<{ success: boolean; error?: string }> {
    const call = this.activeCalls.get(callId);
    if (!call) {
      return { success: false, error: "Call not found" };
    }

    if (!this.provider || !call.providerCallId) {
      return { success: false, error: "Call not connected" };
    }

    if (TerminalStates.has(call.state)) {
      return { success: true };
    }

    try {
      await this.provider.hangupCall({
        callId,
        providerCallId: call.providerCallId,
        reason: "hangup-bot",
      });

      call.state = "hangup-bot";
      call.endedAt = Date.now();
      call.endReason = "hangup-bot";
      this.persistCallRecord(call);
      this.clearMaxDurationTimer(callId);
      this.rejectTranscriptWaiter(callId, "Call ended: hangup-bot");
      
      // Notify callback before cleanup
      if (this.onCallComplete) {
        try {
          this.onCallComplete(call);
        } catch (err) {
          console.error("[supercall] onCallComplete error:", err);
        }
      }
      
      this.activeCalls.delete(callId);
      if (call.providerCallId) {
        this.providerCallIdMap.delete(call.providerCallId);
      }

      return { success: true };
    } catch (err) {
      return {
        success: false,
        error: err instanceof Error ? err.message : String(err),
      };
    }
  }

  /**
   * Process a webhook event.
   */
  processEvent(event: NormalizedEvent): void {
    if (this.processedEventIds.has(event.id)) {
      return;
    }
    this.processedEventIds.add(event.id);

    let call = this.findCall(event.callId);

    if (!call) {
      return;
    }

    if (event.providerCallId && event.providerCallId !== call.providerCallId) {
      const previousProviderCallId = call.providerCallId;
      call.providerCallId = event.providerCallId;
      this.providerCallIdMap.set(event.providerCallId, call.callId);
      if (previousProviderCallId) {
        const mapped = this.providerCallIdMap.get(previousProviderCallId);
        if (mapped === call.callId) {
          this.providerCallIdMap.delete(previousProviderCallId);
        }
      }
    }

    call.processedEventIds.push(event.id);

    switch (event.type) {
      case "call.initiated":
        this.transitionState(call, "initiated");
        break;

      case "call.ringing":
        this.transitionState(call, "ringing");
        break;

      case "call.answered":
        call.answeredAt = event.timestamp;
        this.transitionState(call, "answered");
        this.startMaxDurationTimer(call.callId);
        break;

      case "call.active":
        this.transitionState(call, "active");
        break;

      case "call.speaking":
        this.transitionState(call, "speaking");
        break;

      case "call.speech":
        if (event.isFinal) {
          this.addTranscriptEntryInternal(call, "user", event.transcript);
          this.resolveTranscriptWaiter(call.callId, event.transcript);
        }
        this.transitionState(call, "listening");
        break;

      case "call.ended":
        call.endedAt = event.timestamp;
        call.endReason = event.reason;
        this.transitionState(call, event.reason as CallState);
        this.clearMaxDurationTimer(call.callId);
        this.rejectTranscriptWaiter(call.callId, `Call ended: ${event.reason}`);
        this.persistCallRecord(call);
        
        // Notify callback before cleanup
        if (this.onCallComplete) {
          try {
            this.onCallComplete(call);
          } catch (err) {
            console.error("[supercall] onCallComplete error:", err);
          }
        }
        
        this.activeCalls.delete(call.callId);
        if (call.providerCallId) {
          this.providerCallIdMap.delete(call.providerCallId);
        }
        break;

      case "call.error":
        if (!event.retryable) {
          call.endedAt = event.timestamp;
          call.endReason = "error";
          this.transitionState(call, "error");
          this.clearMaxDurationTimer(call.callId);
          this.rejectTranscriptWaiter(call.callId, `Call error: ${event.error}`);
          this.activeCalls.delete(call.callId);
          if (call.providerCallId) {
            this.providerCallIdMap.delete(call.providerCallId);
          }
        }
        break;
    }

    this.persistCallRecord(call);
  }

  /**
   * Get an active call by ID.
   */
  getCall(callId: CallId): CallRecord | undefined {
    return this.activeCalls.get(callId);
  }

  /**
   * Get an active call by provider call ID.
   */
  getCallByProviderCallId(providerCallId: string): CallRecord | undefined {
    const callId = this.providerCallIdMap.get(providerCallId);
    if (callId) {
      return this.activeCalls.get(callId);
    }

    for (const call of this.activeCalls.values()) {
      if (call.providerCallId === providerCallId) {
        return call;
      }
    }
    return undefined;
  }

  /**
   * Get all active calls.
   */
  getActiveCalls(): CallRecord[] {
    return Array.from(this.activeCalls.values());
  }

  /**
   * Set callback for when a call completes.
   */
  setOnCallComplete(handler: ((call: CallRecord) => void) | null): void {
    this.onCallComplete = handler;
  }

  /**
   * Get a call from the persistent store by ID (for completed calls).
   */
  getCallFromStore(callId: CallId): CallRecord | undefined {
    const logPath = path.join(this.storePath, "calls.jsonl");
    if (!fs.existsSync(logPath)) return undefined;

    try {
      const content = fs.readFileSync(logPath, "utf-8");
      const lines = content.split("\n");
      let result: CallRecord | undefined;

      for (const line of lines) {
        if (!line.trim()) continue;
        try {
          const call = JSON.parse(line) as CallRecord;
          if (call.callId === callId) {
            result = call;
          }
        } catch {
          // Skip invalid lines
        }
      }

      return result;
    } catch {
      return undefined;
    }
  }

  /**
   * Add an entry to the call transcript (public API).
   */
  addTranscriptEntry(
    callId: string,
    speaker: "bot" | "user",
    text: string,
  ): void {
    const call = this.activeCalls.get(callId);
    if (!call) return;
    this.addTranscriptEntryInternal(call, speaker, text);
  }

  // Private methods

  private findCall(callIdOrProviderCallId: string): CallRecord | undefined {
    const directCall = this.activeCalls.get(callIdOrProviderCallId);
    if (directCall) return directCall;
    return this.getCallByProviderCallId(callIdOrProviderCallId);
  }

  private startMaxDurationTimer(callId: CallId): void {
    this.clearMaxDurationTimer(callId);

    const maxDurationMs = this.config.maxDurationSeconds * 1000;
    console.log(
      `[supercall] Starting max duration timer (${this.config.maxDurationSeconds}s) for call ${callId}`,
    );

    const timer = setTimeout(async () => {
      this.maxDurationTimers.delete(callId);
      const call = this.getCall(callId);
      if (call && !TerminalStates.has(call.state)) {
        console.log(
          `[supercall] Max duration reached (${this.config.maxDurationSeconds}s), ending call ${callId}`,
        );
        call.endReason = "timeout";
        this.persistCallRecord(call);
        await this.endCall(callId);
      }
    }, maxDurationMs);

    this.maxDurationTimers.set(callId, timer);
  }

  private clearMaxDurationTimer(callId: CallId): void {
    const timer = this.maxDurationTimers.get(callId);
    if (timer) {
      clearTimeout(timer);
      this.maxDurationTimers.delete(callId);
    }
  }

  private clearTranscriptWaiter(callId: CallId): void {
    const waiter = this.transcriptWaiters.get(callId);
    if (!waiter) return;
    clearTimeout(waiter.timeout);
    this.transcriptWaiters.delete(callId);
  }

  private rejectTranscriptWaiter(callId: CallId, reason: string): void {
    const waiter = this.transcriptWaiters.get(callId);
    if (!waiter) return;
    this.clearTranscriptWaiter(callId);
    waiter.reject(new Error(reason));
  }

  private resolveTranscriptWaiter(callId: CallId, transcript: string): void {
    const waiter = this.transcriptWaiters.get(callId);
    if (!waiter) return;
    this.clearTranscriptWaiter(callId);
    waiter.resolve(transcript);
  }

  private static readonly ConversationStates = new Set<CallState>([
    "speaking",
    "listening",
  ]);

  private static readonly StateOrder: readonly CallState[] = [
    "initiated",
    "ringing",
    "answered",
    "active",
    "speaking",
    "listening",
  ];

  private transitionState(call: CallRecord, newState: CallState): void {
    if (call.state === newState || TerminalStates.has(call.state)) return;

    if (TerminalStates.has(newState)) {
      call.state = newState;
      return;
    }

    if (
      CallManager.ConversationStates.has(call.state) &&
      CallManager.ConversationStates.has(newState)
    ) {
      call.state = newState;
      return;
    }

    const currentIndex = CallManager.StateOrder.indexOf(call.state);
    const newIndex = CallManager.StateOrder.indexOf(newState);

    if (newIndex > currentIndex) {
      call.state = newState;
    }
  }

  private addTranscriptEntryInternal(
    call: CallRecord,
    speaker: "bot" | "user",
    text: string,
  ): void {
    const entry: TranscriptEntry = {
      timestamp: Date.now(),
      speaker,
      text,
      isFinal: true,
    };
    call.transcript.push(entry);
  }

  private persistCallRecord(call: CallRecord): void {
    const logPath = path.join(this.storePath, "calls.jsonl");
    const line = `${JSON.stringify(call)}\n`;
    fs.promises.appendFile(logPath, line).catch((err) => {
      console.error("[supercall] Failed to persist call record:", err);
    });
  }

  /**
   * Maximum age (in ms) for a non-terminal call to be considered active.
   * Calls older than this are assumed stale (e.g., from a crashed process).
   */
  private static readonly STALE_CALL_THRESHOLD_MS = 5 * 60 * 1000; // 5 minutes

  private loadActiveCalls(): void {
    const logPath = path.join(this.storePath, "calls.jsonl");
    if (!fs.existsSync(logPath)) return;

    const content = fs.readFileSync(logPath, "utf-8");
    const lines = content.split("\n");

    const callMap = new Map<CallId, CallRecord>();

    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const call = JSON.parse(line) as CallRecord;
        callMap.set(call.callId, call);
      } catch {
        // Skip invalid lines
      }
    }

    const now = Date.now();
    let staleCount = 0;

    for (const [callId, call] of callMap) {
      if (TerminalStates.has(call.state)) {
        continue; // Already terminal, skip
      }

      // Check if call is stale (started too long ago without reaching terminal state)
      const callAge = now - (call.startedAt || 0);
      if (callAge > CallManager.STALE_CALL_THRESHOLD_MS) {
        staleCount++;
        const prevState = call.state;
        // Mark as stale and persist the terminal state
        call.state = "error";
        call.endedAt = now;
        this.persistCallRecord(call);
        console.log(
          `[supercall] Cleaned up stale call ${callId.slice(0, 8)}... (age: ${Math.round(callAge / 1000)}s, was: ${prevState})`,
        );
        continue;
      }

      // Call is recent and non-terminal, consider it active
      this.activeCalls.set(callId, call);
      if (call.providerCallId) {
        this.providerCallIdMap.set(call.providerCallId, callId);
      }
      for (const eventId of call.processedEventIds) {
        this.processedEventIds.add(eventId);
      }
    }

    if (staleCount > 0) {
      console.log(`[supercall] Cleaned up ${staleCount} stale call(s) on startup`);
    }
  }

}
