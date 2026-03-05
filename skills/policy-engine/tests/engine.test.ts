import { describe, it, beforeEach } from "node:test";
import assert from "node:assert/strict";
import { PolicyEngine } from "../src/engine.js";
import { resolveConfig, type PolicyConfig } from "../src/config.js";
import { StateManager } from "../src/state.js";
import { matchDenyPatterns, checkPathAllowlist } from "../src/patterns.js";
import { getToolTier, isT0 } from "../src/tiers.js";
import { createBeforeToolCallHandler } from "../src/hooks/before-tool-call.js";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeConfig(overrides: Partial<PolicyConfig> = {}): PolicyConfig {
  return {
    enabled: true,
    dryRun: false,
    dryRunAllowT0: true,
    dryRunEssentialTools: ["message", "gateway", "session_status", "sessions_send", "sessions_list", "tts"],
    maxBlockedRetries: 3,
    riskTiers: {},
    denyPatterns: {},
    allowlists: {},
    routing: {},
    pathAllowlists: {},
    ...overrides,
  };
}

function mockLogger() {
  const logs: { level: string; msg: string }[] = [];
  return {
    logger: {
      info: (msg: string) => logs.push({ level: "info", msg }),
      warn: (msg: string) => logs.push({ level: "warn", msg }),
      error: (msg: string) => logs.push({ level: "error", msg }),
      debug: (msg: string) => logs.push({ level: "debug", msg }),
    },
    logs,
  };
}

// ===========================================================================
// 1. Allowlist Enforcement
// ===========================================================================

describe("Allowlist enforcement", () => {
  it("blocks a tool not in the allowlist", () => {
    const config = makeConfig({
      allowlists: { default: ["read", "write"] },
    });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({
      toolName: "exec",
      params: { command: "ls" },
    });

    assert.equal(result.action, "block");
    assert.ok(result.reason?.includes("not in the"));
  });

  it("allows a tool that is in the allowlist", () => {
    const config = makeConfig({
      allowlists: { default: ["read", "write", "exec"] },
    });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({
      toolName: "exec",
      params: { command: "ls" },
    });

    assert.equal(result.action, "allow");
  });

  it("allows all tools when no allowlist is configured", () => {
    const config = makeConfig();
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({
      toolName: "exec",
      params: { command: "ls" },
    });

    assert.equal(result.action, "allow");
  });

  it("applies per-agent allowlist via routing", () => {
    const config = makeConfig({
      allowlists: {
        safe: ["read"],
      },
      routing: {
        "agent-readonly": { toolProfile: "safe" },
      },
    });
    const engine = new PolicyEngine(config);

    // Agent with restriction
    const blocked = engine.evaluate({
      toolName: "exec",
      params: {},
      agentId: "agent-readonly",
    });
    assert.equal(blocked.action, "block");

    // Same tool, different agent (no restriction → falls back to default)
    const allowed = engine.evaluate({
      toolName: "exec",
      params: {},
      agentId: "agent-other",
    });
    assert.equal(allowed.action, "allow");
  });

  it("is case-insensitive for tool names", () => {
    const config = makeConfig({
      allowlists: { default: ["Read", "Write"] },
    });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({
      toolName: "READ",
      params: {},
    });

    assert.equal(result.action, "allow");
  });
});

// ===========================================================================
// 2. Deny Pattern Block
// ===========================================================================

