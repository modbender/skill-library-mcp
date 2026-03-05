import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import {
  expandHome,
  nowSec,
  loadState,
  saveState,
  writeStatusFile,
  isRateLimitLike,
  isAuthScopeLike,
  pickFallback,
  patchSessionModel,
  safeJsonParse,
  parseConfig,
  validateConfig,
  configDiff,
  buildStatusSnapshot,
  isValidIssueRepoSlug,
  resolveIssueRepo,
  buildGhIssueCreateCommand,
  type State,
  type PluginConfig,
  type StatusSnapshot,
} from "../index.js";
import register from "../index.js";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function tmpDir(): string {
  return fs.mkdtempSync(path.join(os.tmpdir(), "self-heal-test-"));
}

function emptyState(): State {
  return {
    limited: {},
    pendingBackups: {},
    whatsapp: {},
    cron: { failCounts: {}, lastIssueCreatedAt: {} },
    plugins: { lastDisableAt: {} },
  };
}

function mockApi(overrides: Record<string, any> = {}) {
  const handlers: Record<string, Function[]> = {};
  const services: any[] = [];
  const emitted: { event: string; payload: any }[] = [];

  return {
    pluginConfig: overrides.pluginConfig ?? {},
    logger: {
      info: vi.fn(),
      warn: vi.fn(),
      error: vi.fn(),
    },
    on(event: string, handler: Function) {
      handlers[event] = handlers[event] || [];
      handlers[event].push(handler);
    },
    emit(event: string, payload: any) {
      emitted.push({ event, payload });
    },
    registerService(svc: any) {
      services.push(svc);
    },
    runtime: {
      system: {
        runCommandWithTimeout: vi.fn().mockResolvedValue({
          exitCode: 1,
          stdout: "",
          stderr: "not available",
        }),
      },
    },
    // test helpers
    _handlers: handlers,
    _services: services,
    _emitted: emitted,
    _emit(event: string, ...args: any[]) {
      for (const h of handlers[event] ?? []) h(...args);
    },
  };
}

// ---------------------------------------------------------------------------
// expandHome
// ---------------------------------------------------------------------------

describe("expandHome", () => {
  it("returns empty string for empty input", () => {
    expect(expandHome("")).toBe("");
  });

  it("expands bare tilde to homedir", () => {
    expect(expandHome("~")).toBe(os.homedir());
  });

  it("expands ~/path to homedir/path", () => {
    expect(expandHome("~/foo/bar")).toBe(path.join(os.homedir(), "foo/bar"));
  });

  it("returns absolute paths unchanged", () => {
    expect(expandHome("/usr/local/bin")).toBe("/usr/local/bin");
  });

  it("returns relative paths unchanged", () => {
    expect(expandHome("relative/path")).toBe("relative/path");
  });
});

// ---------------------------------------------------------------------------
// nowSec
// ---------------------------------------------------------------------------

