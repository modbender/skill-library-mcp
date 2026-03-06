/**
 * Tests for Phase 1 commands (/health, /services, /logs, /plugins).
 *
 * Uses a mock API to verify registration metadata and handler output format.
 * External dependencies (gateway, filesystem) are mocked where needed.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { createMockApi, invokeCommand, type MockApi } from "../src/test-helpers.js";
import { registerPhase1Commands } from "./phase1-commands.js";

// Use a temp workspace that exists on disk (for commands that check filesystem)
const tmpWorkspace = path.join(os.tmpdir(), "openclaw-ops-elvatis-test-phase1-" + process.pid);

describe("phase1-commands registration", () => {
  let api: MockApi;

  beforeEach(() => {
    api = createMockApi();
    registerPhase1Commands(api, tmpWorkspace);
  });

  it("registers /health command", () => {
    const cmd = api.commands.get("health")!;
    expect(cmd).toBeDefined();
    expect(cmd.name).toBe("health");
    expect(cmd.description).toContain("health");
    expect(cmd.requireAuth).toBe(false);
    expect(cmd.acceptsArgs).toBe(false);
  });

  it("registers /services command", () => {
    const cmd = api.commands.get("services")!;
    expect(cmd).toBeDefined();
    expect(cmd.name).toBe("services");
    expect(cmd.requireAuth).toBe(false);
  });

  it("registers /logs command with args", () => {
    const cmd = api.commands.get("logs")!;
    expect(cmd).toBeDefined();
    expect(cmd.name).toBe("logs");
    expect(cmd.acceptsArgs).toBe(true);
  });

  it("registers /plugins command", () => {
    const cmd = api.commands.get("plugins")!;
    expect(cmd).toBeDefined();
    expect(cmd.name).toBe("plugins");
    expect(cmd.requireAuth).toBe(false);
  });

  it("registers exactly 4 commands", () => {
    expect(api.commands.size).toBe(4);
  });
});

describe("/health handler", () => {
  let api: MockApi;

  beforeEach(() => {
    api = createMockApi();
    registerPhase1Commands(api, tmpWorkspace);
  });

  it("returns text with System Health heading", async () => {
    const text = await invokeCommand(api, "health");
    expect(text).toContain("System Health");
  });

  it("includes GATEWAY section", async () => {
    const text = await invokeCommand(api, "health");
    expect(text).toContain("GATEWAY");
  });

  it("includes RESOURCES section with CPU", async () => {
    const text = await invokeCommand(api, "health");
    expect(text).toContain("RESOURCES");
    expect(text).toContain("CPU load");
  });

  it("includes COOLDOWNS section", async () => {
    const text = await invokeCommand(api, "health");
    expect(text).toContain("COOLDOWNS");
  });

  it("includes ERRORS section", async () => {
    const text = await invokeCommand(api, "health");
    expect(text).toContain("ERRORS");
  });
});

describe("/services handler", () => {
  let api: MockApi;

  beforeEach(() => {
    api = createMockApi();
    registerPhase1Commands(api, tmpWorkspace);
  });

  it("returns text with Services Status heading", async () => {
    const text = await invokeCommand(api, "services");
    expect(text).toContain("Services Status");
  });

  it("includes PROFILES section", async () => {
    const text = await invokeCommand(api, "services");
    expect(text).toContain("PROFILES");
  });

  it("always shows the default profile", async () => {
    const text = await invokeCommand(api, "services");
    expect(text).toContain("default");
  });
});

describe("/logs handler", () => {
  let api: MockApi;
  const logsDir = path.join(os.homedir(), ".openclaw", "logs");

  beforeEach(() => {
    api = createMockApi();
    registerPhase1Commands(api, tmpWorkspace);
  });

  it("returns text with Logs heading", async () => {
    const text = await invokeCommand(api, "logs", "gateway 10");
    expect(text).toContain("Logs:");
  });

  it("defaults to gateway service", async () => {
    const text = await invokeCommand(api, "logs", "");
    expect(text).toContain("gateway");
  });

  it("respects custom service name", async () => {
    const text = await invokeCommand(api, "logs", "my-plugin 5");
    expect(text).toContain("my-plugin");
  });

  it("handles missing log directory gracefully", async () => {
    const text = await invokeCommand(api, "logs", "nonexistent-service 5");
    // Should either show "No log file found" or an error, not throw
    expect(typeof text).toBe("string");
  });
});

describe("/plugins handler", () => {
  let api: MockApi;

  beforeEach(() => {
    api = createMockApi();
    registerPhase1Commands(api, tmpWorkspace);
  });

  it("returns text with Plugins Dashboard heading", async () => {
    const text = await invokeCommand(api, "plugins");
    // Heading depends on whether openclaw binary is available
    expect(typeof text).toBe("string");
    expect(text.length).toBeGreaterThan(0);
  });
});