describe("Deny pattern matching", () => {
  it("blocks exec with rm -rf", () => {
    const config = makeConfig();
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({
      toolName: "exec",
      params: { command: "rm -rf /" },
    });

    assert.equal(result.action, "block");
    assert.ok(result.reason?.includes("rm -rf"));
  });

  it("blocks exec with fork bomb", () => {
    const config = makeConfig();
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({
      toolName: "exec",
      params: { command: ":(){ :|:& };:" },
    });

    assert.equal(result.action, "block");
  });

  it("blocks exec with dd if=", () => {
    const result = new PolicyEngine(makeConfig()).evaluate({
      toolName: "exec",
      params: { command: "dd if=/dev/zero of=/dev/sda" },
    });
    assert.equal(result.action, "block");
  });

  it("blocks exec with mkfs", () => {
    const result = new PolicyEngine(makeConfig()).evaluate({
      toolName: "exec",
      params: { command: "mkfs.ext4 /dev/sda1" },
    });
    assert.equal(result.action, "block");
  });

  it("blocks write to system paths", () => {
    const result = new PolicyEngine(makeConfig()).evaluate({
      toolName: "write",
      params: { file_path: "/etc/passwd", content: "hacked" },
    });
    assert.equal(result.action, "block");
    assert.ok(result.reason?.includes("/etc/"));
  });

  it("blocks edit to /boot/", () => {
    const result = new PolicyEngine(makeConfig()).evaluate({
      toolName: "edit",
      params: { file_path: "/boot/grub.cfg", old_string: "a", new_string: "b" },
    });
    assert.equal(result.action, "block");
  });

  it("allows safe exec commands", () => {
    const result = new PolicyEngine(makeConfig()).evaluate({
      toolName: "exec",
      params: { command: "ls -la" },
    });
    assert.equal(result.action, "allow");
  });

  it("allows write to normal paths", () => {
    const result = new PolicyEngine(makeConfig()).evaluate({
      toolName: "write",
      params: { file_path: "/home/user/app/index.ts", content: "hello" },
    });
    assert.equal(result.action, "allow");
  });

  it("supports user-configured deny patterns", () => {
    const config = makeConfig({
      denyPatterns: { exec: ["DROP TABLE"] },
    });
    const result = new PolicyEngine(config).evaluate({
      toolName: "exec",
      params: { command: "psql -c 'DROP TABLE users'" },
    });
    assert.equal(result.action, "block");
    assert.ok(result.reason?.includes("DROP TABLE"));
  });

  it("matchDenyPatterns returns matched=false for safe input", () => {
    const result = matchDenyPatterns("exec", { command: "echo hello" }, {});
    assert.equal(result.matched, false);
  });

  it("matchDenyPatterns checks command param for exec", () => {
    const result = matchDenyPatterns(
      "exec",
      { command: "rm -rf /tmp" },
      {},
    );
    assert.equal(result.matched, true);
  });

  it("write content mentioning system paths is NOT blocked (scoped matching)", () => {
    const result = new PolicyEngine(makeConfig()).evaluate({
      toolName: "write",
      params: {
        file_path: "/Users/joe/notes.md",
        content: "The config file is stored in the system config directory for security.",
      },
    });
    assert.equal(result.action, "allow", "Write with safe path should not be blocked by content");
  });

  it("edit content mentioning dangerous commands is NOT blocked (scoped matching)", () => {
    const result = matchDenyPatterns(
      "edit",
      {
        file_path: "/Users/joe/docs/security.md",
        old_string: "old text",
        new_string: "The deny pattern blocks dangerous rm commands for safety.",
      },
      {},
    );
    assert.equal(result.matched, false, "Edit content should not trigger deny pattern");
  });

  it("exec still blocks dangerous commands in command param", () => {
    const result = matchDenyPatterns(
      "exec",
      { command: "echo test && rm -rf /", workdir: "/tmp", timeout: "30" },
      {},
    );
    assert.equal(result.matched, true, "Exec command param should still be checked");
  });

  it("unknown tools fall back to checking all params", () => {
    const result = matchDenyPatterns(
      "custom_tool",
      { payload: "rm -rf /" },
      { custom_tool: ["rm -rf"] },
    );
    assert.equal(result.matched, true, "Unknown tools should check all params");
  });
});

// ===========================================================================
// 3. Dry-Run Mode
// ===========================================================================

