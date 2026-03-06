import { describe, it, expect, beforeEach, afterEach } from "vitest";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import {
  recordEvent,
  recordRateLimit,
  loadEvents,
  getMetricsSummary,
  getModelHistory,
  queryMetrics,
  resetMetrics,
  formatMetrics,
  formatEvents,
  formatModelHistory,
  DEFAULT_METRICS_FILE,
  type MetricEvent,
  type MetricsSummary,
  type MetricsQueryResult,
  type ModelHistory,
} from "./metrics.js";
import { nowSec } from "./index.js";

// ---------------------------------------------------------------------------
// Test fixtures
// ---------------------------------------------------------------------------

let tmpDir: string;
let metricsPath: string;

beforeEach(() => {
  tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "fo-metrics-"));
  metricsPath = path.join(tmpDir, "metrics.jsonl");
});

afterEach(() => {
  fs.rmSync(tmpDir, { recursive: true, force: true });
});

function sampleEvent(overrides?: Partial<MetricEvent>): MetricEvent {
  return {
    ts: nowSec(),
    type: "rate_limit",
    model: "provA/model1",
    provider: "provA",
    reason: "429 Too Many Requests",
    cooldownSec: 3600,
    trigger: "agent_end",
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// 1. recordEvent and loadEvents
// ---------------------------------------------------------------------------
describe("recordEvent and loadEvents", () => {
  it("appends events to JSONL file and loads them back", () => {
    const e1 = sampleEvent({ ts: 1000 });
    const e2 = sampleEvent({ ts: 2000, model: "provB/model2", provider: "provB" });

    recordEvent(metricsPath, e1);
    recordEvent(metricsPath, e2);

    const events = loadEvents(metricsPath);
    expect(events).toHaveLength(2);
    expect(events[0].ts).toBe(1000);
    expect(events[1].model).toBe("provB/model2");
  });

  it("creates parent directories if they do not exist", () => {
    const deepPath = path.join(tmpDir, "a", "b", "c", "metrics.jsonl");
    recordEvent(deepPath, sampleEvent());

    const events = loadEvents(deepPath);
    expect(events).toHaveLength(1);
  });

  it("returns empty array when file does not exist", () => {
    const events = loadEvents(path.join(tmpDir, "nonexistent.jsonl"));
    expect(events).toHaveLength(0);
  });

  it("skips malformed lines and parses valid ones", () => {
    fs.writeFileSync(
      metricsPath,
      '{"ts":1000,"type":"rate_limit","model":"a/b","provider":"a"}\nnot-json\n{"ts":2000,"type":"failover","model":"a/b","provider":"a","to":"c/d"}\n',
    );

    const events = loadEvents(metricsPath);
    expect(events).toHaveLength(2);
    expect(events[0].ts).toBe(1000);
    expect(events[1].ts).toBe(2000);
  });

  it("handles empty file gracefully", () => {
    fs.writeFileSync(metricsPath, "");
    const events = loadEvents(metricsPath);
    expect(events).toHaveLength(0);
  });

  it("preserves all event fields through serialization", () => {
    const event: MetricEvent = {
      ts: 12345,
      type: "failover",
      model: "provA/model1",
      provider: "provA",
      reason: "rate limit hit",
      cooldownSec: 1800,
      to: "provB/model2",
      trigger: "message_sent",
      session: "sess-abc",
    };

    recordEvent(metricsPath, event);
    const loaded = loadEvents(metricsPath);
    expect(loaded).toHaveLength(1);
    expect(loaded[0]).toEqual(event);
  });
});

// ---------------------------------------------------------------------------
// 2. getMetricsSummary - empty
// ---------------------------------------------------------------------------
describe("getMetricsSummary - empty", () => {
  it("returns zeroed summary when no file exists", () => {
    const summary = getMetricsSummary({
      metricsPath: path.join(tmpDir, "nonexistent.jsonl"),
    });

    expect(summary.totalEvents).toBe(0);
    expect(summary.totalRateLimits).toBe(0);
    expect(summary.totalAuthErrors).toBe(0);
    expect(summary.totalUnavailable).toBe(0);
    expect(summary.totalFailovers).toBe(0);
    expect(summary.since).toBeUndefined();
    expect(Object.keys(summary.models)).toHaveLength(0);
    expect(Object.keys(summary.providers)).toHaveLength(0);
  });
});

// ---------------------------------------------------------------------------
// 3. getMetricsSummary - aggregation
// ---------------------------------------------------------------------------
describe("getMetricsSummary - aggregation", () => {
  it("counts rate limits correctly", () => {
    recordEvent(metricsPath, sampleEvent({ ts: 100 }));
    recordEvent(metricsPath, sampleEvent({ ts: 200 }));
    recordEvent(metricsPath, sampleEvent({ ts: 300, model: "provA/model2" }));

    const summary = getMetricsSummary({ metricsPath });
    expect(summary.totalRateLimits).toBe(3);
    expect(summary.totalEvents).toBe(3);
    expect(summary.since).toBe(100);
    expect(summary.models["provA/model1"].rateLimits).toBe(2);
    expect(summary.models["provA/model2"].rateLimits).toBe(1);
    expect(summary.providers["provA"].rateLimits).toBe(3);
  });

  it("counts auth errors correctly", () => {
    recordEvent(metricsPath, sampleEvent({
      ts: 100,
      type: "auth_error",
      reason: "invalid api key",
      cooldownSec: 43200,
    }));

    const summary = getMetricsSummary({ metricsPath });
    expect(summary.totalAuthErrors).toBe(1);
    expect(summary.models["provA/model1"].authErrors).toBe(1);
    expect(summary.providers["provA"].authErrors).toBe(1);
  });

  it("counts unavailable errors correctly", () => {
    recordEvent(metricsPath, sampleEvent({
      ts: 100,
      type: "unavailable",
      reason: "service unavailable",
      cooldownSec: 900,
    }));

    const summary = getMetricsSummary({ metricsPath });
    expect(summary.totalUnavailable).toBe(1);
    expect(summary.models["provA/model1"].unavailableErrors).toBe(1);
    expect(summary.providers["provA"].unavailableErrors).toBe(1);
  });

  it("counts failovers and tracks from/to", () => {
    recordEvent(metricsPath, sampleEvent({
      ts: 100,
      type: "failover",
      model: "provA/model1",
      to: "provB/model2",
    }));

    const summary = getMetricsSummary({ metricsPath });
    expect(summary.totalFailovers).toBe(1);
    expect(summary.models["provA/model1"].timesFailedFrom).toBe(1);
    expect(summary.models["provB/model2"].timesFailedTo).toBe(1);
  });

  it("accumulates total cooldown seconds", () => {
    recordEvent(metricsPath, sampleEvent({ ts: 100, cooldownSec: 1000 }));
    recordEvent(metricsPath, sampleEvent({ ts: 200, cooldownSec: 2000 }));

    const summary = getMetricsSummary({ metricsPath });
    expect(summary.models["provA/model1"].totalCooldownSec).toBe(3000);
    expect(summary.providers["provA"].totalCooldownSec).toBe(3000);
  });

  it("computes per-model and per-provider cooldownCount and avgCooldownSec", () => {
    recordEvent(metricsPath, sampleEvent({ ts: 100, cooldownSec: 1000 }));
    recordEvent(metricsPath, sampleEvent({ ts: 200, cooldownSec: 3000 }));
    recordEvent(metricsPath, sampleEvent({ ts: 300, cooldownSec: undefined }));

    const summary = getMetricsSummary({ metricsPath });
    // Only events with cooldownSec are counted
    expect(summary.models["provA/model1"].cooldownCount).toBe(2);
    expect(summary.models["provA/model1"].avgCooldownSec).toBe(2000);
    expect(summary.providers["provA"].cooldownCount).toBe(2);
    expect(summary.providers["provA"].avgCooldownSec).toBe(2000);
  });

  it("computes overall avgCooldownSec across all models", () => {
    recordEvent(metricsPath, sampleEvent({ ts: 100, model: "provA/m1", provider: "provA", cooldownSec: 1000 }));
    recordEvent(metricsPath, sampleEvent({ ts: 200, model: "provB/m2", provider: "provB", cooldownSec: 3000 }));

    const summary = getMetricsSummary({ metricsPath });
    expect(summary.avgCooldownSec).toBe(2000);
  });

  it("collects recentCooldowns from error events with cooldownSec", () => {
    recordEvent(metricsPath, sampleEvent({ ts: 100, cooldownSec: 1000, reason: "rate limit" }));
    recordEvent(metricsPath, sampleEvent({ ts: 200, type: "auth_error", cooldownSec: 2000, reason: "bad key" }));
    recordEvent(metricsPath, sampleEvent({ ts: 300, type: "failover", to: "provB/m2" })); // no cooldown

    const summary = getMetricsSummary({ metricsPath });
    expect(summary.recentCooldowns).toHaveLength(2);
    expect(summary.recentCooldowns[0].startedAt).toBe(100);
    expect(summary.recentCooldowns[0].type).toBe("rate_limit");
    expect(summary.recentCooldowns[1].startedAt).toBe(200);
    expect(summary.recentCooldowns[1].type).toBe("auth_error");
  });

  it("limits recentCooldowns via maxRecentCooldowns option", () => {
    for (let i = 0; i < 5; i++) {
      recordEvent(metricsPath, sampleEvent({ ts: 100 + i, cooldownSec: 1000 }));
    }

    const summary = getMetricsSummary({ metricsPath, maxRecentCooldowns: 3 });
    expect(summary.recentCooldowns).toHaveLength(3);
    // Should be the last 3 entries
    expect(summary.recentCooldowns[0].startedAt).toBe(102);
    expect(summary.recentCooldowns[2].startedAt).toBe(104);
  });

  it("tracks lastHitAt as the latest timestamp for each model", () => {
    recordEvent(metricsPath, sampleEvent({ ts: 100 }));
    recordEvent(metricsPath, sampleEvent({ ts: 500 }));
    recordEvent(metricsPath, sampleEvent({ ts: 300 }));

    const summary = getMetricsSummary({ metricsPath });
    // lastHitAt is set per-event, so it will be the last event processed
    expect(summary.models["provA/model1"].lastHitAt).toBe(300);
  });

  it("handles multiple providers and models", () => {
    recordEvent(metricsPath, sampleEvent({ ts: 100, model: "provA/m1", provider: "provA" }));
    recordEvent(metricsPath, sampleEvent({ ts: 200, model: "provA/m2", provider: "provA" }));
    recordEvent(metricsPath, sampleEvent({ ts: 300, model: "provB/m3", provider: "provB", type: "auth_error" }));
    recordEvent(metricsPath, sampleEvent({
      ts: 400,
      type: "failover",
      model: "provA/m1",
      provider: "provA",
      to: "provB/m3",
    }));

    const summary = getMetricsSummary({ metricsPath });
    expect(summary.totalEvents).toBe(4);
    expect(summary.totalRateLimits).toBe(2);
    expect(summary.totalAuthErrors).toBe(1);
    expect(summary.totalFailovers).toBe(1);
    expect(Object.keys(summary.providers)).toHaveLength(2);
    expect(Object.keys(summary.models)).toHaveLength(3);
  });
});

// ---------------------------------------------------------------------------
// 4. getMetricsSummary - time filtering
// ---------------------------------------------------------------------------
describe("getMetricsSummary - time filtering", () => {
  it("filters events by since parameter", () => {
    recordEvent(metricsPath, sampleEvent({ ts: 100 }));
    recordEvent(metricsPath, sampleEvent({ ts: 200 }));
    recordEvent(metricsPath, sampleEvent({ ts: 300 }));

    const summary = getMetricsSummary({ metricsPath, since: 200 });
    expect(summary.totalEvents).toBe(2);
    expect(summary.since).toBe(200);
  });

  it("filters events by until parameter", () => {
    recordEvent(metricsPath, sampleEvent({ ts: 100 }));
    recordEvent(metricsPath, sampleEvent({ ts: 200 }));
    recordEvent(metricsPath, sampleEvent({ ts: 300 }));

    const summary = getMetricsSummary({ metricsPath, until: 200 });
    expect(summary.totalEvents).toBe(2);
  });

  it("filters with both since and until", () => {
    recordEvent(metricsPath, sampleEvent({ ts: 100 }));
    recordEvent(metricsPath, sampleEvent({ ts: 200 }));
    recordEvent(metricsPath, sampleEvent({ ts: 300 }));
    recordEvent(metricsPath, sampleEvent({ ts: 400 }));

    const summary = getMetricsSummary({ metricsPath, since: 150, until: 350 });
    expect(summary.totalEvents).toBe(2);
  });
});

// ---------------------------------------------------------------------------
// 5. resetMetrics
// ---------------------------------------------------------------------------
describe("resetMetrics", () => {
  it("deletes the metrics file and returns true", () => {
    recordEvent(metricsPath, sampleEvent());
    expect(fs.existsSync(metricsPath)).toBe(true);

    const result = resetMetrics(metricsPath);
    expect(result).toBe(true);
    expect(fs.existsSync(metricsPath)).toBe(false);
  });

  it("returns false when file does not exist", () => {
    const result = resetMetrics(path.join(tmpDir, "nonexistent.jsonl"));
    expect(result).toBe(false);
  });

  it("results in empty summary after reset", () => {
    recordEvent(metricsPath, sampleEvent());
    resetMetrics(metricsPath);

    const summary = getMetricsSummary({ metricsPath });
    expect(summary.totalEvents).toBe(0);
  });
});

// ---------------------------------------------------------------------------
// 6. formatMetrics
// ---------------------------------------------------------------------------
describe("formatMetrics", () => {
  it("shows 'no events' message for empty summary", () => {
    const summary = getMetricsSummary({
      metricsPath: path.join(tmpDir, "nonexistent.jsonl"),
    });

    const output = formatMetrics(summary);
    expect(output).toContain("No failover events recorded yet.");
    expect(output).toContain("OpenClaw Model Failover Metrics");
  });

  it("shows summary with counts and breakdowns", () => {
    recordEvent(metricsPath, sampleEvent({ ts: 1000, model: "provA/m1", provider: "provA" }));
    recordEvent(metricsPath, sampleEvent({
      ts: 2000,
      type: "auth_error",
      model: "provB/m2",
      provider: "provB",
      cooldownSec: 43200,
    }));
    recordEvent(metricsPath, sampleEvent({
      ts: 3000,
      type: "failover",
      model: "provA/m1",
      provider: "provA",
      to: "provB/m2",
    }));

    const summary = getMetricsSummary({ metricsPath });
    const output = formatMetrics(summary);

    expect(output).toContain("Total events : 3");
    expect(output).toContain("Rate limits  : 1");
    expect(output).toContain("Auth errors  : 1");
    expect(output).toContain("Failovers    : 1");
    expect(output).toContain("By provider:");
    expect(output).toContain("provA");
    expect(output).toContain("provB");
    expect(output).toContain("By model:");
    expect(output).toContain("provA/m1");
    expect(output).toContain("provB/m2");
  });

  it("shows period range", () => {
    recordEvent(metricsPath, sampleEvent({ ts: 1000000 }));
    recordEvent(metricsPath, sampleEvent({ ts: 2000000 }));

    const summary = getMetricsSummary({ metricsPath });
    const output = formatMetrics(summary);

    expect(output).toContain("Period");
    // Should contain ISO date strings
    expect(output).toMatch(/\d{4}-\d{2}-\d{2}/);
  });
});

// ---------------------------------------------------------------------------
// 7. formatEvents
// ---------------------------------------------------------------------------
describe("formatEvents", () => {
  it("returns 'No events.' for empty array", () => {
    expect(formatEvents([])).toBe("No events.");
  });

  it("formats rate limit events with timestamp and details", () => {
    const events: MetricEvent[] = [
      sampleEvent({ ts: 1709000000, reason: "429 Too Many Requests", cooldownSec: 3600 }),
    ];

    const output = formatEvents(events);
    expect(output).toContain("RATE_LIMIT");
    expect(output).toContain("provA/model1");
    expect(output).toContain("429 Too Many Requests");
    expect(output).toContain("cooldown=3600s");
  });

  it("formats failover events with target model", () => {
    const events: MetricEvent[] = [
      sampleEvent({
        ts: 1709000000,
        type: "failover",
        model: "provA/m1",
        to: "provB/m2",
      }),
    ];

    const output = formatEvents(events);
    expect(output).toContain("FAILOVER");
    expect(output).toContain("provA/m1");
    expect(output).toContain("-> provB/m2");
  });

  it("formats multiple events on separate lines", () => {
    const events: MetricEvent[] = [
      sampleEvent({ ts: 1000 }),
      sampleEvent({ ts: 2000, type: "auth_error" }),
    ];

    const output = formatEvents(events);
    const lines = output.split("\n");
    expect(lines).toHaveLength(2);
  });
});

// ---------------------------------------------------------------------------
// 8. DEFAULT_METRICS_FILE
// ---------------------------------------------------------------------------
describe("DEFAULT_METRICS_FILE", () => {
  it("has a sensible default path", () => {
    expect(DEFAULT_METRICS_FILE).toContain(".openclaw");
    expect(DEFAULT_METRICS_FILE).toContain("metrics");
    expect(DEFAULT_METRICS_FILE.endsWith(".jsonl")).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// 9. getModelHistory - empty / no events
// ---------------------------------------------------------------------------
describe("getModelHistory - empty", () => {
  it("returns empty history when no file exists", () => {
    const history = getModelHistory({
      model: "provA/model1",
      metricsPath: path.join(tmpDir, "nonexistent.jsonl"),
    });

    expect(history.model).toBe("provA/model1");
    expect(history.events).toHaveLength(0);
    expect(history.cooldowns).toHaveLength(0);
    expect(history.totalErrors).toBe(0);
    expect(history.totalCooldownSec).toBe(0);
    expect(history.avgCooldownSec).toBe(0);
    expect(history.maxCooldownSec).toBe(0);
    expect(history.firstSeen).toBeUndefined();
    expect(history.lastSeen).toBeUndefined();
    expect(Object.keys(history.failedToModels)).toHaveLength(0);
    expect(Object.keys(history.receivedFromModels)).toHaveLength(0);
  });

  it("returns empty history when model has no events", () => {
    recordEvent(metricsPath, sampleEvent({ model: "provB/other", provider: "provB" }));

    const history = getModelHistory({
      model: "provA/model1",
      metricsPath,
    });

    expect(history.events).toHaveLength(0);
    expect(history.cooldowns).toHaveLength(0);
    expect(history.totalErrors).toBe(0);
  });
});

// ---------------------------------------------------------------------------
// 10. getModelHistory - cooldown entries
// ---------------------------------------------------------------------------
describe("getModelHistory - cooldown entries", () => {
  it("builds cooldown entries from rate limit events", () => {
    recordEvent(metricsPath, sampleEvent({
      ts: 1000,
      type: "rate_limit",
      cooldownSec: 3600,
      reason: "429 Too Many Requests",
      trigger: "agent_end",
      session: "sess-1",
    }));
    recordEvent(metricsPath, sampleEvent({
      ts: 5000,
      type: "rate_limit",
      cooldownSec: 1800,
      reason: "quota exceeded",
      trigger: "message_sent",
      session: "sess-2",
    }));

    const history = getModelHistory({ model: "provA/model1", metricsPath });

    expect(history.cooldowns).toHaveLength(2);
    expect(history.cooldowns[0].startedAt).toBe(1000);
    expect(history.cooldowns[0].durationSec).toBe(3600);
    expect(history.cooldowns[0].type).toBe("rate_limit");
    expect(history.cooldowns[0].reason).toBe("429 Too Many Requests");
    expect(history.cooldowns[0].trigger).toBe("agent_end");
    expect(history.cooldowns[0].session).toBe("sess-1");
    expect(history.cooldowns[1].startedAt).toBe(5000);
    expect(history.cooldowns[1].durationSec).toBe(1800);
  });

  it("builds cooldown entries from auth_error and unavailable events", () => {
    recordEvent(metricsPath, sampleEvent({
      ts: 1000,
      type: "auth_error",
      cooldownSec: 43200,
      reason: "invalid api key",
    }));
    recordEvent(metricsPath, sampleEvent({
      ts: 2000,
      type: "unavailable",
      cooldownSec: 900,
      reason: "service unavailable",
    }));

    const history = getModelHistory({ model: "provA/model1", metricsPath });

    expect(history.cooldowns).toHaveLength(2);
    expect(history.cooldowns[0].type).toBe("auth_error");
    expect(history.cooldowns[1].type).toBe("unavailable");
    expect(history.totalErrors).toBe(2);
  });

  it("skips events with no cooldownSec when building cooldown entries", () => {
    recordEvent(metricsPath, sampleEvent({
      ts: 1000,
      type: "rate_limit",
      cooldownSec: undefined,
    }));
    recordEvent(metricsPath, sampleEvent({
      ts: 2000,
      type: "rate_limit",
      cooldownSec: 3600,
    }));

    const history = getModelHistory({ model: "provA/model1", metricsPath });

    expect(history.cooldowns).toHaveLength(1);
    expect(history.cooldowns[0].startedAt).toBe(2000);
    // But totalErrors still counts the event without cooldown
    expect(history.totalErrors).toBe(2);
  });

  it("does not create cooldown entries for failover events", () => {
    recordEvent(metricsPath, sampleEvent({
      ts: 1000,
      type: "failover",
      to: "provB/model2",
    }));

    const history = getModelHistory({ model: "provA/model1", metricsPath });

    expect(history.cooldowns).toHaveLength(0);
    expect(history.totalErrors).toBe(0);
    expect(history.events).toHaveLength(1);
  });
});

// ---------------------------------------------------------------------------
// 11. getModelHistory - statistics
// ---------------------------------------------------------------------------
describe("getModelHistory - statistics", () => {
  it("calculates avg, max, and total cooldown correctly", () => {
    recordEvent(metricsPath, sampleEvent({ ts: 1000, cooldownSec: 1000 }));
    recordEvent(metricsPath, sampleEvent({ ts: 2000, cooldownSec: 3000 }));
    recordEvent(metricsPath, sampleEvent({ ts: 3000, cooldownSec: 2000 }));

    const history = getModelHistory({ model: "provA/model1", metricsPath });

    expect(history.totalCooldownSec).toBe(6000);
    expect(history.maxCooldownSec).toBe(3000);
    expect(history.avgCooldownSec).toBe(2000);
  });

  it("tracks firstSeen and lastSeen timestamps", () => {
    recordEvent(metricsPath, sampleEvent({ ts: 500 }));
    recordEvent(metricsPath, sampleEvent({ ts: 100 }));
    recordEvent(metricsPath, sampleEvent({ ts: 900 }));

    const history = getModelHistory({ model: "provA/model1", metricsPath });

    expect(history.firstSeen).toBe(100);
    expect(history.lastSeen).toBe(900);
  });

  it("tracks failover target models", () => {
    recordEvent(metricsPath, sampleEvent({
      ts: 1000,
      type: "failover",
      to: "provB/model2",
    }));
    recordEvent(metricsPath, sampleEvent({
      ts: 2000,
      type: "failover",
      to: "provB/model2",
    }));
    recordEvent(metricsPath, sampleEvent({
      ts: 3000,
      type: "failover",
      to: "provC/model3",
    }));

    const history = getModelHistory({ model: "provA/model1", metricsPath });

    expect(history.failedToModels["provB/model2"]).toBe(2);
    expect(history.failedToModels["provC/model3"]).toBe(1);
  });

  it("tracks models that failed over to this model", () => {
    recordEvent(metricsPath, sampleEvent({
      ts: 1000,
      type: "failover",
      model: "provA/model1",
      provider: "provA",
      to: "provB/model2",
    }));
    recordEvent(metricsPath, sampleEvent({
      ts: 2000,
      type: "failover",
      model: "provC/model3",
      provider: "provC",
      to: "provB/model2",
    }));

    const history = getModelHistory({ model: "provB/model2", metricsPath });

    expect(history.receivedFromModels["provA/model1"]).toBe(1);
    expect(history.receivedFromModels["provC/model3"]).toBe(1);
    // Events where model is primary subject should be empty (model2 had no errors)
    expect(history.events).toHaveLength(0);
  });

  it("updates firstSeen/lastSeen from received failovers", () => {
    recordEvent(metricsPath, sampleEvent({
      ts: 500,
      type: "failover",
      model: "provA/model1",
      provider: "provA",
      to: "provB/model2",
    }));

    const history = getModelHistory({ model: "provB/model2", metricsPath });

    expect(history.firstSeen).toBe(500);
    expect(history.lastSeen).toBe(500);
  });
});

// ---------------------------------------------------------------------------
// 12. getModelHistory - time filtering
// ---------------------------------------------------------------------------
describe("getModelHistory - time filtering", () => {
  it("filters events by since parameter", () => {
    recordEvent(metricsPath, sampleEvent({ ts: 100, cooldownSec: 1000 }));
    recordEvent(metricsPath, sampleEvent({ ts: 200, cooldownSec: 2000 }));
    recordEvent(metricsPath, sampleEvent({ ts: 300, cooldownSec: 3000 }));

    const history = getModelHistory({
      model: "provA/model1",
      metricsPath,
      since: 200,
    });

    expect(history.events).toHaveLength(2);
    expect(history.cooldowns).toHaveLength(2);
    expect(history.totalCooldownSec).toBe(5000);
  });

  it("filters events by until parameter", () => {
    recordEvent(metricsPath, sampleEvent({ ts: 100, cooldownSec: 1000 }));
    recordEvent(metricsPath, sampleEvent({ ts: 200, cooldownSec: 2000 }));
    recordEvent(metricsPath, sampleEvent({ ts: 300, cooldownSec: 3000 }));

    const history = getModelHistory({
      model: "provA/model1",
      metricsPath,
      until: 200,
    });

    expect(history.events).toHaveLength(2);
    expect(history.cooldowns).toHaveLength(2);
    expect(history.totalCooldownSec).toBe(3000);
  });

  it("filters with both since and until", () => {
    recordEvent(metricsPath, sampleEvent({ ts: 100, cooldownSec: 1000 }));
    recordEvent(metricsPath, sampleEvent({ ts: 200, cooldownSec: 2000 }));
    recordEvent(metricsPath, sampleEvent({ ts: 300, cooldownSec: 3000 }));
    recordEvent(metricsPath, sampleEvent({ ts: 400, cooldownSec: 4000 }));

    const history = getModelHistory({
      model: "provA/model1",
      metricsPath,
      since: 150,
      until: 350,
    });

    expect(history.events).toHaveLength(2);
    expect(history.cooldowns).toHaveLength(2);
    expect(history.totalCooldownSec).toBe(5000);
  });
});

// ---------------------------------------------------------------------------
// 13. getModelHistory - mixed events
// ---------------------------------------------------------------------------
describe("getModelHistory - mixed events", () => {
  it("handles a realistic sequence of errors and failovers", () => {
    // Model A gets rate limited
    recordEvent(metricsPath, sampleEvent({
      ts: 1000,
      type: "rate_limit",
      model: "provA/model1",
      provider: "provA",
      cooldownSec: 3600,
      reason: "429 Too Many Requests",
    }));
    // Model A fails over to model B
    recordEvent(metricsPath, sampleEvent({
      ts: 1000,
      type: "failover",
      model: "provA/model1",
      provider: "provA",
      to: "provB/model2",
    }));
    // Later, model A gets another rate limit
    recordEvent(metricsPath, sampleEvent({
      ts: 5000,
      type: "rate_limit",
      model: "provA/model1",
      provider: "provA",
      cooldownSec: 1800,
      reason: "quota exceeded",
    }));
    // Model A fails over to model C this time
    recordEvent(metricsPath, sampleEvent({
      ts: 5000,
      type: "failover",
      model: "provA/model1",
      provider: "provA",
      to: "provC/model3",
    }));
    // Unrelated: model B gets an auth error
    recordEvent(metricsPath, sampleEvent({
      ts: 6000,
      type: "auth_error",
      model: "provB/model2",
      provider: "provB",
      cooldownSec: 43200,
    }));

    const historyA = getModelHistory({ model: "provA/model1", metricsPath });
    expect(historyA.events).toHaveLength(4);
    expect(historyA.cooldowns).toHaveLength(2);
    expect(historyA.totalErrors).toBe(2);
    expect(historyA.totalCooldownSec).toBe(5400);
    expect(historyA.maxCooldownSec).toBe(3600);
    expect(historyA.avgCooldownSec).toBe(2700);
    expect(historyA.failedToModels["provB/model2"]).toBe(1);
    expect(historyA.failedToModels["provC/model3"]).toBe(1);
    expect(Object.keys(historyA.receivedFromModels)).toHaveLength(0);

    const historyB = getModelHistory({ model: "provB/model2", metricsPath });
    expect(historyB.events).toHaveLength(1); // only its own auth_error
    expect(historyB.cooldowns).toHaveLength(1);
    expect(historyB.receivedFromModels["provA/model1"]).toBe(1);
    expect(historyB.firstSeen).toBe(1000); // from received failover
    expect(historyB.lastSeen).toBe(6000); // from its own auth_error
  });
});

// ---------------------------------------------------------------------------
// 14. formatModelHistory
// ---------------------------------------------------------------------------
describe("formatModelHistory", () => {
  it("shows 'no events' message for empty history", () => {
    const history = getModelHistory({
      model: "provA/model1",
      metricsPath: path.join(tmpDir, "nonexistent.jsonl"),
    });

    const output = formatModelHistory(history);
    expect(output).toContain("Cooldown History: provA/model1");
    expect(output).toContain("No events recorded for this model.");
  });

  it("shows summary stats and cooldown timeline", () => {
    recordEvent(metricsPath, sampleEvent({
      ts: 1000000,
      cooldownSec: 3600,
      reason: "429 Too Many Requests",
    }));
    recordEvent(metricsPath, sampleEvent({
      ts: 2000000,
      cooldownSec: 1800,
      reason: "quota exceeded",
    }));

    const history = getModelHistory({ model: "provA/model1", metricsPath });
    const output = formatModelHistory(history);

    expect(output).toContain("Cooldown History: provA/model1");
    expect(output).toContain("Total errors : 2");
    expect(output).toContain("Cooldowns    : 2");
    expect(output).toContain("Avg cooldown");
    expect(output).toContain("Max cooldown : 1h");
    expect(output).toContain("Cooldown timeline:");
    expect(output).toContain("RATE_LIMIT");
    expect(output).toContain("429 Too Many Requests");
    expect(output).toContain("quota exceeded");
  });

  it("shows failover relationships", () => {
    recordEvent(metricsPath, sampleEvent({
      ts: 1000,
      type: "failover",
      model: "provA/model1",
      provider: "provA",
      to: "provB/model2",
    }));
    recordEvent(metricsPath, sampleEvent({
      ts: 2000,
      type: "failover",
      model: "provC/model3",
      provider: "provC",
      to: "provA/model1",
    }));

    const history = getModelHistory({ model: "provA/model1", metricsPath });
    const output = formatModelHistory(history);

    expect(output).toContain("Failed over to:");
    expect(output).toContain("-> provB/model2");
    expect(output).toContain("Received failovers from:");
    expect(output).toContain("<- provC/model3");
  });

  it("shows first/last seen dates", () => {
    recordEvent(metricsPath, sampleEvent({ ts: 1000000 }));
    recordEvent(metricsPath, sampleEvent({ ts: 2000000 }));

    const history = getModelHistory({ model: "provA/model1", metricsPath });
    const output = formatModelHistory(history);

    expect(output).toContain("First seen");
    expect(output).toContain("Last seen");
    expect(output).toMatch(/\d{4}-\d{2}-\d{2}/);
  });

  it("handles model with only received failovers (no own errors)", () => {
    recordEvent(metricsPath, sampleEvent({
      ts: 1000,
      type: "failover",
      model: "provA/model1",
      provider: "provA",
      to: "provB/model2",
    }));

    const history = getModelHistory({ model: "provB/model2", metricsPath });
    const output = formatModelHistory(history);

    expect(output).toContain("Cooldown History: provB/model2");
    expect(output).toContain("Total errors : 0");
    expect(output).toContain("Received failovers from:");
    expect(output).toContain("<- provA/model1");
    expect(output).not.toContain("No events recorded for this model.");
  });
});

// ---------------------------------------------------------------------------
// 15. getMetricsSummary - per-model/provider cooldown stats
// ---------------------------------------------------------------------------
describe("getMetricsSummary - cooldown stats", () => {
  it("computes avgCooldownSec and cooldownCount per model", () => {
    recordEvent(metricsPath, sampleEvent({ ts: 100, cooldownSec: 1000 }));
    recordEvent(metricsPath, sampleEvent({ ts: 200, cooldownSec: 3000 }));
    recordEvent(metricsPath, sampleEvent({ ts: 300, model: "provA/model2", cooldownSec: 2000 }));

    const summary = getMetricsSummary({ metricsPath });

    expect(summary.models["provA/model1"].cooldownCount).toBe(2);
    expect(summary.models["provA/model1"].avgCooldownSec).toBe(2000);
    expect(summary.models["provA/model2"].cooldownCount).toBe(1);
    expect(summary.models["provA/model2"].avgCooldownSec).toBe(2000);
  });

  it("computes avgCooldownSec and cooldownCount per provider", () => {
    recordEvent(metricsPath, sampleEvent({ ts: 100, cooldownSec: 1000, model: "provA/m1", provider: "provA" }));
    recordEvent(metricsPath, sampleEvent({ ts: 200, cooldownSec: 3000, model: "provA/m2", provider: "provA" }));
    recordEvent(metricsPath, sampleEvent({ ts: 300, cooldownSec: 6000, model: "provB/m3", provider: "provB" }));

    const summary = getMetricsSummary({ metricsPath });

    expect(summary.providers["provA"].cooldownCount).toBe(2);
    expect(summary.providers["provA"].avgCooldownSec).toBe(2000);
    expect(summary.providers["provB"].cooldownCount).toBe(1);
    expect(summary.providers["provB"].avgCooldownSec).toBe(6000);
  });

  it("computes global avgCooldownSec across all events", () => {
    recordEvent(metricsPath, sampleEvent({ ts: 100, cooldownSec: 1000 }));
    recordEvent(metricsPath, sampleEvent({ ts: 200, cooldownSec: 3000 }));
    recordEvent(metricsPath, sampleEvent({ ts: 300, cooldownSec: 2000, model: "provB/m2", provider: "provB" }));

    const summary = getMetricsSummary({ metricsPath });
    // (1000 + 3000 + 2000) / 3 = 2000
    expect(summary.avgCooldownSec).toBe(2000);
  });

  it("returns avgCooldownSec=0 when no cooldowns recorded", () => {
    recordEvent(metricsPath, sampleEvent({ ts: 100, type: "failover", to: "provB/m2" }));

    const summary = getMetricsSummary({ metricsPath });
    expect(summary.avgCooldownSec).toBe(0);
  });

  it("returns zero avgCooldownSec for model with only failover events", () => {
    recordEvent(metricsPath, sampleEvent({ ts: 100, type: "failover", to: "provB/m2" }));

    const summary = getMetricsSummary({ metricsPath });
    expect(summary.models["provA/model1"].cooldownCount).toBe(0);
    expect(summary.models["provA/model1"].avgCooldownSec).toBe(0);
  });
});

// ---------------------------------------------------------------------------
// 16. getMetricsSummary - recentCooldowns
// ---------------------------------------------------------------------------
describe("getMetricsSummary - recentCooldowns", () => {
  it("includes recent cooldown entries with timestamps", () => {
    recordEvent(metricsPath, sampleEvent({ ts: 100, cooldownSec: 1000, reason: "first" }));
    recordEvent(metricsPath, sampleEvent({ ts: 200, cooldownSec: 2000, reason: "second" }));

    const summary = getMetricsSummary({ metricsPath });

    expect(summary.recentCooldowns).toHaveLength(2);
    expect(summary.recentCooldowns[0].startedAt).toBe(100);
    expect(summary.recentCooldowns[0].durationSec).toBe(1000);
    expect(summary.recentCooldowns[0].reason).toBe("first");
    expect(summary.recentCooldowns[1].startedAt).toBe(200);
    expect(summary.recentCooldowns[1].durationSec).toBe(2000);
  });

  it("limits recentCooldowns to maxRecentCooldowns", () => {
    for (let i = 0; i < 10; i++) {
      recordEvent(metricsPath, sampleEvent({ ts: 100 + i, cooldownSec: 1000 + i }));
    }

    const summary = getMetricsSummary({ metricsPath, maxRecentCooldowns: 3 });

    expect(summary.recentCooldowns).toHaveLength(3);
    // Should keep the last 3
    expect(summary.recentCooldowns[0].startedAt).toBe(107);
    expect(summary.recentCooldowns[1].startedAt).toBe(108);
    expect(summary.recentCooldowns[2].startedAt).toBe(109);
  });

  it("defaults to 50 max recent cooldowns", () => {
    for (let i = 0; i < 60; i++) {
      recordEvent(metricsPath, sampleEvent({ ts: 100 + i, cooldownSec: 1000 }));
    }

    const summary = getMetricsSummary({ metricsPath });
    expect(summary.recentCooldowns).toHaveLength(50);
  });

  it("excludes failover events from recentCooldowns", () => {
    recordEvent(metricsPath, sampleEvent({ ts: 100, cooldownSec: 1000 }));
    recordEvent(metricsPath, sampleEvent({ ts: 200, type: "failover", to: "provB/m2" }));
    recordEvent(metricsPath, sampleEvent({ ts: 300, cooldownSec: 2000 }));

    const summary = getMetricsSummary({ metricsPath });
    expect(summary.recentCooldowns).toHaveLength(2);
    expect(summary.recentCooldowns[0].startedAt).toBe(100);
    expect(summary.recentCooldowns[1].startedAt).toBe(300);
  });

  it("returns empty recentCooldowns when no cooldowns exist", () => {
    const summary = getMetricsSummary({
      metricsPath: path.join(tmpDir, "empty.jsonl"),
    });
    expect(summary.recentCooldowns).toHaveLength(0);
  });
});

// ---------------------------------------------------------------------------
// 17. recordRateLimit convenience function
// ---------------------------------------------------------------------------
describe("recordRateLimit", () => {
  it("records a rate_limit event with all fields", () => {
    recordRateLimit(metricsPath, {
      model: "provA/model1",
      provider: "provA",
      cooldownSec: 3600,
      reason: "429 Too Many Requests",
      trigger: "agent_end",
      session: "sess-abc",
    });

    const events = loadEvents(metricsPath);
    expect(events).toHaveLength(1);
    expect(events[0].type).toBe("rate_limit");
    expect(events[0].model).toBe("provA/model1");
    expect(events[0].provider).toBe("provA");
    expect(events[0].cooldownSec).toBe(3600);
    expect(events[0].reason).toBe("429 Too Many Requests");
    expect(events[0].trigger).toBe("agent_end");
    expect(events[0].session).toBe("sess-abc");
    expect(events[0].ts).toBeGreaterThan(0);
  });

  it("records without optional fields", () => {
    recordRateLimit(metricsPath, {
      model: "provA/model1",
      provider: "provA",
      cooldownSec: 1800,
    });

    const events = loadEvents(metricsPath);
    expect(events).toHaveLength(1);
    expect(events[0].reason).toBeUndefined();
    expect(events[0].trigger).toBeUndefined();
    expect(events[0].session).toBeUndefined();
  });
});

// ---------------------------------------------------------------------------
// 18. queryMetrics - unified query for /failover-status
// ---------------------------------------------------------------------------
describe("queryMetrics", () => {
  it("returns both summary and per-model histories", () => {
    recordEvent(metricsPath, sampleEvent({ ts: 100, model: "provA/m1", provider: "provA", cooldownSec: 1000 }));
    recordEvent(metricsPath, sampleEvent({ ts: 200, model: "provB/m2", provider: "provB", cooldownSec: 2000 }));
    recordEvent(metricsPath, sampleEvent({
      ts: 300,
      type: "failover",
      model: "provA/m1",
      provider: "provA",
      to: "provB/m2",
    }));

    const result = queryMetrics({ metricsPath });

    // Summary
    expect(result.summary.totalEvents).toBe(3);
    expect(result.summary.totalRateLimits).toBe(2);
    expect(result.summary.totalFailovers).toBe(1);

    // Model histories
    expect(Object.keys(result.modelHistories)).toHaveLength(2);
    expect(result.modelHistories["provA/m1"]).toBeDefined();
    expect(result.modelHistories["provA/m1"].totalErrors).toBe(1);
    expect(result.modelHistories["provA/m1"].failedToModels["provB/m2"]).toBe(1);
    expect(result.modelHistories["provB/m2"]).toBeDefined();
    expect(result.modelHistories["provB/m2"].totalErrors).toBe(1);
  });

  it("returns empty result when no events exist", () => {
    const result = queryMetrics({ metricsPath: path.join(tmpDir, "empty.jsonl") });

    expect(result.summary.totalEvents).toBe(0);
    expect(Object.keys(result.modelHistories)).toHaveLength(0);
  });

  it("respects time filtering", () => {
    recordEvent(metricsPath, sampleEvent({ ts: 100, cooldownSec: 1000 }));
    recordEvent(metricsPath, sampleEvent({ ts: 200, cooldownSec: 2000 }));
    recordEvent(metricsPath, sampleEvent({ ts: 300, cooldownSec: 3000 }));

    const result = queryMetrics({ metricsPath, since: 200, until: 300 });

    expect(result.summary.totalEvents).toBe(2);
    expect(result.modelHistories["provA/model1"].events).toHaveLength(2);
  });
});
