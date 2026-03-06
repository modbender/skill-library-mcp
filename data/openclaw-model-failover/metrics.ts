/**
 * Usage metrics and cooldown history.
 *
 * Provides an append-only JSONL event log for failover events and
 * aggregate summary functions for capacity planning and model order optimization.
 *
 * Standalone CLI usage:
 *   npx tsx metrics.ts                    # pretty-print metrics summary
 *   npx tsx metrics.ts --json             # machine-readable JSON summary
 *   npx tsx metrics.ts tail [N]           # show last N events (default 20)
 *   npx tsx metrics.ts history <model>    # show cooldown history for a model
 *   npx tsx metrics.ts reset              # clear all metrics
 *
 * Programmatic usage:
 *   import { recordEvent, loadEvents, getMetricsSummary, getModelHistory, formatMetrics } from "./metrics.js";
 */

import fs from "node:fs";
import path from "node:path";

import { expandHome, nowSec } from "./index.js";

// -------------------------------------------------------------------------
// Types
// -------------------------------------------------------------------------

export type MetricEventType = "rate_limit" | "auth_error" | "unavailable" | "failover";

export interface MetricEvent {
  ts: number;
  type: MetricEventType;
  model: string;
  provider: string;
  reason?: string;
  cooldownSec?: number;
  /** For failover events: the model we switched to. */
  to?: string;
  /** Hook that triggered the event (agent_end | message_sent). */
  trigger?: string;
  session?: string;
}

export interface ModelMetrics {
  rateLimits: number;
  authErrors: number;
  unavailableErrors: number;
  timesFailedFrom: number;
  timesFailedTo: number;
  lastHitAt?: number;
  totalCooldownSec: number;
  cooldownCount: number;
  avgCooldownSec: number;
}

export interface ProviderMetrics {
  rateLimits: number;
  authErrors: number;
  unavailableErrors: number;
  totalCooldownSec: number;
  cooldownCount: number;
  avgCooldownSec: number;
}

export interface MetricsSummary {
  since: number | undefined;
  until: number;
  totalEvents: number;
  totalRateLimits: number;
  totalAuthErrors: number;
  totalUnavailable: number;
  totalFailovers: number;
  avgCooldownSec: number;
  recentCooldowns: CooldownEntry[];
  models: Record<string, ModelMetrics>;
  providers: Record<string, ProviderMetrics>;
}

export interface CooldownEntry {
  startedAt: number;
  durationSec: number;
  type: MetricEventType;
  reason?: string;
  trigger?: string;
  session?: string;
}

export interface ModelHistory {
  model: string;
  events: MetricEvent[];
  cooldowns: CooldownEntry[];
  totalErrors: number;
  totalCooldownSec: number;
  avgCooldownSec: number;
  maxCooldownSec: number;
  firstSeen?: number;
  lastSeen?: number;
  failedToModels: Record<string, number>;
  receivedFromModels: Record<string, number>;
}

// -------------------------------------------------------------------------
// Default path
// -------------------------------------------------------------------------

export const DEFAULT_METRICS_FILE = "~/.openclaw/workspace/memory/model-failover-metrics.jsonl";

// -------------------------------------------------------------------------
// Event recording
// -------------------------------------------------------------------------

/**
 * Append a single metric event to the JSONL log file.
 * Creates the file and parent directories if they do not exist.
 */
export function recordEvent(metricsPath: string, event: MetricEvent): void {
  const resolved = expandHome(metricsPath);
  fs.mkdirSync(path.dirname(resolved), { recursive: true });
  const line = JSON.stringify(event) + "\n";
  fs.appendFileSync(resolved, line, "utf-8");
}

// -------------------------------------------------------------------------
// Event loading
// -------------------------------------------------------------------------

/**
 * Read and parse all events from the JSONL log file.
 * Returns an empty array if the file does not exist or is corrupt.
 * Malformed lines are silently skipped.
 */
export function loadEvents(metricsPath: string): MetricEvent[] {
  const resolved = expandHome(metricsPath);
  let raw: string;
  try {
    raw = fs.readFileSync(resolved, "utf-8");
  } catch {
    return [];
  }

  const events: MetricEvent[] = [];
  for (const line of raw.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    try {
      events.push(JSON.parse(trimmed) as MetricEvent);
    } catch {
      // skip malformed lines
    }
  }
  return events;
}

// -------------------------------------------------------------------------
// Aggregation
// -------------------------------------------------------------------------

function emptyModelMetrics(): ModelMetrics {
  return {
    rateLimits: 0,
    authErrors: 0,
    unavailableErrors: 0,
    timesFailedFrom: 0,
    timesFailedTo: 0,
    totalCooldownSec: 0,
    cooldownCount: 0,
    avgCooldownSec: 0,
  };
}