describe("nowSec", () => {
  it("returns current time in seconds (integer)", () => {
    const before = Math.floor(Date.now() / 1000);
    const result = nowSec();
    const after = Math.floor(Date.now() / 1000);
    expect(result).toBeGreaterThanOrEqual(before);
    expect(result).toBeLessThanOrEqual(after);
    expect(Number.isInteger(result)).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// isRateLimitLike
// ---------------------------------------------------------------------------

describe("isRateLimitLike", () => {
  it("returns false for undefined", () => {
    expect(isRateLimitLike(undefined)).toBe(false);
  });

  it("returns false for empty string", () => {
    expect(isRateLimitLike("")).toBe(false);
  });

  it("returns false for unrelated error", () => {
    expect(isRateLimitLike("connection timeout")).toBe(false);
  });

  it.each([
    "Rate limit exceeded",
    "RATE LIMIT reached",
    "quota exceeded for project",
    "HTTP 429 Too Many Requests",
    "resource_exhausted: try again later",
  ])("detects rate limit pattern: %s", (err) => {
    expect(isRateLimitLike(err)).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// isAuthScopeLike
// ---------------------------------------------------------------------------

describe("isAuthScopeLike", () => {
  it("returns false for undefined", () => {
    expect(isAuthScopeLike(undefined)).toBe(false);
  });

  it("returns false for empty string", () => {
    expect(isAuthScopeLike("")).toBe(false);
  });

  it("returns false for unrelated error", () => {
    expect(isAuthScopeLike("connection refused")).toBe(false);
  });

  it.each([
    "HTTP 401 Unauthorized",
    "Insufficient permissions for resource",
    "Missing scopes: read:org",
    "api.responses.write is required",
    "unauthorized access to endpoint",
  ])("detects auth/scope pattern: %s", (err) => {
    expect(isAuthScopeLike(err)).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// safeJsonParse
// ---------------------------------------------------------------------------

describe("safeJsonParse", () => {
  it("parses valid JSON", () => {
    expect(safeJsonParse('{"a":1}')).toEqual({ a: 1 });
  });

  it("parses JSON arrays", () => {
    expect(safeJsonParse("[1,2,3]")).toEqual([1, 2, 3]);
  });

  it("returns undefined for invalid JSON", () => {
    expect(safeJsonParse("{broken")).toBeUndefined();
  });

  it("returns undefined for empty string", () => {
    expect(safeJsonParse("")).toBeUndefined();
  });
});

// ---------------------------------------------------------------------------
// loadState / saveState
// ---------------------------------------------------------------------------

describe("loadState / saveState", () => {
  let dir: string;

  beforeEach(() => {
    dir = tmpDir();
  });

  afterEach(() => {
    fs.rmSync(dir, { recursive: true, force: true });
  });

  it("returns default state when file does not exist", () => {
    const s = loadState(path.join(dir, "missing.json"));
    expect(s.limited).toEqual({});
    expect(s.pendingBackups).toEqual({});
    expect(s.whatsapp).toEqual({});
    expect(s.cron).toEqual({ failCounts: {}, lastIssueCreatedAt: {} });
    expect(s.plugins).toEqual({ lastDisableAt: {} });
  });

  it("round-trips state through save and load", () => {
    const p = path.join(dir, "state.json");
    const state: State = {
      limited: {
        "model-a": { lastHitAt: 100, nextAvailableAt: 200, reason: "rate limit" },
      },
      pendingBackups: {},
      whatsapp: { lastSeenConnectedAt: 50 },
      cron: { failCounts: { "job-1": 3 }, lastIssueCreatedAt: {} },
      plugins: { lastDisableAt: {} },
    };
    saveState(p, state);
    const loaded = loadState(p);
    expect(loaded.limited["model-a"].lastHitAt).toBe(100);
    expect(loaded.limited["model-a"].nextAvailableAt).toBe(200);
    expect(loaded.whatsapp?.lastSeenConnectedAt).toBe(50);
    expect(loaded.cron?.failCounts?.["job-1"]).toBe(3);
  });

  it("creates parent directories if they do not exist", () => {
    const p = path.join(dir, "nested", "deep", "state.json");
    saveState(p, emptyState());
    expect(fs.existsSync(p)).toBe(true);
  });

  it("fills missing sub-objects when loading partial state", () => {
    const p = path.join(dir, "partial.json");
    fs.writeFileSync(p, JSON.stringify({ limited: { x: { lastHitAt: 1, nextAvailableAt: 2 } } }));
    const s = loadState(p);
    expect(s.limited.x.lastHitAt).toBe(1);
    expect(s.pendingBackups).toEqual({});
    expect(s.whatsapp).toEqual({});
    expect(s.cron?.failCounts).toEqual({});
    expect(s.plugins?.lastDisableAt).toEqual({});
  });

  it("returns default state for corrupt JSON", () => {
    const p = path.join(dir, "corrupt.json");
    fs.writeFileSync(p, "{not valid json");
    const s = loadState(p);
    expect(s.limited).toEqual({});
  });
});

// ---------------------------------------------------------------------------
// pickFallback
// ---------------------------------------------------------------------------

describe("pickFallback", () => {
  const models = ["model-a", "model-b", "model-c"];

  it("returns first model when none are limited", () => {
    expect(pickFallback(models, emptyState())).toBe("model-a");
  });

  it("skips a model whose cooldown has not expired", () => {
    const future = nowSec() + 9999;
    const state: State = {
      ...emptyState(),
      limited: {
        "model-a": { lastHitAt: nowSec(), nextAvailableAt: future },
      },
    };
    expect(pickFallback(models, state)).toBe("model-b");
  });

  it("returns first model if its cooldown has expired", () => {
    const past = nowSec() - 1;
    const state: State = {
      ...emptyState(),
      limited: {
        "model-a": { lastHitAt: 0, nextAvailableAt: past },
      },
    };
    expect(pickFallback(models, state)).toBe("model-a");
  });

  it("falls through to last model when all are limited", () => {
    const future = nowSec() + 9999;
    const state: State = {
      ...emptyState(),
      limited: {
        "model-a": { lastHitAt: nowSec(), nextAvailableAt: future },
        "model-b": { lastHitAt: nowSec(), nextAvailableAt: future },
        "model-c": { lastHitAt: nowSec(), nextAvailableAt: future },
      },
    };
    expect(pickFallback(models, state)).toBe("model-c");
  });

  it("skips multiple limited models to find available one", () => {
    const future = nowSec() + 9999;
    const state: State = {
      ...emptyState(),
      limited: {
        "model-a": { lastHitAt: nowSec(), nextAvailableAt: future },
        "model-b": { lastHitAt: nowSec(), nextAvailableAt: future },
      },
    };
    expect(pickFallback(models, state)).toBe("model-c");
  });

  it("handles single-model list", () => {
    expect(pickFallback(["only-model"], emptyState())).toBe("only-model");
  });
});

// ---------------------------------------------------------------------------
// patchSessionModel
// ---------------------------------------------------------------------------

describe("patchSessionModel", () => {
  let dir: string;

  beforeEach(() => {
    dir = tmpDir();
  });

  afterEach(() => {
    fs.rmSync(dir, { recursive: true, force: true });
  });

  it("patches the model for an existing session key", () => {
    const p = path.join(dir, "sessions.json");
    fs.writeFileSync(p, JSON.stringify({ "sess-1": { model: "old-model" } }));

    const logger = { warn: vi.fn(), error: vi.fn() };
    const result = patchSessionModel(p, "sess-1", "new-model", logger);

    expect(result).toBe(true);
    const data = JSON.parse(fs.readFileSync(p, "utf-8"));
    expect(data["sess-1"].model).toBe("new-model");
    expect(logger.warn).toHaveBeenCalledOnce();
  });

  it("returns false when session key does not exist", () => {
    const p = path.join(dir, "sessions.json");
    fs.writeFileSync(p, JSON.stringify({ "sess-1": { model: "m" } }));

    const logger = { warn: vi.fn(), error: vi.fn() };
    const result = patchSessionModel(p, "nonexistent", "new-model", logger);

    expect(result).toBe(false);
  });

  it("returns false and logs error when file does not exist", () => {
    const p = path.join(dir, "no-file.json");
    const logger = { warn: vi.fn(), error: vi.fn() };
    const result = patchSessionModel(p, "sess-1", "new-model", logger);

    expect(result).toBe(false);
    expect(logger.error).toHaveBeenCalledOnce();
  });

  it("preserves other session keys when patching", () => {
    const p = path.join(dir, "sessions.json");
    fs.writeFileSync(
      p,
      JSON.stringify({
        "sess-1": { model: "old" },
        "sess-2": { model: "keep" },
      })
    );

    patchSessionModel(p, "sess-1", "new", { warn: vi.fn(), error: vi.fn() });
    const data = JSON.parse(fs.readFileSync(p, "utf-8"));
    expect(data["sess-2"].model).toBe("keep");
  });
});

// ---------------------------------------------------------------------------
// register - event handler integration tests
// ---------------------------------------------------------------------------

describe("register", () => {
  let dir: string;
  let stateFile: string;
  let sessionsFile: string;
  let configFile: string;

  beforeEach(() => {
    dir = tmpDir();
    stateFile = path.join(dir, "state.json");
    sessionsFile = path.join(dir, "sessions.json");
    configFile = path.join(dir, "openclaw.json");
    fs.writeFileSync(configFile, JSON.stringify({ valid: true }));
  });

  afterEach(() => {
    fs.rmSync(dir, { recursive: true, force: true });
  });

  it("does nothing when enabled is false", () => {
    const api = mockApi({ pluginConfig: { enabled: false } });
    register(api);
    expect(Object.keys(api._handlers)).toHaveLength(0);
    expect(api._services).toHaveLength(0);
  });

  it("registers agent_end and message_sent handlers", () => {
    const api = mockApi({
      pluginConfig: {
        stateFile,
        sessionsFile,
        configFile,
        configBackupsDir: path.join(dir, "backups"),
      },
    });
    register(api);
    expect(api._handlers["agent_end"]).toHaveLength(1);
    expect(api._handlers["message_sent"]).toHaveLength(1);
  });

  it("registers the self-heal-monitor service", () => {
    const api = mockApi({
      pluginConfig: {
        stateFile,
        sessionsFile,
        configFile,
        configBackupsDir: path.join(dir, "backups"),
      },
    });
    register(api);
    expect(api._services).toHaveLength(1);
    expect(api._services[0].id).toBe("self-heal-monitor");
  });

  describe("agent_end handler", () => {
    it("ignores successful events", () => {
      const api = mockApi({
        pluginConfig: { stateFile, sessionsFile, configFile },
      });
      register(api);

      api._emit("agent_end", { success: true }, {});
      // State file should not be created for successful events
      expect(fs.existsSync(stateFile)).toBe(false);
    });

    it("ignores failures without rate-limit or auth errors", () => {
      const api = mockApi({
        pluginConfig: { stateFile, sessionsFile, configFile },
      });
      register(api);

      api._emit("agent_end", { success: false, error: "generic timeout" }, {});
      expect(fs.existsSync(stateFile)).toBe(false);
    });

    it("marks model as limited on rate-limit error", () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a", "model-b"],
          cooldownMinutes: 10,
        },
      });
      register(api);

      api._emit(
        "agent_end",
        { success: false, error: "HTTP 429 rate limit exceeded" },
        {}
      );

      const state = loadState(stateFile);
      expect(state.limited["model-a"]).toBeDefined();
      expect(state.limited["model-a"].nextAvailableAt).toBeGreaterThan(nowSec());
    });

    it("applies extra cooldown for auth errors", () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a", "model-b"],
          cooldownMinutes: 10,
        },
      });
      register(api);

      api._emit(
        "agent_end",
        { success: false, error: "HTTP 401 Unauthorized" },
        {}
      );

      const state = loadState(stateFile);
      const entry = state.limited["model-a"];
      // Auth errors add 12 * 60 minutes = 720 min extra on top of 10 min cooldown
      // Total: (10 + 720) * 60 = 43800 seconds
      const minExpected = nowSec() + (10 + 720) * 60 - 5; // 5s tolerance
      expect(entry.nextAvailableAt).toBeGreaterThanOrEqual(minExpected);
    });

    it("patches session model on rate-limit when patchPins is enabled", () => {
      fs.writeFileSync(
        sessionsFile,
        JSON.stringify({ "s1": { model: "model-a" } })
      );

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a", "model-b"],
          cooldownMinutes: 10,
        },
      });
      register(api);

      api._emit(
        "agent_end",
        { success: false, error: "rate limit hit" },
        { sessionKey: "s1" }
      );

      const sessions = JSON.parse(fs.readFileSync(sessionsFile, "utf-8"));
      expect(sessions["s1"].model).toBe("model-b");
    });
  });

  describe("message_sent handler", () => {
    it("ignores messages without rate-limit content", () => {
      const api = mockApi({
        pluginConfig: { stateFile, sessionsFile, configFile },
      });
      register(api);

      api._emit("message_sent", { content: "Hello, world!" }, {});
      expect(fs.existsSync(stateFile)).toBe(false);
    });

    it("marks first model limited when rate-limit content is detected", () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["primary", "fallback"],
          cooldownMinutes: 5,
        },
      });
      register(api);

      api._emit(
        "message_sent",
        { content: "Error: quota exceeded for this model" },
        {}
      );

      const state = loadState(stateFile);
      expect(state.limited["primary"]).toBeDefined();
      expect(state.limited["primary"].reason).toBe("outbound error observed");
    });

    it("patches session model on rate-limit content detection", () => {
      fs.writeFileSync(
        sessionsFile,
        JSON.stringify({ "s1": { model: "primary" } })
      );

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["primary", "fallback"],
          cooldownMinutes: 5,
        },
      });
      register(api);

      api._emit(
        "message_sent",
        { content: "429 Too Many Requests" },
        { sessionKey: "s1" }
      );

      const sessions = JSON.parse(fs.readFileSync(sessionsFile, "utf-8"));
      expect(sessions["s1"].model).toBe("fallback");
    });
  });

  describe("config hot-reload", () => {
    it("picks up modelOrder changes via api.pluginConfig on monitor tick", async () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a", "model-b"],
          cooldownMinutes: 10,
        },
      });
      register(api);

      // Change config before tick
      api.pluginConfig = {
        stateFile,
        sessionsFile,
        configFile,
        modelOrder: ["model-x", "model-y", "model-z"],
        cooldownMinutes: 10,
      };

      // Run the monitor service tick
      const svc = api._services[0];
      await svc.start();
      // Wait a bit for the immediate tick to run
      await new Promise((r) => setTimeout(r, 50));
      await svc.stop();

      // Verify the new model order is used by triggering an agent_end
      api._emit(
        "agent_end",
        { success: false, error: "HTTP 429 rate limit exceeded" },
        {}
      );

      const state = loadState(stateFile);
      // Should mark model-x (new first model), not model-a (old first model)
      expect(state.limited["model-x"]).toBeDefined();
      expect(state.limited["model-a"]).toBeUndefined();
    });

    it("picks up cooldownMinutes changes on monitor tick", async () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a"],
          cooldownMinutes: 10,
        },
      });
      register(api);

      // Change cooldown to 60 minutes
      api.pluginConfig = {
        stateFile,
        sessionsFile,
        configFile,
        modelOrder: ["model-a"],
        cooldownMinutes: 60,
      };

      const svc = api._services[0];
      await svc.start();
      await new Promise((r) => setTimeout(r, 50));
      await svc.stop();

      // Trigger rate limit with new cooldown
      api._emit(
        "agent_end",
        { success: false, error: "rate limit hit" },
        {}
      );

      const state = loadState(stateFile);
      const entry = state.limited["model-a"];
      // With 60 min cooldown, nextAvailableAt should be ~3600 seconds in the future
      const minExpected = nowSec() + 60 * 60 - 5;
      expect(entry.nextAvailableAt).toBeGreaterThanOrEqual(minExpected);
    });

    it("logs changed config keys on reload", async () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a"],
          cooldownMinutes: 10,
        },
      });
      register(api);

      api.pluginConfig = {
        stateFile,
        sessionsFile,
        configFile,
        modelOrder: ["model-a"],
        cooldownMinutes: 99,
      };

      const svc = api._services[0];
      await svc.start();
      await new Promise((r) => setTimeout(r, 50));
      await svc.stop();

      expect(api.logger.info).toHaveBeenCalledWith(
        expect.stringContaining("config reloaded: changed cooldownMinutes")
      );
    });

    it("does not log when config has not changed", async () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a"],
          cooldownMinutes: 10,
        },
      });
      register(api);

      // Don't change config
      const svc = api._services[0];
      await svc.start();
      await new Promise((r) => setTimeout(r, 50));
      await svc.stop();

      // Should not have a "config reloaded" log
      const reloadCalls = api.logger.info.mock.calls.filter(
        (c: any[]) => typeof c[0] === "string" && c[0].includes("config reloaded")
      );
      expect(reloadCalls).toHaveLength(0);
    });

    it("ignores config reload when new config sets enabled=false", async () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a"],
          cooldownMinutes: 10,
        },
      });
      register(api);

      // Try to disable via hot-reload
      api.pluginConfig = {
        enabled: false,
        stateFile,
        sessionsFile,
        configFile,
        modelOrder: ["model-a"],
        cooldownMinutes: 10,
      };

      const svc = api._services[0];
      await svc.start();
      await new Promise((r) => setTimeout(r, 50));
      await svc.stop();

      // Should have logged a warning about ignoring disabled config
      expect(api.logger.warn).toHaveBeenCalledWith(
        expect.stringContaining("plugin disabled in new config")
      );

      // Original config should still be active - trigger event with old model
      api._emit(
        "agent_end",
        { success: false, error: "rate limit hit" },
        {}
      );
      const state = loadState(stateFile);
      expect(state.limited["model-a"]).toBeDefined();
    });

    it("picks up probeIntervalSec changes on monitor tick", async () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a"],
          probeIntervalSec: 300,
        },
      });
      register(api);

      api.pluginConfig = {
        stateFile,
        sessionsFile,
        configFile,
        modelOrder: ["model-a"],
        probeIntervalSec: 60,
      };

      const svc = api._services[0];
      await svc.start();
      await new Promise((r) => setTimeout(r, 50));
      await svc.stop();

      expect(api.logger.info).toHaveBeenCalledWith(
        expect.stringContaining("config reloaded: changed probeIntervalSec")
      );
    });

    it("uses updated config in message_sent handler after reload", async () => {
      fs.writeFileSync(
        sessionsFile,
        JSON.stringify({ "s1": { model: "model-a" } })
      );

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a", "model-b"],
          cooldownMinutes: 10,
        },
      });
      register(api);

      // Update model order
      api.pluginConfig = {
        stateFile,
        sessionsFile,
        configFile,
        modelOrder: ["model-x", "model-y"],
        cooldownMinutes: 10,
      };

      const svc = api._services[0];
      await svc.start();
      await new Promise((r) => setTimeout(r, 50));
      await svc.stop();

      // message_sent should now use new model order
      api._emit(
        "message_sent",
        { content: "429 Too Many Requests" },
        {}
      );

      const state = loadState(stateFile);
      expect(state.limited["model-x"]).toBeDefined();
      expect(state.limited["model-a"]).toBeUndefined();
    });
  });

  describe("active model recovery probing", () => {
    it("probes a model in cooldown and removes it on success", async () => {
      // Seed state with a model in cooldown, lastHitAt far enough in the past
      const hitAt = nowSec() - 400; // 400s ago, probe interval default 300s
      saveState(stateFile, {
        ...emptyState(),
        limited: {
          "model-a": { lastHitAt: hitAt, nextAvailableAt: nowSec() + 9999 },
        },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a", "model-b"],
          probeEnabled: true,
          probeIntervalSec: 300,
        },
      });
      // Probe succeeds
      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: "ok",
        stderr: "",
      });
      register(api);

      const svc = api._services[0];
      await svc.start();
      await new Promise((r) => setTimeout(r, 50));
      await svc.stop();

      const state = loadState(stateFile);
      expect(state.limited["model-a"]).toBeUndefined();
      expect(api.logger.info).toHaveBeenCalledWith(
        expect.stringContaining("model model-a recovered early via probe")
      );
    });

    it("keeps model in cooldown when probe fails", async () => {
      const hitAt = nowSec() - 400;
      saveState(stateFile, {
        ...emptyState(),
        limited: {
          "model-a": { lastHitAt: hitAt, nextAvailableAt: nowSec() + 9999 },
        },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a", "model-b"],
          probeEnabled: true,
          probeIntervalSec: 300,
        },
      });
      // Probe fails (default mock returns exitCode 1)
      register(api);

      const svc = api._services[0];
      await svc.start();
      await new Promise((r) => setTimeout(r, 50));
      await svc.stop();

      const state = loadState(stateFile);
      expect(state.limited["model-a"]).toBeDefined();
      expect(state.limited["model-a"].lastProbeAt).toBeGreaterThan(0);
    });

    it("does not probe when probeEnabled is false", async () => {
      const hitAt = nowSec() - 400;
      saveState(stateFile, {
        ...emptyState(),
        limited: {
          "model-a": { lastHitAt: hitAt, nextAvailableAt: nowSec() + 9999 },
        },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a", "model-b"],
          probeEnabled: false,
          probeIntervalSec: 300,
        },
      });
      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: "ok",
        stderr: "",
      });
      register(api);

      const svc = api._services[0];
      await svc.start();
      await new Promise((r) => setTimeout(r, 50));
      await svc.stop();

      const state = loadState(stateFile);
      // Model should still be in cooldown since probing was disabled
      expect(state.limited["model-a"]).toBeDefined();
    });

    it("respects probe interval and does not probe too soon", async () => {
      const hitAt = nowSec() - 10; // Only 10s ago, far less than 300s interval
      saveState(stateFile, {
        ...emptyState(),
        limited: {
          "model-a": { lastHitAt: hitAt, nextAvailableAt: nowSec() + 9999 },
        },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a", "model-b"],
          probeEnabled: true,
          probeIntervalSec: 300,
        },
      });
      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: "ok",
        stderr: "",
      });
      register(api);

      const svc = api._services[0];
      await svc.start();
      await new Promise((r) => setTimeout(r, 50));
      await svc.stop();

      const state = loadState(stateFile);
      // Should NOT have been probed (too soon), model stays in cooldown
      expect(state.limited["model-a"]).toBeDefined();
      expect(state.limited["model-a"].lastProbeAt).toBeUndefined();
    });

    it("respects lastProbeAt when deciding whether to probe again", async () => {
      // Last probe was only 60s ago, interval is 300s
      const lastProbeAt = nowSec() - 60;
      saveState(stateFile, {
        ...emptyState(),
        limited: {
          "model-a": {
            lastHitAt: nowSec() - 1000,
            nextAvailableAt: nowSec() + 9999,
            lastProbeAt,
          },
        },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a", "model-b"],
          probeEnabled: true,
          probeIntervalSec: 300,
        },
      });
      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: "ok",
        stderr: "",
      });
      register(api);

      const svc = api._services[0];
      await svc.start();
      await new Promise((r) => setTimeout(r, 50));
      await svc.stop();

      const state = loadState(stateFile);
      // Should not have probed again, lastProbeAt should be unchanged
      expect(state.limited["model-a"]).toBeDefined();
      expect(state.limited["model-a"].lastProbeAt).toBe(lastProbeAt);
    });

    it("skips models whose cooldown has already expired", async () => {
      const hitAt = nowSec() - 400;
      saveState(stateFile, {
        ...emptyState(),
        limited: {
          "model-a": { lastHitAt: hitAt, nextAvailableAt: nowSec() - 1 }, // already expired
        },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a", "model-b"],
          probeEnabled: true,
          probeIntervalSec: 300,
        },
      });
      register(api);

      const svc = api._services[0];
      await svc.start();
      await new Promise((r) => setTimeout(r, 50));
      await svc.stop();

      // runCommandWithTimeout should only be called for the gateway status check,
      // not for a probe (since the model's cooldown already expired)
      const probeCalls = api.runtime.system.runCommandWithTimeout.mock.calls.filter(
        (c: any[]) => {
          const cmd = c[0]?.command?.join(" ") ?? "";
          return cmd.includes("model probe");
        }
      );
      expect(probeCalls).toHaveLength(0);
    });

    it("logs preferred model recovery when primary model recovers", async () => {
      const hitAt = nowSec() - 400;
      saveState(stateFile, {
        ...emptyState(),
        limited: {
          "model-a": { lastHitAt: hitAt, nextAvailableAt: nowSec() + 9999 },
        },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a", "model-b"],
          probeEnabled: true,
          probeIntervalSec: 300,
        },
      });
      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: "ok",
        stderr: "",
      });
      register(api);

      const svc = api._services[0];
      await svc.start();
      await new Promise((r) => setTimeout(r, 50));
      await svc.stop();

      expect(api.logger.info).toHaveBeenCalledWith(
        expect.stringContaining("preferred model model-a recovered")
      );
    });

    it("does not log preferred model recovery for non-primary models", async () => {
      const hitAt = nowSec() - 400;
      saveState(stateFile, {
        ...emptyState(),
        limited: {
          "model-b": { lastHitAt: hitAt, nextAvailableAt: nowSec() + 9999 },
        },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a", "model-b"],
          probeEnabled: true,
          probeIntervalSec: 300,
        },
      });
      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: "ok",
        stderr: "",
      });
      register(api);

      const svc = api._services[0];
      await svc.start();
      await new Promise((r) => setTimeout(r, 50));
      await svc.stop();

      const state = loadState(stateFile);
      expect(state.limited["model-b"]).toBeUndefined();

      const preferredCalls = api.logger.info.mock.calls.filter(
        (c: any[]) => typeof c[0] === "string" && c[0].includes("preferred model")
      );
      expect(preferredCalls).toHaveLength(0);
    });

    it("does not probe in dry-run mode but logs what would happen", async () => {
      const hitAt = nowSec() - 400;
      saveState(stateFile, {
        ...emptyState(),
        limited: {
          "model-a": { lastHitAt: hitAt, nextAvailableAt: nowSec() + 9999 },
        },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a", "model-b"],
          probeEnabled: true,
          probeIntervalSec: 300,
          dryRun: true,
        },
      });
      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: "ok",
        stderr: "",
      });
      register(api);

      const svc = api._services[0];
      await svc.start();
      await new Promise((r) => setTimeout(r, 50));
      await svc.stop();

      // Model should still be in cooldown since dry-run skips probing
      const state = loadState(stateFile);
      expect(state.limited["model-a"]).toBeDefined();

      // Should log dry-run message
      expect(api.logger.info).toHaveBeenCalledWith(
        expect.stringContaining("[dry-run] would probe model model-a")
      );

      // Should NOT have called the actual probe command
      const probeCalls = api.runtime.system.runCommandWithTimeout.mock.calls.filter(
        (c: any[]) => {
          const cmd = c[0]?.command?.join(" ") ?? "";
          return cmd.includes("model probe");
        }
      );
      expect(probeCalls).toHaveLength(0);
    });

    it("probes multiple models in cooldown independently", async () => {
      const hitAt = nowSec() - 400;
      saveState(stateFile, {
        ...emptyState(),
        limited: {
          "model-a": { lastHitAt: hitAt, nextAvailableAt: nowSec() + 9999 },
          "model-b": { lastHitAt: hitAt, nextAvailableAt: nowSec() + 9999 },
        },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a", "model-b", "model-c"],
          probeEnabled: true,
          probeIntervalSec: 300,
        },
      });
      // model-a probe succeeds, model-b probe fails
      let probeCount = 0;
      api.runtime.system.runCommandWithTimeout.mockImplementation(async (opts: any) => {
        const cmd = opts?.command?.join(" ") ?? "";
        if (cmd.includes("model probe")) {
          probeCount++;
          if (cmd.includes("model-a")) {
            return { exitCode: 0, stdout: "ok", stderr: "" };
          }
          return { exitCode: 1, stdout: "", stderr: "still limited" };
        }
        return { exitCode: 1, stdout: "", stderr: "not available" };
      });
      register(api);

      const svc = api._services[0];
      await svc.start();
      await new Promise((r) => setTimeout(r, 50));
      await svc.stop();

      const state = loadState(stateFile);
      expect(state.limited["model-a"]).toBeUndefined(); // recovered
      expect(state.limited["model-b"]).toBeDefined(); // still in cooldown
      expect(probeCount).toBe(2);
    });
  });

  describe("dry-run mode", () => {
    it("logs DRY-RUN MODE in startup message", () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: path.join(dir, "backups"),
          dryRun: true,
        },
      });
      register(api);

      expect(api.logger.info).toHaveBeenCalledWith(
        expect.stringContaining("DRY-RUN MODE")
      );
    });

    it("still registers handlers and service in dry-run mode", () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: path.join(dir, "backups"),
          dryRun: true,
        },
      });
      register(api);

      expect(api._handlers["agent_end"]).toHaveLength(1);
      expect(api._handlers["message_sent"]).toHaveLength(1);
      expect(api._services).toHaveLength(1);
    });

    it("updates state but does not patch session on agent_end in dry-run", () => {
      fs.writeFileSync(
        sessionsFile,
        JSON.stringify({ "s1": { model: "model-a" } })
      );

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a", "model-b"],
          cooldownMinutes: 10,
          dryRun: true,
        },
      });
      register(api);

      api._emit(
        "agent_end",
        { success: false, error: "rate limit hit" },
        { sessionKey: "s1" }
      );

      // State should still be updated (model marked as limited)
      const state = loadState(stateFile);
      expect(state.limited["model-a"]).toBeDefined();

      // But session file should NOT be patched
      const sessions = JSON.parse(fs.readFileSync(sessionsFile, "utf-8"));
      expect(sessions["s1"].model).toBe("model-a");

      // Should log dry-run message
      expect(api.logger.info).toHaveBeenCalledWith(
        expect.stringContaining("[dry-run] would patch session s1")
      );
    });

    it("updates state but does not patch session on message_sent in dry-run", () => {
      fs.writeFileSync(
        sessionsFile,
        JSON.stringify({ "s1": { model: "primary" } })
      );

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["primary", "fallback"],
          cooldownMinutes: 5,
          dryRun: true,
        },
      });
      register(api);

      api._emit(
        "message_sent",
        { content: "429 Too Many Requests" },
        { sessionKey: "s1" }
      );

      // State should still be updated
      const state = loadState(stateFile);
      expect(state.limited["primary"]).toBeDefined();

      // But session file should NOT be patched
      const sessions = JSON.parse(fs.readFileSync(sessionsFile, "utf-8"));
      expect(sessions["s1"].model).toBe("primary");

      // Should log dry-run message
      expect(api.logger.info).toHaveBeenCalledWith(
        expect.stringContaining("[dry-run] would patch session s1")
      );
    });

    it("logs but does not restart gateway in dry-run mode", async () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: path.join(dir, "backups"),
          modelOrder: ["model-a"],
          dryRun: true,
          autoFix: { restartWhatsappOnDisconnect: true, whatsappDisconnectThreshold: 2 },
        },
      });

      // Return WhatsApp disconnected status
      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: JSON.stringify({ channels: { whatsapp: { status: "disconnected" } } }),
        stderr: "",
      });

      // Seed state with streak at threshold
      saveState(stateFile, {
        ...emptyState(),
        whatsapp: { disconnectStreak: 2, lastRestartAt: 0 },
      });

      register(api);

      const svc = api._services[0];
      await svc.start();
      await new Promise((r) => setTimeout(r, 50));
      await svc.stop();

      // Should log dry-run message
      expect(api.logger.info).toHaveBeenCalledWith(
        expect.stringContaining("[dry-run] would restart gateway")
      );

      // Should NOT have called gateway restart
      const restartCalls = api.runtime.system.runCommandWithTimeout.mock.calls.filter(
        (c: any[]) => {
          const cmd = c[0]?.command?.join(" ") ?? "";
          return cmd.includes("gateway restart");
        }
      );
      expect(restartCalls).toHaveLength(0);

      // State should still track the restart
      const state = loadState(stateFile);
      expect(state.whatsapp!.lastRestartAt).toBeGreaterThan(0);
      expect(state.whatsapp!.disconnectStreak).toBe(0);
    });

    it("logs but does not disable cron or create issue in dry-run mode", async () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: path.join(dir, "backups"),
          modelOrder: ["model-a"],
          dryRun: true,
          autoFix: { disableFailingCrons: true, cronFailThreshold: 1 },
        },
      });

      // Return failing cron
      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: JSON.stringify({
          jobs: [{ id: "cron-1", name: "test-cron", state: { lastStatus: "error", lastError: "timeout" } }],
        }),
        stderr: "",
      });

      register(api);

      const svc = api._services[0];
      await svc.start();
      await new Promise((r) => setTimeout(r, 50));
      await svc.stop();

      // Should log dry-run messages
      expect(api.logger.info).toHaveBeenCalledWith(
        expect.stringContaining("[dry-run] would disable cron test-cron")
      );
      expect(api.logger.info).toHaveBeenCalledWith(
        expect.stringContaining("[dry-run] would create GitHub issue for cron test-cron")
      );

      // Should NOT have called cron edit disable
      const cronCalls = api.runtime.system.runCommandWithTimeout.mock.calls.filter(
        (c: any[]) => {
          const cmd = c[0]?.command?.join(" ") ?? "";
          return cmd.includes("cron edit");
        }
      );
      expect(cronCalls).toHaveLength(0);

      // Should NOT have called gh issue create
      const issueCalls = api.runtime.system.runCommandWithTimeout.mock.calls.filter(
        (c: any[]) => {
          const cmd = c[0]?.command?.join(" ") ?? "";
          return cmd.includes("gh issue create");
        }
      );
      expect(issueCalls).toHaveLength(0);

      // State should still be updated (fail count reset, issue timestamp set)
      const state = loadState(stateFile);
      expect(state.cron!.failCounts!["cron-1"]).toBe(0);
      expect(state.cron!.lastIssueCreatedAt!["cron-1"]).toBeGreaterThan(0);
    });

    it("picks up dryRun changes via hot-reload", async () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a"],
          dryRun: false,
        },
      });
      register(api);

      // Enable dry-run via hot-reload
      api.pluginConfig = {
        stateFile,
        sessionsFile,
        configFile,
        modelOrder: ["model-a"],
        dryRun: true,
      };

      const svc = api._services[0];
      await svc.start();
      await new Promise((r) => setTimeout(r, 50));
      await svc.stop();

      expect(api.logger.info).toHaveBeenCalledWith(
        expect.stringContaining("config reloaded: changed dryRun")
      );
    });
  });

  describe("observability events", () => {
    it("emits self-heal:model-cooldown on agent_end rate-limit", () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a", "model-b"],
          cooldownMinutes: 10,
        },
      });
      register(api);

      api._emit(
        "agent_end",
        { success: false, error: "HTTP 429 rate limit exceeded" },
        {}
      );

      const ev = api._emitted.find((e) => e.event === "self-heal:model-cooldown");
      expect(ev).toBeDefined();
      expect(ev!.payload.model).toBe("model-a");
      expect(ev!.payload.reason).toBe("HTTP 429 rate limit exceeded");
      expect(ev!.payload.cooldownSec).toBe(10 * 60);
      expect(ev!.payload.trigger).toBe("agent_end");
      expect(ev!.payload.dryRun).toBe(false);
    });

    it("emits self-heal:model-cooldown on message_sent rate-limit", () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["primary", "fallback"],
          cooldownMinutes: 5,
        },
      });
      register(api);

      api._emit(
        "message_sent",
        { content: "Error: quota exceeded for this model" },
        {}
      );

      const ev = api._emitted.find((e) => e.event === "self-heal:model-cooldown");
      expect(ev).toBeDefined();
      expect(ev!.payload.model).toBe("primary");
      expect(ev!.payload.reason).toBe("outbound error observed");
      expect(ev!.payload.cooldownSec).toBe(5 * 60);
      expect(ev!.payload.trigger).toBe("message_sent");
    });

    it("emits self-heal:session-patched on agent_end with session context", () => {
      fs.writeFileSync(
        sessionsFile,
        JSON.stringify({ "s1": { model: "model-a" } })
      );

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a", "model-b"],
          cooldownMinutes: 10,
        },
      });
      register(api);

      api._emit(
        "agent_end",
        { success: false, error: "rate limit hit" },
        { sessionKey: "s1" }
      );

      const ev = api._emitted.find((e) => e.event === "self-heal:session-patched");
      expect(ev).toBeDefined();
      expect(ev!.payload.sessionKey).toBe("s1");
      expect(ev!.payload.oldModel).toBe("model-a");
      expect(ev!.payload.newModel).toBe("model-b");
      expect(ev!.payload.trigger).toBe("agent_end");
      expect(ev!.payload.dryRun).toBe(false);
    });

    it("emits self-heal:session-patched on message_sent with session context", () => {
      fs.writeFileSync(
        sessionsFile,
        JSON.stringify({ "s1": { model: "primary" } })
      );

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["primary", "fallback"],
          cooldownMinutes: 5,
        },
      });
      register(api);

      api._emit(
        "message_sent",
        { content: "429 Too Many Requests" },
        { sessionKey: "s1" }
      );

      const ev = api._emitted.find((e) => e.event === "self-heal:session-patched");
      expect(ev).toBeDefined();
      expect(ev!.payload.sessionKey).toBe("s1");
      expect(ev!.payload.oldModel).toBe("primary");
      expect(ev!.payload.newModel).toBe("fallback");
      expect(ev!.payload.trigger).toBe("message_sent");
    });

    it("does not emit session-patched when no session context", () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a", "model-b"],
          cooldownMinutes: 10,
        },
      });
      register(api);

      api._emit(
        "agent_end",
        { success: false, error: "rate limit hit" },
        {}
      );

      const ev = api._emitted.find((e) => e.event === "self-heal:session-patched");
      expect(ev).toBeUndefined();
    });

    it("emits self-heal:model-cooldown with dryRun=true in dry-run mode", () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a", "model-b"],
          cooldownMinutes: 10,
          dryRun: true,
        },
      });
      register(api);

      api._emit(
        "agent_end",
        { success: false, error: "rate limit hit" },
        {}
      );

      const ev = api._emitted.find((e) => e.event === "self-heal:model-cooldown");
      expect(ev).toBeDefined();
      expect(ev!.payload.dryRun).toBe(true);
    });

    it("emits self-heal:session-patched with dryRun=true in dry-run mode", () => {
      fs.writeFileSync(
        sessionsFile,
        JSON.stringify({ "s1": { model: "model-a" } })
      );

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a", "model-b"],
          cooldownMinutes: 10,
          dryRun: true,
        },
      });
      register(api);

      api._emit(
        "agent_end",
        { success: false, error: "rate limit hit" },
        { sessionKey: "s1" }
      );

      const ev = api._emitted.find((e) => e.event === "self-heal:session-patched");
      expect(ev).toBeDefined();
      expect(ev!.payload.dryRun).toBe(true);
    });

    it("emits self-heal:whatsapp-restart when WhatsApp is restarted", async () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: path.join(dir, "backups"),
          modelOrder: ["model-a"],
          dryRun: true,
          autoFix: { restartWhatsappOnDisconnect: true, whatsappDisconnectThreshold: 2 },
        },
      });

      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: JSON.stringify({ channels: { whatsapp: { status: "disconnected" } } }),
        stderr: "",
      });

      saveState(stateFile, {
        ...emptyState(),
        whatsapp: { disconnectStreak: 2, lastRestartAt: 0 },
      });

      register(api);

      const svc = api._services[0];
      await svc.start();
      await new Promise((r) => setTimeout(r, 50));
      await svc.stop();

      const ev = api._emitted.find((e) => e.event === "self-heal:whatsapp-restart");
      expect(ev).toBeDefined();
      expect(ev!.payload.disconnectStreak).toBeGreaterThanOrEqual(2);
      expect(ev!.payload.dryRun).toBe(true);
    });

    it("emits self-heal:cron-disabled when a cron is disabled", async () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: path.join(dir, "backups"),
          modelOrder: ["model-a"],
          dryRun: true,
          autoFix: { disableFailingCrons: true, cronFailThreshold: 1 },
        },
      });

      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: JSON.stringify({
          jobs: [{ id: "cron-1", name: "test-cron", state: { lastStatus: "error", lastError: "timeout exceeded" } }],
        }),
        stderr: "",
      });

      register(api);

      const svc = api._services[0];
      await svc.start();
      await new Promise((r) => setTimeout(r, 50));
      await svc.stop();

      const ev = api._emitted.find((e) => e.event === "self-heal:cron-disabled");
      expect(ev).toBeDefined();
      expect(ev!.payload.cronId).toBe("cron-1");
      expect(ev!.payload.cronName).toBe("test-cron");
      expect(ev!.payload.consecutiveFailures).toBeGreaterThanOrEqual(1);
      expect(ev!.payload.lastError).toBe("timeout exceeded");
      expect(ev!.payload.dryRun).toBe(true);
    });

    it("emits self-heal:model-recovered when a model recovers via probe", async () => {
      const hitAt = nowSec() - 400;
      saveState(stateFile, {
        ...emptyState(),
        limited: {
          "model-a": { lastHitAt: hitAt, nextAvailableAt: nowSec() + 9999 },
        },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a", "model-b"],
          probeEnabled: true,
          probeIntervalSec: 300,
        },
      });
      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: "ok",
        stderr: "",
      });
      register(api);

      const svc = api._services[0];
      await svc.start();
      await new Promise((r) => setTimeout(r, 50));
      await svc.stop();

      const ev = api._emitted.find((e) => e.event === "self-heal:model-recovered");
      expect(ev).toBeDefined();
      expect(ev!.payload.model).toBe("model-a");
      expect(ev!.payload.isPreferred).toBe(true);
    });

    it("emits model-recovered with isPreferred=false for non-primary models", async () => {
      const hitAt = nowSec() - 400;
      saveState(stateFile, {
        ...emptyState(),
        limited: {
          "model-b": { lastHitAt: hitAt, nextAvailableAt: nowSec() + 9999 },
        },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a", "model-b"],
          probeEnabled: true,
          probeIntervalSec: 300,
        },
      });
      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: "ok",
        stderr: "",
      });
      register(api);

      const svc = api._services[0];
      await svc.start();
      await new Promise((r) => setTimeout(r, 50));
      await svc.stop();

      const ev = api._emitted.find((e) => e.event === "self-heal:model-recovered");
      expect(ev).toBeDefined();
      expect(ev!.payload.model).toBe("model-b");
      expect(ev!.payload.isPreferred).toBe(false);
    });

    it("does not emit model-recovered when probe fails", async () => {
      const hitAt = nowSec() - 400;
      saveState(stateFile, {
        ...emptyState(),
        limited: {
          "model-a": { lastHitAt: hitAt, nextAvailableAt: nowSec() + 9999 },
        },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a", "model-b"],
          probeEnabled: true,
          probeIntervalSec: 300,
        },
      });
      // Default mock returns exitCode 1
      register(api);

      const svc = api._services[0];
      await svc.start();
      await new Promise((r) => setTimeout(r, 50));
      await svc.stop();

      const ev = api._emitted.find((e) => e.event === "self-heal:model-recovered");
      expect(ev).toBeUndefined();
    });

    it("does not emit any events for non-rate-limit errors", () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a"],
        },
      });
      register(api);

      api._emit("agent_end", { success: false, error: "generic timeout" }, {});

      expect(api._emitted).toHaveLength(0);
    });

    it("emits cooldown event with extra duration for auth errors", () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          modelOrder: ["model-a", "model-b"],
          cooldownMinutes: 10,
        },
      });
      register(api);

      api._emit(
        "agent_end",
        { success: false, error: "HTTP 401 Unauthorized" },
        {}
      );

      const ev = api._emitted.find((e) => e.event === "self-heal:model-cooldown");
      expect(ev).toBeDefined();
      // Auth errors add 12 * 60 = 720 minutes, total (10 + 720) * 60 = 43800 seconds
      expect(ev!.payload.cooldownSec).toBe((10 + 720) * 60);
    });
  });
});