describe("Dry-run mode", () => {
  it("blocks all tools and returns stubs in dry-run mode", () => {
    const config = makeConfig({ dryRun: true });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({
      toolName: "exec",
      params: { command: "ls" },
    });

    assert.equal(result.action, "dryrun");
  });

  it("returns a valid dry-run stub", () => {
    const config = makeConfig({ dryRun: true });
    const engine = new PolicyEngine(config);

    const stub = engine.buildDryRunStub("exec", { command: "ls" });
    assert.equal(stub.dryRun, true);
    assert.equal(stub.tool, "exec");
    assert.equal(stub.params, "command");
    assert.ok(typeof stub.note === "string");
  });

  it("allows T0 tools when dryRunAllowT0=true", () => {
    const config = makeConfig({ dryRun: true, dryRunAllowT0: true });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({
      toolName: "read",
      params: { file_path: "/tmp/test" },
    });

    assert.equal(result.action, "allow");
  });

  it("blocks T0 tools when dryRunAllowT0=false", () => {
    const config = makeConfig({ dryRun: true, dryRunAllowT0: false });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({
      toolName: "read",
      params: {},
    });

    assert.equal(result.action, "dryrun");
  });

  it("blocks T1 tools in dry-run even with dryRunAllowT0=true", () => {
    const config = makeConfig({ dryRun: true, dryRunAllowT0: true });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({
      toolName: "write",
      params: { file_path: "/tmp/x", content: "hi" },
    });

    assert.equal(result.action, "dryrun");
  });
});

// ===========================================================================
// 4. Risk Tier T2 Logging
// ===========================================================================

describe("Risk tier T2 logging", () => {
  it("classifies exec as T2", () => {
    assert.equal(getToolTier("exec", {}), "T2");
  });

  it("classifies process as T2", () => {
    assert.equal(getToolTier("process", {}), "T2");
  });

  it("classifies gateway as T2", () => {
    assert.equal(getToolTier("gateway", {}), "T2");
  });

  it("classifies read as T0", () => {
    assert.equal(getToolTier("read", {}), "T0");
    assert.equal(isT0("read", {}), true);
  });

  it("classifies write as T1", () => {
    assert.equal(getToolTier("write", {}), "T1");
    assert.equal(isT0("write", {}), false);
  });

  it("respects user overrides", () => {
    assert.equal(getToolTier("exec", { exec: "T0" }), "T0");
    assert.equal(isT0("exec", { exec: "T0" }), true);
  });

  it("defaults unknown tools to T1", () => {
    assert.equal(getToolTier("some_custom_tool", {}), "T1");
  });

  it("T2 tool calls are logged at info level via before_tool_call handler", () => {
    const config = makeConfig();
    const engine = new PolicyEngine(config);
    const state = new StateManager();
    const { logger, logs } = mockLogger();

    const handler = createBeforeToolCallHandler({ engine, state, logger });
    handler(
      { toolName: "exec", params: { command: "ls" } },
      { toolName: "exec", sessionKey: "s1" },
    );

    const infoLogs = logs.filter((l) => l.level === "info");
    assert.ok(infoLogs.some((l) => l.msg.includes("policy:allow") && l.msg.includes("tier=T2")));
  });
});

// ===========================================================================
// 5. Block Counting / Escalation
// ===========================================================================

describe("Block counting and escalation", () => {
  it("escalates after maxBlockedRetries blocks", () => {
    const config = makeConfig({
      maxBlockedRetries: 2,
      allowlists: { default: ["read"] },
    });
    const engine = new PolicyEngine(config);
    const state = new StateManager();
    const { logger, logs } = mockLogger();

    const handler = createBeforeToolCallHandler({ engine, state, logger });
    const ctx = { toolName: "exec", sessionKey: "s1" };

    // Block 1
    handler({ toolName: "exec", params: {} }, ctx);
    // Block 2
    handler({ toolName: "exec", params: {} }, ctx);
    // Block 3 — should trigger escalation (blockedCount >= maxBlockedRetries)
    handler({ toolName: "exec", params: {} }, ctx);

    const escalationLogs = logs.filter((l) => l.msg.includes("policy:escalate"));
    assert.ok(escalationLogs.length > 0, "Expected at least one escalation log");
  });

  it("tracks blocked count in session state", () => {
    const state = new StateManager();

    state.recordToolCall("s1", "exec", false);
    state.recordToolCall("s1", "exec", false);
    state.recordToolCall("s1", "read", true);

    const s = state.get("s1");
    assert.equal(s.blockedCount, 2);
    assert.equal(s.toolCallHistory.length, 3);
  });

  it("escalation level increments", () => {
    const state = new StateManager();
    state.get("s1"); // initialize

    assert.equal(state.escalate("s1"), 1);
    assert.equal(state.escalate("s1"), 2);
    assert.equal(state.get("s1").escalationLevel, 2);
  });

  it("essential tools bypass escalation block", () => {
    const config = makeConfig({
      maxBlockedRetries: 2,
      allowlists: { default: ["read"] },
    });
    const engine = new PolicyEngine(config);

    // Simulate blockedCount exceeding threshold
    const result = engine.evaluate({
      toolName: "message",
      params: {},
      blockedCount: 5,
    });
    assert.equal(result.action, "allow", "Essential tool 'message' should bypass escalation block");
  });

  it("T0 tools bypass escalation block", () => {
    const config = makeConfig({
      maxBlockedRetries: 2,
      allowlists: { default: ["read"] },
    });
    const engine = new PolicyEngine(config);

    // 'read' is T0 — should still be allowed even past escalation threshold
    const result = engine.evaluate({
      toolName: "read",
      params: {},
      blockedCount: 5,
    });
    assert.equal(result.action, "allow", "T0 tool 'read' should bypass escalation block");
  });

  it("T1/T2 non-essential tools still blocked by escalation", () => {
    const config = makeConfig({
      maxBlockedRetries: 2,
      allowlists: { default: ["exec", "read"] },
    });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({
      toolName: "exec",
      params: {},
      blockedCount: 5,
    });
    assert.equal(result.action, "block", "T2 non-essential tool should still be blocked by escalation");
    assert.ok(result.reason?.includes("exceeded"), "Should mention exceeded retries");
  });
});

