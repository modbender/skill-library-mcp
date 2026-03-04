import { randomUUID } from "crypto";
import { RunStateManager } from "./src/state.js";
import { openClawToKalibr, kalibrToOpenClaw } from "./src/model-mapper.js";

// ── Plugin config shape ────────────────────────────────────

export interface KalibrConfig {
  apiKey: string;
  tenantId?: string;
  apiUrl?: string;
  defaultGoal?: string;
  enabled?: boolean;
  captureOutcomes?: boolean;
  captureLlmTelemetry?: boolean;
  enableRouting?: boolean;
}

// ── Minimal OpenClaw plugin SDK types ──────────────────────

interface PluginLogger {
  info(message: string): void;
  warn(message: string): void;
  error(message: string): void;
  debug?(message: string): void;
}

interface PluginHookAgentContext {
  agentId?: string;
  sessionKey?: string;
  sessionId?: string;
  workspaceDir?: string;
  messageProvider?: string;
}

interface PluginHookBeforeAgentStartEvent {
  prompt: string;
  messages?: unknown[];
}

interface PluginHookBeforeAgentStartResult {
  systemPrompt?: string;
  prependContext?: string;
  modelOverride?: string;
  providerOverride?: string;
}

interface PluginHookLlmInputEvent {
  runId: string;
  sessionId: string;
  provider: string;
  model: string;
  systemPrompt?: string;
  prompt: string;
  historyMessages: unknown[];
  imagesCount: number;
}

interface PluginHookLlmOutputEvent {
  runId: string;
  sessionId: string;
  provider: string;
  model: string;
  assistantTexts: string[];
  lastAssistant?: unknown;
  usage?: {
    input?: number;
    output?: number;
    cacheRead?: number;
    cacheWrite?: number;
    total?: number;
  };
}

interface PluginHookAgentEndEvent {
  messages: unknown[];
  success: boolean;
  error?: string;
  durationMs?: number;
}

interface PluginHookBeforeToolCallEvent {
  toolName: string;
  params: Record<string, unknown>;
}

interface PluginHookToolContext {
  agentId?: string;
  sessionKey?: string;
  toolName: string;
}

interface PluginHookBeforeToolCallResult {
  params?: Record<string, unknown>;
  block?: boolean;
  blockReason?: string;
}

interface CommandHandlerResult {
  text: string;
}

interface CommandContext {
  sessionKey?: string;
}

interface GatewayMethodContext {
  respond(success: boolean, data: unknown): void;
}

interface CliContext {
  program: {
    command(name: string): {
      description(desc: string): { action(fn: () => void): void };
      action(fn: () => void): void;
    };
  };
}

type VoidHookHandler = (event: unknown, ctx?: PluginHookAgentContext) => void | Promise<void>;
type BeforeAgentStartHandler = (
  event: PluginHookBeforeAgentStartEvent,
  ctx?: PluginHookAgentContext,
) => PluginHookBeforeAgentStartResult | Promise<PluginHookBeforeAgentStartResult>;
type BeforeToolCallHandler = (
  event: PluginHookBeforeToolCallEvent,
  ctx?: PluginHookToolContext,
) => PluginHookBeforeToolCallResult | Promise<PluginHookBeforeToolCallResult>;

interface OpenClawPluginApi {
  pluginConfig: unknown;
  logger: PluginLogger;
  on(
    hookName: "before_agent_start",
    handler: BeforeAgentStartHandler,
    opts?: { priority?: number },
  ): void;
  on(
    hookName: "before_tool_call",
    handler: BeforeToolCallHandler,
    opts?: { priority?: number },
  ): void;
  on(
    hookName: string,
    handler: VoidHookHandler,
    opts?: { priority?: number },
  ): void;
  registerCommand(opts: {
    name: string;
    description: string;
    handler: (ctx: CommandContext) => CommandHandlerResult;
  }): void;
  registerGatewayMethod(
    name: string,
    handler: (ctx: GatewayMethodContext) => void,
  ): void;
  registerCli(
    fn: (ctx: CliContext) => void,
    opts?: { commands: string[] },
  ): void;
}

// ── Kalibr SDK shim types ──────────────────────────────────

interface KalibrIntelligenceStatic {
  init(opts: { apiKey: string; tenantId?: string; baseUrl?: string }): void;
}

interface ReportOutcomeOptions {
  score?: number;
  failureReason?: string;
  metadata?: Record<string, unknown>;
  toolId?: string;
  executionParams?: Record<string, unknown>;
  modelId?: string;
}

interface OutcomeResponse {
  success: boolean;
  outcome_id?: string;
  message?: string;
}

type ReportOutcomeFn = (
  traceId: string,
  goal: string,
  success: boolean,
  options?: ReportOutcomeOptions,
) => Promise<OutcomeResponse>;

