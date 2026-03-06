import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { openWitnessLog, computeRecordHash, GENESIS_HASH } from "../scripts/witness.js";
import { createIntent } from "../scripts/intent.js";
import { evaluate } from "../scripts/policy-engine.js";
import type { PolicyFile } from "../scripts/yaml-parse.js";
import { mkdtempSync, writeFileSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";

// ── Helpers ──────────────────────────────────────────────────────────

const NOW = "2026-02-26T12:00:00.000Z";

function tmpWitnessPath(): string {
  const dir = mkdtempSync(join(tmpdir(), "governance-test-"));
  return join(dir, "witness.jsonl");
}

function sampleIntent() {
  return createIntent({
    skill: "test",
    tool: "bash",
    model: "claude",
    actionType: "read",
    target: "./README.md",
    parameters: {},
    dataScope: [],
    conversationId: "c1",
    messageId: "m1",
    userInstruction: "read the readme",
  });
}

function sampleVerdict(intent: ReturnType<typeof sampleIntent>) {
  const policy: PolicyFile = {
    version: "0.1",
    default_verdict: "approve",
    rules: [],
    sensitive_data: [],
  };
  return evaluate(intent, policy, NOW);
}

// ── Tests ────────────────────────────────────────────────────────────

describe("openWitnessLog", () => {
  it("creates witness.jsonl if it does not exist", async () => {
    const path = tmpWitnessPath();
    const log = await openWitnessLog(path);
    assert.equal(log.getSequence(), 0);
    assert.equal(log.getLatest(), null);
  });

  it("opens existing file and rebuilds in-memory index", async () => {
    const path = tmpWitnessPath();

    // Write some records
    const log1 = await openWitnessLog(path);
    const intent = sampleIntent();
    const verdict = sampleVerdict(intent);
    await log1.append(intent, verdict, "executed");

    // Reopen and verify
    const log2 = await openWitnessLog(path);
    assert.equal(log2.getSequence(), 1);
    const latest = log2.getLatest();
    assert.ok(latest !== null);
    assert.equal(latest!.intent.id, intent.id);
  });

  it("recovers from trailing garbage", async () => {
    const path = tmpWitnessPath();

    // Write a valid record then append garbage
    const log1 = await openWitnessLog(path);
    const intent = sampleIntent();
    const verdict = sampleVerdict(intent);
    await log1.append(intent, verdict, "executed");

    // Append garbage
    const content = readFileSync(path, "utf8");
    writeFileSync(path, content + '{"broken json\n', "utf8");

    // Should recover
    const log2 = await openWitnessLog(path);
    assert.equal(log2.getSequence(), 1);
  });
});

describe("append", () => {
  it("writes valid JSONL line", async () => {
    const path = tmpWitnessPath();
    const log = await openWitnessLog(path);
    const intent = sampleIntent();
    const verdict = sampleVerdict(intent);

    await log.append(intent, verdict, "executed");

    const content = readFileSync(path, "utf8").trim();
    const record = JSON.parse(content);
    assert.equal(record.sequence, 0);
    assert.equal(record.intent.id, intent.id);
  });

  it("increments sequence number", async () => {
    const path = tmpWitnessPath();
    const log = await openWitnessLog(path);

    for (let i = 0; i < 3; i++) {
      const intent = sampleIntent();
      const verdict = sampleVerdict(intent);
      const record = await log.append(intent, verdict, "executed");
      assert.equal(record.sequence, i);
    }
    assert.equal(log.getSequence(), 3);
  });

  it("sets genesis prev_hash correctly", async () => {
    const path = tmpWitnessPath();
    const log = await openWitnessLog(path);
    const intent = sampleIntent();
    const verdict = sampleVerdict(intent);

    const record = await log.append(intent, verdict, "executed");
    assert.equal(record.prev_hash, GENESIS_HASH);
  });

  it("chains prev_hash to previous record_hash", async () => {
    const path = tmpWitnessPath();
    const log = await openWitnessLog(path);

    const intent1 = sampleIntent();
    const verdict1 = sampleVerdict(intent1);
    const record1 = await log.append(intent1, verdict1, "executed");

    const intent2 = sampleIntent();
    const verdict2 = sampleVerdict(intent2);
    const record2 = await log.append(intent2, verdict2, "blocked");

    assert.equal(record2.prev_hash, record1.record_hash);
  });

  it("computes record_hash correctly", async () => {
    const path = tmpWitnessPath();
    const log = await openWitnessLog(path);
    const intent = sampleIntent();
    const verdict = sampleVerdict(intent);

    const record = await log.append(intent, verdict, "executed");

    const expected = computeRecordHash(
      record.sequence,
      record.intent.intent_hash,
      record.verdict.verdict_hash,
      record.execution_result,
      record.prev_hash,
    );
    assert.equal(record.record_hash, expected);
  });
});

describe("verifyChain", () => {
  it("verifies valid chain returns { valid: true }", async () => {
    const path = tmpWitnessPath();
    const log = await openWitnessLog(path);

    for (let i = 0; i < 5; i++) {
      const intent = sampleIntent();
      const verdict = sampleVerdict(intent);
      await log.append(intent, verdict, "executed");
    }

    const result = log.verifyChain();
    assert.equal(result.valid, true);
  });

  it("handles empty log as valid", async () => {
    const path = tmpWitnessPath();
    const log = await openWitnessLog(path);
    const result = log.verifyChain();
    assert.equal(result.valid, true);
  });

  // T-010: Tampered record detection
  it("detects tampered record", async () => {
    const path = tmpWitnessPath();
    const log = await openWitnessLog(path);

    for (let i = 0; i < 3; i++) {
      const intent = sampleIntent();
      const verdict = sampleVerdict(intent);
      await log.append(intent, verdict, "executed");
    }

    // Tamper with the file: modify a record's hash
    const content = readFileSync(path, "utf8");
    const lines = content.trim().split("\n");
    const record1 = JSON.parse(lines[1]!);
    record1.record_hash = "0".repeat(64);
    lines[1] = JSON.stringify(record1);
    writeFileSync(path, lines.join("\n") + "\n", "utf8");

    // Reopen and verify
    const log2 = await openWitnessLog(path);
    const result = log2.verifyChain();
    assert.equal(result.valid, false);
    assert.equal(result.brokenAt, 1);
  });
});

describe("getLast", () => {
  it("returns last N records in order", async () => {
    const path = tmpWitnessPath();
    const log = await openWitnessLog(path);

    for (let i = 0; i < 5; i++) {
      const intent = sampleIntent();
      const verdict = sampleVerdict(intent);
      await log.append(intent, verdict, "executed");
    }

    const last3 = log.getLast(3);
    assert.equal(last3.length, 3);
    assert.equal(last3[0]!.sequence, 2);
    assert.equal(last3[1]!.sequence, 3);
    assert.equal(last3[2]!.sequence, 4);
  });

  it("returns all records if N > total", async () => {
    const path = tmpWitnessPath();
    const log = await openWitnessLog(path);

    const intent = sampleIntent();
    const verdict = sampleVerdict(intent);
    await log.append(intent, verdict, "executed");

    const all = log.getLast(100);
    assert.equal(all.length, 1);
  });
});

describe("getByIntentId", () => {
  it("finds record by intent id", async () => {
    const path = tmpWitnessPath();
    const log = await openWitnessLog(path);

    const intent = sampleIntent();
    const verdict = sampleVerdict(intent);
    await log.append(intent, verdict, "executed");

    const found = log.getByIntentId(intent.id);
    assert.ok(found !== null);
    assert.equal(found!.intent.id, intent.id);
  });

  it("returns null for unknown id", async () => {
    const path = tmpWitnessPath();
    const log = await openWitnessLog(path);

    const found = log.getByIntentId("nonexistent");
    assert.equal(found, null);
  });
});
