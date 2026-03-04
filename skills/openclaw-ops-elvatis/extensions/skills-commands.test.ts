/**
 * Tests for skills commands (/skills, /shortcuts).
 *
 * Uses a temp workspace with mock plugin directories to test scanning logic.
 */

import { describe, it, expect, beforeEach, afterEach } from "vitest";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { createMockApi, invokeCommand, type MockApi } from "../src/test-helpers.js";
import { registerSkillsCommands } from "./skills-commands.js";

const tmpWorkspace = path.join(os.tmpdir(), "openclaw-ops-elvatis-test-skills-" + process.pid);

describe("skills-commands registration", () => {
  let api: MockApi;

  beforeEach(() => {
    api = createMockApi();
    registerSkillsCommands(api, tmpWorkspace);
  });

  it("registers /skills command", () => {
    const cmd = api.commands.get("skills")!;
    expect(cmd).toBeDefined();
    expect(cmd.name).toBe("skills");
    expect(cmd.acceptsArgs).toBe(false);
  });

  it("registers /shortcuts command", () => {
    const cmd = api.commands.get("shortcuts")!;
    expect(cmd).toBeDefined();
    expect(cmd.name).toBe("shortcuts");
    expect(cmd.acceptsArgs).toBe(false);
  });

  it("registers exactly 2 commands", () => {
    expect(api.commands.size).toBe(2);
  });
});

describe("/skills handler (empty workspace)", () => {
  let api: MockApi;

  beforeEach(() => {
    api = createMockApi();
    registerSkillsCommands(api, tmpWorkspace);
  });

  it("reports no plugins found when workspace does not exist", async () => {
    const text = await invokeCommand(api, "skills");
    expect(text).toContain("No openclaw-* plugins found");
  });

  it("includes Skills heading", async () => {
    const text = await invokeCommand(api, "skills");
    expect(text).toContain("Skills");
  });
});

describe("/skills handler (with plugins)", () => {
  let api: MockApi;

  beforeEach(() => {
    // Create a mock plugin directory
    const pluginDir = path.join(tmpWorkspace, "openclaw-test-plugin");
    fs.mkdirSync(pluginDir, { recursive: true });

    // Write manifest
    fs.writeFileSync(
      path.join(pluginDir, "openclaw.plugin.json"),
      JSON.stringify({ id: "openclaw-test-plugin", name: "Test Plugin", description: "A test plugin" }),
      "utf-8",
    );

    // Write package.json
    fs.writeFileSync(
      path.join(pluginDir, "package.json"),
      JSON.stringify({ name: "openclaw-test-plugin", version: "1.0.0" }),
      "utf-8",
    );

    // Write a source file with a command
    fs.writeFileSync(
      path.join(pluginDir, "index.ts"),
      `
export default function register(api) {
  api.registerCommand({
    name: "test-cmd",
    description: "A test command for testing",
    requireAuth: false,
    acceptsArgs: true,
    handler: async () => ({ text: "test" }),
  });
}
`,
      "utf-8",
    );

    api = createMockApi();
    registerSkillsCommands(api, tmpWorkspace);
  });

  afterEach(() => {
    try { fs.rmSync(tmpWorkspace, { recursive: true, force: true }); } catch {}
  });

  it("lists the plugin", async () => {
    const text = await invokeCommand(api, "skills");
    expect(text).toContain("Test Plugin");
  });

  it("shows plugin version", async () => {
    const text = await invokeCommand(api, "skills");
    expect(text).toContain("v1.0.0");
  });

  it("extracts commands from source", async () => {
    const text = await invokeCommand(api, "skills");
    expect(text).toContain("/test-cmd");
    expect(text).toContain("A test command for testing");
  });

  it("shows total count", async () => {
    const text = await invokeCommand(api, "skills");
    expect(text).toMatch(/1 skill/);
    expect(text).toMatch(/1 command/);
  });

  it("suggests /shortcuts", async () => {
    const text = await invokeCommand(api, "skills");
    expect(text).toContain("/shortcuts");
  });
});

describe("/shortcuts handler (empty workspace)", () => {
  let api: MockApi;

  beforeEach(() => {
    api = createMockApi();
    registerSkillsCommands(api, tmpWorkspace);
  });

  it("shows 0 commands", async () => {
    const text = await invokeCommand(api, "shortcuts");
    expect(text).toContain("0 commands");
  });
});

describe("/shortcuts handler (with plugins)", () => {
  let api: MockApi;

  beforeEach(() => {
    // Create two mock plugins
    for (const name of ["openclaw-alpha", "openclaw-beta"]) {
      const pluginDir = path.join(tmpWorkspace, name);
      fs.mkdirSync(pluginDir, { recursive: true });
      fs.writeFileSync(
        path.join(pluginDir, "openclaw.plugin.json"),
        JSON.stringify({ id: name, name }),
        "utf-8",
      );
      fs.writeFileSync(
        path.join(pluginDir, "package.json"),
        JSON.stringify({ name, version: "0.1.0" }),
        "utf-8",
      );
      fs.writeFileSync(
        path.join(pluginDir, "index.ts"),
        `
export default function register(api) {
  api.registerCommand({
    name: "${name.replace("openclaw-", "")}",
    description: "Command from ${name}",
    requireAuth: false,
    acceptsArgs: false,
    handler: async () => ({ text: "ok" }),
  });
}
`,
        "utf-8",
      );
    }

    api = createMockApi();
    registerSkillsCommands(api, tmpWorkspace);
  });

  afterEach(() => {
    try { fs.rmSync(tmpWorkspace, { recursive: true, force: true }); } catch {}
  });

  it("shows ALL COMMANDS section", async () => {
    const text = await invokeCommand(api, "shortcuts");
    expect(text).toContain("ALL COMMANDS (A-Z)");
  });

  it("shows BY PLUGIN section", async () => {
    const text = await invokeCommand(api, "shortcuts");
    expect(text).toContain("BY PLUGIN");
  });

  it("lists commands alphabetically", async () => {
    const text = await invokeCommand(api, "shortcuts");
    const alphaIdx = text.indexOf("/alpha");
    const betaIdx = text.indexOf("/beta");
    expect(alphaIdx).toBeGreaterThan(-1);
    expect(betaIdx).toBeGreaterThan(-1);
    expect(alphaIdx).toBeLessThan(betaIdx);
  });

  it("shows total count", async () => {
    const text = await invokeCommand(api, "shortcuts");
    expect(text).toContain("2 commands");
    expect(text).toContain("2 plugins");
  });

  it("suggests /skills", async () => {
    const text = await invokeCommand(api, "shortcuts");
    expect(text).toContain("/skills");
  });
});