function emptyProviderMetrics(): ProviderMetrics {
  return {
    rateLimits: 0,
    authErrors: 0,
    unavailableErrors: 0,
    totalCooldownSec: 0,
    cooldownCount: 0,
    avgCooldownSec: 0,
  };
}

/**
 * Build an aggregate summary from the event log.
 * Optionally filter to events within a time window.
 */
export function getMetricsSummary(opts?: {
  metricsPath?: string;
  since?: number;
  until?: number;
  /** Maximum number of recent cooldown entries to include (default 50). */
  maxRecentCooldowns?: number;
}): MetricsSummary {
  const metricsPath = opts?.metricsPath ?? DEFAULT_METRICS_FILE;
  const allEvents = loadEvents(metricsPath);
  const sinceFilter = opts?.since ?? 0;
  const untilFilter = opts?.until ?? Infinity;

  const events = allEvents.filter(
    (e) => e.ts >= sinceFilter && e.ts <= untilFilter,
  );

  const maxRecentCooldowns = opts?.maxRecentCooldowns ?? 50;

  const models: Record<string, ModelMetrics> = {};
  const providers: Record<string, ProviderMetrics> = {};
  const allCooldowns: CooldownEntry[] = [];

  let totalRateLimits = 0;
  let totalAuthErrors = 0;
  let totalUnavailable = 0;
  let totalFailovers = 0;
  let totalCooldownSec = 0;
  let totalCooldownCount = 0;
  let earliest: number | undefined;

  for (const e of events) {
    if (earliest === undefined || e.ts < earliest) earliest = e.ts;

    // Ensure model and provider buckets exist
    if (!models[e.model]) models[e.model] = emptyModelMetrics();
    if (!providers[e.provider]) providers[e.provider] = emptyProviderMetrics();

    const m = models[e.model];
    const p = providers[e.provider];

    switch (e.type) {
      case "rate_limit":
        totalRateLimits++;
        m.rateLimits++;
        p.rateLimits++;
        m.lastHitAt = e.ts;
        if (e.cooldownSec) {
          m.totalCooldownSec += e.cooldownSec;
          m.cooldownCount++;
          p.totalCooldownSec += e.cooldownSec;
          p.cooldownCount++;
          totalCooldownSec += e.cooldownSec;
          totalCooldownCount++;
          allCooldowns.push({
            startedAt: e.ts,
            durationSec: e.cooldownSec,
            type: e.type,
            reason: e.reason,
            trigger: e.trigger,
            session: e.session,
          });
        }
        break;
      case "auth_error":
        totalAuthErrors++;
        m.authErrors++;
        p.authErrors++;
        m.lastHitAt = e.ts;
        if (e.cooldownSec) {
          m.totalCooldownSec += e.cooldownSec;
          m.cooldownCount++;
          p.totalCooldownSec += e.cooldownSec;
          p.cooldownCount++;
          totalCooldownSec += e.cooldownSec;
          totalCooldownCount++;
          allCooldowns.push({
            startedAt: e.ts,
            durationSec: e.cooldownSec,
            type: e.type,
            reason: e.reason,
            trigger: e.trigger,
            session: e.session,
          });
        }
        break;
      case "unavailable":
        totalUnavailable++;
        m.unavailableErrors++;
        p.unavailableErrors++;
        m.lastHitAt = e.ts;
        if (e.cooldownSec) {
          m.totalCooldownSec += e.cooldownSec;
          m.cooldownCount++;
          p.totalCooldownSec += e.cooldownSec;
          p.cooldownCount++;
          totalCooldownSec += e.cooldownSec;
          totalCooldownCount++;
          allCooldowns.push({
            startedAt: e.ts,
            durationSec: e.cooldownSec,
            type: e.type,
            reason: e.reason,
            trigger: e.trigger,
            session: e.session,
          });
        }
        break;
      case "failover":
        totalFailovers++;
        m.timesFailedFrom++;
        if (e.to) {
          if (!models[e.to]) models[e.to] = emptyModelMetrics();
          models[e.to].timesFailedTo++;
        }
        break;
    }
  }

  // Compute per-model and per-provider average cooldown duration
  for (const m of Object.values(models)) {
    if (m.cooldownCount > 0) {
      m.avgCooldownSec = Math.round(m.totalCooldownSec / m.cooldownCount);
    }
  }
  for (const p of Object.values(providers)) {
    if (p.cooldownCount > 0) {
      p.avgCooldownSec = Math.round(p.totalCooldownSec / p.cooldownCount);
    }
  }

  // Keep last N cooldown entries for the recent history
  const recentCooldowns = allCooldowns.slice(-maxRecentCooldowns);

  return {
    since: earliest,
    until: events.length > 0 ? events[events.length - 1].ts : nowSec(),
    totalEvents: events.length,
    totalRateLimits,
    totalAuthErrors,
    totalUnavailable,
    totalFailovers,
    avgCooldownSec: totalCooldownCount > 0
      ? Math.round(totalCooldownSec / totalCooldownCount)
      : 0,
    recentCooldowns,
    models,
    providers,
  };
}

