import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  createIntent,
  canonicalize,
  computeHash,
  computeIntentHash,
  validateIntent,
} from "../scripts/intent.js";
import type { CreateIntentParams } from "../scripts/intent.js";

const SAMPLE_PARAMS: CreateIntentParams = {
  skill: "browser-automation",
  tool: "fetch",
  model: "claude-opus-4-20250514",
  actionType: "network",
  target: "https://api.example.com/data",
  parameters: { method: "GET" },
  dataScope: ["personal"],
  conversationId: "conv-123",
  messageId: "msg-456",
  userInstruction: "Fetch the user data from the API",
};

describe("canonicalize", () => {
  it("sorts object keys alphabetically at all levels", () => {
    const result = canonicalize({ z: 1, a: 2, m: { z: 3, a: 4 } });
    assert.equal(result, '{"a":2,"m":{"a":4,"z":3},"z":1}');
  });

  it("produces minified JSON (no whitespace)", () => {
    const result = canonicalize({ key: "value", arr: [1, 2, 3] });
    assert.ok(!result.includes(" "));
    assert.ok(!result.includes("\n"));
  });

  it("handles nested objects and arrays", () => {
    const result = canonicalize({ a: [{ c: 1, b: 2 }] });
    assert.equal(result, '{"a":[{"b":2,"c":1}]}');
  });

  it("is idempotent", () => {
    const obj = { z: 1, a: { y: 2, b: [3, 4] } };
    assert.equal(canonicalize(obj), canonicalize(obj));
  });

  it("handles null and primitives", () => {
    assert.equal(canonicalize(null), "null");
    assert.equal(canonicalize("hello"), '"hello"');
    assert.equal(canonicalize(42), "42");
    assert.equal(canonicalize(true), "true");
  });
});

describe("computeHash", () => {
  it("produces a 64-character hex string (SHA-256)", () => {
    const hash = computeHash("test data");
    assert.equal(hash.length, 64);
    assert.match(hash, /^[0-9a-f]{64}$/);
  });

  it("is deterministic", () => {
    assert.equal(computeHash("same input"), computeHash("same input"));
  });

  it("changes with different input", () => {
    assert.notEqual(computeHash("input1"), computeHash("input2"));
  });
});

describe("createIntent", () => {
  it("generates a valid UUID v4 id", () => {
    const intent = createIntent(SAMPLE_PARAMS);
    assert.match(intent.id, /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/);
  });

  it("generates ISO 8601 timestamp", () => {
    const intent = createIntent(SAMPLE_PARAMS);
    const parsed = new Date(intent.timestamp);
    assert.ok(!isNaN(parsed.getTime()), "Timestamp should be valid ISO 8601");
    assert.ok(intent.timestamp.includes("T"), "Should contain T separator");
  });

  it("computes SHA-256 intent_hash from canonical serialization", () => {
    const intent = createIntent(SAMPLE_PARAMS);
    assert.match(intent.intent_hash, /^[0-9a-f]{64}$/);

    // Verify the hash matches recomputation
    const { intent_hash: _hash, ...rest } = intent;
    const recomputed = computeIntentHash(rest);
    assert.equal(intent.intent_hash, recomputed);
  });

  it("produces different hashes for different inputs", () => {
    const intent1 = createIntent(SAMPLE_PARAMS);
    const intent2 = createIntent({ ...SAMPLE_PARAMS, target: "https://other.com" });
    assert.notEqual(intent1.intent_hash, intent2.intent_hash);
  });

  it("maps all fields correctly", () => {
    const intent = createIntent(SAMPLE_PARAMS);
    assert.equal(intent.source.skill, "browser-automation");
    assert.equal(intent.source.tool, "fetch");
    assert.equal(intent.source.model, "claude-opus-4-20250514");
    assert.equal(intent.action.type, "network");
    assert.equal(intent.action.target, "https://api.example.com/data");
    assert.deepEqual(intent.action.parameters, { method: "GET" });
    assert.deepEqual(intent.action.data_scope, ["personal"]);
    assert.equal(intent.context.conversation_id, "conv-123");
    assert.equal(intent.context.message_id, "msg-456");
    assert.equal(intent.context.user_instruction, "Fetch the user data from the API");
  });
});

describe("validateIntent", () => {
  it("accepts valid ActionIntent", () => {
    const intent = createIntent(SAMPLE_PARAMS);
    const result = validateIntent(intent);
    assert.equal(result.valid, true);
  });

  it("rejects null input", () => {
    const result = validateIntent(null);
    assert.equal(result.valid, false);
  });

  it("rejects missing required fields", () => {
    const result = validateIntent({ id: "test" });
    assert.equal(result.valid, false);
    if (!result.valid) {
      assert.ok(result.errors.length > 0);
    }
  });

  it("rejects invalid action_type", () => {
    const intent = createIntent(SAMPLE_PARAMS);
    const modified = { ...intent, action: { ...intent.action, type: "invalid" } };
    const result = validateIntent(modified);
    assert.equal(result.valid, false);
  });

  it("rejects non-string target", () => {
    const intent = createIntent(SAMPLE_PARAMS);
    const modified = { ...intent, action: { ...intent.action, target: 42 } };
    const result = validateIntent(modified);
    assert.equal(result.valid, false);
  });

  it("rejects tampered intent_hash", () => {
    const intent = createIntent(SAMPLE_PARAMS);
    const tampered = { ...intent, intent_hash: "0".repeat(64) };
    const result = validateIntent(tampered);
    assert.equal(result.valid, false);
    if (!result.valid) {
      assert.ok(result.errors.some((e) => e.field === "intent_hash"));
    }
  });

  it("rejects missing source object", () => {
    const result = validateIntent({
      id: "test",
      timestamp: new Date().toISOString(),
      action: { type: "read", target: ".", parameters: {}, data_scope: [] },
      context: { conversation_id: "c", message_id: "m", user_instruction: "u" },
      intent_hash: "abc",
    });
    assert.equal(result.valid, false);
  });
});