// ---------------------------------------------------------------------------
// parseConfig
// ---------------------------------------------------------------------------

describe("parseConfig", () => {
  afterEach(() => {
    delete process.env.GITHUB_REPOSITORY;
  });

  it("returns defaults for empty input", () => {
    const c = parseConfig({});
    expect(c.modelOrder).toEqual([
      "anthropic/claude-opus-4-6",
      "openai-codex/gpt-5.2",
      "google-gemini-cli/gemini-2.5-flash",
    ]);
    expect(c.cooldownMinutes).toBe(300);
    expect(c.patchPins).toBe(true);
    expect(c.disableFailingCrons).toBe(false);
    expect(c.disableFailingPlugins).toBe(false);
    expect(c.whatsappRestartEnabled).toBe(true);
    expect(c.whatsappDisconnectThreshold).toBe(2);
    expect(c.whatsappMinRestartIntervalSec).toBe(300);
    expect(c.cronFailThreshold).toBe(3);
    expect(c.issueCooldownSec).toBe(6 * 3600);
    expect(c.issueRepo).toBe("elvatis/openclaw-self-healing-homeofe");
    expect(c.pluginDisableCooldownSec).toBe(3600);
    expect(c.probeEnabled).toBe(true);
    expect(c.probeIntervalSec).toBe(300);
    expect(c.dryRun).toBe(false);
  });

  it("returns defaults for undefined input", () => {
    const c = parseConfig(undefined);
    expect(c.cooldownMinutes).toBe(300);
    expect(c.modelOrder).toHaveLength(3);
  });

  it("applies custom values", () => {
    const c = parseConfig({
      modelOrder: ["a", "b"],
      cooldownMinutes: 60,
      autoFix: {
        patchSessionPins: false,
        disableFailingCrons: true,
        cronFailThreshold: 5,
      },
    });
    expect(c.modelOrder).toEqual(["a", "b"]);
    expect(c.cooldownMinutes).toBe(60);
    expect(c.patchPins).toBe(false);
    expect(c.disableFailingCrons).toBe(true);
    expect(c.cronFailThreshold).toBe(5);
  });

  it("applies custom issueRepo", () => {
    const c = parseConfig({ autoFix: { issueRepo: "owner/custom-repo" } });
    expect(c.issueRepo).toBe("owner/custom-repo");
  });

  it("uses env issue repo when config value is missing", () => {
    process.env.GITHUB_REPOSITORY = "owner/from-env";
    const c = parseConfig({});
    expect(c.issueRepo).toBe("owner/from-env");
  });

  it("falls back to default when configured issueRepo is invalid", () => {
    const c = parseConfig({ autoFix: { issueRepo: "not-a-slug" } });
    expect(c.issueRepo).toBe("elvatis/openclaw-self-healing-homeofe");
  });

  it("does not share modelOrder array reference with input", () => {
    const input = { modelOrder: ["a", "b"] };
    const c = parseConfig(input);
    input.modelOrder.push("c");
    expect(c.modelOrder).toEqual(["a", "b"]);
  });

  it("expands tilde paths", () => {
    const c = parseConfig({ stateFile: "~/my-state.json" });
    expect(c.stateFile).toBe(path.join(os.homedir(), "my-state.json"));
  });

  it("returns default statusFile path", () => {
    const c = parseConfig({});
    expect(c.statusFile).toBe(
      path.join(os.homedir(), ".openclaw", "workspace", "memory", "self-heal-status.json")
    );
  });

  it("applies custom statusFile path", () => {
    const c = parseConfig({ statusFile: "~/custom-status.json" });
    expect(c.statusFile).toBe(path.join(os.homedir(), "custom-status.json"));
  });

  it("applies custom probe config", () => {
    const c = parseConfig({ probeEnabled: false, probeIntervalSec: 120 });
    expect(c.probeEnabled).toBe(false);
    expect(c.probeIntervalSec).toBe(120);
  });

  it("applies dryRun config", () => {
    const c = parseConfig({ dryRun: true });
    expect(c.dryRun).toBe(true);
  });
});

