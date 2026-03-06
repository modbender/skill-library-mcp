import { describe, it, expect, vi, afterEach } from "vitest";
import os from "node:os";
import fs from "node:fs";
import path from "node:path";
import {
  expandHome,
  safeExec,
  runCmd,
  latestFile,
  formatBytes,
  loadActiveCooldowns,
  formatCooldownLine,
  formatIsoCompact,
  readJsonSafe,
  listWorkspacePluginDirs,
  getSystemResources,
  checkGatewayStatus,
  detectWindowsDriveRoot,
} from "./utils.js";
import type { CooldownEntry } from "./utils.js";

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

  it("expands ~/subpath to homedir/subpath", () => {
    const result = expandHome("~/documents/file.txt");
    expect(result).toBe(path.join(os.homedir(), "documents/file.txt"));
  });

  it("leaves absolute paths unchanged", () => {
    const abs = "/usr/local/bin";
    expect(expandHome(abs)).toBe(abs);
  });

  it("leaves relative paths without tilde unchanged", () => {
    expect(expandHome("some/relative/path")).toBe("some/relative/path");
  });
});

// ---------------------------------------------------------------------------
// safeExec
// ---------------------------------------------------------------------------
describe("safeExec", () => {
  it("returns trimmed stdout for a successful command", () => {
    // 'node -e' works cross-platform
    const result = safeExec('node -e "process.stdout.write(\'hello world  \')"');
    expect(result).toBe("hello world");
  });

  it("returns empty string when command fails", () => {
    const result = safeExec("this-command-should-not-exist-anywhere-12345");
    expect(result).toBe("");
  });
});

// ---------------------------------------------------------------------------
// runCmd
// ---------------------------------------------------------------------------
describe("runCmd", () => {
  it("returns exit code 0 and output for a successful command", () => {
    const result = runCmd("node", ["-e", "console.log('test-output')"]);
    expect(result.code).toBe(0);
    expect(result.out).toContain("test-output");
  });

  it("returns non-zero exit code for a failing command", () => {
    const result = runCmd("node", ["-e", "process.exit(42)"]);
    expect(result.code).toBe(42);
  });

  it("returns code 1 when the executable does not exist", () => {
    const result = runCmd("nonexistent-binary-xyz-99999", []);
    expect(result.code).toBe(1);
    // On some platforms the error message may be empty, so we only assert the code
    expect(typeof result.out).toBe("string");
  });

  it("respects custom timeout parameter", () => {
    // A very short timeout should cause a timeout error
    const result = runCmd("node", ["-e", "setTimeout(() => {}, 60000)"], 100);
    // On timeout, spawnSync sets status to null and error is populated
    expect(result.code).toBe(1);
  });
});

// ---------------------------------------------------------------------------
// formatBytes
// ---------------------------------------------------------------------------
describe("formatBytes", () => {
  it("formats bytes below 1 KB", () => {
    expect(formatBytes(512)).toBe("512B");
  });

  it("formats kilobytes", () => {
    expect(formatBytes(2048)).toBe("2.0KB");
  });

  it("formats megabytes", () => {
    expect(formatBytes(5 * 1024 * 1024)).toBe("5.0MB");
  });

  it("formats gigabytes", () => {
    expect(formatBytes(2.5 * 1024 ** 3)).toBe("2.50GB");
  });

  it("formats zero bytes", () => {
    expect(formatBytes(0)).toBe("0B");
  });
});

