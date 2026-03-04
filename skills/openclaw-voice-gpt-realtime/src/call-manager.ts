import { mkdirSync, appendFileSync } from "node:fs";
import { join } from "node:path";
import { homedir } from "node:os";
const DATA_DIR = join(homedir(), ".openclaw", "voice-calls-realtime");
const CALLS_FILE = join(DATA_DIR, "calls.jsonl");

export interface CallRecord {
  callId: string;
  callSid?: string;
  to: string;
  from: string;
  task: string;
  direction: "outbound" | "inbound";
  status: "initiating" | "ringing" | "in-progress" | "completed" | "failed" | "no-answer" | "busy";
  startedAt: number;
  answeredAt?: number;
  endedAt?: number;
  duration?: number;
  amdResult?: string;
  transcript: Array<{ role: string; text: string; ts: number }>;
  outcome?: CallOutcome;
  error?: string;
  streamSid?: string;
}

export interface CallOutcome {
  success: boolean;
  summary: string;
  details?: Record<string, unknown>;
}

type CallEventCallback = (callId: string, record: CallRecord) => void;

export class CallManager {
  private calls = new Map<string, CallRecord>();
  private sidToCallId = new Map<string, string>();
  private streamSidToCallId = new Map<string, string>();
  private onComplete?: CallEventCallback;

  constructor() {
    mkdirSync(DATA_DIR, { recursive: true, mode: 0o700 });
  }

  setOnComplete(cb: CallEventCallback): void {
    this.onComplete = cb;
  }

  createCall(callId: string, to: string, from: string, task: string, direction: "outbound" | "inbound" = "outbound"): CallRecord {
    const record: CallRecord = {
      callId,
      to,
      from,
      task,
      direction,
      status: direction === "inbound" ? "ringing" : "initiating",
      startedAt: Date.now(),
      transcript: [],
    };
    this.calls.set(callId, record);
    return record;
  }

  setCallSid(callId: string, callSid: string): void {
    const record = this.calls.get(callId);
    if (record) {
      record.callSid = callSid;
      this.sidToCallId.set(callSid, callId);
    }
  }

  setStreamSid(callId: string, streamSid: string): void {
    const record = this.calls.get(callId);
    if (record) {
      record.streamSid = streamSid;
      this.streamSidToCallId.set(streamSid, callId);
    }
  }

  getByCallId(callId: string): CallRecord | undefined {
    return this.calls.get(callId);
  }

  getByCallSid(callSid: string): CallRecord | undefined {
    const callId = this.sidToCallId.get(callSid);
    return callId ? this.calls.get(callId) : undefined;
  }

  getByStreamSid(streamSid: string): CallRecord | undefined {
    const callId = this.streamSidToCallId.get(streamSid);
    return callId ? this.calls.get(callId) : undefined;
  }

  updateStatus(callId: string, status: CallRecord["status"]): void {
    const record = this.calls.get(callId);
    if (!record) return;

    record.status = status;

    if (status === "in-progress" && !record.answeredAt) {
      record.answeredAt = Date.now();
    }

    if (status === "completed" || status === "failed" || status === "no-answer" || status === "busy") {
      record.endedAt = Date.now();
      if (record.answeredAt) {
        record.duration = Math.floor((record.endedAt - record.answeredAt) / 1000);
      }
      this.persist(record);
      this.onComplete?.(callId, record);
    }
  }

  setAmdResult(callId: string, result: string): void {
    const record = this.calls.get(callId);
    if (record) {
      record.amdResult = result;
    }
  }

  addTranscript(callId: string, role: string, text: string): void {
    const record = this.calls.get(callId);
    if (record) {
      record.transcript.push({ role, text, ts: Date.now() });
    }
  }

  setOutcome(callId: string, outcome: CallOutcome): void {
    const record = this.calls.get(callId);
    if (record) {
      record.outcome = outcome;
    }
  }

  setError(callId: string, error: string): void {
    const record = this.calls.get(callId);
    if (record) {
      record.error = error;
    }
  }

  cleanup(callId: string): void {
    const record = this.calls.get(callId);
    if (record) {
      if (record.callSid) this.sidToCallId.delete(record.callSid);
      if (record.streamSid) this.streamSidToCallId.delete(record.streamSid);
      this.calls.delete(callId);
    }
  }

  getActiveCalls(): CallRecord[] {
    return Array.from(this.calls.values()).filter(
      (r) => r.status === "initiating" || r.status === "ringing" || r.status === "in-progress"
    );
  }

  private persist(record: CallRecord): void {
    const line = JSON.stringify({
      callId: record.callId,
      callSid: record.callSid,
      to: record.to,
      from: record.from,
      task: record.task,
      direction: record.direction,
      status: record.status,
      startedAt: record.startedAt,
      answeredAt: record.answeredAt,
      endedAt: record.endedAt,
      duration: record.duration,
      amdResult: record.amdResult,
      outcome: record.outcome,
      transcriptLength: record.transcript.length,
      error: record.error,
    });
    appendFileSync(CALLS_FILE, line + "\n", { mode: 0o600 });
  }
}