interface DecideResponse {
  path_id: string;
  model_id: string;
  tool_id?: string;
  params?: Record<string, unknown>;
  reason: string;
  confidence: number;
  exploration: boolean;
  success_rate?: number;
  sample_count?: number;
}

type DecideFn = (goal: string, options?: { taskRiskLevel?: string }) => Promise<DecideResponse>;

// ── Dynamic imports resolved at runtime ────────────────────

let _kalibrIntelligence: KalibrIntelligenceStatic | undefined;
let _reportOutcome: ReportOutcomeFn | undefined;
let _decide: DecideFn | undefined;

async function loadKalibrSdk(): Promise<{
  KalibrIntelligence: KalibrIntelligenceStatic;
  reportOutcome: ReportOutcomeFn;
  decide: DecideFn;
}> {
  if (_kalibrIntelligence && _reportOutcome && _decide) {
    return {
      KalibrIntelligence: _kalibrIntelligence,
      reportOutcome: _reportOutcome,
      decide: _decide,
    };
  }
  const sdk = await import("@kalibr/sdk");
  _kalibrIntelligence = sdk.KalibrIntelligence;
  _reportOutcome = sdk.reportOutcome;
  _decide = sdk.decide;
  return {
    KalibrIntelligence: _kalibrIntelligence!,
    reportOutcome: _reportOutcome!,
    decide: _decide!,
  };
}

// ── Plugin ─────────────────────────────────────────────────