// ---------------------------------------------------------------------------
// latestFile
// ---------------------------------------------------------------------------
describe("latestFile", () => {
  it("returns null for a non-existent directory", () => {
    expect(latestFile("/tmp/this-dir-should-not-exist-xyz-12345", "prefix")).toBeNull();
  });

  it("returns null when no files match the prefix", () => {
    // os.tmpdir() exists but is unlikely to have files starting with this prefix
    expect(latestFile(os.tmpdir(), "zzz-nonexistent-prefix-xyz-99999")).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// loadActiveCooldowns
// ---------------------------------------------------------------------------
describe("loadActiveCooldowns", () => {
  const tmpDir = path.join(os.tmpdir(), "openclaw-ops-elvatis-test-cooldowns-" + process.pid);
  const memoryDir = path.join(tmpDir, "memory");
  const statePath = path.join(memoryDir, "model-ratelimits.json");

  afterEach(() => {
    try {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    } catch {
      // ignore cleanup failures
    }
  });

  it("returns empty array when workspace does not exist", () => {
    expect(loadActiveCooldowns("/tmp/nonexistent-workspace-xyz-99999")).toEqual([]);
  });

  it("returns empty array when state file does not exist", () => {
    fs.mkdirSync(memoryDir, { recursive: true });
    expect(loadActiveCooldowns(tmpDir)).toEqual([]);
  });

  it("returns empty array when state file has invalid JSON", () => {
    fs.mkdirSync(memoryDir, { recursive: true });
    fs.writeFileSync(statePath, "not-json{{", "utf-8");
    expect(loadActiveCooldowns(tmpDir)).toEqual([]);
  });

  it("returns empty array when no models are in cooldown", () => {
    fs.mkdirSync(memoryDir, { recursive: true });
    fs.writeFileSync(statePath, JSON.stringify({ limited: {} }), "utf-8");
    expect(loadActiveCooldowns(tmpDir)).toEqual([]);
  });

  it("filters out expired cooldowns", () => {
    const pastTime = Math.floor(Date.now() / 1000) - 3600;
    fs.mkdirSync(memoryDir, { recursive: true });
    fs.writeFileSync(
      statePath,
      JSON.stringify({
        limited: {
          "openai/gpt-4": { lastHitAt: pastTime - 100, nextAvailableAt: pastTime },
        },
      }),
      "utf-8",
    );
    expect(loadActiveCooldowns(tmpDir)).toEqual([]);
  });

  it("returns active cooldowns sorted by soonest-to-expire", () => {
    const now = Math.floor(Date.now() / 1000);
    const soon = now + 600;
    const later = now + 3600;
    fs.mkdirSync(memoryDir, { recursive: true });
    fs.writeFileSync(
      statePath,
      JSON.stringify({
        limited: {
          "anthropic/claude-opus": {
            lastHitAt: now - 100,
            nextAvailableAt: later,
            reason: "daily limit",
          },
          "openai/gpt-5": {
            lastHitAt: now - 50,
            nextAvailableAt: soon,
            reason: "rate limit",
          },
        },
      }),
      "utf-8",
    );
    const result = loadActiveCooldowns(tmpDir);
    expect(result).toHaveLength(2);
    expect(result[0].model).toBe("openai/gpt-5");
    expect(result[1].model).toBe("anthropic/claude-opus");
    expect(result[0].reason).toBe("rate limit");
    expect(result[1].reason).toBe("daily limit");
  });
});

// ---------------------------------------------------------------------------
// formatCooldownLine
// ---------------------------------------------------------------------------
describe("formatCooldownLine", () => {
  it("formats a cooldown entry with minutes remaining", () => {
    const now = Math.floor(Date.now() / 1000);
    const entry: CooldownEntry = {
      model: "openai/gpt-5",
      lastHitAt: now - 100,
      nextAvailableAt: now + 1800,
    };
    const line = formatCooldownLine(entry);
    expect(line).toContain("openai/gpt-5");
    expect(line).toContain("UTC");
    expect(line).toMatch(/~\d+m/);
  });

  it("formats hours for long cooldowns", () => {
    const now = Math.floor(Date.now() / 1000);
    const entry: CooldownEntry = {
      model: "anthropic/claude-opus",
      lastHitAt: now - 100,
      nextAvailableAt: now + 7200, // 2 hours
    };
    const line = formatCooldownLine(entry);
    expect(line).toContain("anthropic/claude-opus");
    expect(line).toMatch(/~2h/);
  });

  it("shows at least 1 minute even for very short remaining times", () => {
    const now = Math.floor(Date.now() / 1000);
    const entry: CooldownEntry = {
      model: "test/model",
      lastHitAt: now - 10,
      nextAvailableAt: now + 5, // 5 seconds
    };
    const line = formatCooldownLine(entry);
    expect(line).toMatch(/~1m/);
  });
});

// ---------------------------------------------------------------------------
// formatIsoCompact
// ---------------------------------------------------------------------------
describe("formatIsoCompact", () => {
  it("formats a Date object into YYYY-MM-DD HH:MM", () => {
    const d = new Date("2026-03-15T14:30:00Z");
    expect(formatIsoCompact(d)).toBe("2026-03-15 14:30");
  });

  it("formats an epoch-ms number", () => {
    const ms = new Date("2026-01-01T00:00:00Z").getTime();
    expect(formatIsoCompact(ms)).toBe("2026-01-01 00:00");
  });

  it("returns a 16-character string (YYYY-MM-DD HH:MM)", () => {
    expect(formatIsoCompact(new Date())).toMatch(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/);
  });
});

// ---------------------------------------------------------------------------
// readJsonSafe
// ---------------------------------------------------------------------------
describe("readJsonSafe", () => {
  const tmpDir = path.join(os.tmpdir(), "openclaw-ops-elvatis-test-json-" + process.pid);

  afterEach(() => {
    try {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    } catch {
      // ignore
    }
  });

  it("parses a valid JSON file", () => {
    fs.mkdirSync(tmpDir, { recursive: true });
    const fp = path.join(tmpDir, "valid.json");
    fs.writeFileSync(fp, JSON.stringify({ name: "test", version: "1.0" }), "utf-8");
    const result = readJsonSafe(fp, null);
    expect(result).toEqual({ name: "test", version: "1.0" });
  });

  it("returns fallback for non-existent file", () => {
    const result = readJsonSafe("/tmp/does-not-exist-xyz-99999.json", { default: true });
    expect(result).toEqual({ default: true });
  });

  it("returns fallback for invalid JSON", () => {
    fs.mkdirSync(tmpDir, { recursive: true });
    const fp = path.join(tmpDir, "bad.json");
    fs.writeFileSync(fp, "not json{{{", "utf-8");
    expect(readJsonSafe(fp, "fallback")).toBe("fallback");
  });
});

// ---------------------------------------------------------------------------
// listWorkspacePluginDirs
// ---------------------------------------------------------------------------
describe("listWorkspacePluginDirs", () => {
  const tmpDir = path.join(os.tmpdir(), "openclaw-ops-elvatis-test-plugins-" + process.pid);

  afterEach(() => {
    try {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    } catch {
      // ignore
    }
  });

  it("returns empty array for non-existent workspace", () => {
    expect(listWorkspacePluginDirs("/tmp/nonexistent-ws-xyz-99999")).toEqual([]);
  });

  it("returns empty array when no plugin dirs exist", () => {
    fs.mkdirSync(tmpDir, { recursive: true });
    fs.mkdirSync(path.join(tmpDir, "some-other-dir"), { recursive: true });
    expect(listWorkspacePluginDirs(tmpDir)).toEqual([]);
  });

  it("only returns openclaw-* dirs that have openclaw.plugin.json", () => {
    fs.mkdirSync(tmpDir, { recursive: true });

    // Dir with manifest - should be included
    const goodDir = path.join(tmpDir, "openclaw-alpha");
    fs.mkdirSync(goodDir, { recursive: true });
    fs.writeFileSync(path.join(goodDir, "openclaw.plugin.json"), "{}", "utf-8");

    // Dir without manifest - should be excluded
    const noManifest = path.join(tmpDir, "openclaw-beta");
    fs.mkdirSync(noManifest, { recursive: true });

    // Non-openclaw dir - should be excluded
    const unrelated = path.join(tmpDir, "other-project");
    fs.mkdirSync(unrelated, { recursive: true });
    fs.writeFileSync(path.join(unrelated, "openclaw.plugin.json"), "{}", "utf-8");

    const result = listWorkspacePluginDirs(tmpDir);
    expect(result).toEqual(["openclaw-alpha"]);
  });

  it("returns sorted results", () => {
    fs.mkdirSync(tmpDir, { recursive: true });
    for (const name of ["openclaw-zeta", "openclaw-alpha", "openclaw-mid"]) {
      const dir = path.join(tmpDir, name);
      fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(path.join(dir, "openclaw.plugin.json"), "{}", "utf-8");
    }
    expect(listWorkspacePluginDirs(tmpDir)).toEqual([
      "openclaw-alpha",
      "openclaw-mid",
      "openclaw-zeta",
    ]);
  });
});

// ---------------------------------------------------------------------------
// detectWindowsDriveRoot
// ---------------------------------------------------------------------------
describe("detectWindowsDriveRoot", () => {
  it("extracts drive letter from standard Windows path", () => {
    expect(detectWindowsDriveRoot("E:\\_data\\workspace")).toBe("E:\\");
  });

  it("extracts drive letter from path with forward slashes", () => {
    expect(detectWindowsDriveRoot("D:/projects/openclaw")).toBe("D:\\");
  });

  it("normalizes lowercase drive letters to uppercase", () => {
    expect(detectWindowsDriveRoot("c:\\Users\\test")).toBe("C:\\");
  });

  it("handles bare drive letter without trailing separator", () => {
    expect(detectWindowsDriveRoot("E:")).toBe("E:\\");
  });

  it("falls back to C:\\ for UNC or unusual paths", () => {
    expect(detectWindowsDriveRoot("\\\\server\\share")).toBe("C:\\");
  });

  it("falls back to C:\\ for Unix-style paths", () => {
    expect(detectWindowsDriveRoot("/home/user/workspace")).toBe("C:\\");
  });

  it("falls back to C:\\ for empty string", () => {
    expect(detectWindowsDriveRoot("")).toBe("C:\\");
  });
});

// ---------------------------------------------------------------------------
// getSystemResources
// ---------------------------------------------------------------------------
describe("getSystemResources", () => {
  it("returns cpu, memory, and disk keys", () => {
    const res = getSystemResources();
    expect(res).toHaveProperty("cpu");
    expect(res).toHaveProperty("memory");
    expect(res).toHaveProperty("disk");
  });

  it("cpu contains three load average values", () => {
    const res = getSystemResources();
    // Format is "x.xx, x.xx, x.xx"
    expect(res.cpu).toMatch(/\d+\.\d+, \d+\.\d+, \d+\.\d+/);
  });

  it("memory contains usage percentage", () => {
    const res = getSystemResources();
    // Format includes "XX.X%"
    expect(res.memory).toMatch(/\d+\.\d+%/);
  });

  it("memory contains formatted byte values", () => {
    const res = getSystemResources();
    // Contains "X.XGB / X.XGB" or similar
    expect(res.memory).toMatch(/\//);
  });

  it("disk returns a string (may be N/A on some platforms)", () => {
    const res = getSystemResources();
    expect(typeof res.disk).toBe("string");
    expect(res.disk.length).toBeGreaterThan(0);
  });

  it("disk shows usage details on Linux, macOS, and Windows", () => {
    const platform = os.platform();
    if (platform !== "linux" && platform !== "darwin" && platform !== "win32") return;
    const res = getSystemResources();
    // Should contain percentage and byte values, not just "N/A"
    expect(res.disk).toMatch(/\d+\.\d+% used/);
    expect(res.disk).toMatch(/\//);
  });

  it("accepts a workspace path argument for drive detection", () => {
    const res = getSystemResources(process.cwd());
    expect(typeof res.disk).toBe("string");
    expect(res.disk.length).toBeGreaterThan(0);
  });

  it("on Windows, disk output includes drive letter indicator", () => {
    if (os.platform() !== "win32") return;
    const res = getSystemResources("E:\\_data\\workspace");
    // On Windows the output should include the drive letter in brackets
    expect(res.disk).toMatch(/\[[A-Z]:\]/);
  });
});

// ---------------------------------------------------------------------------
// checkGatewayStatus
// ---------------------------------------------------------------------------
describe("checkGatewayStatus", () => {
  it("returns an object with running boolean", () => {
    // openclaw binary likely not installed in test env, so this should return not running
    const result = checkGatewayStatus("default");
    expect(typeof result.running).toBe("boolean");
  });

  it("returns not running when openclaw binary is unavailable", () => {
    const result = checkGatewayStatus("nonexistent-profile-xyz");
    expect(result.running).toBe(false);
  });

  it("pid and uptime are optional", () => {
    const result = checkGatewayStatus();
    expect(result.pid === undefined || typeof result.pid === "number").toBe(true);
    expect(result.uptime === undefined || typeof result.uptime === "string").toBe(true);
  });
});
