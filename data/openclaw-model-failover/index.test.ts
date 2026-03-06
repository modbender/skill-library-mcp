import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { spawn } from "node:child_process";
import register, {
  nowSec,
  getNextMidnightPT,
  getNextMidnightUTC,
  parseWaitTime,
  calculateCooldown,
  isRateLimitLike,
  isAuthOrScopeLike,
  isTemporarilyUnavailableLike,
  loadState,
  saveState,
  atomicWriteFile,
  firstAvailableModel,
  expandHome,
  type LimitState,
} from "./index.js";

vi.mock("node:child_process", () => ({
  spawn: vi.fn(() => ({ unref: vi.fn() })),
}));

vi.mock("./metrics.js", () => ({
  recordEvent: vi.fn(),
  DEFAULT_METRICS_FILE: "~/.openclaw/workspace/memory/model-failover-metrics.jsonl",
}));

// ---------------------------------------------------------------------------
// 1. Rate-limit detection
// ---------------------------------------------------------------------------
describe("isRateLimitLike", () => {
  it("detects 429 status code in error string", () => {
    expect(isRateLimitLike("Error: 429 Too Many Requests")).toBe(true);
  });

  it("detects quota exhaustion", () => {
    expect(isRateLimitLike("Quota exceeded for quota metric 'Queries'")).toBe(true);
  });

  it("detects 'rate limit' text", () => {
    expect(isRateLimitLike("API rate limit reached")).toBe(true);
  });

  it("detects 'resource_exhausted'", () => {
    expect(isRateLimitLike("RESOURCE_EXHAUSTED: out of capacity")).toBe(true);
  });

  it("detects 'too many requests'", () => {
    expect(isRateLimitLike("too many requests, slow down")).toBe(true);
  });

  it("returns false for unrelated errors", () => {
    expect(isRateLimitLike("Connection refused")).toBe(false);
    expect(isRateLimitLike("ENOTFOUND")).toBe(false);
    expect(isRateLimitLike(undefined)).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// 2. Auth/scope error detection
// ---------------------------------------------------------------------------
describe("isAuthOrScopeLike", () => {
  it("detects HTTP 401", () => {
    expect(isAuthOrScopeLike("HTTP 401 Unauthorized")).toBe(true);
  });

  it("detects missing scopes", () => {
    expect(isAuthOrScopeLike("Missing scopes: api.responses.write")).toBe(true);
  });

  it("detects invalid api key", () => {
    expect(isAuthOrScopeLike("Invalid API key provided")).toBe(true);
  });

  it("returns false for rate-limit errors", () => {
    expect(isAuthOrScopeLike("429 Too Many Requests")).toBe(false);
  });

  it("returns false for undefined", () => {
    expect(isAuthOrScopeLike(undefined)).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// 3. Temporarily unavailable detection
// ---------------------------------------------------------------------------
describe("isTemporarilyUnavailableLike", () => {
  it("detects 'plugin is in cooldown'", () => {
    expect(isTemporarilyUnavailableLike("plugin is in cooldown")).toBe(true);
  });

  it("detects 'temporarily unavailable'", () => {
    expect(isTemporarilyUnavailableLike("Service temporarily unavailable")).toBe(true);
  });

  it("detects copilot-proxy mention", () => {
    expect(isTemporarilyUnavailableLike("copilot-proxy not responding")).toBe(true);
  });

  it("detects 'temporarily overloaded' (gateway chat message)", () => {
    expect(isTemporarilyUnavailableLike("The AI service is temporarily overloaded. Please try again in a moment.")).toBe(true);
  });

  it("detects bare 'overloaded'", () => {
    expect(isTemporarilyUnavailableLike("Overloaded")).toBe(true);
  });

  it("detects HTTP 529 (Anthropic overloaded status)", () => {
    expect(isTemporarilyUnavailableLike("HTTP 529")).toBe(true);
  });

  it("detects 'service is temporarily'", () => {
    expect(isTemporarilyUnavailableLike("service is temporarily down")).toBe(true);
  });

  it("returns false for unrelated errors", () => {
    expect(isTemporarilyUnavailableLike("Syntax error")).toBe(false);
    expect(isTemporarilyUnavailableLike(undefined)).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// 4. parseWaitTime
// ---------------------------------------------------------------------------
describe("parseWaitTime", () => {
  it("parses 'in Xm' format", () => {
    expect(parseWaitTime("Try again in 4m30s")).toBe(240); // 4 minutes
  });

  it("parses 'in Xs' format", () => {
    expect(parseWaitTime("Try again in 30s")).toBe(30);
  });

  it("parses 'in Xh' format", () => {
    expect(parseWaitTime("Try again in 2h")).toBe(7200);
  });

  it("parses 'after X seconds' format", () => {
    expect(parseWaitTime("Retry after 60 seconds")).toBe(60);
  });

  it("returns undefined for unparseable errors", () => {
    expect(parseWaitTime("Unknown error occurred")).toBeUndefined();
  });
});

// ---------------------------------------------------------------------------
// 5. Cooldown calculation
// ---------------------------------------------------------------------------
describe("calculateCooldown", () => {
  it("returns default cooldown in seconds when no error provided", () => {
    // default 60 minutes = 3600 seconds
    expect(calculateCooldown("openai", undefined, 60)).toBe(3600);
  });

  it("uses parsed wait time when error contains retry timing", () => {
    expect(calculateCooldown("openai", "Try again in 5m", 60)).toBe(300);
  });

  it("returns 1 hour for openai rolling window", () => {
    expect(calculateCooldown("openai", "rate limit exceeded")).toBe(3600);
  });

  it("returns time until PT midnight for google quota errors", () => {
    const result = calculateCooldown("google-gemini-cli", "Quota exceeded");
    const expectedApprox = getNextMidnightPT() - nowSec();
    // Allow 2 second variance for execution time
    expect(Math.abs(result - expectedApprox)).toBeLessThan(3);
  });

  it("returns time until UTC midnight for anthropic daily errors", () => {
    const result = calculateCooldown("anthropic", "daily limit exceeded");
    const expectedApprox = getNextMidnightUTC() - nowSec();
    // Allow 2 second variance
    expect(Math.abs(result - expectedApprox)).toBeLessThan(3);
  });

  it("uses custom default minutes", () => {
    expect(calculateCooldown("unknown-provider", "some error", 120)).toBe(7200);
  });
});

// ---------------------------------------------------------------------------
// 6. Model selection (firstAvailableModel)
// ---------------------------------------------------------------------------
describe("firstAvailableModel", () => {
  const modelOrder = [
    "openai-codex/gpt-5.3",
    "anthropic/claude-opus",
    "google-gemini-cli/gemini-pro",
  ];

  it("returns the first model when nothing is limited", () => {
    const state: LimitState = { limited: {} };
    expect(firstAvailableModel(modelOrder, state)).toBe("openai-codex/gpt-5.3");
  });

  it("skips limited models and returns the next available one", () => {
    const futureTs = nowSec() + 3600;
    const state: LimitState = {
      limited: {
        "openai-codex/gpt-5.3": {
          lastHitAt: nowSec(),
          nextAvailableAt: futureTs,
          reason: "rate limit",
        },
      },
    };
    expect(firstAvailableModel(modelOrder, state)).toBe("anthropic/claude-opus");
  });

  it("skips multiple limited models", () => {
    const futureTs = nowSec() + 3600;
    const state: LimitState = {
      limited: {
        "openai-codex/gpt-5.3": {
          lastHitAt: nowSec(),
          nextAvailableAt: futureTs,
        },
        "anthropic/claude-opus": {
          lastHitAt: nowSec(),
          nextAvailableAt: futureTs,
        },
      },
    };
    expect(firstAvailableModel(modelOrder, state)).toBe("google-gemini-cli/gemini-pro");
  });

  it("returns a model whose cooldown has expired", () => {
    const pastTs = nowSec() - 10; // expired 10 seconds ago
    const state: LimitState = {
      limited: {
        "openai-codex/gpt-5.3": {
          lastHitAt: nowSec() - 3600,
          nextAvailableAt: pastTs,
        },
      },
    };
    expect(firstAvailableModel(modelOrder, state)).toBe("openai-codex/gpt-5.3");
  });

  it("returns last model as ultimate fallback when all are limited", () => {
    const futureTs = nowSec() + 3600;
    const state: LimitState = {
      limited: {
        "openai-codex/gpt-5.3": { lastHitAt: nowSec(), nextAvailableAt: futureTs },
        "anthropic/claude-opus": { lastHitAt: nowSec(), nextAvailableAt: futureTs },
        "google-gemini-cli/gemini-pro": { lastHitAt: nowSec(), nextAvailableAt: futureTs },
      },
    };
    expect(firstAvailableModel(modelOrder, state)).toBe("google-gemini-cli/gemini-pro");
  });

  it("returns undefined for empty model order", () => {
    expect(firstAvailableModel([], { limited: {} })).toBeUndefined();
  });
});

// ---------------------------------------------------------------------------
// 7. getNextMidnightPT - DST-aware (Issue #2 fix verification)
// ---------------------------------------------------------------------------
describe("getNextMidnightPT", () => {
  it("returns a timestamp in the future", () => {
    const midnight = getNextMidnightPT();
    expect(midnight).toBeGreaterThan(nowSec());
  });

  it("returns a timestamp no more than ~25 hours from now", () => {
    const midnight = getNextMidnightPT();
    const maxDelta = 25 * 3600; // 25 hours to account for edge cases
    expect(midnight - nowSec()).toBeLessThanOrEqual(maxDelta);
  });

  it("midnight PT corresponds to 00:00 in America/Los_Angeles", () => {
    const midnightSec = getNextMidnightPT();
    const midnightDate = new Date(midnightSec * 1000);
    // Format the timestamp in PT and check it represents midnight.
    // Intl.DateTimeFormat with hour12:false may return "24" for midnight in some
    // engines/locales (end-of-day representation), so accept both "00" and "24".
    const fmt = new Intl.DateTimeFormat("en-US", {
      timeZone: "America/Los_Angeles",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
    const parts = fmt.formatToParts(midnightDate);
    const hour = parts.find((p) => p.type === "hour")?.value;
    const minute = parts.find((p) => p.type === "minute")?.value;
    const second = parts.find((p) => p.type === "second")?.value;
    expect(["00", "24"]).toContain(hour);
    expect(minute).toBe("00");
    expect(second).toBe("00");
  });
});

// ---------------------------------------------------------------------------
// 7b. getNextMidnightPT - DST transition edge cases (Issue #2 core fix)
// ---------------------------------------------------------------------------
describe("getNextMidnightPT DST transitions", () => {
  // Helper: format a UTC timestamp in PT and return { hour, day, month }
  function formatInPT(utcMs: number) {
    const fmt = new Intl.DateTimeFormat("en-US", {
      timeZone: "America/Los_Angeles",
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
    const parts = fmt.formatToParts(new Date(utcMs));
    const get = (type: string) =>
      parts.find((p) => p.type === type)?.value ?? "0";
    return {
      year: parseInt(get("year"), 10),
      month: parseInt(get("month"), 10),
      day: parseInt(get("day"), 10),
      hour: parseInt(get("hour"), 10),
      minute: parseInt(get("minute"), 10),
    };
  }

  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("normal PST day: Jan 15, 2025 3 PM PST -> midnight Jan 16 PST", () => {
    // Jan 15, 2025 3:00 PM PST = Jan 15 23:00 UTC
    vi.setSystemTime(new Date("2025-01-15T23:00:00Z"));
    const midnight = getNextMidnightPT();
    // Jan 16 00:00 PST = Jan 16 08:00 UTC
    const expected = Math.floor(Date.UTC(2025, 0, 16, 8, 0, 0) / 1000);
    expect(midnight).toBe(expected);
  });

  it("normal PDT day: Jul 15, 2025 3 PM PDT -> midnight Jul 16 PDT", () => {
    // Jul 15, 2025 3:00 PM PDT = Jul 15 22:00 UTC
    vi.setSystemTime(new Date("2025-07-15T22:00:00Z"));
    const midnight = getNextMidnightPT();
    // Jul 16 00:00 PDT = Jul 16 07:00 UTC
    const expected = Math.floor(Date.UTC(2025, 6, 16, 7, 0, 0) / 1000);
    expect(midnight).toBe(expected);
  });

  it("spring forward: PST day before transition, next midnight is still PST", () => {
    // March 8, 2025 11:00 PM PST = March 9 07:00 UTC
    // Spring forward on March 9 at 2:00 AM PST = 10:00 UTC
    // Next midnight = March 9 00:00 is past, so next = March 9 00:00? No...
    // Actually at 11 PM March 8, next midnight is March 9 00:00 which is
    // only 1 hour away and still in PST (before the 2 AM transition).
    // Wait - 11 PM PST on March 8 means the next midnight is March 9 00:00 PST.
    // That's March 9 08:00 UTC. The DST change at March 9 10:00 UTC is AFTER that.
    vi.setSystemTime(new Date("2025-03-09T07:00:00Z"));
    const midnight = getNextMidnightPT();
    // Next midnight PT from 11 PM March 8 PST = March 9 00:00 PST = March 9 08:00 UTC
    const expected = Math.floor(Date.UTC(2025, 2, 9, 8, 0, 0) / 1000);
    expect(midnight).toBe(expected);
  });

  it("spring forward: 1:30 AM PST on transition day, next midnight is PDT (bug case)", () => {
    // March 9, 2025 at 1:30 AM PST = March 9 09:30 UTC
    // Spring forward at 2:00 AM PST (10:00 UTC): clocks jump to 3:00 AM PDT
    // Next midnight = March 10 00:00 PDT = March 10 07:00 UTC
    vi.setSystemTime(new Date("2025-03-09T09:30:00Z"));
    const midnight = getNextMidnightPT();
    const expected = Math.floor(Date.UTC(2025, 2, 10, 7, 0, 0) / 1000);
    expect(midnight).toBe(expected);
    // Verify it's actually midnight PT
    const pt = formatInPT(midnight * 1000);
    expect(pt.hour === 0 || pt.hour === 24).toBe(true);
    expect(pt.minute).toBe(0);
    expect(pt.day).toBe(10);
    expect(pt.month).toBe(3);
  });

  it("spring forward: 4 PM PDT after transition, next midnight is PDT", () => {
    // March 9, 2025 at 4:00 PM PDT = March 9 23:00 UTC
    vi.setSystemTime(new Date("2025-03-09T23:00:00Z"));
    const midnight = getNextMidnightPT();
    // March 10 00:00 PDT = March 10 07:00 UTC
    const expected = Math.floor(Date.UTC(2025, 2, 10, 7, 0, 0) / 1000);
    expect(midnight).toBe(expected);
  });

  it("fall back: 12:30 AM PDT on transition day, next midnight is PST (bug case)", () => {
    // November 2, 2025 at 12:30 AM PDT = November 2 07:30 UTC
    // Fall back at 2:00 AM PDT (09:00 UTC): clocks go to 1:00 AM PST
    // Next midnight = November 3 00:00 PST = November 3 08:00 UTC
    vi.setSystemTime(new Date("2025-11-02T07:30:00Z"));
    const midnight = getNextMidnightPT();
    const expected = Math.floor(Date.UTC(2025, 10, 3, 8, 0, 0) / 1000);
    expect(midnight).toBe(expected);
    // Verify it's actually midnight PT
    const pt = formatInPT(midnight * 1000);
    expect(pt.hour === 0 || pt.hour === 24).toBe(true);
    expect(pt.minute).toBe(0);
    expect(pt.day).toBe(3);
    expect(pt.month).toBe(11);
  });

  it("fall back: 3 AM PST after transition, next midnight is PST", () => {
    // November 2, 2025 at 3:00 AM PST = November 2 11:00 UTC
    vi.setSystemTime(new Date("2025-11-02T11:00:00Z"));
    const midnight = getNextMidnightPT();
    // November 3 00:00 PST = November 3 08:00 UTC
    const expected = Math.floor(Date.UTC(2025, 10, 3, 8, 0, 0) / 1000);
    expect(midnight).toBe(expected);
  });

  it("fall back: 11 PM PDT night before transition, next midnight is PDT", () => {
    // November 1, 2025 at 11:00 PM PDT = November 2 06:00 UTC
    // Next midnight = November 2 00:00 PDT = November 2 07:00 UTC
    // (Midnight Nov 2 is before the 2 AM fall-back, so still PDT)
    vi.setSystemTime(new Date("2025-11-02T06:00:00Z"));
    const midnight = getNextMidnightPT();
    const expected = Math.floor(Date.UTC(2025, 10, 2, 7, 0, 0) / 1000);
    expect(midnight).toBe(expected);
  });
});

// ---------------------------------------------------------------------------
// 8. getNextMidnightUTC
// ---------------------------------------------------------------------------
describe("getNextMidnightUTC", () => {
  it("returns a timestamp in the future", () => {
    expect(getNextMidnightUTC()).toBeGreaterThan(nowSec());
  });

  it("corresponds to 00:00:00 UTC", () => {
    const ts = getNextMidnightUTC();
    const d = new Date(ts * 1000);
    expect(d.getUTCHours()).toBe(0);
    expect(d.getUTCMinutes()).toBe(0);
    expect(d.getUTCSeconds()).toBe(0);
  });
});

// ---------------------------------------------------------------------------
// 8b. atomicWriteFile utility
// ---------------------------------------------------------------------------
describe("atomicWriteFile", () => {
  let tmpDir: string;

  beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "awf-test-"));
  });

  afterEach(() => {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  it("writes data to the target file", () => {
    const target = path.join(tmpDir, "out.json");
    atomicWriteFile(target, '{"hello":"world"}');
    expect(fs.readFileSync(target, "utf-8")).toBe('{"hello":"world"}');
  });

  it("creates parent directories if they do not exist", () => {
    const target = path.join(tmpDir, "deep", "nested", "dir", "file.txt");
    atomicWriteFile(target, "content");
    expect(fs.existsSync(target)).toBe(true);
    expect(fs.readFileSync(target, "utf-8")).toBe("content");
  });

  it("does not leave a .tmp file after successful write", () => {
    const target = path.join(tmpDir, "clean.json");
    atomicWriteFile(target, "data");
    expect(fs.existsSync(target)).toBe(true);
    expect(fs.existsSync(target + ".tmp")).toBe(false);
  });

  it("preserves existing file when temp write fails", () => {
    const target = path.join(tmpDir, "keep.json");
    atomicWriteFile(target, "original");

    // Place a directory at the .tmp path to force writeFileSync to fail
    fs.mkdirSync(target + ".tmp", { recursive: true });

    expect(() => atomicWriteFile(target, "replacement")).toThrow();
    expect(fs.readFileSync(target, "utf-8")).toBe("original");
  });

  it("overwrites existing file atomically", () => {
    const target = path.join(tmpDir, "replace.json");
    atomicWriteFile(target, "first");
    atomicWriteFile(target, "second");
    expect(fs.readFileSync(target, "utf-8")).toBe("second");
  });
});

// ---------------------------------------------------------------------------
// 9. State persistence (loadState / saveState)
// ---------------------------------------------------------------------------
describe("loadState / saveState", () => {
  let tmpDir: string;
  let tmpFile: string;

  beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "failover-test-"));
    tmpFile = path.join(tmpDir, "state.json");
  });

  afterEach(() => {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  it("returns empty state when file does not exist", () => {
    const state = loadState(path.join(tmpDir, "nonexistent.json"));
    expect(state).toEqual({ limited: {} });
  });

  it("round-trips state through save and load", () => {
    const original: LimitState = {
      limited: {
        "openai/gpt-4": {
          lastHitAt: 1000000,
          nextAvailableAt: 1003600,
          reason: "rate limit",
        },
      },
    };
    saveState(tmpFile, original);
    const loaded = loadState(tmpFile);
    expect(loaded).toEqual(original);
  });

  it("handles corrupted JSON gracefully", () => {
    fs.writeFileSync(tmpFile, "not valid json {{{");
    const state = loadState(tmpFile);
    expect(state).toEqual({ limited: {} });
  });

  it("creates parent directories when saving", () => {
    const deepPath = path.join(tmpDir, "a", "b", "c", "state.json");
    const state: LimitState = { limited: {} };
    saveState(deepPath, state);
    expect(fs.existsSync(deepPath)).toBe(true);
  });

  it("does not leave a .tmp file after successful save (atomic write)", () => {
    const state: LimitState = {
      limited: {
        "test/model": { lastHitAt: 1000, nextAvailableAt: 2000 },
      },
    };
    saveState(tmpFile, state);
    expect(fs.existsSync(tmpFile)).toBe(true);
    expect(fs.existsSync(tmpFile + ".tmp")).toBe(false);
  });

  it("preserves existing state file when write of temp file fails", () => {
    // Save initial valid state
    const original: LimitState = {
      limited: {
        "openai/gpt-4": { lastHitAt: 100, nextAvailableAt: 200 },
      },
    };
    saveState(tmpFile, original);

    // Attempt to save to an unwritable temp path by making the directory read-only.
    // Use a subdirectory so we can control permissions.
    const subDir = path.join(tmpDir, "readonly");
    const subFile = path.join(subDir, "state.json");
    fs.mkdirSync(subDir, { recursive: true });
    fs.writeFileSync(subFile, JSON.stringify(original, null, 2));

    // Make the .tmp target unwritable by placing a directory at .tmp path
    fs.mkdirSync(subFile + ".tmp", { recursive: true });

    expect(() =>
      saveState(subFile, { limited: { "broken/m": { lastHitAt: 1, nextAvailableAt: 2 } } })
    ).toThrow();

    // Original file should remain intact
    const preserved = loadState(subFile);
    expect(preserved).toEqual(original);
  });

  it("overwrites existing state file atomically", () => {
    const state1: LimitState = {
      limited: { "m/a": { lastHitAt: 1, nextAvailableAt: 2 } },
    };
    const state2: LimitState = {
      limited: { "m/b": { lastHitAt: 3, nextAvailableAt: 4 } },
    };
    saveState(tmpFile, state1);
    saveState(tmpFile, state2);
    const loaded = loadState(tmpFile);
    expect(loaded).toEqual(state2);
    expect(loaded.limited["m/a"]).toBeUndefined();
  });
});

// ---------------------------------------------------------------------------
// 10. unavailableCooldownMinutes logic
// ---------------------------------------------------------------------------
describe("unavailableCooldownMinutes logic", () => {
  it("calculateCooldown respects custom default minutes for unavailable errors", () => {
    // When a "temporarily unavailable" error is detected, the caller passes
    // unavailableCooldownMinutes (e.g. 15) as defaultMinutes.
    // Since the error doesn't match provider-specific patterns, it falls through
    // to the generic default.
    const cooldown = calculateCooldown("some-provider", "service unavailable", 15);
    expect(cooldown).toBe(15 * 60); // 900 seconds
  });

  it("unavailable cooldown is shorter than rate-limit cooldown", () => {
    const unavailableCd = calculateCooldown("some-provider", "service unavailable", 15);
    const rateLimitCd = calculateCooldown("some-provider", "rate limit hit", 300);
    expect(unavailableCd).toBeLessThan(rateLimitCd);
  });
});

// ---------------------------------------------------------------------------
// 11. expandHome
// ---------------------------------------------------------------------------
describe("expandHome", () => {
  it("expands ~ to home directory", () => {
    expect(expandHome("~")).toBe(os.homedir());
  });

  it("expands ~/ prefix", () => {
    const result = expandHome("~/.openclaw/state.json");
    expect(result).toBe(path.join(os.homedir(), ".openclaw/state.json"));
  });

  it("returns non-tilde paths unchanged", () => {
    expect(expandHome("/tmp/state.json")).toBe("/tmp/state.json");
  });

  it("returns empty string unchanged", () => {
    expect(expandHome("")).toBe("");
  });
});

// ---------------------------------------------------------------------------
// 12. Provider-wide blocking simulation (integration-like)
// ---------------------------------------------------------------------------
describe("provider-wide blocking", () => {
  it("blocks all models from the same provider on rate limit", () => {
    const modelOrder = [
      "openai-codex/gpt-5.3",
      "openai-codex/gpt-5.2",
      "anthropic/claude-opus",
      "google-gemini-cli/gemini-pro",
    ];

    const state: LimitState = { limited: {} };
    const failedModel = "openai-codex/gpt-5.3";
    const provider = failedModel.split("/")[0];
    const hitAt = nowSec();
    const nextAvail = hitAt + 3600;

    // Simulate provider-wide blocking as index.ts does in agent_end handler
    for (const m of modelOrder) {
      if (m.startsWith(provider + "/")) {
        state.limited[m] = {
          lastHitAt: hitAt,
          nextAvailableAt: nextAvail,
          reason: `Provider ${provider} exhausted`,
        };
      }
    }

    // Both openai-codex models should be blocked
    expect(state.limited["openai-codex/gpt-5.3"]).toBeDefined();
    expect(state.limited["openai-codex/gpt-5.2"]).toBeDefined();
    // Other providers should NOT be blocked
    expect(state.limited["anthropic/claude-opus"]).toBeUndefined();
    expect(state.limited["google-gemini-cli/gemini-pro"]).toBeUndefined();

    // firstAvailableModel should skip the blocked provider
    const fallback = firstAvailableModel(modelOrder, state);
    expect(fallback).toBe("anthropic/claude-opus");
  });
});

// ---------------------------------------------------------------------------
// Helpers for register() integration tests
// ---------------------------------------------------------------------------
function createMockApi(opts: {
  pluginConfig?: Record<string, any>;
  gatewayConfig?: any;
} = {}) {
  const handlers: Record<string, Function> = {};
  const logs: string[] = [];

  const api: any = {
    pluginConfig: opts.pluginConfig ?? {},
    logger: {
      info: (msg: string) => logs.push(msg),
      warn: (msg: string) => logs.push(msg),
    },
    on: vi.fn((event: string, handler: Function) => {
      handlers[event] = handler;
    }),
    runtime: {
      config: {
        loadConfig: vi.fn(() => opts.gatewayConfig ?? null),
      },
    },
  };

  return { api, handlers, logs };
}

function writeSessionsJson(homeDir: string, data: Record<string, any>) {
  const dir = path.join(homeDir, ".openclaw", "agents", "main", "sessions");
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, "sessions.json"), JSON.stringify(data));
}

// ---------------------------------------------------------------------------
// 13. register() - Plugin registration basics
// ---------------------------------------------------------------------------
describe("register()", () => {
  let tmpDir: string;
  let statePath: string;
  let fakeHome: string;

  beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "fo-reg-"));
    statePath = path.join(tmpDir, "state.json");
    fakeHome = path.join(tmpDir, "home");
    fs.mkdirSync(fakeHome, { recursive: true });
    vi.spyOn(os, "homedir").mockReturnValue(fakeHome);
    vi.mocked(spawn).mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  it("does not register handlers when enabled=false", () => {
    const { api } = createMockApi({ pluginConfig: { enabled: false } });
    register(api);
    expect(api.on).not.toHaveBeenCalled();
  });

  it("registers before_model_resolve, agent_end, and message_sent handlers", () => {
    const { api } = createMockApi({
      pluginConfig: { stateFile: statePath, restartOnSwitch: false },
    });
    register(api);
    const events = api.on.mock.calls.map((c: any[]) => c[0]);
    expect(events).toContain("before_model_resolve");
    expect(events).toContain("agent_end");
    expect(events).toContain("message_sent");
  });
});

// ---------------------------------------------------------------------------
// 14. before_model_resolve handler
// ---------------------------------------------------------------------------
describe("before_model_resolve handler", () => {
  const models = ["modelA/one", "modelB/two", "modelC/three"];
  let tmpDir: string;
  let statePath: string;
  let fakeHome: string;

  beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "fo-bmr-"));
    statePath = path.join(tmpDir, "state.json");
    fakeHome = path.join(tmpDir, "home");
    fs.mkdirSync(fakeHome, { recursive: true });
    vi.spyOn(os, "homedir").mockReturnValue(fakeHome);
    vi.mocked(spawn).mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  function setup(pluginConfig: Record<string, any> = {}) {
    const cfg = {
      stateFile: statePath,
      modelOrder: models,
      restartOnSwitch: false,
      ...pluginConfig,
    };
    const { api, handlers, logs } = createMockApi({ pluginConfig: cfg });
    register(api);
    return { handlers, logs };
  }

  it("returns no override when there is no pinned model", () => {
    const { handlers } = setup();
    const result = handlers["before_model_resolve"]({}, { sessionKey: "s1" });
    expect(result).toBeUndefined();
  });

  it("returns override when forceOverride is true", () => {
    const { handlers } = setup({ forceOverride: true });
    const result = handlers["before_model_resolve"]({}, { sessionKey: "s1" });
    expect(result).toEqual({ modelOverride: "modelA/one" });
  });

  it("returns no override when pinned model is available", () => {
    writeSessionsJson(fakeHome, { s1: { model: "modelA/one" } });
    const { handlers } = setup();
    const result = handlers["before_model_resolve"]({}, { sessionKey: "s1" });
    expect(result).toBeUndefined();
  });

  it("overrides when pinned model is rate-limited", () => {
    writeSessionsJson(fakeHome, { s1: { model: "modelA/one" } });
    const state: LimitState = {
      limited: {
        "modelA/one": {
          lastHitAt: nowSec(),
          nextAvailableAt: nowSec() + 3600,
          reason: "rate limit",
        },
      },
    };
    saveState(statePath, state);
    const { handlers } = setup();
    const result = handlers["before_model_resolve"]({}, { sessionKey: "s1" });
    expect(result).toEqual({ modelOverride: "modelB/two" });
  });

  it("skips multiple limited models to find fallback", () => {
    writeSessionsJson(fakeHome, { s1: { model: "modelA/one" } });
    const state: LimitState = {
      limited: {
        "modelA/one": {
          lastHitAt: nowSec(),
          nextAvailableAt: nowSec() + 3600,
        },
        "modelB/two": {
          lastHitAt: nowSec(),
          nextAvailableAt: nowSec() + 3600,
        },
      },
    };
    saveState(statePath, state);
    const { handlers } = setup();
    const result = handlers["before_model_resolve"]({}, { sessionKey: "s1" });
    expect(result).toEqual({ modelOverride: "modelC/three" });
  });

  it("overrides when pinned model is not in model order", () => {
    writeSessionsJson(fakeHome, { s1: { model: "unknown/model" } });
    const { handlers } = setup();
    const result = handlers["before_model_resolve"]({}, { sessionKey: "s1" });
    expect(result).toEqual({ modelOverride: "modelA/one" });
  });
});

// ---------------------------------------------------------------------------
// 15. agent_end handler
// ---------------------------------------------------------------------------
describe("agent_end handler", () => {
  const models = [
    "provA/model1",
    "provA/model2",
    "provB/model3",
    "provC/model4",
  ];
  let tmpDir: string;
  let statePath: string;
  let fakeHome: string;

  beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "fo-ae-"));
    statePath = path.join(tmpDir, "state.json");
    fakeHome = path.join(tmpDir, "home");
    fs.mkdirSync(fakeHome, { recursive: true });
    vi.spyOn(os, "homedir").mockReturnValue(fakeHome);
    vi.mocked(spawn).mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  function setup(pluginConfig: Record<string, any> = {}) {
    const cfg = {
      stateFile: statePath,
      modelOrder: models,
      restartOnSwitch: false,
      ...pluginConfig,
    };
    const { api, handlers, logs } = createMockApi({ pluginConfig: cfg });
    register(api);
    return { handlers, logs };
  }

  it("ignores successful events", () => {
    const { handlers } = setup();
    handlers["agent_end"]({ success: true }, { model: "provA/model1", sessionKey: "s1" });
    const state = loadState(statePath);
    expect(Object.keys(state.limited)).toHaveLength(0);
  });

  it("ignores non-rate-limit/non-auth errors", () => {
    const { handlers } = setup();
    handlers["agent_end"](
      { success: false, error: "Connection timeout" },
      { model: "provA/model1", sessionKey: "s1" }
    );
    const state = loadState(statePath);
    expect(Object.keys(state.limited)).toHaveLength(0);
  });

  it("blocks all models from same provider on rate limit", () => {
    const { handlers } = setup();
    handlers["agent_end"](
      { success: false, error: "429 Too Many Requests" },
      { model: "provA/model1", sessionKey: "s1" }
    );
    const state = loadState(statePath);
    expect(state.limited["provA/model1"]).toBeDefined();
    expect(state.limited["provA/model2"]).toBeDefined();
    expect(state.limited["provB/model3"]).toBeUndefined();
    expect(state.limited["provC/model4"]).toBeUndefined();
  });

  it("blocks only the specific model on auth error (not provider-wide)", () => {
    const { handlers } = setup();
    handlers["agent_end"](
      { success: false, error: "HTTP 401 Unauthorized" },
      { model: "provA/model1", sessionKey: "s1" }
    );
    const state = loadState(statePath);
    expect(state.limited["provA/model1"]).toBeDefined();
    expect(state.limited["provA/model2"]).toBeUndefined();
  });

  it("uses shorter cooldown for unavailable errors", () => {
    const { handlers } = setup({ unavailableCooldownMinutes: 10, cooldownMinutes: 300 });
    handlers["agent_end"](
      { success: false, error: "plugin is in cooldown" },
      { model: "provA/model1", sessionKey: "s1" }
    );
    const state = loadState(statePath);
    const entry = state.limited["provA/model1"];
    expect(entry).toBeDefined();
    const cooldownSec = entry!.nextAvailableAt - entry!.lastHitAt;
    // unavailableCooldownMinutes = 10 -> 600 seconds
    expect(cooldownSec).toBeGreaterThanOrEqual(595);
    expect(cooldownSec).toBeLessThanOrEqual(605);
  });

  it("patches sessions.json with fallback model", () => {
    writeSessionsJson(fakeHome, { s1: { model: "provA/model1" } });
    const { handlers } = setup({ patchSessionPins: true });
    handlers["agent_end"](
      { success: false, error: "429 Too Many Requests" },
      { model: "provA/model1", sessionKey: "s1" }
    );
    const sessionsPath = path.join(fakeHome, ".openclaw", "agents", "main", "sessions", "sessions.json");
    const sessions = JSON.parse(fs.readFileSync(sessionsPath, "utf-8"));
    expect(sessions.s1.model).toBe("provB/model3");
  });

  it("patches sessions.json atomically (no .tmp left behind)", () => {
    writeSessionsJson(fakeHome, { s1: { model: "provA/model1" } });
    const { handlers } = setup({ patchSessionPins: true });
    handlers["agent_end"](
      { success: false, error: "429 Too Many Requests" },
      { model: "provA/model1", sessionKey: "s1" }
    );
    const sessionsPath = path.join(fakeHome, ".openclaw", "agents", "main", "sessions", "sessions.json");
    expect(fs.existsSync(sessionsPath)).toBe(true);
    expect(fs.existsSync(sessionsPath + ".tmp")).toBe(false);
    // Verify the content is valid JSON
    const sessions = JSON.parse(fs.readFileSync(sessionsPath, "utf-8"));
    expect(sessions.s1.model).toBe("provB/model3");
  });

  it("skips limitation update when model cannot be determined", () => {
    const { handlers } = setup();
    handlers["agent_end"](
      { success: false, error: "429 Too Many Requests" },
      { sessionKey: "s1" }
    );
    const state = loadState(statePath);
    expect(Object.keys(state.limited)).toHaveLength(0);
  });
});

// ---------------------------------------------------------------------------
// 16. message_sent handler
// ---------------------------------------------------------------------------
describe("message_sent handler", () => {
  const models = ["provA/m1", "provA/m2", "provB/m3"];
  let tmpDir: string;
  let statePath: string;
  let fakeHome: string;

  beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "fo-ms-"));
    statePath = path.join(tmpDir, "state.json");
    fakeHome = path.join(tmpDir, "home");
    fs.mkdirSync(fakeHome, { recursive: true });
    vi.spyOn(os, "homedir").mockReturnValue(fakeHome);
    vi.mocked(spawn).mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  function setup(pluginConfig: Record<string, any> = {}) {
    const cfg = {
      stateFile: statePath,
      modelOrder: models,
      restartOnSwitch: false,
      ...pluginConfig,
    };
    const { api, handlers, logs } = createMockApi({ pluginConfig: cfg });
    register(api);
    return { handlers, logs };
  }

  it("ignores messages without rate-limit content", () => {
    const { handlers } = setup();
    handlers["message_sent"](
      { content: "Hello, how can I help you?" },
      { model: "provA/m1", sessionKey: "s1" }
    );
    const state = loadState(statePath);
    expect(Object.keys(state.limited)).toHaveLength(0);
  });

  it("blocks provider when rate-limit content detected", () => {
    const { handlers } = setup();
    handlers["message_sent"](
      { content: "API rate limit reached for this model." },
      { model: "provA/m1", sessionKey: "s1" }
    );
    const state = loadState(statePath);
    expect(state.limited["provA/m1"]).toBeDefined();
    expect(state.limited["provA/m2"]).toBeDefined();
    expect(state.limited["provB/m3"]).toBeUndefined();
  });

  it("falls back to first model in order when model cannot be determined from ctx", () => {
    const { handlers } = setup();
    handlers["message_sent"](
      { content: "API rate limit reached" },
      { sessionKey: "s1" }
    );
    const state = loadState(statePath);
    // Should block first provider's models (provA) since it defaults to order[0]
    expect(state.limited["provA/m1"]).toBeDefined();
    expect(state.limited["provA/m2"]).toBeDefined();
    expect(state.limited["provB/m3"]).toBeUndefined();
  });

  it("patches sessions.json on rate-limit detection", () => {
    writeSessionsJson(fakeHome, { s1: { model: "provA/m1" } });
    const { handlers } = setup({ patchSessionPins: true });
    handlers["message_sent"](
      { content: "429 Too Many Requests" },
      { model: "provA/m1", sessionKey: "s1" }
    );
    const sessionsPath = path.join(fakeHome, ".openclaw", "agents", "main", "sessions", "sessions.json");
    const sessions = JSON.parse(fs.readFileSync(sessionsPath, "utf-8"));
    expect(sessions.s1.model).toBe("provB/m3");
  });

  it("patches sessions.json atomically via message_sent (no .tmp left)", () => {
    writeSessionsJson(fakeHome, { s1: { model: "provA/m1" } });
    const { handlers } = setup({ patchSessionPins: true });
    handlers["message_sent"](
      { content: "API rate limit reached" },
      { model: "provA/m1", sessionKey: "s1" }
    );
    const sessionsPath = path.join(fakeHome, ".openclaw", "agents", "main", "sessions", "sessions.json");
    expect(fs.existsSync(sessionsPath)).toBe(true);
    expect(fs.existsSync(sessionsPath + ".tmp")).toBe(false);
    const sessions = JSON.parse(fs.readFileSync(sessionsPath, "utf-8"));
    expect(sessions.s1.model).toBe("provB/m3");
  });
});

// ---------------------------------------------------------------------------
// 17. Copilot model filtering in effectiveOrder
// ---------------------------------------------------------------------------
describe("copilot model filtering", () => {
  let tmpDir: string;
  let statePath: string;
  let fakeHome: string;

  beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "fo-cp-"));
    statePath = path.join(tmpDir, "state.json");
    fakeHome = path.join(tmpDir, "home");
    fs.mkdirSync(fakeHome, { recursive: true });
    vi.spyOn(os, "homedir").mockReturnValue(fakeHome);
    vi.mocked(spawn).mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  it("skips copilot models when copilot-proxy is disabled", () => {
    const order = ["github-copilot/model1", "anthropic/claude", "google/gemini"];
    writeSessionsJson(fakeHome, { s1: { model: "github-copilot/model1" } });

    const gwConfig = {
      plugins: { entries: { "copilot-proxy": { enabled: false } } },
      agents: { defaults: { models: {
        "github-copilot/model1": {},
        "anthropic/claude": {},
        "google/gemini": {},
      } } },
    };

    const { api, handlers } = createMockApi({
      pluginConfig: {
        stateFile: statePath,
        modelOrder: order,
        restartOnSwitch: false,
        requireCopilotProxyForCopilotModels: true,
      },
      gatewayConfig: gwConfig,
    });
    register(api);

    const result = handlers["before_model_resolve"]({}, { sessionKey: "s1" });
    expect(result).toEqual({ modelOverride: "anthropic/claude" });
  });

  it("includes copilot models when copilot-proxy is enabled", () => {
    const order = ["github-copilot/model1", "anthropic/claude"];
    writeSessionsJson(fakeHome, { s1: { model: "github-copilot/model1" } });

    const gwConfig = {
      plugins: { entries: { "copilot-proxy": { enabled: true } } },
      agents: { defaults: { models: {
        "github-copilot/model1": {},
        "anthropic/claude": {},
      } } },
    };

    const { api, handlers } = createMockApi({
      pluginConfig: {
        stateFile: statePath,
        modelOrder: order,
        restartOnSwitch: false,
        requireCopilotProxyForCopilotModels: true,
      },
      gatewayConfig: gwConfig,
    });
    register(api);

    const result = handlers["before_model_resolve"]({}, { sessionKey: "s1" });
    expect(result).toBeUndefined();
  });
});

