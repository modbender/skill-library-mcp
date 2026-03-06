import { resolveConfig, type PluginConfig } from "./config.js";
import { runPreflight, type PreflightResult } from "./preflight.js";
import { ShieldClient } from "./shield-client.js";
import { createPreRequestHook } from "./hooks/pre-request.js";
import { createPreToolExecHook } from "./hooks/pre-tool-exec.js";
import { createPreResponseHook } from "./hooks/pre-response.js";
import { createPreRecallHook } from "./hooks/pre-recall.js";
import { createStatusCommand, createStubStatusCommand } from "./commands/status.js";
import { createReportCommand } from "./commands/report.js";

/**
 * OpenClaw Plugin API interface — the subset we use.
 * Matches the api object passed to register(api) by OpenClaw.
 */
interface OpenClawApi {
  pluginConfig?: Partial<PluginConfig>;
  logger: {
    info(msg: string, ...args: unknown[]): void;
    warn(msg: string, ...args: unknown[]): void;
    error(msg: string, ...args: unknown[]): void;
    debug(msg: string, ...args: unknown[]): void;
  };
  registerService(opts: {
    id: string;
    start: () => Promise<void>;
    stop: () => Promise<void>;
  }): void;
  registerHook(
    phase: string,
    handler: (ctx: any) => Promise<void> | void,
    options?: { priority?: number; timeoutMs?: number; criticality?: string },
  ): void;
  registerCommand(opts: {
    name: string;
    description: string;
    acceptsArgs?: boolean;
    handler: (ctx: any) => { text: string } | Promise<{ text: string }>;
  }): void;
}

/**
 * ZugaShield OpenClaw Plugin Entry Point.
 *
 * Flow:
 * 1. Merge user config with defaults
 * 2. Run preflight (Python + zugashield_mcp check)
 * 3. If preflight fails → register stub /shield command only (no false security)
 * 4. If preflight passes → create ShieldClient, register service + 4 hooks + commands
 *
 * The plugin hooks into OpenClaw's Gateway lifecycle so all channels
 * (Signal, Telegram, Discord, WhatsApp, web) are protected by one plugin.
 */
export default function register(api: OpenClawApi): void {
  const config = resolveConfig(api.pluginConfig);
  const logger = api.logger;

  // Preflight is async, but register() is sync in OpenClaw's plugin loader.
  // We run preflight eagerly and defer hook registration to after it resolves.
  runPreflight(config.mcp.python_executable).then((preflight) => {
    if (!preflight.ok) {
      registerStubOnly(api, preflight);
      return;
    }
    registerFull(api, config, preflight, logger);
  }).catch((err) => {
    logger.error("ZugaShield: preflight crashed:", (err as Error).message);
    registerStubOnly(api, {
      ok: false,
      python: false,
      pythonVersion: "",
      zugashieldMcp: false,
      errors: [`Preflight error: ${(err as Error).message}`],
    });
  });
}

function registerStubOnly(api: OpenClawApi, preflight: PreflightResult): void {
  api.logger.warn("ZugaShield: preflight failed — no security hooks registered");
  for (const err of preflight.errors) {
    api.logger.warn(`  - ${err}`);
  }

  api.registerCommand({
    name: "shield",
    description: "ZugaShield security scanner status",
    acceptsArgs: true,
    handler: createStubStatusCommand(preflight),
  });
}

function registerFull(
  api: OpenClawApi,
  config: PluginConfig,
  preflight: PreflightResult,
  logger: typeof api.logger,
): void {
  const client = new ShieldClient(config, logger);

  // ─── Managed service: OpenClaw starts/stops the MCP process ───
  api.registerService({
    id: "zugashield-mcp",
    start: () => client.start(),
    stop: () => client.stop(),
  });

  // ─── Security hooks (priority 100 = run early, before other plugins) ───

  // Hook timeout must exceed the MCP call timeout to avoid false positives.
  // We add 50ms headroom above the configured call_timeout_ms.
  const hookTimeout = config.mcp.call_timeout_ms + 50;

  if (config.scan.inputs) {
    api.registerHook(
      "preRequest",
      createPreRequestHook(client, config),
      { priority: 100, timeoutMs: hookTimeout, criticality: "required" },
    );
  }

  if (config.scan.tool_calls) {
    api.registerHook(
      "preToolExecution",
      createPreToolExecHook(client, config),
      { priority: 100, timeoutMs: hookTimeout, criticality: "required" },
    );
  }

  if (config.scan.outputs) {
    api.registerHook(
      "preResponse",
      createPreResponseHook(client, config),
      { priority: 100, timeoutMs: hookTimeout, criticality: "required" },
    );
  }

  if (config.scan.memory) {
    api.registerHook(
      "preRecall",
      createPreRecallHook(client, config),
      { priority: 100, timeoutMs: hookTimeout, criticality: "required" },
    );
  }

  // ─── Commands ─────────────────────────────────────────────

  api.registerCommand({
    name: "shield",
    description: "ZugaShield security scanner",
    acceptsArgs: true,
    handler: async (ctx: { args?: string }) => {
      const sub = ctx.args?.trim().split(/\s+/)[0] || "status";

      switch (sub) {
        case "status":
          return createStatusCommand(client, config, preflight)();
        case "report":
          return createReportCommand(client)();
        default:
          return {
            text: [
              "Usage: /shield <command>",
              "",
              "Commands:",
              "  status  — Connection state, version, enabled layers",
              "  report  — Scan stats and recent threats",
            ].join("\n"),
          };
      }
    },
  });

  logger.info(
    `ZugaShield: registered ${countHooks(config)} hooks + /shield command`,
  );
}

function countHooks(config: PluginConfig): number {
  let n = 0;
  if (config.scan.inputs) n++;
  if (config.scan.tool_calls) n++;
  if (config.scan.outputs) n++;
  if (config.scan.memory) n++;
  return n;
}