describe("GitHub issue helpers", () => {
  it("validates owner/repo slug", () => {
    expect(isValidIssueRepoSlug("elvatis/openclaw-self-healing-homeofe")).toBe(true);
    expect(isValidIssueRepoSlug("owner/repo_1")).toBe(true);
    expect(isValidIssueRepoSlug("bad")).toBe(false);
    expect(isValidIssueRepoSlug("owner/repo/extra")).toBe(false);
  });

  it("resolves issue repo from config then env then default", () => {
    expect(resolveIssueRepo("owner/config-repo", "owner/env-repo")).toBe("owner/config-repo");
    expect(resolveIssueRepo("bad", "owner/env-repo")).toBe("owner/env-repo");
    expect(resolveIssueRepo(undefined, "bad")).toBe("elvatis/openclaw-self-healing-homeofe");
  });

  it("builds shell-safe gh issue command with labels", () => {
    const cmd = buildGhIssueCreateCommand({
      repo: "owner/repo",
      title: "Cron disabled: Bob's job",
      body: "Line1\nLine2 with 'quote'",
      labels: ["security", "triage"],
    });

    expect(cmd).toContain("gh issue create");
    expect(cmd).toContain("-R 'owner/repo'");
    expect(cmd).toContain("--label 'security,triage'");
    expect(cmd).toContain("Bob'\"'\"'s job");
  });

  it("throws on invalid repo in command builder", () => {
    expect(() =>
      buildGhIssueCreateCommand({
        repo: "bad-repo",
        title: "t",
        body: "b",
      })
    ).toThrow("Invalid issue repository slug");
  });
});