// ===========================================================================
// 6. Config Disabled (enabled=false)
// ===========================================================================

describe("Config disabled (enabled=false)", () => {
  it("allows all tools when disabled", () => {
    const config = makeConfig({ enabled: false });
    const engine = new PolicyEngine(config);

    // Even dangerous patterns should pass through
    const result = engine.evaluate({
      toolName: "exec",
      params: { command: "rm -rf /" },
    });

    assert.equal(result.action, "allow");
  });

  it("ignores allowlists when disabled", () => {
    const config = makeConfig({
      enabled: false,
      allowlists: { default: ["read"] },
    });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({
      toolName: "exec",
      params: {},
    });

    assert.equal(result.action, "allow");
  });

  it("ignores dry-run when disabled", () => {
    const config = makeConfig({
      enabled: false,
      dryRun: true,
    });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({
      toolName: "write",
      params: {},
    });

    assert.equal(result.action, "allow");
  });
});

// ===========================================================================
// 7. T0 in Dry-Run
// ===========================================================================

describe("T0 in dry-run", () => {
  it("allows T0 tools in dry-run when dryRunAllowT0=true", () => {
    const config = makeConfig({ dryRun: true, dryRunAllowT0: true });
    const engine = new PolicyEngine(config);

    for (const tool of ["read", "memory_search", "memory_get", "web_fetch", "image", "session_status", "sessions_list", "agents_list"]) {
      const result = engine.evaluate({ toolName: tool, params: {} });
      assert.equal(result.action, "allow", `Expected ${tool} to be allowed`);
    }
  });

  it("blocks T0 tools in dry-run when dryRunAllowT0=false", () => {
    const config = makeConfig({ dryRun: true, dryRunAllowT0: false });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({ toolName: "read", params: {} });
    assert.equal(result.action, "dryrun");
  });
});

// ===========================================================================
// Config Resolution
// ===========================================================================

describe("Config resolution", () => {
  it("returns defaults for undefined input", () => {
    const config = resolveConfig(undefined);
    assert.equal(config.enabled, true);
    assert.equal(config.dryRun, false);
    assert.equal(config.dryRunAllowT0, true);
    assert.equal(config.maxBlockedRetries, 3);
  });

  it("merges partial config with defaults", () => {
    const config = resolveConfig({ dryRun: true, maxBlockedRetries: 5 });
    assert.equal(config.enabled, true); // default
    assert.equal(config.dryRun, true); // overridden
    assert.equal(config.maxBlockedRetries, 5); // overridden
  });

  it("ignores invalid riskTiers values", () => {
    const config = resolveConfig({
      riskTiers: { exec: "T0", read: "INVALID", write: 42 },
    });
    assert.equal(config.riskTiers["exec"], "T0");
    assert.equal(config.riskTiers["read"], undefined);
    assert.equal(config.riskTiers["write"], undefined);
  });

  it("filters non-string values from denyPatterns arrays", () => {
    const config = resolveConfig({
      denyPatterns: { exec: ["rm -rf", 42, null, "mkfs"] },
    });
    assert.deepEqual(config.denyPatterns["exec"], ["rm -rf", "mkfs"]);
  });

  it("handles maxBlockedRetries <= 0 by using default", () => {
    const config = resolveConfig({ maxBlockedRetries: 0 });
    assert.equal(config.maxBlockedRetries, 3);
  });
});