// -------------------------------------------------------------------------
// Per-model history
// -------------------------------------------------------------------------

/**
 * Build a detailed history for a single model including all cooldown entries.
 * Returns events where the model is the primary subject (not just a failover target),
 * plus a structured cooldown timeline.
 */
export function getModelHistory(opts: {
  model: string;
  metricsPath?: string;
  since?: number;
  until?: number;
}): ModelHistory {
  const metricsPath = opts.metricsPath ?? DEFAULT_METRICS_FILE;
  const allEvents = loadEvents(metricsPath);
  const sinceFilter = opts.since ?? 0;
  const untilFilter = opts.until ?? Infinity;

  const filtered = allEvents.filter(
    (e) => e.ts >= sinceFilter && e.ts <= untilFilter,
  );

  // Events where this model is the primary subject
  const modelEvents = filtered.filter((e) => e.model === opts.model);
  // Failover events where this model was the target
  const receivedFailovers = filtered.filter(
    (e) => e.type === "failover" && e.to === opts.model,
  );

  const cooldowns: CooldownEntry[] = [];
  let totalCooldownSec = 0;
  let maxCooldownSec = 0;
  let totalErrors = 0;
  let firstSeen: number | undefined;
  let lastSeen: number | undefined;
  const failedToModels: Record<string, number> = {};
  const receivedFromModels: Record<string, number> = {};

  for (const e of modelEvents) {
    if (firstSeen === undefined || e.ts < firstSeen) firstSeen = e.ts;
    if (lastSeen === undefined || e.ts > lastSeen) lastSeen = e.ts;

    if (e.type === "rate_limit" || e.type === "auth_error" || e.type === "unavailable") {
      totalErrors++;
      const dur = e.cooldownSec ?? 0;
      if (dur > 0) {
        cooldowns.push({
          startedAt: e.ts,
          durationSec: dur,
          type: e.type,
          reason: e.reason,
          trigger: e.trigger,
          session: e.session,
        });
        totalCooldownSec += dur;
        if (dur > maxCooldownSec) maxCooldownSec = dur;
      }
    }

    if (e.type === "failover" && e.to) {
      failedToModels[e.to] = (failedToModels[e.to] ?? 0) + 1;
    }
  }

  for (const e of receivedFailovers) {
    if (firstSeen === undefined || e.ts < firstSeen) firstSeen = e.ts;
    if (lastSeen === undefined || e.ts > lastSeen) lastSeen = e.ts;
    receivedFromModels[e.model] = (receivedFromModels[e.model] ?? 0) + 1;
  }

  const avgCooldownSec = cooldowns.length > 0
    ? Math.round(totalCooldownSec / cooldowns.length)
    : 0;

  return {
    model: opts.model,
    events: modelEvents,
    cooldowns,
    totalErrors,
    totalCooldownSec,
    avgCooldownSec,
    maxCooldownSec,
    firstSeen,
    lastSeen,
    failedToModels,
    receivedFromModels,
  };
}

// -------------------------------------------------------------------------
// Convenience: record a rate-limit detection
// -------------------------------------------------------------------------

/**
 * Record a rate-limit event with all required fields.
 * This is a convenience wrapper around recordEvent for use when a rate limit
 * is detected in the failover plugin.
 */
export function recordRateLimit(
  metricsPath: string,
  opts: {
    model: string;
    provider: string;
    cooldownSec: number;
    reason?: string;
    trigger?: string;
    session?: string;
  },
): void {
  recordEvent(metricsPath, {
    ts: nowSec(),
    type: "rate_limit",
    model: opts.model,
    provider: opts.provider,
    cooldownSec: opts.cooldownSec,
    reason: opts.reason,
    trigger: opts.trigger,
    session: opts.session,
  });
}

// -------------------------------------------------------------------------
// Query: unified metrics query for /failover-status command
// -------------------------------------------------------------------------

export interface MetricsQueryResult {
  summary: MetricsSummary;
  modelHistories: Record<string, ModelHistory>;
}

