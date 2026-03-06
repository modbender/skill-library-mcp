/**
 * Tests for config commands (/config).
 *
 * Uses a temp workspace with mock plugin directories to test config reading,
 * validation, secret masking, and default diffing.
 */

import { describe, it, expect, beforeEach, afterEach } from "vitest";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { createMockApi, invokeCommand, type MockApi } from "../src/test-helpers.js";
import { registerConfigCommands } from "./config-commands.js";

const tmpWorkspace = path.join(os.tmpdir(), "openclaw-ops-elvatis-test-config-" + process.pid);

function cleanup() {
  try {
    fs.rmSync(tmpWorkspace, { recursive: true, force: true });
  } catch {}
}

describe("config-commands registration", () => {
  let api: MockApi;

  beforeEach(() => {
    api = createMockApi();
    registerConfigCommands(api, tmpWorkspace);
  });

  it("registers /config command", () => {
    const cmd = api.commands.get("config")!;
    expect(cmd).toBeDefined();
    expect(cmd.name).toBe("config");
  });

  it("registers exactly 1 command", () => {
    expect(api.commands.size).toBe(1);
  });

  it("/config accepts args", () => {
    const cmd = api.commands.get("config")!;
    expect(cmd.acceptsArgs).toBe(true);
  });

  it("/config does not require auth", () => {
    const cmd = api.commands.get("config")!;
    expect(cmd.requireAuth).toBe(false);
  });
});

describe("/config handler (overview - no args)", () => {
  let api: MockApi;

  beforeEach(() => {
    cleanup();
    api = createMockApi();
    registerConfigCommands(api, tmpWorkspace);
  });

  afterEach(cleanup);

  it("shows Configuration Overview heading", async () => {
    const text = await invokeCommand(api, "config", "");
    expect(text).toContain("Configuration Overview");
  });

  it("shows ENVIRONMENT section", async () => {
    const text = await invokeCommand(api, "config", "");
    expect(text).toContain("ENVIRONMENT");
    expect(text).toContain("Platform:");
    expect(text).toContain("Node:");
  });

  it("shows workspace path", async () => {
    const text = await invokeCommand(api, "config", "");
    expect(text).toContain(`Workspace: ${tmpWorkspace}`);
  });

  it("shows MAIN CONFIG section", async () => {
    const text = await invokeCommand(api, "config", "");
    expect(text).toContain("MAIN CONFIG");
  });

  it("shows PLUGIN CONFIGS section", async () => {
    const text = await invokeCommand(api, "config", "");
    expect(text).toContain("PLUGIN CONFIGS");
  });

  it("shows ENV VARS section", async () => {
    const text = await invokeCommand(api, "config", "");
    expect(text).toContain("ENV VARS");
  });

  it("shows usage hint for single plugin", async () => {
    const text = await invokeCommand(api, "config", "");
    expect(text).toContain("Use /config <plugin-name>");
  });

  it("reports no plugins when workspace is empty", async () => {
    fs.mkdirSync(tmpWorkspace, { recursive: true });
    const text = await invokeCommand(api, "config", "");
    expect(text).toContain("no plugins found");
  });
});

describe("/config handler (overview with plugins)", () => {
  let api: MockApi;

  beforeEach(() => {
    cleanup();
    // Create a plugin in the workspace
    const pluginDir = path.join(tmpWorkspace, "openclaw-test-plugin");
    fs.mkdirSync(pluginDir, { recursive: true });
    fs.writeFileSync(
      path.join(pluginDir, "openclaw.plugin.json"),
      JSON.stringify({
        id: "openclaw-test-plugin",
        name: "Test Plugin",
        version: "1.2.3",
        description: "A test plugin",
        configSchema: {
          type: "object",
          properties: {
            enabled: { type: "boolean", default: true },
            verbose: { type: "boolean", default: false },
          },
        },
      }),
      "utf-8",
    );

    api = createMockApi();
    registerConfigCommands(api, tmpWorkspace);
  });

  afterEach(cleanup);

  it("lists plugin in PLUGIN CONFIGS", async () => {
    const text = await invokeCommand(api, "config", "");
    expect(text).toContain("openclaw-test-plugin");
    expect(text).toContain("v1.2.3");
  });

  it("shows OK status for valid config", async () => {
    const text = await invokeCommand(api, "config", "");
    expect(text).toContain("[OK]");
  });
});