// ===========================================================================
// State Manager
// ===========================================================================

describe("StateManager", () => {
  let state: StateManager;

  beforeEach(() => {
    state = new StateManager();
  });

  it("creates new session state on first access", () => {
    const s = state.get("new-session");
    assert.equal(s.blockedCount, 0);
    assert.equal(s.escalationLevel, 0);
    assert.deepEqual(s.toolCallHistory, []);
  });

  it("returns same state for same session key", () => {
    const s1 = state.get("s1");
    s1.blockedCount = 5;
    const s2 = state.get("s1");
    assert.equal(s2.blockedCount, 5);
  });

  it("tracks session count", () => {
    state.get("s1");
    state.get("s2");
    assert.equal(state.size, 2);
  });

  it("clear removes all state", () => {
    state.get("s1");
    state.get("s2");
    state.clear();
    assert.equal(state.size, 0);
  });
});

// ===========================================================================
// Before-tool-call hook integration
// ===========================================================================

describe("before_tool_call hook handler", () => {
  it("returns undefined (allow) for safe tools", () => {
    const config = makeConfig();
    const engine = new PolicyEngine(config);
    const state = new StateManager();
    const { logger } = mockLogger();

    const handler = createBeforeToolCallHandler({ engine, state, logger });
    const result = handler(
      { toolName: "read", params: { file_path: "/tmp/test" } },
      { toolName: "read", sessionKey: "s1" },
    );

    assert.equal(result, undefined);
  });

  it("returns block result for denied tool", () => {
    const config = makeConfig({
      allowlists: { default: ["read"] },
    });
    const engine = new PolicyEngine(config);
    const state = new StateManager();
    const { logger } = mockLogger();

    const handler = createBeforeToolCallHandler({ engine, state, logger });
    const result = handler(
      { toolName: "exec", params: {} },
      { toolName: "exec", sessionKey: "s1" },
    );

    assert.ok(result);
    assert.equal(result!.block, true);
    assert.ok(result!.blockReason);
  });

  it("returns dry-run stub as blockReason JSON", () => {
    const config = makeConfig({ dryRun: true });
    const engine = new PolicyEngine(config);
    const state = new StateManager();
    const { logger } = mockLogger();

    const handler = createBeforeToolCallHandler({ engine, state, logger });
    const result = handler(
      { toolName: "write", params: { file_path: "/tmp/x", content: "hi" } },
      { toolName: "write", sessionKey: "s1" },
    );

    assert.ok(result);
    assert.equal(result!.block, true);
    const parsed = JSON.parse(result!.blockReason!);
    assert.equal(parsed.dryRun, true);
    assert.equal(parsed.tool, "write");
  });

  it("fails open on handler error", () => {
    const config = makeConfig();
    const engine = new PolicyEngine(config);
    const state = new StateManager();
    const { logger, logs } = mockLogger();

    // Force an error by making evaluate throw
    engine.evaluate = () => { throw new Error("test error"); };

    const handler = createBeforeToolCallHandler({ engine, state, logger });
    const result = handler(
      { toolName: "exec", params: {} },
      { toolName: "exec", sessionKey: "s1" },
    );

    // Should fail open
    assert.equal(result, undefined);
    // Should log the error
    assert.ok(logs.some((l) => l.level === "error" && l.msg.includes("test error")));
  });

  it("handles missing sessionKey gracefully", () => {
    const config = makeConfig();
    const engine = new PolicyEngine(config);
    const state = new StateManager();
    const { logger } = mockLogger();

    const handler = createBeforeToolCallHandler({ engine, state, logger });
    const result = handler(
      { toolName: "read", params: {} },
      { toolName: "read" } as any, // no sessionKey
    );

    assert.equal(result, undefined);
  });
});