// ---------------------------------------------------------------------------
// 18. Gateway restart scheduling
// ---------------------------------------------------------------------------
describe("gateway restart scheduling", () => {
  let tmpDir: string;
  let statePath: string;
  let fakeHome: string;

  beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "fo-gw-"));
    statePath = path.join(tmpDir, "state.json");
    fakeHome = path.join(tmpDir, "home");
    fs.mkdirSync(fakeHome, { recursive: true });
    vi.spyOn(os, "homedir").mockReturnValue(fakeHome);
    vi.mocked(spawn).mockClear();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  it("spawns gateway restart after delay when restartOnSwitch is true", () => {
    const order = ["provA/m1", "provB/m2"];
    const { api, handlers } = createMockApi({
      pluginConfig: {
        stateFile: statePath,
        modelOrder: order,
        restartOnSwitch: true,
        restartDelayMs: 500,
      },
    });
    register(api);

    handlers["agent_end"](
      { success: false, error: "429 Too Many Requests" },
      { model: "provA/m1", sessionKey: "s1" }
    );

    expect(spawn).not.toHaveBeenCalled();
    vi.advanceTimersByTime(500);
    expect(spawn).toHaveBeenCalledWith(
      "openclaw",
      ["gateway", "restart"],
      expect.objectContaining({ detached: true, stdio: "ignore" })
    );
  });

  it("does not spawn when restartOnSwitch is false", () => {
    const order = ["provA/m1", "provB/m2"];
    const { api, handlers } = createMockApi({
      pluginConfig: {
        stateFile: statePath,
        modelOrder: order,
        restartOnSwitch: false,
      },
    });
    register(api);

    handlers["agent_end"](
      { success: false, error: "429 Too Many Requests" },
      { model: "provA/m1", sessionKey: "s1" }
    );

    vi.advanceTimersByTime(10000);
    expect(spawn).not.toHaveBeenCalled();
  });
});

