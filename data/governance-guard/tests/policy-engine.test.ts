import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { evaluate, matchRule, matchGlob, checkSensitiveData, computeVerdictHash } from "../scripts/policy-engine.js";
import { createIntent } from "../scripts/intent.js";
import type { ActionIntent, CreateIntentParams } from "../scripts/intent.js";
import type { PolicyFile, PolicyRule } from "../scripts/yaml-parse.js";

// ── Helpers ──────────────────────────────────────────────────────────

const NOW = "2026-02-26T12:00:00.000Z";

function makeIntent(overrides: Partial<CreateIntentParams> = {}): ActionIntent {
  return createIntent({
    skill: "test-skill",
    tool: "test-tool",
    model: "claude",
    actionType: "read",
    target: "./src/main.ts",
    parameters: {},
    dataScope: [],
    conversationId: "c1",
    messageId: "m1",
    userInstruction: "test",
    ...overrides,
  });
}

function makePolicy(overrides: Partial<PolicyFile> = {}): PolicyFile {
  return {
    version: "0.1",
    default_verdict: "deny",
    rules: [],
    sensitive_data: [],
    ...overrides,
  };
}

// ── T-001: No matching rule, default deny ────────────────────────────

describe("T-001: default deny", () => {
  it("returns deny when no rules match and default is deny", () => {
    const intent = makeIntent();
    const policy = makePolicy({ default_verdict: "deny" });
    const verdict = evaluate(intent, policy, NOW);
    assert.equal(verdict.decision, "deny");
    assert.equal(verdict.rule_matched, "__default__");
  });
});

// ── T-002: No matching rule, default approve ─────────────────────────

describe("T-002: default approve", () => {
  it("returns approve when no rules match and default is approve", () => {
    const intent = makeIntent();
    const policy = makePolicy({ default_verdict: "approve" });
    const verdict = evaluate(intent, policy, NOW);
    assert.equal(verdict.decision, "approve");
    assert.equal(verdict.rule_matched, "__default__");
  });
});

// ── T-003: Matching approve rule ─────────────────────────────────────

describe("T-003: approve rule", () => {
  it("returns approve with correct rule_matched", () => {
    const intent = makeIntent({ actionType: "read", target: "./README.md" });
    const policy = makePolicy({
      rules: [{
        name: "allow-reads",
        match: { action_type: "read" },
        verdict: "approve",
        reason: "Reads are safe",
      }],
    });
    const verdict = evaluate(intent, policy, NOW);
    assert.equal(verdict.decision, "approve");
    assert.equal(verdict.rule_matched, "allow-reads");
    assert.equal(verdict.reason, "Reads are safe");
  });
});

// ── T-004: Matching deny rule ────────────────────────────────────────

describe("T-004: deny rule", () => {
  it("returns deny with correct reason", () => {
    const intent = makeIntent({ actionType: "delete", target: "/tmp/file.txt" });
    const policy = makePolicy({
      rules: [{
        name: "block-delete",
        match: { action_type: "delete" },
        verdict: "deny",
        reason: "Deletion not allowed",
      }],
    });
    const verdict = evaluate(intent, policy, NOW);
    assert.equal(verdict.decision, "deny");
    assert.equal(verdict.rule_matched, "block-delete");
    assert.equal(verdict.reason, "Deletion not allowed");
  });
});

// ── T-005: Matching escalate rule ────────────────────────────────────

describe("T-005: escalate rule", () => {
  it("returns escalate for matching rule", () => {
    const intent = makeIntent({ actionType: "network", target: "https://api.example.com" });
    const policy = makePolicy({
      rules: [{
        name: "escalate-network",
        match: { action_type: "network" },
        verdict: "escalate",
        reason: "Network requires approval",
      }],
    });
    const verdict = evaluate(intent, policy, NOW);
    assert.equal(verdict.decision, "escalate");
    assert.equal(verdict.rule_matched, "escalate-network");
  });
});

// ── First-match-wins semantics ───────────────────────────────────────

describe("first-match-wins", () => {
  it("returns the first matching rule, not later ones", () => {
    const intent = makeIntent({ actionType: "read" });
    const policy = makePolicy({
      rules: [
        { name: "deny-reads", match: { action_type: "read" }, verdict: "deny" },
        { name: "allow-reads", match: { action_type: "read" }, verdict: "approve" },
      ],
    });
    const verdict = evaluate(intent, policy, NOW);
    assert.equal(verdict.decision, "deny");
    assert.equal(verdict.rule_matched, "deny-reads");
  });
});

// ── matchGlob ────────────────────────────────────────────────────────

describe("matchGlob", () => {
  it("matches single-segment wildcard", () => {
    assert.ok(matchGlob("./src/main.ts", "./**"));
  });

  it("matches recursive wildcard", () => {
    assert.ok(matchGlob("./src/deep/nested/file.ts", "./**"));
  });

  it("rejects non-matching patterns", () => {
    assert.ok(!matchGlob("/etc/passwd", "./**"));
  });

  it("handles negation pattern", () => {
    assert.ok(matchGlob("https://api.example.com", "!*.local"));
    assert.ok(!matchGlob("server.local", "!*.local"));
  });
});

// ── matchRule ────────────────────────────────────────────────────────