// ---------------------------------------------------------------------------
// configDiff
// ---------------------------------------------------------------------------

describe("configDiff", () => {
  function defaultConfig(overrides: Partial<PluginConfig> = {}): PluginConfig {
    return parseConfig(overrides);
  }

  it("returns empty array for identical configs", () => {
    const a = defaultConfig();
    const b = defaultConfig();
    expect(configDiff(a, b)).toEqual([]);
  });

  it("detects scalar value changes", () => {
    const a = defaultConfig();
    const b = defaultConfig();
    b.cooldownMinutes = 999;
    expect(configDiff(a, b)).toEqual(["cooldownMinutes"]);
  });

  it("detects array value changes", () => {
    const a = defaultConfig();
    const b = defaultConfig();
    b.modelOrder = ["different-model"];
    expect(configDiff(a, b)).toContain("modelOrder");
  });

  it("detects boolean changes", () => {
    const a = defaultConfig();
    const b = defaultConfig();
    b.patchPins = !a.patchPins;
    expect(configDiff(a, b)).toContain("patchPins");
  });

  it("detects multiple changes", () => {
    const a = defaultConfig();
    const b = defaultConfig();
    b.cooldownMinutes = 1;
    b.cronFailThreshold = 99;
    b.whatsappRestartEnabled = !a.whatsappRestartEnabled;
    const diff = configDiff(a, b);
    expect(diff).toContain("cooldownMinutes");
    expect(diff).toContain("cronFailThreshold");
    expect(diff).toContain("whatsappRestartEnabled");
  });
});