/**
 * Query metrics for the /failover-status command.
 * Returns both the aggregate summary and per-model histories for all models
 * that have recorded events.
 */
export function queryMetrics(opts?: {
  metricsPath?: string;
  since?: number;
  until?: number;
  maxRecentCooldowns?: number;
}): MetricsQueryResult {
  const metricsPath = opts?.metricsPath ?? DEFAULT_METRICS_FILE;
  const summary = getMetricsSummary({
    metricsPath,
    since: opts?.since,
    until: opts?.until,
    maxRecentCooldowns: opts?.maxRecentCooldowns,
  });

  const modelHistories: Record<string, ModelHistory> = {};
  for (const model of Object.keys(summary.models)) {
    modelHistories[model] = getModelHistory({
      model,
      metricsPath,
      since: opts?.since,
      until: opts?.until,
    });
  }

  return { summary, modelHistories };
}

// -------------------------------------------------------------------------
// Reset
// -------------------------------------------------------------------------

/**
 * Delete the metrics log file. Returns true if the file existed.
 */
export function resetMetrics(metricsPath?: string): boolean {
  const resolved = expandHome(metricsPath ?? DEFAULT_METRICS_FILE);
  try {
    fs.unlinkSync(resolved);
    return true;
  } catch {
    return false;
  }
}

// -------------------------------------------------------------------------
// Formatting
// -------------------------------------------------------------------------

function pad(s: string, n: number): string {
  return s.length >= n ? s : s + " ".repeat(n - s.length);
}

/**
 * Pretty-print a MetricsSummary for terminal output.
 */
export function formatMetrics(summary: MetricsSummary): string {
  const lines: string[] = [];

  lines.push("=== OpenClaw Model Failover Metrics ===");
  lines.push("");

  if (summary.totalEvents === 0) {
    lines.push("No failover events recorded yet.");
    return lines.join("\n");
  }

  const sinceStr = summary.since
    ? new Date(summary.since * 1000).toISOString()
    : "n/a";
  const untilStr = new Date(summary.until * 1000).toISOString();

  lines.push(`Period       : ${sinceStr} - ${untilStr}`);
  lines.push(`Total events : ${summary.totalEvents}`);
  lines.push(`Rate limits  : ${summary.totalRateLimits}`);
  lines.push(`Auth errors  : ${summary.totalAuthErrors}`);
  lines.push(`Unavailable  : ${summary.totalUnavailable}`);
  lines.push(`Failovers    : ${summary.totalFailovers}`);

  // Provider breakdown
  const providerNames = Object.keys(summary.providers).sort();
  if (providerNames.length > 0) {
    lines.push("");
    lines.push("By provider:");
    for (const name of providerNames) {
      const p = summary.providers[name];
      const total = p.rateLimits + p.authErrors + p.unavailableErrors;
      lines.push(
        `  ${pad(name, 30)} ${total} error${total !== 1 ? "s" : ""}  (rate=${p.rateLimits} auth=${p.authErrors} unavail=${p.unavailableErrors})`,
      );
    }
  }

  // Model breakdown
  const modelNames = Object.keys(summary.models).sort();
  if (modelNames.length > 0) {
    lines.push("");
    lines.push("By model:");
    for (const name of modelNames) {
      const m = summary.models[name];
      const errors = m.rateLimits + m.authErrors + m.unavailableErrors;
      const parts: string[] = [];
      if (errors > 0) parts.push(`${errors} error${errors !== 1 ? "s" : ""}`);
      if (m.timesFailedFrom > 0) parts.push(`failed-from=${m.timesFailedFrom}`);
      if (m.timesFailedTo > 0) parts.push(`failed-to=${m.timesFailedTo}`);
      lines.push(`  ${pad(name, 40)} ${parts.join("  ")}`);
    }
  }

  return lines.join("\n");
}

/**
 * Format a list of events for terminal output (tail view).
 */
export function formatEvents(events: MetricEvent[]): string {
  if (events.length === 0) return "No events.";

  const lines: string[] = [];
  for (const e of events) {
    const ts = new Date(e.ts * 1000).toISOString().replace("T", " ").slice(0, 19);
    const parts = [`[${ts}]`, e.type.toUpperCase()];
    parts.push(e.model);
    if (e.type === "failover" && e.to) parts.push(`-> ${e.to}`);
    if (e.reason) parts.push(`(${e.reason.slice(0, 80)})`);
    if (e.cooldownSec) parts.push(`cooldown=${e.cooldownSec}s`);
    lines.push(parts.join(" "));
  }
  return lines.join("\n");
}

/**
 * Pretty-print a ModelHistory for terminal output.
 */