describe("matchRule", () => {
  it("matches action_type exact", () => {
    const intent = makeIntent({ actionType: "write" });
    const rule: PolicyRule = { name: "test", match: { action_type: "write" }, verdict: "deny" };
    assert.ok(matchRule(intent, rule));
  });

  it("matches action_type array (any-of)", () => {
    const intent = makeIntent({ actionType: "delete" });
    const rule: PolicyRule = {
      name: "test",
      match: { action_type: ["write", "delete"] },
      verdict: "deny",
    };
    assert.ok(matchRule(intent, rule));
  });

  it("fails when action_type doesn't match", () => {
    const intent = makeIntent({ actionType: "read" });
    const rule: PolicyRule = { name: "test", match: { action_type: "write" }, verdict: "deny" };
    assert.ok(!matchRule(intent, rule));
  });

  it("matches data_scope intersection", () => {
    const intent = makeIntent({ dataScope: ["personal", "financial"] });
    const rule: PolicyRule = {
      name: "test",
      match: { data_scope: ["personal", "identity"] },
      verdict: "deny",
    };
    assert.ok(matchRule(intent, rule));
  });

  it("fails when data_scope has no intersection", () => {
    const intent = makeIntent({ dataScope: ["financial"] });
    const rule: PolicyRule = {
      name: "test",
      match: { data_scope: ["personal", "identity"] },
      verdict: "deny",
    };
    assert.ok(!matchRule(intent, rule));
  });

  it("matches when rule has no data_scope (wildcard)", () => {
    const intent = makeIntent({ dataScope: ["personal"] });
    const rule: PolicyRule = { name: "test", match: { action_type: "read" }, verdict: "approve" };
    assert.ok(matchRule(intent, rule));
  });

  it("matches target_pattern glob", () => {
    const intent = makeIntent({ target: "./src/app.ts" });
    const rule: PolicyRule = {
      name: "test",
      match: { target_pattern: "./**" },
      verdict: "approve",
    };
    assert.ok(matchRule(intent, rule));
  });
});

// ── checkSensitiveData ───────────────────────────────────────────────

describe("checkSensitiveData", () => {
  const sensitiveRules = [
    { category: "credentials", patterns: ["**/*.env", "**/.ssh/**"], action: "deny" as const },
    { category: "financial", patterns: ["**/*wallet*"], action: "escalate" as const },
  ];

  it("detects credential file patterns", () => {
    const intent = makeIntent({ target: "./config/.env" });
    const result = checkSensitiveData(intent, sensitiveRules);
    assert.ok(result !== null);
    assert.equal(result!.category, "credentials");
  });

  it("detects ssh key patterns", () => {
    const intent = makeIntent({ target: "/home/user/.ssh/id_rsa" });
    const result = checkSensitiveData(intent, sensitiveRules);
    assert.ok(result !== null);
    assert.equal(result!.category, "credentials");
  });

  it("detects data_scope category overlap", () => {
    const intent = makeIntent({ dataScope: ["financial"] });
    const result = checkSensitiveData(intent, sensitiveRules);
    assert.ok(result !== null);
    assert.equal(result!.category, "financial");
  });

  it("returns null for non-sensitive targets", () => {
    const intent = makeIntent({ target: "./src/main.ts" });
    const result = checkSensitiveData(intent, sensitiveRules);
    assert.equal(result, null);
  });
});

// ── Fail-closed behavior ─────────────────────────────────────────────

describe("fail-closed", () => {
  it("returns deny on empty policy (no rules)", () => {
    const intent = makeIntent();
    const policy = makePolicy({ default_verdict: "deny", rules: [] });
    const verdict = evaluate(intent, policy, NOW);
    assert.equal(verdict.decision, "deny");
  });
});

// ── Determinism ──────────────────────────────────────────────────────

describe("determinism", () => {
  it("same intent + same policy = same verdict hash", () => {
    const intent = makeIntent();
    const policy = makePolicy({
      rules: [{ name: "test", match: { action_type: "read" }, verdict: "approve" }],
    });

    const v1 = evaluate(intent, policy, NOW);
    const v2 = evaluate(intent, policy, NOW);
    assert.equal(v1.verdict_hash, v2.verdict_hash);
    assert.equal(v1.decision, v2.decision);
    assert.equal(v1.rule_matched, v2.rule_matched);
  });

  it("verdict_hash is deterministic for identical inputs (100 iterations)", () => {
    const intent = makeIntent();
    const policy = makePolicy();
    const first = evaluate(intent, policy, NOW);
    for (let i = 0; i < 100; i++) {
      const v = evaluate(intent, policy, NOW);
      assert.equal(v.verdict_hash, first.verdict_hash);
    }
  });
});

// ── Verdict hash computation ─────────────────────────────────────────

describe("computeVerdictHash", () => {
  it("produces consistent hash for same inputs", () => {
    const h1 = computeVerdictHash("deny", "abc123", "rule1", NOW);
    const h2 = computeVerdictHash("deny", "abc123", "rule1", NOW);
    assert.equal(h1, h2);
  });

  it("produces different hash for different inputs", () => {
    const h1 = computeVerdictHash("deny", "abc123", "rule1", NOW);
    const h2 = computeVerdictHash("approve", "abc123", "rule1", NOW);
    assert.notEqual(h1, h2);
  });
});

// ── Sensitive data takes priority over rules ─────────────────────────

describe("sensitive data priority", () => {
  it("sensitive data match overrides regular approve rule", () => {
    const intent = makeIntent({ target: "./secrets/.env", actionType: "read" });
    const policy = makePolicy({
      rules: [{ name: "allow-all-reads", match: { action_type: "read" }, verdict: "approve" }],
      sensitive_data: [{ category: "credentials", patterns: ["**/*.env"], action: "deny" }],
    });
    const verdict = evaluate(intent, policy, NOW);
    assert.equal(verdict.decision, "deny");
    assert.ok(verdict.rule_matched.includes("__sensitive_data__"));
  });
});