// ---------------------------------------------------------------------------
// 19. End-to-end failover cascade
// ---------------------------------------------------------------------------
describe("end-to-end failover cascade", () => {
  const models = ["alpha/m1", "alpha/m2", "beta/m1", "gamma/m1"];
  let tmpDir: string;
  let statePath: string;
  let fakeHome: string;

  beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "fo-e2e-"));
    statePath = path.join(tmpDir, "state.json");
    fakeHome = path.join(tmpDir, "home");
    fs.mkdirSync(fakeHome, { recursive: true });
    vi.spyOn(os, "homedir").mockReturnValue(fakeHome);
    vi.mocked(spawn).mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  it("cascades failover through multiple providers", () => {
    writeSessionsJson(fakeHome, { s1: { model: "alpha/m1" } });
    const { api, handlers } = createMockApi({
      pluginConfig: {
        stateFile: statePath,
        modelOrder: models,
        restartOnSwitch: false,
        patchSessionPins: true,
      },
    });
    register(api);

    // Step 1: alpha/m1 hits rate limit
    handlers["agent_end"](
      { success: false, error: "rate limit exceeded" },
      { model: "alpha/m1", sessionKey: "s1" }
    );

    // Verify alpha provider is blocked, beta/gamma are not
    let state = loadState(statePath);
    expect(state.limited["alpha/m1"]).toBeDefined();
    expect(state.limited["alpha/m2"]).toBeDefined();
    expect(state.limited["beta/m1"]).toBeUndefined();

    // Step 2: before_model_resolve should pick beta/m1
    let result = handlers["before_model_resolve"]({}, { sessionKey: "s1" });
    expect(result).toEqual({ modelOverride: "beta/m1" });

    // Step 3: beta/m1 also hits rate limit
    handlers["agent_end"](
      { success: false, error: "too many requests" },
      { model: "beta/m1", sessionKey: "s1" }
    );

    state = loadState(statePath);
    expect(state.limited["beta/m1"]).toBeDefined();

    // Step 4: before_model_resolve should cascade to gamma/m1
    result = handlers["before_model_resolve"]({}, { sessionKey: "s1" });
    expect(result).toEqual({ modelOverride: "gamma/m1" });
  });

  it("recovers when a previously limited model becomes available", () => {
    writeSessionsJson(fakeHome, { s1: { model: "alpha/m1" } });

    // Pre-seed state with alpha blocked but cooldown already expired
    const state: LimitState = {
      limited: {
        "alpha/m1": {
          lastHitAt: nowSec() - 7200,
          nextAvailableAt: nowSec() - 1, // expired 1 second ago
        },
        "alpha/m2": {
          lastHitAt: nowSec() - 7200,
          nextAvailableAt: nowSec() - 1,
        },
      },
    };
    saveState(statePath, state);

    const { api, handlers } = createMockApi({
      pluginConfig: {
        stateFile: statePath,
        modelOrder: models,
        restartOnSwitch: false,
      },
    });
    register(api);

    // Pinned model cooldown expired -> should be available again, no override
    const result = handlers["before_model_resolve"]({}, { sessionKey: "s1" });
    expect(result).toBeUndefined();
  });
});
