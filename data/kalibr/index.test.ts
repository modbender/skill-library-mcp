import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock @kalibr/sdk before importing plugin
vi.mock("@kalibr/sdk", () => ({
  KalibrIntelligence: {
    init: vi.fn(),
  },
  reportOutcome: vi.fn().mockResolvedValue({ success: true }),
  decide: vi.fn().mockResolvedValue({
    path_id: "path-1",
    model_id: "claude-sonnet-4-5",
    reason: "highest success rate",
    confidence: 0.92,
    exploration: false,
    success_rate: 0.95,
    sample_count: 150,
  }),
}));

import plugin from "./index.js";
import type { KalibrConfig } from "./index.js";

// ── Helpers ────────────────────────────────────────────────

interface HookRegistration {
  name: string;
  handler: (event: unknown, ctx?: unknown) => unknown | Promise<unknown>;
  opts?: { priority?: number };
}

interface CommandRegistration {
  name: string;
  description: string;
  handler: (ctx: unknown) => { text: string };
}

interface GatewayRegistration {
  name: string;
  handler: (ctx: { respond: (success: boolean, data: unknown) => void }) => void;
}

function createMockApi(config: KalibrConfig) {
  const hooks: HookRegistration[] = [];
  const commands: CommandRegistration[] = [];
  const gatewayMethods: GatewayRegistration[] = [];
  const cliRegistrations: Array<{ fn: unknown; opts: unknown }> = [];

  const api = {
    pluginConfig: config,
    logger: {
      info: vi.fn(),
      warn: vi.fn(),
      error: vi.fn(),
    },
    on: vi.fn((name: string, handler: HookRegistration["handler"], opts?: { priority?: number }) => {
      hooks.push({ name, handler, opts });
    }),
    registerCommand: vi.fn((cmd: CommandRegistration) => {
      commands.push(cmd);
    }),
    registerGatewayMethod: vi.fn((name: string, handler: GatewayRegistration["handler"]) => {
      gatewayMethods.push({ name, handler });
    }),
    registerCli: vi.fn((fn: unknown, opts: unknown) => {
      cliRegistrations.push({ fn, opts });
    }),
  };

  return { api, hooks, commands, gatewayMethods, cliRegistrations };
}

function findHook(hooks: HookRegistration[], name: string): HookRegistration | undefined {
  return hooks.find((h) => h.name === name);
}

// ── Tests ──────────────────────────────────────────────────

