import type { ShieldClient } from "../shield-client.js";
import type { PluginConfig } from "../config.js";
import type { PreflightResult } from "../preflight.js";

/**
 * `/shield status` — Shows connection state, version, and enabled layers.
 * Works even when the MCP server is down (shows disconnected state).
 */
export function createStatusCommand(
  client: ShieldClient | null,
  config: PluginConfig,
  preflight: PreflightResult,
) {
  return async (): Promise<{ text: string }> => {
    const lines: string[] = ["--- ZugaShield Status ---"];

    // Preflight
    if (!preflight.ok) {
      lines.push(`Preflight: FAILED`);
      for (const err of preflight.errors) lines.push(`  - ${err}`);
      lines.push("", "Hooks are NOT registered. Fix the above and restart.");
      return { text: lines.join("\n") };
    }

    lines.push(`Python: ${preflight.pythonVersion}`);

    // Connection
    if (!client) {
      lines.push("Scanner: NOT INITIALIZED");
      return { text: lines.join("\n") };
    }

    lines.push(`Scanner: ${client.connected ? "CONNECTED" : "DISCONNECTED"}`);

    // Config summary
    lines.push(`Fail-closed: ${config.fail_closed}`);
    lines.push(`Strict mode: ${config.strict_mode}`);
    lines.push(
      `Scanning: inputs=${config.scan.inputs} outputs=${config.scan.outputs} ` +
      `tools=${config.scan.tool_calls} memory=${config.scan.memory}`,
    );

    if (config.excluded_channels.length > 0) {
      lines.push(`Excluded channels: ${config.excluded_channels.join(", ")}`);
    }

    // Live config from the MCP server
    if (client.connected) {
      try {
        const remote = await client.getConfig();
        lines.push("");
        lines.push("--- ZugaShield Engine ---");
        if (remote.version) lines.push(`Version: ${remote.version}`);
        if (remote.enabled !== undefined) lines.push(`Enabled: ${remote.enabled}`);
        if (remote.strict_mode !== undefined) lines.push(`Engine strict: ${remote.strict_mode}`);
      } catch {
        lines.push("(Could not fetch engine config)");
      }
    }

    return { text: lines.join("\n") };
  };
}

/** Stub command shown when preflight fails. */
export function createStubStatusCommand(preflight: PreflightResult) {
  return (): { text: string } => {
    const lines = [
      "--- ZugaShield Status ---",
      "Status: NOT ACTIVE (preflight failed)",
      "",
    ];
    for (const err of preflight.errors) lines.push(`  - ${err}`);
    lines.push(
      "",
      "No security hooks are registered.",
      'Install: pip install "zugashield[mcp]"',
      "Then restart OpenClaw.",
    );
    return { text: lines.join("\n") };
  };
}