// ===========================================================================
// Policy Engine — updateConfig
// ===========================================================================

describe("PolicyEngine.updateConfig", () => {
  it("applies updated configuration", () => {
    const engine = new PolicyEngine(makeConfig({ dryRun: false }));

    let result = engine.evaluate({ toolName: "exec", params: { command: "ls" } });
    assert.equal(result.action, "allow");

    engine.updateConfig(makeConfig({ dryRun: true }));
    result = engine.evaluate({ toolName: "exec", params: { command: "ls" } });
    assert.equal(result.action, "dryrun");
  });
});

// ===========================================================================
// Deny patterns: combined built-in + user patterns
// ===========================================================================

describe("Combined deny patterns", () => {
  it("blocks both built-in and user patterns", () => {
    const config = makeConfig({
      denyPatterns: { exec: ["CUSTOM_DANGER"] },
    });
    const engine = new PolicyEngine(config);

    // Built-in pattern
    const r1 = engine.evaluate({ toolName: "exec", params: { command: "rm -rf /" } });
    assert.equal(r1.action, "block");

    // User pattern
    const r2 = engine.evaluate({ toolName: "exec", params: { command: "CUSTOM_DANGER here" } });
    assert.equal(r2.action, "block");

    // Safe command
    const r3 = engine.evaluate({ toolName: "exec", params: { command: "echo hello" } });
    assert.equal(r3.action, "allow");
  });
});

// ===========================================================================
// Deny patterns take precedence over allowlists
// ===========================================================================

describe("Deny patterns vs allowlists", () => {
  it("deny patterns block even if tool is in allowlist", () => {
    const config = makeConfig({
      allowlists: { default: ["exec"] },
    });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({
      toolName: "exec",
      params: { command: "rm -rf /" },
    });

    assert.equal(result.action, "block");
    assert.ok(result.reason?.includes("deny pattern"));
  });
});

// ===========================================================================
// Edge cases
// ===========================================================================

describe("Edge cases", () => {
  it("handles empty params", () => {
    const engine = new PolicyEngine(makeConfig());
    const result = engine.evaluate({ toolName: "exec", params: {} });
    assert.equal(result.action, "allow");
  });

  it("dry-run stub with empty params shows (none)", () => {
    const engine = new PolicyEngine(makeConfig({ dryRun: true }));
    const stub = engine.buildDryRunStub("exec", {});
    assert.equal(stub.params, "(none)");
  });

  it("handles tools with mixed case in allowlists and risk tiers", () => {
    const config = makeConfig({
      allowlists: { default: ["Exec", "READ"] },
      riskTiers: { EXEC: "T0" } as any,
    });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({ toolName: "exec", params: {} });
    assert.equal(result.action, "allow");
  });
});

// ===========================================================================
// 8. Essential Tools in Dry-Run (deadlock prevention)
// ===========================================================================

describe("Essential tools in dry-run", () => {
  it("allows message tool in dry-run mode", () => {
    const config = makeConfig({ dryRun: true });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({ toolName: "message", params: { action: "send" } });
    assert.equal(result.action, "allow");
    assert.ok(result.reason?.includes("Essential"));
  });

  it("allows gateway tool in dry-run mode", () => {
    const config = makeConfig({ dryRun: true });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({ toolName: "gateway", params: { action: "config.patch" } });
    assert.equal(result.action, "allow");
  });

  it("allows sessions_send in dry-run mode", () => {
    const config = makeConfig({ dryRun: true });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({ toolName: "sessions_send", params: {} });
    assert.equal(result.action, "allow");
  });

  it("still blocks non-essential T1 tools in dry-run", () => {
    const config = makeConfig({ dryRun: true });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({ toolName: "write", params: { file_path: "/tmp/x" } });
    assert.equal(result.action, "dryrun");
  });

  it("still blocks exec in dry-run (not essential)", () => {
    const config = makeConfig({ dryRun: true });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({ toolName: "exec", params: { command: "ls" } });
    assert.equal(result.action, "dryrun");
  });

  it("respects custom essential tools list", () => {
    const config = makeConfig({
      dryRun: true,
      dryRunEssentialTools: ["exec"],
    });
    const engine = new PolicyEngine(config);

    // exec is now essential
    const r1 = engine.evaluate({ toolName: "exec", params: {} });
    assert.equal(r1.action, "allow");

    // message is no longer essential
    const r2 = engine.evaluate({ toolName: "message", params: {} });
    assert.equal(r2.action, "dryrun");
  });

  it("is case-insensitive for essential tools", () => {
    const config = makeConfig({ dryRun: true });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({ toolName: "MESSAGE", params: {} });
    assert.equal(result.action, "allow");
  });
});

