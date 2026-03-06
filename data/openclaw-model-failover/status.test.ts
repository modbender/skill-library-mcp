import { describe, it, expect, beforeEach, afterEach } from "vitest";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import {
  getFailoverStatus,
  clearModel,
  clearAllModels,
  formatDuration,
  formatStatus,
  type FailoverStatus,
} from "./status.js";
import {
  saveState,
  loadState,
  nowSec,
  type LimitState,
} from "./index.js";

// ---------------------------------------------------------------------------
// Test fixtures
// ---------------------------------------------------------------------------

const TEST_MODEL_ORDER = [
  "provA/model1",
  "provA/model2",
  "provB/model3",
  "provC/model4",
];

let tmpDir: string;
let statePath: string;

beforeEach(() => {
  tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "fo-status-"));
  statePath = path.join(tmpDir, "state.json");
});

afterEach(() => {
  fs.rmSync(tmpDir, { recursive: true, force: true });
});

// ---------------------------------------------------------------------------
// 1. formatDuration
// ---------------------------------------------------------------------------
describe("formatDuration", () => {
  it("formats zero or negative as 'now'", () => {
    expect(formatDuration(0)).toBe("now");
    expect(formatDuration(-5)).toBe("now");
  });

  it("formats seconds only (< 1 minute)", () => {
    expect(formatDuration(45)).toBe("45s");
  });

  it("formats minutes and seconds", () => {
    expect(formatDuration(125)).toBe("2m 5s");
  });

  it("formats hours and minutes (omits seconds)", () => {
    expect(formatDuration(3661)).toBe("1h 1m");
  });

  it("formats exact hours", () => {
    expect(formatDuration(7200)).toBe("2h");
  });

  it("formats minutes only", () => {
    expect(formatDuration(300)).toBe("5m");
  });
});

// ---------------------------------------------------------------------------
// 2. getFailoverStatus - empty state
// ---------------------------------------------------------------------------
describe("getFailoverStatus - empty state", () => {
  it("returns all models as available when no state file exists", () => {
    const status = getFailoverStatus({
      statePath: path.join(tmpDir, "nonexistent.json"),
      modelOrder: TEST_MODEL_ORDER,
    });

    expect(status.blockedCount).toBe(0);
    expect(status.availableCount).toBe(TEST_MODEL_ORDER.length);
    expect(status.activeModel).toBe("provA/model1");
    expect(status.models.every((m) => m.available)).toBe(true);
  });

  it("returns all models as available when state file is empty", () => {
    saveState(statePath, { limited: {} });
    const status = getFailoverStatus({
      statePath,
      modelOrder: TEST_MODEL_ORDER,
    });
    expect(status.blockedCount).toBe(0);
    expect(status.availableCount).toBe(TEST_MODEL_ORDER.length);
  });
});

// ---------------------------------------------------------------------------
// 3. getFailoverStatus - with blocked models
// ---------------------------------------------------------------------------
describe("getFailoverStatus - with blocked models", () => {
  it("reports blocked models with remaining time", () => {
    const now = nowSec();
    const state: LimitState = {
      limited: {
        "provA/model1": {
          lastHitAt: now - 60,
          nextAvailableAt: now + 3600,
          reason: "rate limit exceeded",
        },
        "provA/model2": {
          lastHitAt: now - 60,
          nextAvailableAt: now + 3600,
          reason: "Provider provA exhausted",
        },
      },
    };
    saveState(statePath, state);

    const status = getFailoverStatus({
      statePath,
      modelOrder: TEST_MODEL_ORDER,
    });

    expect(status.blockedCount).toBe(2);
    expect(status.availableCount).toBe(2);
    expect(status.activeModel).toBe("provB/model3");

    const blocked = status.models.filter((m) => !m.available);
    expect(blocked).toHaveLength(2);
    expect(blocked[0].model).toBe("provA/model1");
    expect(blocked[0].reason).toBe("rate limit exceeded");
    expect(blocked[0].remainingSeconds).toBeGreaterThan(3500);
    expect(blocked[0].remainingSeconds).toBeLessThanOrEqual(3600);
    expect(blocked[0].nextAvailableAt).toBeDefined();
  });

  it("treats expired cooldowns as available", () => {
    const now = nowSec();
    const state: LimitState = {
      limited: {
        "provA/model1": {
          lastHitAt: now - 7200,
          nextAvailableAt: now - 1, // expired
        },
      },
    };
    saveState(statePath, state);

    const status = getFailoverStatus({
      statePath,
      modelOrder: TEST_MODEL_ORDER,
    });

    expect(status.blockedCount).toBe(0);
    expect(status.availableCount).toBe(TEST_MODEL_ORDER.length);
    expect(status.activeModel).toBe("provA/model1");

    const m1 = status.models.find((m) => m.model === "provA/model1")!;
    expect(m1.available).toBe(true);
    // lastHitAt is still present for historical reference
    expect(m1.lastHitAt).toBeDefined();
    // but no remaining time or nextAvailableAt
    expect(m1.remainingSeconds).toBeUndefined();
    expect(m1.nextAvailableAt).toBeUndefined();
  });

  it("includes models from state not in configured order", () => {
    const now = nowSec();
    const state: LimitState = {
      limited: {
        "unknown-provider/stale-model": {
          lastHitAt: now - 60,
          nextAvailableAt: now + 1800,
          reason: "stale entry",
        },
      },
    };
    saveState(statePath, state);

    const status = getFailoverStatus({
      statePath,
      modelOrder: TEST_MODEL_ORDER,
    });

    // 4 from order + 1 stale = 5 total
    expect(status.models).toHaveLength(5);
    expect(status.blockedCount).toBe(1);

    const stale = status.models.find(
      (m) => m.model === "unknown-provider/stale-model",
    )!;
    expect(stale).toBeDefined();
    expect(stale.available).toBe(false);
    expect(stale.reason).toBe("stale entry");
  });
});