const plugin = {
  id: "kalibr" as const,
  name: "Kalibr Intelligence" as const,
  configSchema: {},

  register(api: OpenClawPluginApi) {
    const cfg = api.pluginConfig as KalibrConfig;
    if (cfg?.enabled === false) return;

    const runs = new RunStateManager();
    const goal = cfg.defaultGoal || "openclaw_agent_run";
    let sdkReady = false;

    loadKalibrSdk()
      .then(({ KalibrIntelligence }) => {
        KalibrIntelligence.init({
          apiKey: cfg.apiKey,
          ...(cfg.tenantId && { tenantId: cfg.tenantId }),
          ...(cfg.apiUrl && { baseUrl: cfg.apiUrl }),
        });
        sdkReady = true;
        api.logger.info("[kalibr] SDK initialized");
      })
      .catch((err) => {
        api.logger.warn("[kalibr] SDK init deferred: " + String(err));
      });

    // ── Routing hook (modifying — sequential, merged) ─────

    if (cfg.enableRouting === true) {
      api.on("before_agent_start", async (
        event: PluginHookBeforeAgentStartEvent,
        ctx?: PluginHookAgentContext,
      ): Promise<PluginHookBeforeAgentStartResult> => {
        if (!sdkReady) return {};

        try {
          const { decide } = await loadKalibrSdk();
          const decision = await decide(goal);

          const sessionKey = ctx?.sessionKey;
          if (sessionKey) {
            runs.setLastDecision(sessionKey, {
              tool_id: decision.tool_id,
              params: decision.params,
            });
          }

          const mapping = kalibrToOpenClaw(decision.model_id);

          if (!mapping) {
            api.logger.warn(
              "[kalibr] decide() returned unknown model_id: " + decision.model_id
            );
            return {};
          }

          api.logger.info(
            "[kalibr] Routing to " + mapping.provider + "/" + mapping.model
            + " (confidence: " + decision.confidence
            + ", exploration: " + decision.exploration + ")"
          );

          return {
            modelOverride: mapping.model,
            providerOverride: mapping.provider,
          };
        } catch (err) {
          api.logger.error("[kalibr] decide() failed, using default model: " + String(err));
          return {};
        }
      });
    }

    // ── Tool call hook (modifying — param injection + telemetry) ─────

    if (cfg.enableRouting === true || cfg.captureLlmTelemetry !== false) {
      api.on("before_tool_call", async (
        event: PluginHookBeforeToolCallEvent,
        ctx?: PluginHookToolContext,
      ): Promise<PluginHookBeforeToolCallResult> => {
        try {
          const sessionKey = ctx?.sessionKey;
          if (!sessionKey) return {};

          runs.recordToolCall(sessionKey, event.toolName);

          if (cfg.enableRouting !== true) return {};

          const decision = runs.getLastDecision(sessionKey);
          if (!decision || !decision.params || Object.keys(decision.params).length === 0) {
            return {};
          }

          if (decision.tool_id && decision.tool_id !== event.toolName) {
            api.logger.info(
              "[kalibr] Decision tool_id (" + decision.tool_id
              + ") differs from current tool (" + event.toolName + "), proceeding anyway"
            );
          }

          api.logger.info(
            "[kalibr] Injecting params for tool " + event.toolName + ": "
            + JSON.stringify(decision.params)
          );

          const merged = { ...event.params, ...decision.params };
          return { params: merged };
        } catch {
          return {};
        }
      });
    }

    // ── Telemetry hooks (void — fire-and-forget, parallel) ─────

    if (cfg.captureLlmTelemetry !== false) {
      api.on("llm_input", async (event: unknown, ctx?: PluginHookAgentContext) => {
        const e = event as PluginHookLlmInputEvent;
        const sessionKey = ctx?.sessionKey;
        if (!sessionKey) return;

        runs.recordLlmInput(sessionKey, {
          runId: e.runId,
          provider: e.provider,
          model: e.model,
          timestamp: Date.now(),
        });
      });

      api.on("llm_output", async (event: unknown, ctx?: PluginHookAgentContext) => {
        const e = event as PluginHookLlmOutputEvent;
        const sessionKey = ctx?.sessionKey;
        if (!sessionKey) return;

        runs.recordLlmOutput(sessionKey, {
          runId: e.runId,
          provider: e.provider,
          model: e.model,
          inputTokens: e.usage?.input ?? 0,
          outputTokens: e.usage?.output ?? 0,
          cacheReadTokens: e.usage?.cacheRead ?? 0,
          cacheWriteTokens: e.usage?.cacheWrite ?? 0,
          totalTokens: e.usage?.total ?? 0,
          timestamp: Date.now(),
        });
      });
    }

    // ── Outcome reporting (void — fire-and-forget) ─────

    if (cfg.captureOutcomes !== false) {
      api.on("agent_end", async (event: unknown, ctx?: PluginHookAgentContext) => {
        const e = event as PluginHookAgentEndEvent;
        const sessionKey = ctx?.sessionKey;
        if (!sessionKey) return;

        const runData = runs.getAndClear(sessionKey);
        if (!runData) return;

        try {
          const { reportOutcome } = await loadKalibrSdk();
          await reportOutcome(
            runData.traceId,
            goal,
            e.success,
            {
              modelId: runData.primaryModel
                ? openClawToKalibr(runData.primaryModel)
                : undefined,
              toolId: runData.toolsCalled.length > 0
                ? runData.toolsCalled[0]
                : undefined,
              metadata: {
                provider: runData.primaryProvider,
                agentId: ctx?.agentId,
                sessionKey,
                durationMs: e.durationMs,
                llmCalls: runData.llmCallCount,
                totalInputTokens: runData.totalInputTokens,
                totalOutputTokens: runData.totalOutputTokens,
                totalTokens: runData.totalTokens,
                cacheReadTokens: runData.totalCacheReadTokens,
                cacheWriteTokens: runData.totalCacheWriteTokens,
                toolsCalled: runData.toolsCalled,
                toolCallCount: runData.toolsCalled.length,
              },
              ...(e.error && { failureReason: e.error }),
            },
          );
        } catch (err) {
          api.logger.error("[kalibr] Outcome report failed: " + String(err));
        }
      });
    }

    // ── Slash Command ──────────────────────────────────────

    api.registerCommand({
      name: "kalibr",
      description: "Show Kalibr plugin status",
      handler: (_ctx) => ({
        text: [
          "Kalibr: active",
          "Goal: " + goal,
          "Routing: " + (cfg.enableRouting === true ? "on" : "off"),
          "Param injection: " + (cfg.enableRouting === true ? "on" : "off"),
          "Telemetry: " + (cfg.captureLlmTelemetry !== false ? "on" : "off"),
          "Outcomes: " + (cfg.captureOutcomes !== false ? "on" : "off"),
        ].join("\n"),
      }),
    });

    // ── Gateway RPC ────────────────────────────────────────

    api.registerGatewayMethod("kalibr.status", ({ respond }) => {
      respond(true, {
        enabled: true,
        goal,
        routing: cfg.enableRouting === true,
        paramInjection: cfg.enableRouting === true,
        sdkReady,
        telemetry: cfg.captureLlmTelemetry !== false,
        outcomes: cfg.captureOutcomes !== false,
      });
    });

    // ── CLI ────────────────────────────────────────────────

    api.registerCli(
      ({ program }) => {
        program.command("kalibr").action(() => {
          console.log("Kalibr: active");
          console.log("Goal: " + goal);
          console.log("Routing: " + (cfg.enableRouting === true ? "on" : "off"));
          console.log("Param injection: " + (cfg.enableRouting === true ? "on" : "off"));
          console.log("Telemetry: " + (cfg.captureLlmTelemetry !== false ? "on" : "off"));
          console.log("Outcomes: " + (cfg.captureOutcomes !== false ? "on" : "off"));
        });
      },
      { commands: ["kalibr"] },
    );

    api.logger.info("[kalibr] Plugin registered");
  },
};

export default plugin;

// Named exports for testing
export { RunStateManager } from "./src/state.js";
export { openClawToKalibr, kalibrToOpenClaw } from "./src/model-mapper.js";
