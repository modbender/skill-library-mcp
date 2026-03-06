/**
 * Tests for legacy commands (/cron, /privacy-scan, /release, /staging-smoke, /handoff, /limits).
 *
 * Uses a mock API to verify registration metadata and handler output format.
 * Filesystem-dependent handlers use a temp directory.
 */

import { describe, it, expect, beforeEach, afterEach } from "vitest";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { createMockApi, invokeCommand, type MockApi } from "../src/test-helpers.js";
import { registerLegacyCommands } from "./legacy-commands.js";

const tmpWorkspace = path.join(os.tmpdir(), "openclaw-ops-elvatis-test-legacy-" + process.pid);
const cronDir = path.join(tmpWorkspace, "cron");
const cronScripts = path.join(cronDir, "scripts");
const cronReports = path.join(cronDir, "reports");

describe("legacy-commands registration", () => {
  let api: MockApi;

  beforeEach(() => {
    api = createMockApi();
    registerLegacyCommands(api, tmpWorkspace, cronDir, cronScripts, cronReports);
  });

  it("registers /cron command", () => {
    expect(api.commands.has("cron")).toBe(true);
    expect(api.commands.get("cron")!.acceptsArgs).toBe(false);
  });

  it("registers /privacy-scan command", () => {
    expect(api.commands.has("privacy-scan")).toBe(true);
  });

  it("registers /release command", () => {
    expect(api.commands.has("release")).toBe(true);
  });

  it("registers /staging-smoke command", () => {
    expect(api.commands.has("staging-smoke")).toBe(true);
  });

  it("registers /handoff command", () => {
    expect(api.commands.has("handoff")).toBe(true);
  });

  it("registers /limits command", () => {
    expect(api.commands.has("limits")).toBe(true);
  });

  it("registers exactly 6 commands", () => {
    expect(api.commands.size).toBe(6);
  });

  it("all commands have descriptions", () => {
    for (const [, cmd] of api.commands) {
      expect(cmd.description).toBeTruthy();
      expect(cmd.description.length).toBeGreaterThan(5);
    }
  });
});

describe("/cron handler", () => {
  let api: MockApi;

  beforeEach(() => {
    api = createMockApi();
    registerLegacyCommands(api, tmpWorkspace, cronDir, cronScripts, cronReports);
  });

  it("returns Cron dashboard heading", async () => {
    const text = await invokeCommand(api, "cron");
    expect(text).toContain("Cron dashboard");
  });

  it("includes CRONTAB JOBS section", async () => {
    const text = await invokeCommand(api, "cron");
    expect(text).toContain("CRONTAB JOBS");
  });

  it("includes SCRIPTS section", async () => {
    const text = await invokeCommand(api, "cron");
    expect(text).toContain("SCRIPTS");
  });

  it("includes REPORTS section", async () => {
    const text = await invokeCommand(api, "cron");
    expect(text).toContain("REPORTS");
  });

  it("handles missing cron scripts directory gracefully", async () => {
    const text = await invokeCommand(api, "cron");
    // Should show "(cron/scripts missing)" rather than crash
    expect(text).toContain("cron/scripts missing");
  });
});

describe("/cron handler with filesystem", () => {
  let api: MockApi;

  beforeEach(() => {
    fs.mkdirSync(cronScripts, { recursive: true });
    fs.mkdirSync(cronReports, { recursive: true });
    api = createMockApi();
    registerLegacyCommands(api, tmpWorkspace, cronDir, cronScripts, cronReports);
  });

  afterEach(() => {
    try { fs.rmSync(tmpWorkspace, { recursive: true, force: true }); } catch {}
  });

  it("lists .sh scripts when present", async () => {
    fs.writeFileSync(path.join(cronScripts, "backup.sh"), "#!/bin/bash\necho hi", "utf-8");
    const text = await invokeCommand(api, "cron");
    expect(text).toContain("backup.sh");
  });

  it("lists latest privacy scan report when present", async () => {
    fs.writeFileSync(
      path.join(cronReports, "github-privacy-scan_20260227.txt"),
      "scan results",
      "utf-8",
    );
    const text = await invokeCommand(api, "cron");
    expect(text).toContain("github-privacy-scan_20260227");
  });

  it("shows (none) when no scripts exist", async () => {
    // cronScripts dir exists but is empty
    const text = await invokeCommand(api, "cron");
    expect(text).toContain("(none)");
  });
});