// ---------------------------------------------------------------------------
// 4. getFailoverStatus - all models blocked
// ---------------------------------------------------------------------------
describe("getFailoverStatus - all models blocked", () => {
  it("returns last model as active (fallback behavior)", () => {
    const now = nowSec();
    const state: LimitState = { limited: {} };
    for (const model of TEST_MODEL_ORDER) {
      state.limited[model] = {
        lastHitAt: now - 60,
        nextAvailableAt: now + 3600,
        reason: "all blocked",
      };
    }
    saveState(statePath, state);

    const status = getFailoverStatus({
      statePath,
      modelOrder: TEST_MODEL_ORDER,
    });

    expect(status.blockedCount).toBe(TEST_MODEL_ORDER.length);
    expect(status.availableCount).toBe(0);
    // firstAvailableModel returns the last model as ultimate fallback
    expect(status.activeModel).toBe("provC/model4");
  });
});

// ---------------------------------------------------------------------------
// 5. clearModel
// ---------------------------------------------------------------------------
describe("clearModel", () => {
  it("removes a specific model's rate-limit entry", () => {
    const now = nowSec();
    const state: LimitState = {
      limited: {
        "provA/model1": {
          lastHitAt: now,
          nextAvailableAt: now + 3600,
          reason: "rate limit",
        },
        "provB/model3": {
          lastHitAt: now,
          nextAvailableAt: now + 3600,
          reason: "rate limit",
        },
      },
    };
    saveState(statePath, state);

    const result = clearModel("provA/model1", statePath);
    expect(result).toBe(true);

    const updated = loadState(statePath);
    expect(updated.limited["provA/model1"]).toBeUndefined();
    expect(updated.limited["provB/model3"]).toBeDefined();
  });

  it("returns false when model is not in state", () => {
    saveState(statePath, { limited: {} });
    const result = clearModel("nonexistent/model", statePath);
    expect(result).toBe(false);
  });

  it("returns false when state file does not exist", () => {
    const result = clearModel(
      "provA/model1",
      path.join(tmpDir, "missing.json"),
    );
    expect(result).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// 6. clearAllModels
// ---------------------------------------------------------------------------
describe("clearAllModels", () => {
  it("removes all rate-limit entries and returns count", () => {
    const now = nowSec();
    const state: LimitState = {
      limited: {
        "provA/model1": {
          lastHitAt: now,
          nextAvailableAt: now + 3600,
        },
        "provA/model2": {
          lastHitAt: now,
          nextAvailableAt: now + 3600,
        },
        "provB/model3": {
          lastHitAt: now,
          nextAvailableAt: now + 1800,
        },
      },
    };
    saveState(statePath, state);

    const count = clearAllModels(statePath);
    expect(count).toBe(3);

    const updated = loadState(statePath);
    expect(Object.keys(updated.limited)).toHaveLength(0);
  });

  it("returns 0 when state is already empty", () => {
    saveState(statePath, { limited: {} });
    const count = clearAllModels(statePath);
    expect(count).toBe(0);
  });

  it("returns 0 when state file does not exist", () => {
    const count = clearAllModels(path.join(tmpDir, "missing.json"));
    expect(count).toBe(0);
  });
});

// ---------------------------------------------------------------------------
// 7. formatStatus
// ---------------------------------------------------------------------------
describe("formatStatus", () => {
  it("includes header and active model", () => {
    const status: FailoverStatus = {
      timestamp: nowSec(),
      statePath: "/tmp/state.json",
      models: [
        { model: "provA/m1", available: true },
        { model: "provB/m2", available: true },
      ],
      activeModel: "provA/m1",
      blockedCount: 0,
      availableCount: 2,
    };

    const output = formatStatus(status);
    expect(output).toContain("OpenClaw Model Failover Status");
    expect(output).toContain("Active model : provA/m1");
    expect(output).toContain("2 available, 0 blocked");
    expect(output).toContain("[OK     ] provA/m1");
    expect(output).toContain("[OK     ] provB/m2");
  });

  it("shows blocked model details", () => {
    const now = nowSec();
    const status: FailoverStatus = {
      timestamp: now,
      statePath: "/tmp/state.json",
      models: [
        {
          model: "provA/m1",
          available: false,
          reason: "rate limit exceeded",
          lastHitAt: now - 60,
          nextAvailableAt: now + 3540,
          remainingSeconds: 3540,
        },
        { model: "provB/m2", available: true },
      ],
      activeModel: "provB/m2",
      blockedCount: 1,
      availableCount: 1,
    };

    const output = formatStatus(status);
    expect(output).toContain("Blocked models:");
    expect(output).toContain("- provA/m1");
    expect(output).toContain("rate limit exceeded");
    expect(output).toContain("[BLOCKED] provA/m1");
    expect(output).toContain("[OK     ] provB/m2");
  });

  it("handles no active model gracefully", () => {
    const status: FailoverStatus = {
      timestamp: nowSec(),
      statePath: "/tmp/state.json",
      models: [],
      activeModel: undefined,
      blockedCount: 0,
      availableCount: 0,
    };

    const output = formatStatus(status);
    expect(output).toContain("Active model : (none)");
  });
});