export function formatModelHistory(history: ModelHistory): string {
  const lines: string[] = [];

  lines.push(`=== Cooldown History: ${history.model} ===`);
  lines.push("");

  if (history.events.length === 0 && Object.keys(history.receivedFromModels).length === 0) {
    lines.push("No events recorded for this model.");
    return lines.join("\n");
  }

  if (history.firstSeen) {
    lines.push(`First seen   : ${new Date(history.firstSeen * 1000).toISOString()}`);
  }
  if (history.lastSeen) {
    lines.push(`Last seen    : ${new Date(history.lastSeen * 1000).toISOString()}`);
  }
  lines.push(`Total errors : ${history.totalErrors}`);
  lines.push(`Cooldowns    : ${history.cooldowns.length}`);

  if (history.cooldowns.length > 0) {
    lines.push(`Avg cooldown : ${formatDurationCompact(history.avgCooldownSec)}`);
    lines.push(`Max cooldown : ${formatDurationCompact(history.maxCooldownSec)}`);
    lines.push(`Total time   : ${formatDurationCompact(history.totalCooldownSec)}`);
  }

  // Failover relationships
  const failedToKeys = Object.keys(history.failedToModels);
  if (failedToKeys.length > 0) {
    lines.push("");
    lines.push("Failed over to:");
    for (const model of failedToKeys.sort()) {
      lines.push(`  -> ${pad(model, 40)} ${history.failedToModels[model]}x`);
    }
  }

  const receivedFromKeys = Object.keys(history.receivedFromModels);
  if (receivedFromKeys.length > 0) {
    lines.push("");
    lines.push("Received failovers from:");
    for (const model of receivedFromKeys.sort()) {
      lines.push(`  <- ${pad(model, 40)} ${history.receivedFromModels[model]}x`);
    }
  }

  // Cooldown timeline
  if (history.cooldowns.length > 0) {
    lines.push("");
    lines.push("Cooldown timeline:");
    for (const c of history.cooldowns) {
      const ts = new Date(c.startedAt * 1000).toISOString().replace("T", " ").slice(0, 19);
      const dur = formatDurationCompact(c.durationSec);
      const typeLabel = c.type.toUpperCase();
      const reason = c.reason ? ` (${c.reason.slice(0, 60)})` : "";
      lines.push(`  [${ts}] ${typeLabel} ${dur}${reason}`);
    }
  }

  return lines.join("\n");
}

function formatDurationCompact(seconds: number): string {
  if (seconds <= 0) return "0s";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  const parts: string[] = [];
  if (h > 0) parts.push(`${h}h`);
  if (m > 0) parts.push(`${m}m`);
  if (s > 0 && h === 0) parts.push(`${s}s`);
  return parts.join(" ") || "0s";
}

// -------------------------------------------------------------------------
// CLI entry point
// -------------------------------------------------------------------------

const isDirectRun =
  typeof process !== "undefined" &&
  process.argv[1] &&
  (process.argv[1].endsWith("metrics.ts") || process.argv[1].endsWith("metrics.js"));

if (isDirectRun) {
  const args = process.argv.slice(2);

  if (args[0] === "tail") {
    const count = parseInt(args[1] ?? "20", 10);
    const events = loadEvents(DEFAULT_METRICS_FILE);
    const tail = events.slice(-count);
    console.log(formatEvents(tail));
  } else if (args[0] === "history") {
    const model = args[1];
    if (!model) {
      console.log("Usage: npx tsx metrics.ts history <model-id>");
      process.exit(1);
    }
    const jsonFlag = args.includes("--json");
    const history = getModelHistory({ model });
    if (jsonFlag) {
      console.log(JSON.stringify(history, null, 2));
    } else {
      console.log(formatModelHistory(history));
    }
  } else if (args[0] === "reset") {
    const existed = resetMetrics();
    console.log(
      existed
        ? "Metrics log cleared."
        : "No metrics log found.",
    );
  } else if (args[0] === "--json") {
    const summary = getMetricsSummary();
    console.log(JSON.stringify(summary, null, 2));
  } else if (args[0] === "--help" || args[0] === "-h") {
    console.log(
      [
        "Usage: npx tsx metrics.ts [command] [options]",
        "",
        "Commands:",
        "  (default)             Pretty-print metrics summary",
        "  --json                Output summary as JSON",
        "  tail [N]              Show last N events (default 20)",
        "  history <model-id>    Show cooldown history for a model",
        "  reset                 Clear all metrics",
        "  --help, -h            Show this help message",
      ].join("\n"),
    );
  } else {
    const summary = getMetricsSummary();
    console.log(formatMetrics(summary));
  }
}
