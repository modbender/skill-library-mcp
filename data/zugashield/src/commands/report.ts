import type { ShieldClient } from "../shield-client.js";

/**
 * `/shield report` — Shows scan statistics and recent threat events.
 * Requires an active MCP connection.
 */
export function createReportCommand(client: ShieldClient) {
  return async (): Promise<{ text: string }> => {
    const lines: string[] = ["--- ZugaShield Report ---"];

    // Local stats
    lines.push(`Total scans: ${client.stats.scans}`);
    lines.push(`Blocks: ${client.stats.blocks}`);
    lines.push(`Errors: ${client.stats.errors}`);

    if (!client.connected) {
      lines.push("", "(Scanner disconnected — no remote data available)");
      return { text: lines.join("\n") };
    }

    // Remote threat report
    try {
      const report = await client.getThreatReport(10);

      if (report.dashboard) {
        const d = report.dashboard;
        lines.push("");
        lines.push("--- Engine Dashboard ---");
        if (d.audit && typeof d.audit === "object") {
          const audit = d.audit as Record<string, unknown>;
          if (audit.total_events !== undefined) lines.push(`Total events: ${audit.total_events}`);
          if (audit.blocked_count !== undefined) lines.push(`Blocked: ${audit.blocked_count}`);
        }
      }

      if (report.recent_events && report.recent_events.length > 0) {
        lines.push("");
        lines.push("--- Recent Threats ---");
        for (const event of report.recent_events.slice(0, 5)) {
          const e = event as Record<string, unknown>;
          lines.push(`  [${e.timestamp || "?"}] ${e.layer || "?"}: ${e.verdict || "?"} — ${e.description || ""}`);
        }
      }
    } catch {
      lines.push("", "(Could not fetch threat report from engine)");
    }

    return { text: lines.join("\n") };
  };
}