// ---------------------------------------------------------------------------
// buildStatusSnapshot
// ---------------------------------------------------------------------------

describe("buildStatusSnapshot", () => {
  function defaultConfig(overrides: Partial<PluginConfig> = {}): PluginConfig {
    return parseConfig(overrides);
  }

  it("returns healthy status when no models are in cooldown", () => {
    const state = emptyState();
    const config = defaultConfig();
    const snap = buildStatusSnapshot(state, config);

    expect(snap.health).toBe("healthy");
    expect(snap.activeModel).toBe(config.modelOrder[0]);
    expect(snap.models).toHaveLength(config.modelOrder.length);
    expect(snap.models.every((m) => m.status === "available")).toBe(true);
    expect(snap.generatedAt).toBeGreaterThan(0);
  });

  it("returns degraded status when some models are in cooldown", () => {
    const state = emptyState();
    const config = defaultConfig();
    const t = nowSec();
    state.limited[config.modelOrder[0]] = {
      lastHitAt: t,
      nextAvailableAt: t + 3600,
      reason: "rate limit",
    };
    const snap = buildStatusSnapshot(state, config);

    expect(snap.health).toBe("degraded");
    expect(snap.activeModel).toBe(config.modelOrder[1]);
    expect(snap.models[0].status).toBe("cooldown");
    expect(snap.models[0].cooldownReason).toBe("rate limit");
    expect(snap.models[0].cooldownRemainingSec).toBeGreaterThan(0);
    expect(snap.models[0].nextAvailableAt).toBe(t + 3600);
    expect(snap.models[1].status).toBe("available");
  });

  it("returns healing status when all models are in cooldown", () => {
    const state = emptyState();
    const config = defaultConfig();
    const t = nowSec();
    for (const m of config.modelOrder) {
      state.limited[m] = { lastHitAt: t, nextAvailableAt: t + 3600 };
    }
    const snap = buildStatusSnapshot(state, config);

    expect(snap.health).toBe("healing");
    expect(snap.models.every((m) => m.status === "cooldown")).toBe(true);
    // activeModel falls back to the last model in order
    expect(snap.activeModel).toBe(config.modelOrder[config.modelOrder.length - 1]);
  });

  it("excludes expired cooldowns from cooldown status", () => {
    const state = emptyState();
    const config = defaultConfig();
    const t = nowSec();
    state.limited[config.modelOrder[0]] = {
      lastHitAt: t - 7200,
      nextAvailableAt: t - 100, // expired
    };
    const snap = buildStatusSnapshot(state, config);

    expect(snap.health).toBe("healthy");
    expect(snap.models[0].status).toBe("available");
    expect(snap.models[0].cooldownReason).toBeUndefined();
  });

  it("includes lastProbeAt in cooldown model details", () => {
    const state = emptyState();
    const config = defaultConfig();
    const t = nowSec();
    state.limited[config.modelOrder[0]] = {
      lastHitAt: t,
      nextAvailableAt: t + 3600,
      reason: "429",
      lastProbeAt: t + 300,
    };
    const snap = buildStatusSnapshot(state, config);

    expect(snap.models[0].lastProbeAt).toBe(t + 300);
  });

  it("reports WhatsApp as connected when lastSeenConnectedAt is set and streak is 0", () => {
    const state = emptyState();
    const config = defaultConfig();
    state.whatsapp = { lastSeenConnectedAt: nowSec(), disconnectStreak: 0 };
    const snap = buildStatusSnapshot(state, config);

    expect(snap.whatsapp.status).toBe("connected");
    expect(snap.whatsapp.disconnectStreak).toBe(0);
    expect(snap.whatsapp.lastSeenConnectedAt).toBeGreaterThan(0);
  });

  it("reports WhatsApp as disconnected when streak > 0", () => {
    const state = emptyState();
    const config = defaultConfig();
    state.whatsapp = { disconnectStreak: 3, lastRestartAt: 1000 };
    const snap = buildStatusSnapshot(state, config);

    expect(snap.whatsapp.status).toBe("disconnected");
    expect(snap.whatsapp.disconnectStreak).toBe(3);
    expect(snap.whatsapp.lastRestartAt).toBe(1000);
  });

  it("reports WhatsApp as unknown when no data is available", () => {
    const state = emptyState();
    const config = defaultConfig();
    const snap = buildStatusSnapshot(state, config);

    expect(snap.whatsapp.status).toBe("unknown");
    expect(snap.whatsapp.disconnectStreak).toBe(0);
    expect(snap.whatsapp.lastRestartAt).toBeNull();
    expect(snap.whatsapp.lastSeenConnectedAt).toBeNull();
  });

  it("reports cron failing jobs", () => {
    const state = emptyState();
    const config = defaultConfig();
    state.cron = {
      failCounts: { "job-1": 3, "job-2": 0, "job-3": 1 },
      lastIssueCreatedAt: {},
    };
    const snap = buildStatusSnapshot(state, config);

    expect(snap.cron.trackedJobs).toBe(3);
    expect(snap.cron.failingJobs).toHaveLength(2);
    expect(snap.cron.failingJobs).toEqual(
      expect.arrayContaining([
        { id: "job-1", consecutiveFailures: 3 },
        { id: "job-3", consecutiveFailures: 1 },
      ])
    );
  });

  it("reports empty cron state when no jobs are tracked", () => {
    const state = emptyState();
    const config = defaultConfig();
    const snap = buildStatusSnapshot(state, config);

    expect(snap.cron.trackedJobs).toBe(0);
    expect(snap.cron.failingJobs).toEqual([]);
  });

  it("includes config summary in snapshot", () => {
    const config = defaultConfig({ dryRun: true, probeEnabled: false, cooldownMinutes: 60 });
    const snap = buildStatusSnapshot(emptyState(), config);

    expect(snap.config.dryRun).toBe(true);
    expect(snap.config.probeEnabled).toBe(false);
    expect(snap.config.cooldownMinutes).toBe(60);
    expect(snap.config.modelOrder).toEqual(config.modelOrder);
  });

  it("config.modelOrder is a copy, not a reference", () => {
    const config = defaultConfig();
    const snap = buildStatusSnapshot(emptyState(), config);

    snap.config.modelOrder.push("mutated");
    expect(config.modelOrder).not.toContain("mutated");
  });

  it("emits self-heal:status event during monitor tick", async () => {
    const dir = tmpDir();
    const stateFile = path.join(dir, "state.json");
    const sessionsFile = path.join(dir, "sessions.json");
    const configFile = path.join(dir, "config.json");
    const backupsDir = path.join(dir, "backups");
    fs.writeFileSync(stateFile, JSON.stringify({ limited: {} }));
    fs.writeFileSync(sessionsFile, "{}");
    fs.writeFileSync(configFile, "{}");

    const api = mockApi({
      pluginConfig: { stateFile, sessionsFile, configFile, configBackupsDir: backupsDir },
    });
    register(api);

    const svc = api._services[0];
    await svc.start();
    await svc.stop();

    const statusEvents = api._emitted.filter((e: any) => e.event === "self-heal:status");
    expect(statusEvents).toHaveLength(1);

    const snap = statusEvents[0].payload as StatusSnapshot;
    expect(snap.health).toBe("healthy");
    expect(snap.generatedAt).toBeGreaterThan(0);
    expect(snap.activeModel).toBeTruthy();
    expect(snap.models).toBeDefined();
    expect(snap.whatsapp).toBeDefined();
    expect(snap.cron).toBeDefined();
    expect(snap.config).toBeDefined();
  });
});

