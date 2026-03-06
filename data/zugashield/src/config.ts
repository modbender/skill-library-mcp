import { Type, type Static } from "@sinclair/typebox";

/**
 * TypeBox schema for the plugin's configuration in openclaw.json.
 * Validated automatically by OpenClaw's config loader.
 */
export const ConfigSchema = Type.Object({
  fail_closed: Type.Boolean({ default: true }),
  strict_mode: Type.Boolean({ default: false }),
  scan: Type.Object({
    inputs: Type.Boolean({ default: true }),
    outputs: Type.Boolean({ default: true }),
    tool_calls: Type.Boolean({ default: true }),
    memory: Type.Boolean({ default: true }),
  }, { default: {} }),
  excluded_channels: Type.Array(Type.String(), { default: [] }),
  mcp: Type.Object({
    python_executable: Type.String({ default: "python" }),
    call_timeout_ms: Type.Number({ default: 80, minimum: 10, maximum: 5000 }),
    startup_timeout_ms: Type.Number({ default: 8000, minimum: 1000, maximum: 30000 }),
    max_reconnect_attempts: Type.Integer({ default: 10, minimum: 0, maximum: 100 }),
  }, { default: {} }),
});

export type PluginConfig = Static<typeof ConfigSchema>;

/** Fully-resolved defaults used when the user provides no config at all. */
export const DEFAULT_CONFIG: PluginConfig = {
  fail_closed: true,
  strict_mode: false,
  scan: { inputs: true, outputs: true, tool_calls: true, memory: true },
  excluded_channels: [],
  mcp: {
    python_executable: "python",
    call_timeout_ms: 80,
    startup_timeout_ms: 8000,
    max_reconnect_attempts: 10,
  },
};

/** Deep-merge user config onto defaults. Handles partial/missing sections. */
export function resolveConfig(raw?: Partial<PluginConfig>): PluginConfig {
  if (!raw) return { ...DEFAULT_CONFIG };
  return {
    fail_closed: raw.fail_closed ?? DEFAULT_CONFIG.fail_closed,
    strict_mode: raw.strict_mode ?? DEFAULT_CONFIG.strict_mode,
    scan: {
      inputs: raw.scan?.inputs ?? DEFAULT_CONFIG.scan.inputs,
      outputs: raw.scan?.outputs ?? DEFAULT_CONFIG.scan.outputs,
      tool_calls: raw.scan?.tool_calls ?? DEFAULT_CONFIG.scan.tool_calls,
      memory: raw.scan?.memory ?? DEFAULT_CONFIG.scan.memory,
    },
    excluded_channels: raw.excluded_channels ?? DEFAULT_CONFIG.excluded_channels,
    mcp: {
      python_executable: raw.mcp?.python_executable ?? DEFAULT_CONFIG.mcp.python_executable,
      call_timeout_ms: raw.mcp?.call_timeout_ms ?? DEFAULT_CONFIG.mcp.call_timeout_ms,
      startup_timeout_ms: raw.mcp?.startup_timeout_ms ?? DEFAULT_CONFIG.mcp.startup_timeout_ms,
      max_reconnect_attempts: raw.mcp?.max_reconnect_attempts ?? DEFAULT_CONFIG.mcp.max_reconnect_attempts,
    },
  };
}