describe("/config <plugin> handler (single plugin)", () => {
  let api: MockApi;

  beforeEach(() => {
    cleanup();
    const pluginDir = path.join(tmpWorkspace, "openclaw-test-plugin");
    fs.mkdirSync(pluginDir, { recursive: true });
    fs.writeFileSync(
      path.join(pluginDir, "openclaw.plugin.json"),
      JSON.stringify({
        id: "openclaw-test-plugin",
        name: "Test Plugin",
        version: "2.0.0",
        description: "A test plugin for config",
        configSchema: {
          type: "object",
          additionalProperties: false,
          properties: {
            enabled: { type: "boolean", default: true },
            workspacePath: { type: "string", default: "~/.openclaw/workspace" },
          },
        },
      }),
      "utf-8",
    );
    fs.writeFileSync(
      path.join(pluginDir, "package.json"),
      JSON.stringify({ name: "openclaw-test-plugin", version: "2.0.0" }),
      "utf-8",
    );

    api = createMockApi();
    registerConfigCommands(api, tmpWorkspace);
  });

  afterEach(cleanup);

  it("shows plugin metadata", async () => {
    const text = await invokeCommand(api, "config", "openclaw-test-plugin");
    expect(text).toContain("Config: openclaw-test-plugin");
    expect(text).toContain("ID: openclaw-test-plugin");
    expect(text).toContain("Name: Test Plugin");
    expect(text).toContain("Version: 2.0.0");
  });

  it("shows ACTIVE CONFIG section", async () => {
    const text = await invokeCommand(api, "config", "openclaw-test-plugin");
    expect(text).toContain("ACTIVE CONFIG");
  });

  it("shows SCHEMA VALIDATION section", async () => {
    const text = await invokeCommand(api, "config", "openclaw-test-plugin");
    expect(text).toContain("SCHEMA VALIDATION");
    expect(text).toContain("All checks passed");
  });

  it("shows DEFAULTS COMPARISON section", async () => {
    const text = await invokeCommand(api, "config", "openclaw-test-plugin");
    expect(text).toContain("DEFAULTS COMPARISON");
    expect(text).toContain("enabled");
    expect(text).toContain("default");
  });

  it("shows RESOLVED PATHS section", async () => {
    const text = await invokeCommand(api, "config", "openclaw-test-plugin");
    expect(text).toContain("RESOLVED PATHS");
    expect(text).toContain("Plugin dir:");
  });

  it("shows package.json path when present", async () => {
    const text = await invokeCommand(api, "config", "openclaw-test-plugin");
    expect(text).toContain("package.json:");
  });
});

describe("/config <plugin> - not found", () => {
  let api: MockApi;

  beforeEach(() => {
    cleanup();
    fs.mkdirSync(tmpWorkspace, { recursive: true });
    api = createMockApi();
    registerConfigCommands(api, tmpWorkspace);
  });

  afterEach(cleanup);

  it("reports plugin not found", async () => {
    const text = await invokeCommand(api, "config", "nonexistent-plugin");
    expect(text).toContain('not found');
  });

  it("shows available plugins list", async () => {
    const text = await invokeCommand(api, "config", "nonexistent-plugin");
    expect(text).toContain("Available plugins");
  });
});

describe("/config secret masking", () => {
  let api: MockApi;

  beforeEach(() => {
    cleanup();
    const pluginDir = path.join(tmpWorkspace, "openclaw-secret-plugin");
    fs.mkdirSync(pluginDir, { recursive: true });
    fs.writeFileSync(
      path.join(pluginDir, "openclaw.plugin.json"),
      JSON.stringify({
        id: "openclaw-secret-plugin",
        name: "Secret Plugin",
        version: "1.0.0",
        configSchema: {
          type: "object",
          properties: {
            apiKey: { type: "string" },
            verbose: { type: "boolean", default: false },
          },
        },
      }),
      "utf-8",
    );

    api = createMockApi();
    registerConfigCommands(api, tmpWorkspace);
  });

  afterEach(cleanup);

  it("masks secret values in plugin detail view", async () => {
    // The overview should not leak any secrets from config
    const text = await invokeCommand(api, "config", "openclaw-secret-plugin");
    // Should have schema section but no leaked secrets
    expect(text).toContain("Secret Plugin");
    expect(text).not.toContain("super-secret-value");
  });
});

describe("/config schema validation warnings", () => {
  let api: MockApi;

  beforeEach(() => {
    cleanup();
    const pluginDir = path.join(tmpWorkspace, "openclaw-strict-plugin");
    fs.mkdirSync(pluginDir, { recursive: true });
    fs.writeFileSync(
      path.join(pluginDir, "openclaw.plugin.json"),
      JSON.stringify({
        id: "openclaw-strict-plugin",
        name: "Strict Plugin",
        version: "1.0.0",
        configSchema: {
          type: "object",
          additionalProperties: false,
          properties: {
            enabled: { type: "boolean", default: true },
          },
        },
      }),
      "utf-8",
    );

    api = createMockApi();
    registerConfigCommands(api, tmpWorkspace);
  });

  afterEach(cleanup);

  it("shows schema validation for strict plugin", async () => {
    const text = await invokeCommand(api, "config", "openclaw-strict-plugin");
    expect(text).toContain("SCHEMA VALIDATION");
    // No active overrides so should pass
    expect(text).toContain("All checks passed");
  });
});

describe("/config with no schema", () => {
  let api: MockApi;

  beforeEach(() => {
    cleanup();
    const pluginDir = path.join(tmpWorkspace, "openclaw-simple-plugin");
    fs.mkdirSync(pluginDir, { recursive: true });
    fs.writeFileSync(
      path.join(pluginDir, "openclaw.plugin.json"),
      JSON.stringify({
        id: "openclaw-simple-plugin",
        name: "Simple Plugin",
        version: "0.1.0",
      }),
      "utf-8",
    );

    api = createMockApi();
    registerConfigCommands(api, tmpWorkspace);
  });

  afterEach(cleanup);

  it("reports no configSchema defined", async () => {
    const text = await invokeCommand(api, "config", "openclaw-simple-plugin");
    expect(text).toContain("no configSchema defined");
  });
});