// ---------------------------------------------------------------------------
// validateConfig
// ---------------------------------------------------------------------------

describe("validateConfig", () => {
  function validConfig(overrides: Partial<PluginConfig> = {}): PluginConfig {
    const dir = tmpDir();
    return {
      modelOrder: ["anthropic/claude-opus-4-6"],
      cooldownMinutes: 300,
      stateFile: path.join(dir, "state.json"),
      statusFile: path.join(dir, "status.json"),
      sessionsFile: path.join(dir, "sessions.json"),
      configFile: path.join(dir, "openclaw.json"),
      configBackupsDir: path.join(dir, "backups"),
      patchPins: true,
      disableFailingCrons: false,
      disableFailingPlugins: false,
      whatsappRestartEnabled: true,
      whatsappDisconnectThreshold: 2,
      whatsappMinRestartIntervalSec: 300,
      cronFailThreshold: 3,
      issueCooldownSec: 21600,
      issueRepo: "elvatis/openclaw-self-healing-homeofe",
      pluginDisableCooldownSec: 3600,
      probeEnabled: true,
      probeIntervalSec: 300,
      dryRun: false,
      ...overrides,
    };
  }

  it("accepts a valid default config", () => {
    const result = validateConfig(validConfig());
    expect(result.valid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  it("rejects empty modelOrder", () => {
    const result = validateConfig(validConfig({ modelOrder: [] }));
    expect(result.valid).toBe(false);
    expect(result.errors).toContain("modelOrder must have at least one entry");
  });

  it("rejects modelOrder that is not an array", () => {
    const result = validateConfig(validConfig({ modelOrder: "not-array" as any }));
    expect(result.valid).toBe(false);
    expect(result.errors).toContain("modelOrder must have at least one entry");
  });

  it("rejects cooldownMinutes below 1", () => {
    const result = validateConfig(validConfig({ cooldownMinutes: 0 }));
    expect(result.valid).toBe(false);
    expect(result.errors).toContain("cooldownMinutes must be between 1 and 10080 (1 week)");
  });

  it("rejects cooldownMinutes above 10080", () => {
    const result = validateConfig(validConfig({ cooldownMinutes: 10081 }));
    expect(result.valid).toBe(false);
    expect(result.errors).toContain("cooldownMinutes must be between 1 and 10080 (1 week)");
  });

  it("accepts cooldownMinutes at boundary 1", () => {
    const result = validateConfig(validConfig({ cooldownMinutes: 1 }));
    expect(result.valid).toBe(true);
  });

  it("accepts cooldownMinutes at boundary 10080", () => {
    const result = validateConfig(validConfig({ cooldownMinutes: 10080 }));
    expect(result.valid).toBe(true);
  });

  it("rejects cooldownMinutes that is not a number", () => {
    const result = validateConfig(validConfig({ cooldownMinutes: "abc" as any }));
    expect(result.valid).toBe(false);
    expect(result.errors).toContain("cooldownMinutes must be between 1 and 10080 (1 week)");
  });

  it("rejects probeIntervalSec below 60", () => {
    const result = validateConfig(validConfig({ probeIntervalSec: 59 }));
    expect(result.valid).toBe(false);
    expect(result.errors).toContain("probeIntervalSec must be >= 60");
  });

  it("accepts probeIntervalSec at boundary 60", () => {
    const result = validateConfig(validConfig({ probeIntervalSec: 60 }));
    expect(result.valid).toBe(true);
  });

  it("rejects whatsappMinRestartIntervalSec below 60", () => {
    const result = validateConfig(validConfig({ whatsappMinRestartIntervalSec: 30 }));
    expect(result.valid).toBe(false);
    expect(result.errors).toContain("whatsappMinRestartIntervalSec must be >= 60");
  });

  it("accepts whatsappMinRestartIntervalSec at boundary 60", () => {
    const result = validateConfig(validConfig({ whatsappMinRestartIntervalSec: 60 }));
    expect(result.valid).toBe(true);
  });

  it("rejects non-writable stateFile directory", () => {
    // Create a file, then try to use a path inside it as a directory - fails on all platforms
    const dir = tmpDir();
    const blocker = path.join(dir, "blocker");
    fs.writeFileSync(blocker, "occupied");
    const result = validateConfig(validConfig({ stateFile: path.join(blocker, "sub", "state.json") }));
    expect(result.valid).toBe(false);
    expect(result.errors.some((e) => e.includes("stateFile directory is not writable"))).toBe(true);
  });

  it("collects multiple errors at once", () => {
    const result = validateConfig(
      validConfig({
        modelOrder: [],
        cooldownMinutes: 0,
        probeIntervalSec: 10,
        whatsappMinRestartIntervalSec: 5,
      })
    );
    expect(result.valid).toBe(false);
    expect(result.errors.length).toBeGreaterThanOrEqual(4);
  });

  it("accepts parseConfig defaults (valid config from defaults)", () => {
    // parseConfig with no overrides should produce a valid config
    // (state directory may not be writable in CI, so we override stateFile)
    const dir = tmpDir();
    const cfg = parseConfig({});
    cfg.stateFile = path.join(dir, "state.json");
    const result = validateConfig(cfg);
    expect(result.valid).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// register() fail-fast on invalid config
// ---------------------------------------------------------------------------

describe("register() config validation fail-fast", () => {
  it("does not register services or event handlers when config is invalid", () => {
    const dir = tmpDir();
    const api = mockApi({
      pluginConfig: {
        cooldownMinutes: 0,
        probeIntervalSec: 10,
        stateFile: path.join(dir, "state.json"),
      },
    });

    register(api);

    expect(api._services).toHaveLength(0);
    expect(api._handlers["agent_end"]).toBeUndefined();
    expect(api._handlers["message_sent"]).toBeUndefined();
    expect(api.logger.error).toHaveBeenCalled();

    const errorCalls = api.logger.error.mock.calls.map((c: any) => c[0]);
    expect(errorCalls.some((m: string) => m.includes("config validation failed"))).toBe(true);
    expect(errorCalls.some((m: string) => m.includes("plugin not started"))).toBe(true);
  });

  it("logs all validation errors individually", () => {
    const dir = tmpDir();
    const blocker = path.join(dir, "blocker");
    fs.writeFileSync(blocker, "occupied");
    const api = mockApi({
      pluginConfig: {
        cooldownMinutes: 0,
        probeIntervalSec: 10,
        autoFix: { whatsappMinRestartIntervalSec: 5 },
        stateFile: path.join(blocker, "sub", "state.json"),
      },
    });

    register(api);

    const errorCalls = api.logger.error.mock.calls.map((c: any) => c[0]);
    const validationErrors = errorCalls.filter((m: string) => m.includes("config validation failed"));
    expect(validationErrors.length).toBeGreaterThanOrEqual(4);
  });

  it("registers services and handlers when config is valid", () => {
    const dir = tmpDir();
    const api = mockApi({
      pluginConfig: {
        modelOrder: ["anthropic/claude-opus-4-6"],
        cooldownMinutes: 300,
        probeIntervalSec: 300,
        whatsappMinRestartIntervalSec: 300,
        stateFile: path.join(dir, "state.json"),
      },
    });

    register(api);

    expect(api._services).toHaveLength(1);
    expect(api._handlers["agent_end"]).toBeDefined();
    expect(api._handlers["message_sent"]).toBeDefined();
  });
});

// ---------------------------------------------------------------------------
// writeStatusFile
// ---------------------------------------------------------------------------

describe("writeStatusFile", () => {
  function sampleSnapshot(): StatusSnapshot {
    return {
      health: "healthy",
      activeModel: "anthropic/claude-opus-4-6",
      models: [
        { id: "anthropic/claude-opus-4-6", status: "available" },
      ],
      whatsapp: {
        status: "unknown",
        disconnectStreak: 0,
        lastRestartAt: null,
        lastSeenConnectedAt: null,
      },
      cron: { trackedJobs: 0, failingJobs: [] },
      config: {
        dryRun: false,
        probeEnabled: true,
        cooldownMinutes: 300,
        modelOrder: ["anthropic/claude-opus-4-6"],
      },
      generatedAt: 1700000000,
    };
  }

  it("writes valid JSON matching the snapshot", () => {
    const dir = tmpDir();
    const filePath = path.join(dir, "status.json");
    const snap = sampleSnapshot();

    writeStatusFile(filePath, snap);

    const content = fs.readFileSync(filePath, "utf-8");
    const parsed = JSON.parse(content);
    expect(parsed).toEqual(snap);
  });

  it("creates parent directories if they do not exist", () => {
    const dir = tmpDir();
    const filePath = path.join(dir, "nested", "deep", "status.json");

    writeStatusFile(filePath, sampleSnapshot());

    expect(fs.existsSync(filePath)).toBe(true);
  });

  it("overwrites existing file on subsequent writes", () => {
    const dir = tmpDir();
    const filePath = path.join(dir, "status.json");

    const snap1 = sampleSnapshot();
    writeStatusFile(filePath, snap1);

    const snap2 = sampleSnapshot();
    snap2.health = "degraded";
    snap2.generatedAt = 1700000060;
    writeStatusFile(filePath, snap2);

    const parsed = JSON.parse(fs.readFileSync(filePath, "utf-8"));
    expect(parsed.health).toBe("degraded");
    expect(parsed.generatedAt).toBe(1700000060);
  });

  it("does not leave a .tmp file after successful write", () => {
    const dir = tmpDir();
    const filePath = path.join(dir, "status.json");

    writeStatusFile(filePath, sampleSnapshot());

    expect(fs.existsSync(filePath + ".tmp")).toBe(false);
    expect(fs.existsSync(filePath)).toBe(true);
  });

  it("writes pretty-printed JSON (2-space indent)", () => {
    const dir = tmpDir();
    const filePath = path.join(dir, "status.json");
    const snap = sampleSnapshot();

    writeStatusFile(filePath, snap);

    const content = fs.readFileSync(filePath, "utf-8");
    expect(content).toBe(JSON.stringify(snap, null, 2));
  });

  it("monitor tick writes status file", async () => {
    const dir = tmpDir();
    const stateFile = path.join(dir, "state.json");
    const statusFile = path.join(dir, "status.json");
    const sessionsFile = path.join(dir, "sessions.json");
    const configFile = path.join(dir, "config.json");
    const backupsDir = path.join(dir, "backups");
    fs.writeFileSync(stateFile, JSON.stringify({ limited: {} }));
    fs.writeFileSync(sessionsFile, "{}");
    fs.writeFileSync(configFile, "{}");

    const api = mockApi({
      pluginConfig: { stateFile, statusFile, sessionsFile, configFile, configBackupsDir: backupsDir },
    });
    register(api);

    const svc = api._services[0];
    await svc.start();
    await svc.stop();

    expect(fs.existsSync(statusFile)).toBe(true);
    const parsed = JSON.parse(fs.readFileSync(statusFile, "utf-8")) as StatusSnapshot;
    expect(parsed.health).toBe("healthy");
    expect(parsed.generatedAt).toBeGreaterThan(0);
    expect(parsed.activeModel).toBeTruthy();
    expect(parsed.models).toBeDefined();
    expect(parsed.whatsapp).toBeDefined();
    expect(parsed.cron).toBeDefined();
    expect(parsed.config).toBeDefined();
  });

  it("logs warning but does not throw when status file write fails", async () => {
    const dir = tmpDir();
    const stateFile = path.join(dir, "state.json");
    // Point statusFile at a path that cannot be created (file used as directory)
    const blocker = path.join(dir, "blocker");
    fs.writeFileSync(blocker, "not-a-directory");
    const statusFile = path.join(blocker, "sub", "status.json");
    const sessionsFile = path.join(dir, "sessions.json");
    const configFile = path.join(dir, "config.json");
    const backupsDir = path.join(dir, "backups");
    fs.writeFileSync(stateFile, JSON.stringify({ limited: {} }));
    fs.writeFileSync(sessionsFile, "{}");
    fs.writeFileSync(configFile, "{}");

    const api = mockApi({
      pluginConfig: { stateFile, statusFile, sessionsFile, configFile, configBackupsDir: backupsDir },
    });
    register(api);

    const svc = api._services[0];
    // Should not throw
    await svc.start();
    await svc.stop();

    // Should have logged a warning about failed status file write
    const warnCalls = api.logger.warn.mock.calls.map((c: any[]) => c[0]);
    expect(warnCalls.some((msg: string) => msg.includes("failed to write status file"))).toBe(true);
  });
});