describe("/privacy-scan handler", () => {
  let api: MockApi;

  beforeEach(() => {
    api = createMockApi();
    registerLegacyCommands(api, tmpWorkspace, cronDir, cronScripts, cronReports);
  });

  it("reports missing script when not found", async () => {
    const text = await invokeCommand(api, "privacy-scan");
    expect(text).toContain("not found");
  });
});

describe("/release handler", () => {
  let api: MockApi;

  beforeEach(() => {
    api = createMockApi();
    registerLegacyCommands(api, tmpWorkspace, cronDir, cronScripts, cronReports);
  });

  it("returns Release / QA heading", async () => {
    const text = await invokeCommand(api, "release");
    expect(text).toContain("Release / QA");
  });

  it("reports missing RELEASE.md when not found", async () => {
    const text = await invokeCommand(api, "release");
    expect(text).toContain("Missing:");
  });
});

describe("/release handler with filesystem", () => {
  let api: MockApi;

  beforeEach(() => {
    const opsDir = path.join(tmpWorkspace, "openclaw-ops-elvatis");
    fs.mkdirSync(opsDir, { recursive: true });
    fs.writeFileSync(path.join(opsDir, "RELEASE.md"), "# Release checklist\n- Step 1\n- Step 2", "utf-8");
    api = createMockApi();
    registerLegacyCommands(api, tmpWorkspace, cronDir, cronScripts, cronReports);
  });

  afterEach(() => {
    try { fs.rmSync(tmpWorkspace, { recursive: true, force: true }); } catch {}
  });

  it("shows RELEASE.md content when file exists", async () => {
    const text = await invokeCommand(api, "release");
    expect(text).toContain("Release checklist");
    expect(text).toContain("Step 1");
  });
});

describe("/handoff handler", () => {
  let api: MockApi;

  beforeEach(() => {
    api = createMockApi();
    registerLegacyCommands(api, tmpWorkspace, cronDir, cronScripts, cronReports);
  });

  it("reports missing handoff log when not found", async () => {
    const text = await invokeCommand(api, "handoff");
    expect(text).toContain("Missing:");
  });
});

describe("/handoff handler with filesystem", () => {
  let api: MockApi;

  beforeEach(() => {
    const handoffDir = path.join(tmpWorkspace, "openclaw-ops-elvatis", ".ai", "handoff");
    fs.mkdirSync(handoffDir, { recursive: true });
    fs.writeFileSync(path.join(handoffDir, "LOG.md"), "## 2026-02-27\nSession completed.\n", "utf-8");
    api = createMockApi();
    registerLegacyCommands(api, tmpWorkspace, cronDir, cronScripts, cronReports);
  });

  afterEach(() => {
    try { fs.rmSync(tmpWorkspace, { recursive: true, force: true }); } catch {}
  });

  it("shows handoff log tail when file exists", async () => {
    const text = await invokeCommand(api, "handoff");
    expect(text).toContain("handoff (tail)");
    expect(text).toContain("Session completed");
  });
});

describe("/limits handler", () => {
  let api: MockApi;

  beforeEach(() => {
    api = createMockApi();
    registerLegacyCommands(api, tmpWorkspace, cronDir, cronScripts, cronReports);
  });

  it("returns text output (even when openclaw binary unavailable)", async () => {
    const text = await invokeCommand(api, "limits");
    expect(typeof text).toBe("string");
    expect(text.length).toBeGreaterThan(0);
  });

  it("includes Limits heading or error message", async () => {
    const text = await invokeCommand(api, "limits");
    // Either shows "Limits" section or failure message
    expect(text).toMatch(/Limits|Failed/);
  });
});
