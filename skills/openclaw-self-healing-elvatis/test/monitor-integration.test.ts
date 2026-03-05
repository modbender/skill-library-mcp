import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import {
  nowSec,
  loadState,
  saveState,
  type State,
} from "../index.js";
import register from "../index.js";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function tmpDir(): string {
  return fs.mkdtempSync(path.join(os.tmpdir(), "self-heal-integ-"));
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

/** Start the monitor service, wait for the initial tick, then stop. */
async function runOneTick(api: ReturnType<typeof mockApi>) {
  const svc = api._services[0];
  await svc.start();
  await new Promise((r) => setTimeout(r, 50));
  await svc.stop();
}

/** Build a command-matching predicate for runCommandWithTimeout call args. */
function cmdContains(call: any[], fragment: string): boolean {
  const cmd = call[0]?.command?.join(" ") ?? "";
  return cmd.includes(fragment);
}

/** Filter all runCommandWithTimeout calls by command fragment. */
function filterCmdCalls(api: ReturnType<typeof mockApi>, fragment: string): any[][] {
  return api.runtime.system.runCommandWithTimeout.mock.calls.filter(
    (c: any[]) => cmdContains(c, fragment)
  );
}

/** Find emitted events by name. */
function findEmitted(api: ReturnType<typeof mockApi>, eventName: string) {
  return api._emitted.filter((e) => e.event === eventName);
}

// ---------------------------------------------------------------------------
// Monitor Integration Tests - Full Tick Cycle
// ---------------------------------------------------------------------------

describe("monitor service - integration tick flows", () => {
  let dir: string;
  let stateFile: string;
  let sessionsFile: string;
  let configFile: string;
  let backupsDir: string;

  beforeEach(() => {
    dir = tmpDir();
    stateFile = path.join(dir, "state.json");
    sessionsFile = path.join(dir, "sessions.json");
    configFile = path.join(dir, "openclaw.json");
    backupsDir = path.join(dir, "backups");
    fs.writeFileSync(configFile, JSON.stringify({ valid: true }));
  });

  afterEach(() => {
    fs.rmSync(dir, { recursive: true, force: true });
  });

  // -------------------------------------------------------------------------
  // WhatsApp disconnect streak -> restart path
  // -------------------------------------------------------------------------

  describe("WhatsApp disconnect streak -> restart path", () => {
    it("increments disconnect streak on each tick with disconnected status", async () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a"],
          autoFix: { restartWhatsappOnDisconnect: true, whatsappDisconnectThreshold: 5 },
        },
      });
      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: JSON.stringify({ channels: { whatsapp: { status: "disconnected" } } }),
        stderr: "",
      });
      register(api);

      await runOneTick(api);

      const state = loadState(stateFile);
      expect(state.whatsapp!.disconnectStreak).toBe(1);
    });

    it("resets disconnect streak when WhatsApp is connected", async () => {
      saveState(stateFile, {
        ...emptyState(),
        whatsapp: { disconnectStreak: 3, lastRestartAt: nowSec() - 1000 },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a"],
        },
      });
      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: JSON.stringify({ channels: { whatsapp: { status: "connected" } } }),
        stderr: "",
      });
      register(api);

      await runOneTick(api);

      const state = loadState(stateFile);
      expect(state.whatsapp!.disconnectStreak).toBe(0);
      expect(state.whatsapp!.lastSeenConnectedAt).toBeGreaterThan(0);
    });

    it("triggers gateway restart when disconnect streak reaches threshold", async () => {
      // Pre-seed state with streak at threshold - 1 so next tick triggers restart
      saveState(stateFile, {
        ...emptyState(),
        whatsapp: { disconnectStreak: 1, lastRestartAt: 0 },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a"],
          autoFix: { whatsappDisconnectThreshold: 2, whatsappMinRestartIntervalSec: 60 },
        },
      });
      api.runtime.system.runCommandWithTimeout.mockImplementation(async (opts: any) => {
        const cmd = opts?.command?.join(" ") ?? "";
        if (cmd.includes("channels status")) {
          return {
            exitCode: 0,
            stdout: JSON.stringify({ channels: { whatsapp: { status: "disconnected" } } }),
            stderr: "",
          };
        }
        if (cmd.includes("gateway restart")) {
          return { exitCode: 0, stdout: "restarted", stderr: "" };
        }
        if (cmd.includes("gateway status")) {
          return { exitCode: 0, stdout: "ok", stderr: "" };
        }
        return { exitCode: 1, stdout: "", stderr: "unknown" };
      });
      register(api);

      await runOneTick(api);

      // Verify gateway restart was called
      const restartCalls = filterCmdCalls(api, "gateway restart");
      expect(restartCalls.length).toBeGreaterThanOrEqual(1);

      // Verify state was reset
      const state = loadState(stateFile);
      expect(state.whatsapp!.disconnectStreak).toBe(0);
      expect(state.whatsapp!.lastRestartAt).toBeGreaterThan(0);

      // Verify event emitted
      const events = findEmitted(api, "self-heal:whatsapp-restart");
      expect(events).toHaveLength(1);
      expect(events[0].payload.dryRun).toBe(false);
    });

    it("does not restart if minimum restart interval has not elapsed", async () => {
      saveState(stateFile, {
        ...emptyState(),
        whatsapp: { disconnectStreak: 5, lastRestartAt: nowSec() - 10 }, // restarted 10s ago
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a"],
          autoFix: { whatsappDisconnectThreshold: 2, whatsappMinRestartIntervalSec: 300 },
        },
      });
      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: JSON.stringify({ channels: { whatsapp: { status: "disconnected" } } }),
        stderr: "",
      });
      register(api);

      await runOneTick(api);

      // Should NOT have restarted - interval not elapsed
      const restartCalls = filterCmdCalls(api, "gateway restart");
      expect(restartCalls).toHaveLength(0);

      // Streak should still be incremented
      const state = loadState(stateFile);
      expect(state.whatsapp!.disconnectStreak).toBe(6);
    });

    it("does not restart if openclaw.json config is invalid", async () => {
      // Make the config file invalid
      fs.writeFileSync(configFile, "NOT VALID JSON{{{");
      saveState(stateFile, {
        ...emptyState(),
        whatsapp: { disconnectStreak: 5, lastRestartAt: 0 },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a"],
          autoFix: { whatsappDisconnectThreshold: 2, whatsappMinRestartIntervalSec: 60 },
        },
      });
      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: JSON.stringify({ channels: { whatsapp: { status: "disconnected" } } }),
        stderr: "",
      });
      register(api);

      await runOneTick(api);

      // Should NOT have restarted
      const restartCalls = filterCmdCalls(api, "gateway restart");
      expect(restartCalls).toHaveLength(0);

      // Should log error about invalid config
      expect(api.logger.error).toHaveBeenCalledWith(
        expect.stringContaining("NOT restarting gateway: openclaw.json invalid")
      );
    });

    it("backs up config before gateway restart and cleans up after", async () => {
      saveState(stateFile, {
        ...emptyState(),
        whatsapp: { disconnectStreak: 1, lastRestartAt: 0 },
      });

      const commandLog: string[] = [];
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a"],
          autoFix: { whatsappDisconnectThreshold: 2, whatsappMinRestartIntervalSec: 60 },
        },
      });
      api.runtime.system.runCommandWithTimeout.mockImplementation(async (opts: any) => {
        const cmd = opts?.command?.join(" ") ?? "";
        commandLog.push(cmd);
        if (cmd.includes("channels status")) {
          return {
            exitCode: 0,
            stdout: JSON.stringify({ channels: { whatsapp: { status: "disconnected" } } }),
            stderr: "",
          };
        }
        if (cmd.includes("gateway restart")) {
          return { exitCode: 0, stdout: "restarted", stderr: "" };
        }
        if (cmd.includes("gateway status")) {
          return { exitCode: 0, stdout: "ok", stderr: "" };
        }
        return { exitCode: 1, stdout: "", stderr: "" };
      });
      register(api);

      await runOneTick(api);

      // Verify backup was created
      expect(api.logger.info).toHaveBeenCalledWith(
        expect.stringContaining("backed up openclaw.json (pre-gateway-restart)")
      );

      // Verify restart happened after backup
      const restartIdx = commandLog.findIndex((c) => c.includes("gateway restart"));
      expect(restartIdx).toBeGreaterThan(-1);
    });
  });

  // -------------------------------------------------------------------------
  // Cron failure accumulation -> disable + issue create path
  // -------------------------------------------------------------------------

  describe("cron failure accumulation -> disable + issue create path", () => {
    it("accumulates cron failure counts across ticks", async () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a"],
          autoFix: { disableFailingCrons: true, cronFailThreshold: 5 },
        },
      });
      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: JSON.stringify({
          jobs: [{ id: "cron-1", name: "daily-report", state: { lastStatus: "error", lastError: "timeout" } }],
        }),
        stderr: "",
      });
      register(api);

      // Run two ticks
      await runOneTick(api);
      let state = loadState(stateFile);
      expect(state.cron!.failCounts!["cron-1"]).toBe(1);

      // Second tick: re-register to get fresh service registration
      const api2 = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a"],
          autoFix: { disableFailingCrons: true, cronFailThreshold: 5 },
        },
      });
      api2.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: JSON.stringify({
          jobs: [{ id: "cron-1", name: "daily-report", state: { lastStatus: "error", lastError: "timeout" } }],
        }),
        stderr: "",
      });
      register(api2);

      await runOneTick(api2);
      state = loadState(stateFile);
      expect(state.cron!.failCounts!["cron-1"]).toBe(2);
    });

    it("resets fail count when cron job succeeds", async () => {
      saveState(stateFile, {
        ...emptyState(),
        cron: { failCounts: { "cron-1": 2 }, lastIssueCreatedAt: {} },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a"],
          autoFix: { disableFailingCrons: true, cronFailThreshold: 3 },
        },
      });
      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: JSON.stringify({
          jobs: [{ id: "cron-1", name: "daily-report", state: { lastStatus: "ok" } }],
        }),
        stderr: "",
      });
      register(api);

      await runOneTick(api);

      const state = loadState(stateFile);
      expect(state.cron!.failCounts!["cron-1"]).toBe(0);
    });

    it("disables cron and creates issue when failure threshold is reached", async () => {
      saveState(stateFile, {
        ...emptyState(),
        cron: { failCounts: { "cron-1": 2 }, lastIssueCreatedAt: {} },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a"],
          autoFix: {
            disableFailingCrons: true,
            cronFailThreshold: 3,
            issueCooldownSec: 0,
            issueRepo: "elvatis/test-repo",
          },
        },
      });
      api.runtime.system.runCommandWithTimeout.mockImplementation(async (opts: any) => {
        const cmd = opts?.command?.join(" ") ?? "";
        if (cmd.includes("cron list")) {
          return {
            exitCode: 0,
            stdout: JSON.stringify({
              jobs: [{
                id: "cron-1",
                name: "daily-report",
                state: { lastStatus: "error", lastError: "Connection refused" },
              }],
            }),
            stderr: "",
          };
        }
        if (cmd.includes("gateway status")) {
          return { exitCode: 0, stdout: "ok", stderr: "" };
        }
        return { exitCode: 0, stdout: "", stderr: "" };
      });
      register(api);

      await runOneTick(api);

      // Verify cron was disabled
      const disableCalls = filterCmdCalls(api, "cron edit cron-1 --disable");
      expect(disableCalls).toHaveLength(1);

      // Verify issue was created
      const issueCalls = filterCmdCalls(api, "gh issue create");
      expect(issueCalls).toHaveLength(1);

      // Verify event emitted
      const events = findEmitted(api, "self-heal:cron-disabled");
      expect(events).toHaveLength(1);
      expect(events[0].payload.cronId).toBe("cron-1");
      expect(events[0].payload.cronName).toBe("daily-report");
      expect(events[0].payload.consecutiveFailures).toBe(3);

      // Verify fail count reset after disable
      const state = loadState(stateFile);
      expect(state.cron!.failCounts!["cron-1"]).toBe(0);
    });

    it("rate-limits issue creation via issueCooldownSec", async () => {
      saveState(stateFile, {
        ...emptyState(),
        cron: {
          failCounts: { "cron-1": 2 },
          lastIssueCreatedAt: { "cron-1": nowSec() - 100 }, // created 100s ago
        },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a"],
          autoFix: {
            disableFailingCrons: true,
            cronFailThreshold: 3,
            issueCooldownSec: 3600, // 1 hour cooldown
            issueRepo: "elvatis/test-repo",
          },
        },
      });
      api.runtime.system.runCommandWithTimeout.mockImplementation(async (opts: any) => {
        const cmd = opts?.command?.join(" ") ?? "";
        if (cmd.includes("cron list")) {
          return {
            exitCode: 0,
            stdout: JSON.stringify({
              jobs: [{
                id: "cron-1",
                name: "daily-report",
                state: { lastStatus: "error", lastError: "timeout" },
              }],
            }),
            stderr: "",
          };
        }
        if (cmd.includes("gateway status")) {
          return { exitCode: 0, stdout: "ok", stderr: "" };
        }
        return { exitCode: 0, stdout: "", stderr: "" };
      });
      register(api);

      await runOneTick(api);

      // Cron should still be disabled
      const disableCalls = filterCmdCalls(api, "cron edit cron-1 --disable");
      expect(disableCalls).toHaveLength(1);

      // But issue should NOT be created (cooldown not elapsed)
      const issueCalls = filterCmdCalls(api, "gh issue create");
      expect(issueCalls).toHaveLength(0);
    });

    it("does not disable cron if config file is invalid", async () => {
      fs.writeFileSync(configFile, "INVALID JSON!!!");
      saveState(stateFile, {
        ...emptyState(),
        cron: { failCounts: { "cron-1": 2 }, lastIssueCreatedAt: {} },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a"],
          autoFix: { disableFailingCrons: true, cronFailThreshold: 3 },
        },
      });
      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: JSON.stringify({
          jobs: [{
            id: "cron-1",
            name: "daily-report",
            state: { lastStatus: "error", lastError: "fail" },
          }],
        }),
        stderr: "",
      });
      register(api);

      await runOneTick(api);

      // Should NOT have disabled cron
      const disableCalls = filterCmdCalls(api, "cron edit");
      expect(disableCalls).toHaveLength(0);

      // Should log error
      expect(api.logger.error).toHaveBeenCalledWith(
        expect.stringContaining("NOT disabling cron: openclaw.json invalid")
      );
    });

    it("tracks multiple cron jobs independently", async () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a"],
          autoFix: { disableFailingCrons: true, cronFailThreshold: 3 },
        },
      });
      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: JSON.stringify({
          jobs: [
            { id: "cron-1", name: "report", state: { lastStatus: "error", lastError: "fail" } },
            { id: "cron-2", name: "backup", state: { lastStatus: "ok" } },
            { id: "cron-3", name: "cleanup", state: { lastStatus: "error", lastError: "disk full" } },
          ],
        }),
        stderr: "",
      });
      register(api);

      await runOneTick(api);

      const state = loadState(stateFile);
      expect(state.cron!.failCounts!["cron-1"]).toBe(1);
      expect(state.cron!.failCounts!["cron-2"]).toBe(0);
      expect(state.cron!.failCounts!["cron-3"]).toBe(1);
    });
  });

  // -------------------------------------------------------------------------
  // Active model recovery probe -> cooldown removal path
  // -------------------------------------------------------------------------

  describe("active model recovery probe -> cooldown removal path", () => {
    it("removes model from cooldown when probe succeeds during tick", async () => {
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
          configBackupsDir: backupsDir,
          modelOrder: ["model-a", "model-b"],
          probeEnabled: true,
          probeIntervalSec: 300,
        },
      });
      api.runtime.system.runCommandWithTimeout.mockImplementation(async (opts: any) => {
        const cmd = opts?.command?.join(" ") ?? "";
        if (cmd.includes("model probe")) {
          return { exitCode: 0, stdout: "ok", stderr: "" };
        }
        return { exitCode: 1, stdout: "", stderr: "" };
      });
      register(api);

      await runOneTick(api);

      const state = loadState(stateFile);
      expect(state.limited["model-a"]).toBeUndefined();

      const events = findEmitted(api, "self-heal:model-recovered");
      expect(events).toHaveLength(1);
      expect(events[0].payload.model).toBe("model-a");
      expect(events[0].payload.isPreferred).toBe(true);
    });

    it("updates lastProbeAt but keeps cooldown when probe fails", async () => {
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
          configBackupsDir: backupsDir,
          modelOrder: ["model-a", "model-b"],
          probeEnabled: true,
          probeIntervalSec: 300,
        },
      });
      api.runtime.system.runCommandWithTimeout.mockImplementation(async (opts: any) => {
        const cmd = opts?.command?.join(" ") ?? "";
        if (cmd.includes("model probe")) {
          return { exitCode: 1, stdout: "", stderr: "still limited" };
        }
        return { exitCode: 1, stdout: "", stderr: "" };
      });
      register(api);

      await runOneTick(api);

      const state = loadState(stateFile);
      expect(state.limited["model-a"]).toBeDefined();
      expect(state.limited["model-a"].lastProbeAt).toBeGreaterThan(0);

      const events = findEmitted(api, "self-heal:model-recovered");
      expect(events).toHaveLength(0);
    });

    it("sets isPreferred=false for non-primary model recovery", async () => {
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
          configBackupsDir: backupsDir,
          modelOrder: ["model-a", "model-b"],
          probeEnabled: true,
          probeIntervalSec: 300,
        },
      });
      api.runtime.system.runCommandWithTimeout.mockImplementation(async (opts: any) => {
        const cmd = opts?.command?.join(" ") ?? "";
        if (cmd.includes("model probe")) {
          return { exitCode: 0, stdout: "ok", stderr: "" };
        }
        return { exitCode: 1, stdout: "", stderr: "" };
      });
      register(api);

      await runOneTick(api);

      const events = findEmitted(api, "self-heal:model-recovered");
      expect(events).toHaveLength(1);
      expect(events[0].payload.isPreferred).toBe(false);
    });
  });

  // -------------------------------------------------------------------------
  // Config hot-reload during tick
  // -------------------------------------------------------------------------

  describe("config hot-reload during tick", () => {
    it("applies new whatsappDisconnectThreshold from reloaded config", async () => {
      saveState(stateFile, {
        ...emptyState(),
        whatsapp: { disconnectStreak: 2, lastRestartAt: 0 },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a"],
          autoFix: { whatsappDisconnectThreshold: 2, whatsappMinRestartIntervalSec: 60 },
        },
      });
      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: JSON.stringify({ channels: { whatsapp: { status: "disconnected" } } }),
        stderr: "",
      });
      register(api);

      // Raise threshold before tick so restart should NOT happen
      api.pluginConfig = {
        stateFile,
        sessionsFile,
        configFile,
        configBackupsDir: backupsDir,
        modelOrder: ["model-a"],
        autoFix: { whatsappDisconnectThreshold: 10, whatsappMinRestartIntervalSec: 60 },
      };

      await runOneTick(api);

      // Should NOT restart since threshold increased to 10
      const restartCalls = filterCmdCalls(api, "gateway restart");
      expect(restartCalls).toHaveLength(0);
    });

    it("applies new cronFailThreshold from reloaded config", async () => {
      saveState(stateFile, {
        ...emptyState(),
        cron: { failCounts: { "cron-1": 2 }, lastIssueCreatedAt: {} },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a"],
          autoFix: { disableFailingCrons: true, cronFailThreshold: 3 },
        },
      });
      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: JSON.stringify({
          jobs: [{ id: "cron-1", name: "report", state: { lastStatus: "error", lastError: "fail" } }],
        }),
        stderr: "",
      });
      register(api);

      // Raise threshold so cron should NOT be disabled
      api.pluginConfig = {
        stateFile,
        sessionsFile,
        configFile,
        configBackupsDir: backupsDir,
        modelOrder: ["model-a"],
        autoFix: { disableFailingCrons: true, cronFailThreshold: 10 },
      };

      await runOneTick(api);

      const disableCalls = filterCmdCalls(api, "cron edit");
      expect(disableCalls).toHaveLength(0);

      // Fail count should still increment
      const state = loadState(stateFile);
      expect(state.cron!.failCounts!["cron-1"]).toBe(3);
    });

    it("applies new dryRun flag from reloaded config mid-session", async () => {
      saveState(stateFile, {
        ...emptyState(),
        whatsapp: { disconnectStreak: 5, lastRestartAt: 0 },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a"],
          autoFix: { whatsappDisconnectThreshold: 2, whatsappMinRestartIntervalSec: 60 },
        },
      });
      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: JSON.stringify({ channels: { whatsapp: { status: "disconnected" } } }),
        stderr: "",
      });
      register(api);

      // Switch to dry-run before tick
      api.pluginConfig = {
        stateFile,
        sessionsFile,
        configFile,
        configBackupsDir: backupsDir,
        modelOrder: ["model-a"],
        dryRun: true,
        autoFix: { whatsappDisconnectThreshold: 2, whatsappMinRestartIntervalSec: 60 },
      };

      await runOneTick(api);

      // Should NOT call actual restart (dry-run)
      const restartCalls = filterCmdCalls(api, "gateway restart");
      expect(restartCalls).toHaveLength(0);

      // Should log dry-run message
      expect(api.logger.info).toHaveBeenCalledWith(
        expect.stringContaining("[dry-run] would restart gateway")
      );
    });
  });

  // -------------------------------------------------------------------------
  // Dry-run flag suppresses all side-effects
  // -------------------------------------------------------------------------

  describe("dry-run flag suppresses all side-effects", () => {
    it("does not restart gateway in dry-run mode", async () => {
      saveState(stateFile, {
        ...emptyState(),
        whatsapp: { disconnectStreak: 5, lastRestartAt: 0 },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a"],
          dryRun: true,
          autoFix: { whatsappDisconnectThreshold: 2, whatsappMinRestartIntervalSec: 60 },
        },
      });
      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: JSON.stringify({ channels: { whatsapp: { status: "disconnected" } } }),
        stderr: "",
      });
      register(api);

      await runOneTick(api);

      const restartCalls = filterCmdCalls(api, "gateway restart");
      expect(restartCalls).toHaveLength(0);

      // But state should still be updated
      const state = loadState(stateFile);
      expect(state.whatsapp!.disconnectStreak).toBe(0);
      expect(state.whatsapp!.lastRestartAt).toBeGreaterThan(0);

      // dry-run event should still be emitted
      const events = findEmitted(api, "self-heal:whatsapp-restart");
      expect(events).toHaveLength(1);
      expect(events[0].payload.dryRun).toBe(true);
    });

    it("does not disable cron in dry-run mode", async () => {
      saveState(stateFile, {
        ...emptyState(),
        cron: { failCounts: { "cron-1": 2 }, lastIssueCreatedAt: {} },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a"],
          dryRun: true,
          autoFix: {
            disableFailingCrons: true,
            cronFailThreshold: 3,
            issueCooldownSec: 0,
          },
        },
      });
      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: JSON.stringify({
          jobs: [{
            id: "cron-1",
            name: "daily-report",
            state: { lastStatus: "error", lastError: "timeout" },
          }],
        }),
        stderr: "",
      });
      register(api);

      await runOneTick(api);

      // Should NOT call cron edit or gh issue create
      const disableCalls = filterCmdCalls(api, "cron edit");
      expect(disableCalls).toHaveLength(0);
      const issueCalls = filterCmdCalls(api, "gh issue create");
      expect(issueCalls).toHaveLength(0);

      // Should log dry-run messages
      expect(api.logger.info).toHaveBeenCalledWith(
        expect.stringContaining("[dry-run] would disable cron")
      );
      expect(api.logger.info).toHaveBeenCalledWith(
        expect.stringContaining("[dry-run] would create GitHub issue")
      );

      // Should emit event with dryRun=true
      const events = findEmitted(api, "self-heal:cron-disabled");
      expect(events).toHaveLength(1);
      expect(events[0].payload.dryRun).toBe(true);
    });

    it("does not probe models in dry-run mode", async () => {
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
          configBackupsDir: backupsDir,
          modelOrder: ["model-a", "model-b"],
          dryRun: true,
          probeEnabled: true,
          probeIntervalSec: 300,
        },
      });
      register(api);

      await runOneTick(api);

      const probeCalls = filterCmdCalls(api, "model probe");
      expect(probeCalls).toHaveLength(0);

      expect(api.logger.info).toHaveBeenCalledWith(
        expect.stringContaining("[dry-run] would probe model model-a")
      );

      // Model should still be in cooldown
      const state = loadState(stateFile);
      expect(state.limited["model-a"]).toBeDefined();
    });
  });

  // -------------------------------------------------------------------------
  // Status snapshot emission on every tick
  // -------------------------------------------------------------------------

  describe("status snapshot on every tick", () => {
    it("emits self-heal:status event with correct health status", async () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a", "model-b"],
        },
      });
      register(api);

      await runOneTick(api);

      const events = findEmitted(api, "self-heal:status");
      expect(events.length).toBeGreaterThanOrEqual(1);
      const snapshot = events[0].payload;
      expect(snapshot.health).toBe("healthy");
      expect(snapshot.activeModel).toBe("model-a");
      expect(snapshot.models).toHaveLength(2);
      expect(snapshot.generatedAt).toBeGreaterThan(0);
    });

    it("emits degraded health when a model is in cooldown", async () => {
      saveState(stateFile, {
        ...emptyState(),
        limited: {
          "model-a": { lastHitAt: nowSec() - 10, nextAvailableAt: nowSec() + 9999 },
        },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a", "model-b"],
          probeEnabled: false,
        },
      });
      register(api);

      await runOneTick(api);

      const events = findEmitted(api, "self-heal:status");
      expect(events.length).toBeGreaterThanOrEqual(1);
      expect(events[0].payload.health).toBe("degraded");
      expect(events[0].payload.activeModel).toBe("model-b");
    });

    it("emits healing health when all models are in cooldown", async () => {
      saveState(stateFile, {
        ...emptyState(),
        limited: {
          "model-a": { lastHitAt: nowSec() - 10, nextAvailableAt: nowSec() + 9999 },
          "model-b": { lastHitAt: nowSec() - 10, nextAvailableAt: nowSec() + 9999 },
        },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a", "model-b"],
          probeEnabled: false,
        },
      });
      register(api);

      await runOneTick(api);

      const events = findEmitted(api, "self-heal:status");
      expect(events.length).toBeGreaterThanOrEqual(1);
      expect(events[0].payload.health).toBe("healing");
    });

    it("includes WhatsApp and cron status in snapshot", async () => {
      saveState(stateFile, {
        ...emptyState(),
        whatsapp: { disconnectStreak: 3, lastSeenConnectedAt: nowSec() - 60 },
        cron: { failCounts: { "c1": 2, "c2": 0 }, lastIssueCreatedAt: {} },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a"],
          probeEnabled: false,
        },
      });
      register(api);

      await runOneTick(api);

      const events = findEmitted(api, "self-heal:status");
      const snapshot = events[0].payload;
      expect(snapshot.whatsapp.status).toBe("disconnected");
      expect(snapshot.whatsapp.disconnectStreak).toBe(3);
      expect(snapshot.cron.trackedJobs).toBe(2);
      expect(snapshot.cron.failingJobs).toHaveLength(1);
      expect(snapshot.cron.failingJobs[0].id).toBe("c1");
    });
  });

  // -------------------------------------------------------------------------
  // Combined multi-domain tick
  // -------------------------------------------------------------------------

  describe("combined multi-domain tick", () => {
    it("handles WhatsApp, cron, and probe healing in a single tick", async () => {
      const hitAt = nowSec() - 400;
      saveState(stateFile, {
        ...emptyState(),
        whatsapp: { disconnectStreak: 0 },
        cron: { failCounts: { "cron-1": 2 }, lastIssueCreatedAt: {} },
        limited: {
          "model-b": { lastHitAt: hitAt, nextAvailableAt: nowSec() + 9999 },
        },
      });

      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a", "model-b"],
          probeEnabled: true,
          probeIntervalSec: 300,
          autoFix: {
            disableFailingCrons: true,
            cronFailThreshold: 3,
            issueCooldownSec: 0,
            issueRepo: "elvatis/test-repo",
            whatsappDisconnectThreshold: 5,
          },
        },
      });
      api.runtime.system.runCommandWithTimeout.mockImplementation(async (opts: any) => {
        const cmd = opts?.command?.join(" ") ?? "";
        if (cmd.includes("channels status")) {
          return {
            exitCode: 0,
            stdout: JSON.stringify({ channels: { whatsapp: { status: "connected" } } }),
            stderr: "",
          };
        }
        if (cmd.includes("cron list")) {
          return {
            exitCode: 0,
            stdout: JSON.stringify({
              jobs: [{
                id: "cron-1",
                name: "report",
                state: { lastStatus: "error", lastError: "timeout" },
              }],
            }),
            stderr: "",
          };
        }
        if (cmd.includes("model probe")) {
          return { exitCode: 0, stdout: "ok", stderr: "" };
        }
        if (cmd.includes("gateway status")) {
          return { exitCode: 0, stdout: "ok", stderr: "" };
        }
        return { exitCode: 0, stdout: "", stderr: "" };
      });
      register(api);

      await runOneTick(api);

      const state = loadState(stateFile);

      // WhatsApp: connected, streak reset
      expect(state.whatsapp!.disconnectStreak).toBe(0);
      expect(state.whatsapp!.lastSeenConnectedAt).toBeGreaterThan(0);

      // Cron: threshold reached, disabled
      const disableCalls = filterCmdCalls(api, "cron edit cron-1 --disable");
      expect(disableCalls).toHaveLength(1);
      const cronEvents = findEmitted(api, "self-heal:cron-disabled");
      expect(cronEvents).toHaveLength(1);

      // Probe: model-b recovered
      expect(state.limited["model-b"]).toBeUndefined();
      const recoveryEvents = findEmitted(api, "self-heal:model-recovered");
      expect(recoveryEvents).toHaveLength(1);
      expect(recoveryEvents[0].payload.model).toBe("model-b");

      // Status snapshot emitted
      const statusEvents = findEmitted(api, "self-heal:status");
      expect(statusEvents.length).toBeGreaterThanOrEqual(1);
    });

    it("handles all domains being inactive gracefully", async () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a"],
          autoFix: {
            restartWhatsappOnDisconnect: false,
            disableFailingCrons: false,
            disableFailingPlugins: false,
          },
          probeEnabled: false,
        },
      });
      register(api);

      await runOneTick(api);

      // Only status event should be emitted
      const statusEvents = findEmitted(api, "self-heal:status");
      expect(statusEvents.length).toBeGreaterThanOrEqual(1);
      expect(statusEvents[0].payload.health).toBe("healthy");

      // No healing commands should have been run (no WA check, no cron check, no probes)
      // Note: startup cleanup calls "openclaw gateway status" once, so we check
      // that no healing-specific commands were issued
      const healingCalls = api.runtime.system.runCommandWithTimeout.mock.calls.filter(
        (c: any[]) => {
          const cmd = c[0]?.command?.join(" ") ?? "";
          return cmd.includes("channels status") || cmd.includes("cron list") || cmd.includes("model probe");
        }
      );
      expect(healingCalls).toHaveLength(0);
    });
  });

  // -------------------------------------------------------------------------
  // Edge cases and error handling
  // -------------------------------------------------------------------------

  describe("edge cases and error handling", () => {
    it("handles command timeout gracefully during tick", async () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a"],
        },
      });
      api.runtime.system.runCommandWithTimeout.mockRejectedValue(
        new Error("command timed out")
      );
      register(api);

      // Should not throw
      await runOneTick(api);

      // Status should still be emitted
      const statusEvents = findEmitted(api, "self-heal:status");
      expect(statusEvents.length).toBeGreaterThanOrEqual(1);
    });

    it("handles malformed JSON from channels status command", async () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a"],
        },
      });
      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: "NOT JSON {{{",
        stderr: "",
      });
      register(api);

      // Should not throw
      await runOneTick(api);

      // WhatsApp: malformed JSON means safeJsonParse returns undefined,
      // so the wa object is undefined, connected=false, and streak increments by 1
      const state = loadState(stateFile);
      expect(state.whatsapp!.disconnectStreak).toBe(1);
    });

    it("handles malformed JSON from cron list command", async () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a"],
          autoFix: { disableFailingCrons: true },
        },
      });
      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: "this is not json",
        stderr: "",
      });
      register(api);

      // Should not throw
      await runOneTick(api);

      const statusEvents = findEmitted(api, "self-heal:status");
      expect(statusEvents.length).toBeGreaterThanOrEqual(1);
    });

    it("persists state at end of tick even when no healing actions taken", async () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a"],
          probeEnabled: false,
          autoFix: { restartWhatsappOnDisconnect: false, disableFailingCrons: false },
        },
      });
      register(api);

      await runOneTick(api);

      // State file should exist and be valid
      expect(fs.existsSync(stateFile)).toBe(true);
      const state = loadState(stateFile);
      expect(state.limited).toBeDefined();
    });

    it("uses whatsapp connected=true as alternative connected indicator", async () => {
      const api = mockApi({
        pluginConfig: {
          stateFile,
          sessionsFile,
          configFile,
          configBackupsDir: backupsDir,
          modelOrder: ["model-a"],
        },
      });
      api.runtime.system.runCommandWithTimeout.mockResolvedValue({
        exitCode: 0,
        stdout: JSON.stringify({ channels: { whatsapp: { connected: true } } }),
        stderr: "",
      });
      register(api);

      await runOneTick(api);

      const state = loadState(stateFile);
      expect(state.whatsapp!.disconnectStreak).toBe(0);
      expect(state.whatsapp!.lastSeenConnectedAt).toBeGreaterThan(0);
    });
  });
});