describe("plugin", () => {
  it("has correct id and name", () => {
    expect(plugin.id).toBe("kalibr");
    expect(plugin.name).toBe("Kalibr Intelligence");
  });

  it("uses export default", async () => {
    const mod = await import("./index.js");
    expect(mod.default).toBe(plugin);
  });

  describe("register()", () => {
    it("does not register anything when enabled is false", () => {
      const { api } = createMockApi({ apiKey: "test", enabled: false });
      plugin.register(api as never);
      expect(api.on).not.toHaveBeenCalled();
      expect(api.registerCommand).not.toHaveBeenCalled();
    });

    it("registers when enabled is undefined (default)", () => {
      const { api } = createMockApi({ apiKey: "test" });
      plugin.register(api as never);
      expect(api.on).toHaveBeenCalled();
    });

    it("registers all telemetry + outcome hooks when fully enabled", async () => {
      const { api, hooks } = createMockApi({
        apiKey: "test-key",
        captureLlmTelemetry: true,
        captureOutcomes: true,
      });

      plugin.register(api as never);
      await new Promise((r) => setTimeout(r, 10));

      const hookNames = hooks.map((h) => h.name);
      expect(hookNames).toContain("llm_input");
      expect(hookNames).toContain("llm_output");
      expect(hookNames).toContain("agent_end");
    });

    it("skips telemetry hooks when captureLlmTelemetry is false", () => {
      const { api, hooks } = createMockApi({
        apiKey: "test-key",
        captureLlmTelemetry: false,
        captureOutcomes: true,
      });

      plugin.register(api as never);

      const hookNames = hooks.map((h) => h.name);
      expect(hookNames).not.toContain("llm_input");
      expect(hookNames).not.toContain("llm_output");
      expect(hookNames).toContain("agent_end");
    });

    it("skips outcome hook when captureOutcomes is false", () => {
      const { api, hooks } = createMockApi({
        apiKey: "test-key",
        captureLlmTelemetry: true,
        captureOutcomes: false,
      });

      plugin.register(api as never);

      const hookNames = hooks.map((h) => h.name);
      expect(hookNames).toContain("llm_input");
      expect(hookNames).toContain("llm_output");
      expect(hookNames).not.toContain("agent_end");
    });

    it("does not register before_agent_start when enableRouting is not true", () => {
      const { api, hooks } = createMockApi({ apiKey: "test" });
      plugin.register(api as never);

      const hookNames = hooks.map((h) => h.name);
      expect(hookNames).not.toContain("before_agent_start");
    });

    it("registers before_agent_start when enableRouting is true", () => {
      const { api, hooks } = createMockApi({
        apiKey: "test",
        enableRouting: true,
      });
      plugin.register(api as never);

      const hookNames = hooks.map((h) => h.name);
      expect(hookNames).toContain("before_agent_start");
    });

    it("calls api.logger.info directly (logger is not optional)", async () => {
      const { api } = createMockApi({ apiKey: "test" });
      plugin.register(api as never);
      await new Promise((r) => setTimeout(r, 50));

      expect(api.logger.info).toHaveBeenCalledWith("[kalibr] Plugin registered");
    });
  });

  describe("before_agent_start hook (routing)", () => {
    it("calls decide() and returns modelOverride/providerOverride", async () => {
      const sdk = await import("@kalibr/sdk");
      const mockDecide = sdk.decide as ReturnType<typeof vi.fn>;
      mockDecide.mockClear();
      mockDecide.mockResolvedValueOnce({
        path_id: "path-1",
        model_id: "claude-sonnet-4-5",
        reason: "best",
        confidence: 0.9,
        exploration: false,
      });

      const { api, hooks } = createMockApi({
        apiKey: "test",
        enableRouting: true,
        defaultGoal: "my_goal",
      });
      plugin.register(api as never);

      // Wait for SDK init
      await new Promise((r) => setTimeout(r, 50));

      const handler = findHook(hooks, "before_agent_start")!.handler;
      const result = await handler(
        { prompt: "hello" },
        { sessionKey: "sk-1" },
      );

      expect(mockDecide).toHaveBeenCalledWith("my_goal");
      expect(result).toEqual({
        modelOverride: "claude-sonnet-4-5",
        providerOverride: "anthropic",
      });
    });

    it("returns empty object when decide() returns unknown model_id", async () => {
      const sdk = await import("@kalibr/sdk");
      const mockDecide = sdk.decide as ReturnType<typeof vi.fn>;
      mockDecide.mockClear();
      mockDecide.mockResolvedValueOnce({
        path_id: "path-2",
        model_id: "unknown-model-xyz",
        reason: "test",
        confidence: 0.5,
        exploration: true,
      });

      const { api, hooks } = createMockApi({
        apiKey: "test",
        enableRouting: true,
      });
      plugin.register(api as never);
      await new Promise((r) => setTimeout(r, 50));

      const handler = findHook(hooks, "before_agent_start")!.handler;
      const result = await handler({ prompt: "hello" }, {});

      expect(result).toEqual({});
      expect(api.logger.warn).toHaveBeenCalledWith(
        expect.stringContaining("unknown model_id: unknown-model-xyz"),
      );
    });

    it("returns empty object when decide() throws", async () => {
      const sdk = await import("@kalibr/sdk");
      const mockDecide = sdk.decide as ReturnType<typeof vi.fn>;
      mockDecide.mockClear();
      mockDecide.mockRejectedValueOnce(new Error("network timeout"));

      const { api, hooks } = createMockApi({
        apiKey: "test",
        enableRouting: true,
      });
      plugin.register(api as never);
      await new Promise((r) => setTimeout(r, 50));

      const handler = findHook(hooks, "before_agent_start")!.handler;
      const result = await handler({ prompt: "hello" }, {});

      expect(result).toEqual({});
      expect(api.logger.error).toHaveBeenCalledWith(
        expect.stringContaining("decide() failed"),
      );
    });

    it("returns empty object when SDK is not ready", async () => {
      const { api, hooks } = createMockApi({
        apiKey: "test",
        enableRouting: true,
      });
      plugin.register(api as never);

      const handler = findHook(hooks, "before_agent_start")!.handler;
      const result = await handler({ prompt: "hello" }, {});

      expect(result).toEqual({});
    });

    it("handles model_id that already contains slash (passthrough)", async () => {
      const sdk = await import("@kalibr/sdk");
      const mockDecide = sdk.decide as ReturnType<typeof vi.fn>;
      mockDecide.mockClear();
      mockDecide.mockResolvedValueOnce({
        path_id: "path-3",
        model_id: "google/gemini-ultra",
        reason: "test",
        confidence: 0.8,
        exploration: false,
      });

      const { api, hooks } = createMockApi({
        apiKey: "test",
        enableRouting: true,
      });
      plugin.register(api as never);
      await new Promise((r) => setTimeout(r, 50));

      const handler = findHook(hooks, "before_agent_start")!.handler;
      const result = await handler({ prompt: "hello" }, {});

      expect(result).toEqual({
        modelOverride: "gemini-ultra",
        providerOverride: "google",
      });
    });
  });

  describe("before_tool_call hook registration", () => {
    it("registers before_tool_call when enableRouting is true", () => {
      const { api, hooks } = createMockApi({
        apiKey: "test",
        enableRouting: true,
      });
      plugin.register(api as never);

      const hookNames = hooks.map((h) => h.name);
      expect(hookNames).toContain("before_tool_call");
    });

    it("registers before_tool_call when enableRouting is false but captureLlmTelemetry is true", () => {
      const { api, hooks } = createMockApi({
        apiKey: "test",
        enableRouting: false,
        captureLlmTelemetry: true,
      });
      plugin.register(api as never);

      const hookNames = hooks.map((h) => h.name);
      expect(hookNames).toContain("before_tool_call");
    });

    it("does NOT register before_tool_call when both enableRouting is false and captureLlmTelemetry is false", () => {
      const { api, hooks } = createMockApi({
        apiKey: "test",
        enableRouting: false,
        captureLlmTelemetry: false,
      });
      plugin.register(api as never);

      const hookNames = hooks.map((h) => h.name);
      expect(hookNames).not.toContain("before_tool_call");
    });

    it("registers only ONE before_tool_call hook when both enableRouting and captureLlmTelemetry are true", () => {
      const { api, hooks } = createMockApi({
        apiKey: "test",
        enableRouting: true,
        captureLlmTelemetry: true,
      });
      plugin.register(api as never);

      const toolCallHooks = hooks.filter((h) => h.name === "before_tool_call");
      expect(toolCallHooks).toHaveLength(1);
    });
  });

  describe("before_tool_call hook behavior", () => {
    it("returns {} when no decision stored but still records tool name", async () => {
      const { api, hooks } = createMockApi({
        apiKey: "test",
        enableRouting: true,
      });
      plugin.register(api as never);

      const handler = findHook(hooks, "before_tool_call")!.handler;
      const result = await handler(
        { toolName: "Read", params: { file_path: "/foo" } },
        { sessionKey: "sk-1", toolName: "Read" },
      );

      expect(result).toEqual({});
    });

    it("returns {} when decision has no params", async () => {
      const sdk = await import("@kalibr/sdk");
      const mockDecide = sdk.decide as ReturnType<typeof vi.fn>;
      mockDecide.mockClear();
      mockDecide.mockResolvedValueOnce({
        path_id: "path-1",
        model_id: "claude-sonnet-4-5",
        reason: "best",
        confidence: 0.9,
        exploration: false,
      });

      const { api, hooks } = createMockApi({
        apiKey: "test",
        enableRouting: true,
      });
      plugin.register(api as never);
      await new Promise((r) => setTimeout(r, 50));

      // Trigger before_agent_start to store decision (no params)
      const agentStartHandler = findHook(hooks, "before_agent_start")!.handler;
      await agentStartHandler(
        { prompt: "hello" },
        { sessionKey: "sk-1" },
      );

      const handler = findHook(hooks, "before_tool_call")!.handler;
      const result = await handler(
        { toolName: "Read", params: { file_path: "/foo" } },
        { sessionKey: "sk-1", toolName: "Read" },
      );

      expect(result).toEqual({});
    });

    it("returns { params } with merged params when decision has params (decision wins on conflicts)", async () => {
      const sdk = await import("@kalibr/sdk");
      const mockDecide = sdk.decide as ReturnType<typeof vi.fn>;
      mockDecide.mockClear();
      mockDecide.mockResolvedValueOnce({
        path_id: "path-1",
        model_id: "claude-sonnet-4-5",
        tool_id: "Read",
        params: { temperature: 0.5, max_tokens: 1000 },
        reason: "best",
        confidence: 0.9,
        exploration: false,
      });

      const { api, hooks } = createMockApi({
        apiKey: "test",
        enableRouting: true,
      });
      plugin.register(api as never);
      await new Promise((r) => setTimeout(r, 50));

      // Trigger before_agent_start to store decision with params
      const agentStartHandler = findHook(hooks, "before_agent_start")!.handler;
      await agentStartHandler(
        { prompt: "hello" },
        { sessionKey: "sk-1" },
      );

      const handler = findHook(hooks, "before_tool_call")!.handler;
      const result = await handler(
        { toolName: "Read", params: { file_path: "/foo", temperature: 0.8 } },
        { sessionKey: "sk-1", toolName: "Read" },
      );

      // decision.params wins on conflict (temperature)
      expect(result).toEqual({
        params: { file_path: "/foo", temperature: 0.5, max_tokens: 1000 },
      });
    });

    it("in telemetry-only mode returns {} and still records tool name", async () => {
      const { api, hooks } = createMockApi({
        apiKey: "test",
        enableRouting: false,
        captureLlmTelemetry: true,
      });
      plugin.register(api as never);

      const handler = findHook(hooks, "before_tool_call")!.handler;
      const result = await handler(
        { toolName: "Bash", params: { command: "ls" } },
        { sessionKey: "sk-1", toolName: "Bash" },
      );

      expect(result).toEqual({});
    });

    it("returns {} when sessionKey is missing", async () => {
      const { api, hooks } = createMockApi({
        apiKey: "test",
        enableRouting: true,
      });
      plugin.register(api as never);

      const handler = findHook(hooks, "before_tool_call")!.handler;
      const result = await handler(
        { toolName: "Read", params: {} },
        { toolName: "Read" }, // no sessionKey
      );

      expect(result).toEqual({});
    });

    it("returns {} on error (graceful degradation)", async () => {
      const { api, hooks } = createMockApi({
        apiKey: "test",
        enableRouting: true,
      });
      plugin.register(api as never);

      const handler = findHook(hooks, "before_tool_call")!.handler;
      // Pass null ctx to force an error path
      const result = await handler(
        { toolName: "Read", params: {} },
        undefined,
      );

      expect(result).toEqual({});
    });
  });

  describe("integration: before_agent_start stores decision, before_tool_call reads it", () => {
    it("injects params from decide() into tool calls", async () => {
      const sdk = await import("@kalibr/sdk");
      const mockDecide = sdk.decide as ReturnType<typeof vi.fn>;
      mockDecide.mockClear();
      mockDecide.mockResolvedValueOnce({
        path_id: "path-1",
        model_id: "claude-sonnet-4-5",
        tool_id: "Write",
        params: { encoding: "utf-8", overwrite: true },
        reason: "optimized",
        confidence: 0.95,
        exploration: false,
      });

      const { api, hooks } = createMockApi({
        apiKey: "test",
        enableRouting: true,
      });
      plugin.register(api as never);
      await new Promise((r) => setTimeout(r, 50));

      // Step 1: before_agent_start stores decision
      const agentStartHandler = findHook(hooks, "before_agent_start")!.handler;
      await agentStartHandler(
        { prompt: "write a file" },
        { sessionKey: "sk-integration" },
      );

      // Step 2: before_tool_call reads and injects params
      const toolCallHandler = findHook(hooks, "before_tool_call")!.handler;
      const result = await toolCallHandler(
        { toolName: "Write", params: { file_path: "/test.txt", content: "hello" } },
        { sessionKey: "sk-integration", toolName: "Write" },
      );

      expect(result).toEqual({
        params: {
          file_path: "/test.txt",
          content: "hello",
          encoding: "utf-8",
          overwrite: true,
        },
      });
    });
  });

  describe("tool telemetry in outcome reporting", () => {
    it("includes toolsCalled and toolCallCount in outcome metadata", async () => {
      const sdk = await import("@kalibr/sdk");
      const mockReportOutcome = sdk.reportOutcome as ReturnType<typeof vi.fn>;
      mockReportOutcome.mockClear();

      const { api, hooks } = createMockApi({
        apiKey: "test",
        enableRouting: true,
        defaultGoal: "my_goal",
      });
      plugin.register(api as never);
      await new Promise((r) => setTimeout(r, 50));

      const inputHandler = findHook(hooks, "llm_input")!.handler;
      const toolCallHandler = findHook(hooks, "before_tool_call")!.handler;
      const endHandler = findHook(hooks, "agent_end")!.handler;

      const ctx = { sessionKey: "sk-tools", agentId: "agent-1" };

      await inputHandler(
        { runId: "r1", sessionId: "s1", provider: "anthropic", model: "anthropic/claude-sonnet-4-5", prompt: "p", historyMessages: [], imagesCount: 0 },
        ctx,
      );

      // Record tool calls
      await toolCallHandler(
        { toolName: "Read", params: {} },
        { sessionKey: "sk-tools", toolName: "Read" },
      );
      await toolCallHandler(
        { toolName: "Edit", params: {} },
        { sessionKey: "sk-tools", toolName: "Edit" },
      );

      await endHandler(
        { messages: [], success: true, durationMs: 500 },
        ctx,
      );

      await new Promise((r) => setTimeout(r, 50));

      expect(mockReportOutcome).toHaveBeenCalledTimes(1);
      const [, , , options] = mockReportOutcome.mock.calls[0];
      expect(options.toolId).toBe("Read"); // first tool called
      expect(options.metadata.toolsCalled).toEqual(["Read", "Edit"]);
      expect(options.metadata.toolCallCount).toBe(2);
    });

    it("does not include toolId when no tools were called", async () => {
      const sdk = await import("@kalibr/sdk");
      const mockReportOutcome = sdk.reportOutcome as ReturnType<typeof vi.fn>;
      mockReportOutcome.mockClear();

      const { api, hooks } = createMockApi({
        apiKey: "test",
        defaultGoal: "my_goal",
      });
      plugin.register(api as never);

      const inputHandler = findHook(hooks, "llm_input")!.handler;
      const endHandler = findHook(hooks, "agent_end")!.handler;
      const ctx = { sessionKey: "sk-no-tools" };

      await inputHandler(
        { runId: "r1", sessionId: "s1", provider: "anthropic", model: "anthropic/claude-sonnet-4-5", prompt: "p", historyMessages: [], imagesCount: 0 },
        ctx,
      );

      await endHandler(
        { messages: [], success: true },
        ctx,
      );

      await new Promise((r) => setTimeout(r, 50));

      expect(mockReportOutcome).toHaveBeenCalledTimes(1);
      const [, , , options] = mockReportOutcome.mock.calls[0];
      expect(options.toolId).toBeUndefined();
      expect(options.metadata.toolsCalled).toEqual([]);
      expect(options.metadata.toolCallCount).toBe(0);
    });
  });

  describe("status outputs include param injection", () => {
    it("slash command shows param injection on when routing enabled", () => {
      const { api, commands } = createMockApi({
        apiKey: "test",
        enableRouting: true,
      });
      plugin.register(api as never);

      const cmd = commands.find((c) => c.name === "kalibr")!;
      const result = cmd.handler({});
      expect(result.text).toContain("Param injection: on");
    });

    it("slash command shows param injection off when routing disabled", () => {
      const { api, commands } = createMockApi({
        apiKey: "test",
        enableRouting: false,
      });
      plugin.register(api as never);

      const cmd = commands.find((c) => c.name === "kalibr")!;
      const result = cmd.handler({});
      expect(result.text).toContain("Param injection: off");
    });

    it("gateway status includes paramInjection field", () => {
      const { api, gatewayMethods } = createMockApi({
        apiKey: "test",
        enableRouting: true,
      });
      plugin.register(api as never);

      const method = gatewayMethods.find((m) => m.name === "kalibr.status")!;
      let responseData: Record<string, unknown> = {};
      method.handler({
        respond: (_success: boolean, data: unknown) => {
          responseData = data as Record<string, unknown>;
        },
      });

      expect(responseData.paramInjection).toBe(true);
    });
  });

  describe("llm_input hook", () => {
    it("ignores events without sessionKey in context", async () => {
      const { api, hooks } = createMockApi({ apiKey: "test" });
      plugin.register(api as never);

      const handler = findHook(hooks, "llm_input")!.handler;
      await handler(
        { runId: "r1", sessionId: "s1", provider: "anthropic", model: "m1", prompt: "p", historyMessages: [], imagesCount: 0 },
        { /* no sessionKey */ },
      );
    });

    it("records input when sessionKey is present", async () => {
      const { api, hooks } = createMockApi({ apiKey: "test" });
      plugin.register(api as never);

      const handler = findHook(hooks, "llm_input")!.handler;
      await handler(
        { runId: "r1", sessionId: "s1", provider: "anthropic", model: "anthropic/claude-sonnet-4-5", prompt: "p", historyMessages: [], imagesCount: 0 },
        { sessionKey: "sk-1" },
      );
    });
  });

  describe("llm_output hook", () => {
    it("handles missing usage fields gracefully", async () => {
      const { api, hooks } = createMockApi({ apiKey: "test" });
      plugin.register(api as never);

      const handler = findHook(hooks, "llm_output")!.handler;
      await handler(
        { runId: "r1", sessionId: "s1", provider: "anthropic", model: "m1", assistantTexts: ["hello"] },
        { sessionKey: "sk-1" },
      );
    });

    it("handles partial usage fields", async () => {
      const { api, hooks } = createMockApi({ apiKey: "test" });
      plugin.register(api as never);

      const handler = findHook(hooks, "llm_output")!.handler;
      await handler(
        { runId: "r1", sessionId: "s1", provider: "anthropic", model: "m1", assistantTexts: ["hello"], usage: { input: 100 } },
        { sessionKey: "sk-1" },
      );
    });
  });

  describe("agent_end hook", () => {
    it("reports outcome via reportOutcome with correct 4-arg signature", async () => {
      const sdk = await import("@kalibr/sdk");
      const mockReportOutcome = sdk.reportOutcome as ReturnType<typeof vi.fn>;
      mockReportOutcome.mockClear();

      const { api, hooks } = createMockApi({
        apiKey: "test",
        defaultGoal: "my_goal",
      });
      plugin.register(api as never);

      const inputHandler = findHook(hooks, "llm_input")!.handler;
      const outputHandler = findHook(hooks, "llm_output")!.handler;
      const endHandler = findHook(hooks, "agent_end")!.handler;

      const ctx = { sessionKey: "sk-test", agentId: "agent-1" };

      await inputHandler(
        { runId: "r1", sessionId: "s1", provider: "anthropic", model: "anthropic/claude-sonnet-4-5", prompt: "p", historyMessages: [], imagesCount: 0 },
        ctx,
      );

      await outputHandler(
        { runId: "r1", sessionId: "s1", provider: "anthropic", model: "anthropic/claude-sonnet-4-5", assistantTexts: ["done"], usage: { input: 500, output: 200, cacheRead: 50, cacheWrite: 25, total: 700 } },
        ctx,
      );

      await endHandler(
        { messages: [], success: true, durationMs: 1234 },
        ctx,
      );

      await new Promise((r) => setTimeout(r, 50));

      expect(mockReportOutcome).toHaveBeenCalledTimes(1);

      const [traceId, reportedGoal, success, options] = mockReportOutcome.mock.calls[0];

      expect(traceId).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-/);
      expect(reportedGoal).toBe("my_goal");
      expect(success).toBe(true);

      expect(options.modelId).toBe("claude-sonnet-4-5");
      expect(options.metadata).toMatchObject({
        provider: "anthropic",
        agentId: "agent-1",
        sessionKey: "sk-test",
        durationMs: 1234,
        llmCalls: 1,
        totalInputTokens: 500,
        totalOutputTokens: 200,
        totalTokens: 700,
        cacheReadTokens: 50,
        cacheWriteTokens: 25,
      });
    });

    it("includes failureReason when event has error", async () => {
      const sdk = await import("@kalibr/sdk");
      const mockReportOutcome = sdk.reportOutcome as ReturnType<typeof vi.fn>;
      mockReportOutcome.mockClear();

      const { api, hooks } = createMockApi({ apiKey: "test" });
      plugin.register(api as never);

      const inputHandler = findHook(hooks, "llm_input")!.handler;
      const endHandler = findHook(hooks, "agent_end")!.handler;
      const ctx = { sessionKey: "sk-err" };

      await inputHandler(
        { runId: "r1", sessionId: "s1", provider: "openai", model: "openai/gpt-5.2", prompt: "p", historyMessages: [], imagesCount: 0 },
        ctx,
      );

      await endHandler(
        { messages: [], success: false, error: "timeout exceeded" },
        ctx,
      );

      await new Promise((r) => setTimeout(r, 50));

      expect(mockReportOutcome).toHaveBeenCalledTimes(1);
      const [, , success, options] = mockReportOutcome.mock.calls[0];
      expect(success).toBe(false);
      expect(options.failureReason).toBe("timeout exceeded");
    });

    it("does not call reportOutcome if no run data exists", async () => {
      const sdk = await import("@kalibr/sdk");
      const mockReportOutcome = sdk.reportOutcome as ReturnType<typeof vi.fn>;
      mockReportOutcome.mockClear();

      const { api, hooks } = createMockApi({ apiKey: "test" });
      plugin.register(api as never);

      const endHandler = findHook(hooks, "agent_end")!.handler;
      await endHandler(
        { messages: [], success: true },
        { sessionKey: "sk-no-data" },
      );

      await new Promise((r) => setTimeout(r, 50));
      expect(mockReportOutcome).not.toHaveBeenCalled();
    });

    it("logs error when reportOutcome fails", async () => {
      const sdk = await import("@kalibr/sdk");
      const mockReportOutcome = sdk.reportOutcome as ReturnType<typeof vi.fn>;
      mockReportOutcome.mockClear();
      mockReportOutcome.mockRejectedValueOnce(new Error("network error"));

      const { api, hooks } = createMockApi({ apiKey: "test" });
      plugin.register(api as never);

      const inputHandler = findHook(hooks, "llm_input")!.handler;
      const endHandler = findHook(hooks, "agent_end")!.handler;
      const ctx = { sessionKey: "sk-fail" };

      await inputHandler(
        { runId: "r1", sessionId: "s1", provider: "anthropic", model: "m1", prompt: "p", historyMessages: [], imagesCount: 0 },
        ctx,
      );

      await endHandler({ messages: [], success: false }, ctx);
      await new Promise((r) => setTimeout(r, 50));

      expect(api.logger.error).toHaveBeenCalledWith(
        expect.stringContaining("[kalibr] Outcome report failed"),
      );
    });
  });

  describe("slash command", () => {
    it("registers /kalibr command", () => {
      const { api, commands } = createMockApi({
        apiKey: "test",
        defaultGoal: "custom_goal",
      });
      plugin.register(api as never);

      const cmd = commands.find((c) => c.name === "kalibr");
      expect(cmd).toBeDefined();
      expect(cmd!.description).toBe("Show Kalibr plugin status");
    });

    it("returns status text with config values including routing", () => {
      const { api, commands } = createMockApi({
        apiKey: "test",
        defaultGoal: "custom_goal",
        enableRouting: true,
        captureLlmTelemetry: false,
        captureOutcomes: true,
      });
      plugin.register(api as never);

      const cmd = commands.find((c) => c.name === "kalibr")!;
      const result = cmd.handler({});
      expect(result.text).toContain("Kalibr: active");
      expect(result.text).toContain("Goal: custom_goal");
      expect(result.text).toContain("Routing: on");
      expect(result.text).toContain("Telemetry: off");
      expect(result.text).toContain("Outcomes: on");
    });

    it("shows routing off when not enabled", () => {
      const { api, commands } = createMockApi({ apiKey: "test" });
      plugin.register(api as never);

      const cmd = commands.find((c) => c.name === "kalibr")!;
      const result = cmd.handler({});
      expect(result.text).toContain("Routing: off");
    });
  });

  describe("gateway method", () => {
    it("registers kalibr.status method", () => {
      const { api, gatewayMethods } = createMockApi({ apiKey: "test" });
      plugin.register(api as never);

      const method = gatewayMethods.find((m) => m.name === "kalibr.status");
      expect(method).toBeDefined();
    });

    it("responds with status data including routing", () => {
      const { api, gatewayMethods } = createMockApi({
        apiKey: "test",
        defaultGoal: "my_goal",
        enableRouting: true,
        captureLlmTelemetry: true,
        captureOutcomes: false,
      });
      plugin.register(api as never);

      const method = gatewayMethods.find((m) => m.name === "kalibr.status")!;
      let responseData: unknown;
      method.handler({
        respond: (_success: boolean, data: unknown) => {
          responseData = data;
        },
      });

      expect(responseData).toMatchObject({
        enabled: true,
        goal: "my_goal",
        routing: true,
        telemetry: true,
        outcomes: false,
      });
    });
  });

  describe("CLI registration", () => {
    it("registers cli with kalibr command", () => {
      const { api, cliRegistrations } = createMockApi({ apiKey: "test" });
      plugin.register(api as never);

      expect(cliRegistrations).toHaveLength(1);
      expect(cliRegistrations[0].opts).toEqual({ commands: ["kalibr"] });
    });
  });
});