// ===========================================================================
// 9. Environment Variable Bypass (break-glass)
// ===========================================================================

describe("OPENCLAW_POLICY_BYPASS env var", () => {
  it("bypasses all policy when env var is set", () => {
    const config = makeConfig({
      dryRun: true,
      allowlists: { default: ["read"] },
    });
    const engine = new PolicyEngine(config);
    const state = new StateManager();
    const { logger, logs } = mockLogger();

    // Set bypass
    process.env.OPENCLAW_POLICY_BYPASS = "1";
    try {
      const handler = createBeforeToolCallHandler({ engine, state, logger });
      const result = handler(
        { toolName: "exec", params: { command: "rm -rf /" } },
        { toolName: "exec", sessionKey: "s1" },
      );

      // Should allow (undefined = pass through)
      assert.equal(result, undefined);
      // Should log warning
      assert.ok(logs.some((l) => l.level === "warn" && l.msg.includes("policy:bypass")));
    } finally {
      delete process.env.OPENCLAW_POLICY_BYPASS;
    }
  });

  it("does not bypass when env var is not set", () => {
    delete process.env.OPENCLAW_POLICY_BYPASS;

    const config = makeConfig({
      allowlists: { default: ["read"] },
    });
    const engine = new PolicyEngine(config);
    const state = new StateManager();
    const { logger } = mockLogger();

    const handler = createBeforeToolCallHandler({ engine, state, logger });
    const result = handler(
      { toolName: "exec", params: {} },
      { toolName: "exec", sessionKey: "s1" },
    );

    assert.ok(result);
    assert.equal(result!.block, true);
  });
});

// ===========================================================================
// 10. Path Allowlist Enforcement
// ===========================================================================

import nodePath from "node:path";

