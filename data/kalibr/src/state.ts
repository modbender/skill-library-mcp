import { randomUUID } from "crypto";

export interface StoredDecision {
  tool_id?: string;
  params?: Record<string, unknown>;
}

export interface LlmInputRecord {
  runId: string;
  provider: string;
  model: string;
  timestamp: number;
}

export interface LlmOutputRecord {
  runId: string;
  provider: string;
  model: string;
  inputTokens: number;
  outputTokens: number;
  cacheReadTokens: number;
  cacheWriteTokens: number;
  totalTokens: number;
  timestamp: number;
}

interface RunState {
  traceId: string;
  inputs: LlmInputRecord[];
  outputs: LlmOutputRecord[];
  toolsCalled: string[];
}

export interface AggregatedRunData {
  traceId: string;
  primaryModel: string | undefined;
  primaryProvider: string | undefined;
  llmCallCount: number;
  totalInputTokens: number;
  totalOutputTokens: number;
  totalTokens: number;
  totalCacheReadTokens: number;
  totalCacheWriteTokens: number;
  inputs: LlmInputRecord[];
  outputs: LlmOutputRecord[];
  toolsCalled: string[];
}

export class RunStateManager {
  private runs = new Map<string, RunState>();
  private lastDecisions = new Map<string, { decision: StoredDecision; storedAt: number }>();
  private readonly TTL_MS = 10 * 60 * 1000; // 10 min TTL for orphaned runs

  private evictStale(): void {
    const now = Date.now();
    for (const [key, run] of this.runs) {
      const lastActivity =
        run.outputs.length > 0
          ? run.outputs[run.outputs.length - 1].timestamp
          : run.inputs.length > 0
            ? run.inputs[run.inputs.length - 1].timestamp
            : now;
      if (now - lastActivity > this.TTL_MS) {
        this.runs.delete(key);
      }
    }
    for (const [key, entry] of this.lastDecisions) {
      if (now - entry.storedAt > this.TTL_MS) {
        this.lastDecisions.delete(key);
      }
    }
  }

  recordLlmInput(sessionKey: string, record: LlmInputRecord): void {
    this.evictStale();
    if (!this.runs.has(sessionKey)) {
      this.runs.set(sessionKey, {
        traceId: randomUUID(),
        inputs: [],
        outputs: [],
        toolsCalled: [],
      });
    }
    this.runs.get(sessionKey)!.inputs.push(record);
  }

  recordLlmOutput(sessionKey: string, record: LlmOutputRecord): void {
    if (!this.runs.has(sessionKey)) {
      this.runs.set(sessionKey, {
        traceId: randomUUID(),
        inputs: [],
        outputs: [],
        toolsCalled: [],
      });
    }
    this.runs.get(sessionKey)!.outputs.push(record);
  }

  setLastDecision(sessionKey: string, decision: StoredDecision): void {
    this.lastDecisions.set(sessionKey, {
      decision,
      storedAt: Date.now(),
    });
  }

  getLastDecision(sessionKey: string): StoredDecision | null {
    const entry = this.lastDecisions.get(sessionKey);
    if (!entry) return null;
    return entry.decision;
  }

  recordToolCall(sessionKey: string, toolName: string): void {
    this.evictStale();
    if (!this.runs.has(sessionKey)) {
      this.runs.set(sessionKey, {
        traceId: randomUUID(),
        inputs: [],
        outputs: [],
        toolsCalled: [],
      });
    }
    this.runs.get(sessionKey)!.toolsCalled.push(toolName);
  }

  getAndClear(sessionKey: string): AggregatedRunData | null {
    const run = this.runs.get(sessionKey);
    if (!run) return null;
    this.runs.delete(sessionKey);
    this.lastDecisions.delete(sessionKey);

    const firstInput = run.inputs[0];
    const outputs = run.outputs;

    return {
      traceId: run.traceId,
      primaryModel: firstInput?.model,
      primaryProvider: firstInput?.provider,
      llmCallCount: outputs.length,
      totalInputTokens: outputs.reduce((s, o) => s + o.inputTokens, 0),
      totalOutputTokens: outputs.reduce((s, o) => s + o.outputTokens, 0),
      totalTokens: outputs.reduce((s, o) => s + o.totalTokens, 0),
      totalCacheReadTokens: outputs.reduce((s, o) => s + o.cacheReadTokens, 0),
      totalCacheWriteTokens: outputs.reduce((s, o) => s + o.cacheWriteTokens, 0),
      inputs: run.inputs,
      outputs,
      toolsCalled: run.toolsCalled,
    };
  }

  /** Visible for testing */
  get size(): number {
    return this.runs.size;
  }
}
