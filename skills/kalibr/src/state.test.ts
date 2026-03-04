import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { RunStateManager } from "./state.js";
import type { LlmInputRecord, LlmOutputRecord } from "./state.js";

function makeInput(overrides?: Partial<LlmInputRecord>): LlmInputRecord {
  return {
    runId: "run-1",
    provider: "anthropic",
    model: "anthropic/claude-sonnet-4-5",
    timestamp: Date.now(),
    ...overrides,
  };
}

function makeOutput(overrides?: Partial<LlmOutputRecord>): LlmOutputRecord {
  return {
    runId: "run-1",
    provider: "anthropic",
    model: "anthropic/claude-sonnet-4-5",
    inputTokens: 100,
    outputTokens: 50,
    cacheReadTokens: 10,
    cacheWriteTokens: 5,
    totalTokens: 150,
    timestamp: Date.now(),
    ...overrides,
  };
}

describe("RunStateManager", () => {
  let manager: RunStateManager;

  beforeEach(() => {
    manager = new RunStateManager();
  });

  describe("recordLlmInput", () => {
    it("creates a new run state on first input", () => {
      manager.recordLlmInput("session-1", makeInput());
      expect(manager.size).toBe(1);
    });

    it("appends to existing run state", () => {
      manager.recordLlmInput("session-1", makeInput({ runId: "run-1" }));
      manager.recordLlmInput("session-1", makeInput({ runId: "run-2" }));
      const data = manager.getAndClear("session-1");
      expect(data).not.toBeNull();
      expect(data!.inputs).toHaveLength(2);
    });

    it("generates a traceId (UUID format)", () => {
      manager.recordLlmInput("session-1", makeInput());
      const data = manager.getAndClear("session-1");
      expect(data!.traceId).toMatch(
        /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/,
      );
    });

    it("tracks separate sessions independently", () => {
      manager.recordLlmInput("session-1", makeInput({ provider: "anthropic" }));
      manager.recordLlmInput("session-2", makeInput({ provider: "openai" }));
      expect(manager.size).toBe(2);

      const data1 = manager.getAndClear("session-1");
      const data2 = manager.getAndClear("session-2");
      expect(data1!.primaryProvider).toBe("anthropic");
      expect(data2!.primaryProvider).toBe("openai");
    });
  });

  describe("recordLlmOutput", () => {
    it("creates a new run state if no input was recorded first", () => {
      manager.recordLlmOutput("session-1", makeOutput());
      expect(manager.size).toBe(1);
    });

    it("appends outputs to existing run state", () => {
      manager.recordLlmInput("session-1", makeInput());
      manager.recordLlmOutput("session-1", makeOutput());
      manager.recordLlmOutput("session-1", makeOutput());
      const data = manager.getAndClear("session-1");
      expect(data!.outputs).toHaveLength(2);
    });
  });

  describe("getAndClear", () => {
    it("returns null for unknown session", () => {
      expect(manager.getAndClear("nonexistent")).toBeNull();
    });

    it("removes the session after retrieval", () => {
      manager.recordLlmInput("session-1", makeInput());
      manager.getAndClear("session-1");
      expect(manager.size).toBe(0);
      expect(manager.getAndClear("session-1")).toBeNull();
    });

    it("aggregates token counts from multiple outputs", () => {
      manager.recordLlmInput("session-1", makeInput());
      manager.recordLlmOutput("session-1", makeOutput({
        inputTokens: 100,
        outputTokens: 50,
        cacheReadTokens: 10,
        cacheWriteTokens: 5,
        totalTokens: 150,
      }));
      manager.recordLlmOutput("session-1", makeOutput({
        inputTokens: 200,
        outputTokens: 100,
        cacheReadTokens: 20,
        cacheWriteTokens: 10,
        totalTokens: 300,
      }));

      const data = manager.getAndClear("session-1")!;
      expect(data.llmCallCount).toBe(2);
      expect(data.totalInputTokens).toBe(300);
      expect(data.totalOutputTokens).toBe(150);
      expect(data.totalCacheReadTokens).toBe(30);
      expect(data.totalCacheWriteTokens).toBe(15);
      expect(data.totalTokens).toBe(450);
    });

    it("returns primaryModel and primaryProvider from first input", () => {
      manager.recordLlmInput("session-1", makeInput({
        model: "anthropic/claude-sonnet-4-5",
        provider: "anthropic",
      }));
      manager.recordLlmInput("session-1", makeInput({
        model: "openai/gpt-5.2",
        provider: "openai",
      }));

      const data = manager.getAndClear("session-1")!;
      expect(data.primaryModel).toBe("anthropic/claude-sonnet-4-5");
      expect(data.primaryProvider).toBe("anthropic");
    });

    it("returns undefined for primaryModel/primaryProvider if no inputs recorded", () => {
      manager.recordLlmOutput("session-1", makeOutput());
      const data = manager.getAndClear("session-1")!;
      expect(data.primaryModel).toBeUndefined();
      expect(data.primaryProvider).toBeUndefined();
    });

    it("returns zero aggregates when no outputs recorded", () => {
      manager.recordLlmInput("session-1", makeInput());
      const data = manager.getAndClear("session-1")!;
      expect(data.llmCallCount).toBe(0);
      expect(data.totalInputTokens).toBe(0);
      expect(data.totalOutputTokens).toBe(0);
      expect(data.totalTokens).toBe(0);
      expect(data.totalCacheReadTokens).toBe(0);
      expect(data.totalCacheWriteTokens).toBe(0);
    });
  });

  describe("stale eviction", () => {
    it("evicts runs older than TTL on next recordLlmInput call", () => {
      // Record a run with a very old timestamp
      manager.recordLlmInput("old-session", makeInput({
        timestamp: Date.now() - 11 * 60 * 1000, // 11 min ago
      }));
      expect(manager.size).toBe(1);

      // Trigger eviction via new recordLlmInput
      manager.recordLlmInput("new-session", makeInput());
      expect(manager.size).toBe(1); // old evicted, new added
      expect(manager.getAndClear("old-session")).toBeNull();
    });
  });

  describe("setLastDecision / getLastDecision", () => {
    it("round-trips a stored decision", () => {
      manager.setLastDecision("session-1", {
        tool_id: "tool-abc",
        params: { temperature: 0.5 },
      });

      const decision = manager.getLastDecision("session-1");
      expect(decision).toEqual({
        tool_id: "tool-abc",
        params: { temperature: 0.5 },
      });
    });

    it("returns null for unknown session", () => {
      expect(manager.getLastDecision("nonexistent")).toBeNull();
    });

    it("getAndClear also clears lastDecision", () => {
      manager.recordLlmInput("session-1", makeInput());
      manager.setLastDecision("session-1", {
        tool_id: "tool-1",
        params: { key: "value" },
      });

      manager.getAndClear("session-1");
      expect(manager.getLastDecision("session-1")).toBeNull();
    });

    it("evicts stale lastDecisions past TTL", () => {
      vi.useFakeTimers();

      const now = Date.now();
      manager.setLastDecision("stale-session", {
        tool_id: "tool-old",
        params: { old: true },
      });

      // Advance time past TTL (10 min + 1 min)
      vi.advanceTimersByTime(11 * 60 * 1000);

      // Trigger eviction via recordLlmInput which calls evictStale
      manager.recordLlmInput("new-session", makeInput({ timestamp: now + 11 * 60 * 1000 }));

      expect(manager.getLastDecision("stale-session")).toBeNull();
    });

    afterEach(() => {
      vi.useRealTimers();
    });
  });

  describe("recordToolCall", () => {
    it("adds tool names to the run state", () => {
      manager.recordLlmInput("session-1", makeInput());
      manager.recordToolCall("session-1", "Read");
      manager.recordToolCall("session-1", "Write");

      const data = manager.getAndClear("session-1");
      expect(data!.toolsCalled).toEqual(["Read", "Write"]);
    });

    it("creates run entry if none exists", () => {
      manager.recordToolCall("session-new", "Bash");
      expect(manager.size).toBe(1);

      const data = manager.getAndClear("session-new");
      expect(data).not.toBeNull();
      expect(data!.toolsCalled).toEqual(["Bash"]);
      expect(data!.inputs).toEqual([]);
      expect(data!.outputs).toEqual([]);
    });

    it("calls evictStale (evicts old runs)", () => {
      manager.recordLlmInput("old-session", makeInput({
        timestamp: Date.now() - 11 * 60 * 1000,
      }));
      expect(manager.size).toBe(1);

      manager.recordToolCall("new-session", "Read");
      expect(manager.size).toBe(1); // old evicted, new added
      expect(manager.getAndClear("old-session")).toBeNull();
    });
  });

  describe("getAndClear returns toolsCalled", () => {
    it("includes toolsCalled in aggregated data", () => {
      manager.recordLlmInput("session-1", makeInput());
      manager.recordToolCall("session-1", "Read");
      manager.recordToolCall("session-1", "Edit");
      manager.recordToolCall("session-1", "Bash");

      const data = manager.getAndClear("session-1");
      expect(data!.toolsCalled).toEqual(["Read", "Edit", "Bash"]);
    });

    it("returns empty toolsCalled when no tools were called", () => {
      manager.recordLlmInput("session-1", makeInput());
      const data = manager.getAndClear("session-1");
      expect(data!.toolsCalled).toEqual([]);
    });
  });
});