describe("Path allowlist enforcement", () => {
  const WORKSPACE = "/Users/joe/.openclaw/workspace";

  it("blocks write to path outside allowlist", () => {
    const config = makeConfig({
      pathAllowlists: { write: [`${WORKSPACE}/`] },
    });
    const engine = new PolicyEngine(config);

    // Use a path that won't trigger built-in deny patterns
    const result = engine.evaluate({
      toolName: "write",
      params: { file_path: "/home/other/file.txt", content: "data" },
    });
    assert.equal(result.action, "block");
    assert.ok(result.reason?.includes("outside allowed directories"));
  });

  it("allows write to path inside allowlist", () => {
    const config = makeConfig({
      pathAllowlists: { write: [`${WORKSPACE}/`] },
    });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({
      toolName: "write",
      params: { file_path: `${WORKSPACE}/test.md`, content: "hello" },
    });
    assert.equal(result.action, "allow");
  });

  it("blocks path traversal attempt", () => {
    const config = makeConfig({
      pathAllowlists: { write: ["/tmp/openclaw/downloads/"] },
    });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({
      toolName: "write",
      params: { file_path: "/tmp/openclaw/downloads/../../../etc/passwd", content: "x" },
    });
    assert.equal(result.action, "block");
    assert.ok(result.resolvedPath === undefined || result.reason?.includes("/etc/passwd"));
  });

  it("blocks path traversal with allowed prefix", () => {
    const config = makeConfig({
      pathAllowlists: { write: [`${WORKSPACE}/`] },
    });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({
      toolName: "write",
      params: { file_path: `${WORKSPACE}/../../.ssh/authorized_keys`, content: "key" },
    });
    assert.equal(result.action, "block");
  });

  it("allows when no pathAllowlist configured for tool", () => {
    const config = makeConfig({
      pathAllowlists: { write: [`${WORKSPACE}/`] },
    });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({
      toolName: "exec",
      params: { command: "ls" },
    });
    assert.equal(result.action, "allow");
  });

  it("allows when pathAllowlists is empty", () => {
    const config = makeConfig({ pathAllowlists: {} });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({
      toolName: "write",
      params: { file_path: "/etc/passwd", content: "x" },
    });
    // Still blocked by deny patterns (built-in /etc/)
    // Test with a non-system path
    const r2 = engine.evaluate({
      toolName: "write",
      params: { file_path: "/anywhere/file.txt", content: "x" },
    });
    assert.equal(r2.action, "allow");
  });

  it("handles relative paths by resolving against cwd", () => {
    const cwd = process.cwd();
    const config = makeConfig({
      pathAllowlists: { write: [`${cwd}/`] },
    });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({
      toolName: "write",
      params: { file_path: "./test.md", content: "hello" },
    });
    assert.equal(result.action, "allow");
  });

  it("blocks relative path that resolves outside allowlist", () => {
    const config = makeConfig({
      pathAllowlists: { write: ["/some/specific/dir/"] },
    });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({
      toolName: "write",
      params: { file_path: "./test.md", content: "hello" },
    });
    assert.equal(result.action, "block");
  });

  it("handles multiple allowed directories", () => {
    const config = makeConfig({
      pathAllowlists: { write: [`${WORKSPACE}/`, "/tmp/"] },
    });
    const engine = new PolicyEngine(config);

    const r1 = engine.evaluate({
      toolName: "write",
      params: { file_path: `${WORKSPACE}/file.txt`, content: "a" },
    });
    assert.equal(r1.action, "allow");

    const r2 = engine.evaluate({
      toolName: "write",
      params: { file_path: "/tmp/scratch.txt", content: "b" },
    });
    assert.equal(r2.action, "allow");

    const r3 = engine.evaluate({
      toolName: "write",
      params: { file_path: "/home/other/file.txt", content: "c" },
    });
    assert.equal(r3.action, "block");
  });

  it("path allowlist blocks even essential tools with path params", () => {
    // If someone adds an essential tool to pathAllowlists and it has path params,
    // the path check runs before the essential tool bypass
    const config = makeConfig({
      pathAllowlists: { write: [`${WORKSPACE}/`] },
    });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({
      toolName: "write",
      params: { path: "/root/.bashrc", content: "malicious" },
    });
    assert.equal(result.action, "block");
  });

  it("checkPathAllowlist function: no entry returns not blocked", () => {
    const result = checkPathAllowlist("exec", { command: "ls" }, {});
    assert.equal(result.blocked, false);
  });

  it("checkPathAllowlist function: blocks traversal", () => {
    const result = checkPathAllowlist(
      "write",
      { file_path: "/tmp/safe/../../../etc/shadow" },
      { write: ["/tmp/safe/"] },
    );
    assert.equal(result.blocked, true);
    assert.ok(result.resolvedPath?.includes("/etc/shadow"));
  });

  it("checkPathAllowlist: no path params with allowlist configured returns not blocked", () => {
    const result = checkPathAllowlist(
      "write",
      { content: "hello" },
      { write: [`${WORKSPACE}/`] },
    );
    assert.equal(result.blocked, false);
  });

  it("edit tool also enforces path allowlist", () => {
    const config = makeConfig({
      pathAllowlists: { edit: [`${WORKSPACE}/`] },
    });
    const engine = new PolicyEngine(config);

    const result = engine.evaluate({
      toolName: "edit",
      params: { file_path: "/home/other/file.ts", old_string: "a", new_string: "b" },
    });
    assert.equal(result.action, "block");
    assert.ok(result.reason?.includes("outside allowed"));
  });

  it("config resolution parses pathAllowlists", () => {
    const config = resolveConfig({
      pathAllowlists: {
        write: ["/tmp/", "/home/"],
        edit: ["/tmp/", 42, null],
      },
    });
    assert.deepEqual(config.pathAllowlists["write"], ["/tmp/", "/home/"]);
    assert.deepEqual(config.pathAllowlists["edit"], ["/tmp/"]);
  });
});
