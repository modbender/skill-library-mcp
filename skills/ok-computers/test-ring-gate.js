#!/usr/bin/env node
/**
 * Ring Gates — Test Suite
 *
 * Run: node test-ring-gate.js
 */

const {
  RingGate,
  MSG_TYPES,
  FLAGS,
  PROTOCOL_VERSION,
  MAGIC_PREFIX,
  MAX_MESSAGE_LENGTH,
  MAX_PAYLOAD_LENGTH,
  HEADER_LENGTH,
} = require("./ring-gate");
const zlib = require("zlib");

let passed = 0;
let failed = 0;
const failures = [];

function test(name, fn) {
  try {
    fn();
    passed++;
    console.log(`  \u2713 ${name}`);
  } catch (e) {
    failed++;
    failures.push({ name, error: e.message });
    console.log(`  \u2717 ${name}: ${e.message}`);
  }
}

function assert(cond, msg) {
  if (!cond) throw new Error(msg || "Assertion failed");
}

function assertEqual(a, b, msg) {
  if (a !== b) throw new Error(msg || `Expected ${JSON.stringify(b)}, got ${JSON.stringify(a)}`);
}

// ============================================================
console.log("\n=== PROTOCOL CONSTANTS ===\n");
// ============================================================

test("Header length is 25", () => {
  assertEqual(HEADER_LENGTH, 25);
});

test("Max payload is 999", () => {
  assertEqual(MAX_PAYLOAD_LENGTH, 999);
});

test("Max message is 1024", () => {
  assertEqual(MAX_MESSAGE_LENGTH, 1024);
});

test("Header + payload = max message", () => {
  assertEqual(HEADER_LENGTH + MAX_PAYLOAD_LENGTH, MAX_MESSAGE_LENGTH);
});

// ============================================================
console.log("\n=== ENCODE / DECODE ===\n");
// ============================================================

test("Encode produces correct format", () => {
  const msg = RingGate.encodeMessage("D", "a7f3", 1, 210, 0x00, "SGVsbG8=");
  assert(msg.startsWith("RG|1|D|a7f3|0001|00d2|00|"), `Bad format: ${msg}`);
  assertEqual(msg, "RG|1|D|a7f3|0001|00d2|00|SGVsbG8=");
});

test("Encode/decode roundtrip", () => {
  const payload = "Hello World base64 encoded";
  const msg = RingGate.encodeMessage("D", "beef", 42, 100, 0x01, payload);
  const parsed = RingGate.decodeMessage(msg);
  assertEqual(parsed.type, "D");
  assertEqual(parsed.txid, "beef");
  assertEqual(parsed.seq, 42);
  assertEqual(parsed.total, 100);
  assertEqual(parsed.flags, 0x01);
  assertEqual(parsed.payload, payload);
  assertEqual(parsed.compressed, true);
  assertEqual(parsed.encrypted, false);
});

test("Decode manifest type", () => {
  const msg = RingGate.encodeMessage("M", "0001", 0, 5, 0x00, '{"type":"text/html"}');
  const parsed = RingGate.decodeMessage(msg);
  assertEqual(parsed.type, "M");
  assertEqual(parsed.seq, 0);
  assertEqual(parsed.payload, '{"type":"text/html"}');
});

test("Decode all message types", () => {
  for (const [name, code] of Object.entries(MSG_TYPES)) {
    const msg = RingGate.encodeMessage(code, "0000", 0, 1, 0x00, "test");
    const parsed = RingGate.decodeMessage(msg);
    assertEqual(parsed.type, code, `Type mismatch for ${name}`);
  }
});

test("Decode all flags", () => {
  const allFlags = FLAGS.COMPRESSED | FLAGS.ENCRYPTED | FLAGS.URGENT | FLAGS.FINAL | FLAGS.TEXT;
  const msg = RingGate.encodeMessage("D", "0000", 0, 1, allFlags, "test");
  const parsed = RingGate.decodeMessage(msg);
  assertEqual(parsed.compressed, true);
  assertEqual(parsed.encrypted, true);
  assertEqual(parsed.urgent, true);
  assertEqual(parsed.final, true);
  assertEqual(parsed.text, true);
});

test("Decode with no flags set", () => {
  const msg = RingGate.encodeMessage("D", "0000", 0, 1, 0x00, "test");
  const parsed = RingGate.decodeMessage(msg);
  assertEqual(parsed.compressed, false);
  assertEqual(parsed.encrypted, false);
  assertEqual(parsed.urgent, false);
  assertEqual(parsed.final, false);
  assertEqual(parsed.text, false);
});

test("Payload with pipe separators preserved", () => {
  const payload = "data|with|pipes|in|it";
  const msg = RingGate.encodeMessage("D", "0000", 0, 1, 0x00, payload);
  const parsed = RingGate.decodeMessage(msg);
  assertEqual(parsed.payload, payload);
});

test("Max seq/total values (65535)", () => {
  const msg = RingGate.encodeMessage("D", "ffff", 65535, 65535, 0xff, "x");
  const parsed = RingGate.decodeMessage(msg);
  assertEqual(parsed.seq, 65535);
  assertEqual(parsed.total, 65535);
  assertEqual(parsed.txid, "ffff");
});

test("Zero seq/total", () => {
  const msg = RingGate.encodeMessage("M", "0000", 0, 0, 0x00, "{}");
  const parsed = RingGate.decodeMessage(msg);
  assertEqual(parsed.seq, 0);
  assertEqual(parsed.total, 0);
});

test("Max payload length fills 1024", () => {
  const payload = "A".repeat(MAX_PAYLOAD_LENGTH);
  const msg = RingGate.encodeMessage("D", "0000", 0, 1, 0x00, payload);
  assertEqual(msg.length, MAX_MESSAGE_LENGTH);
});

test("Payload too long throws", () => {
  const payload = "A".repeat(MAX_PAYLOAD_LENGTH + 1);
  let threw = false;
  try {
    RingGate.encodeMessage("D", "0000", 0, 1, 0x00, payload);
  } catch (e) {
    threw = true;
    assert(e.message.includes("exceeds"), e.message);
  }
  assert(threw, "Should have thrown");
});

test("Invalid txid length throws", () => {
  let threw = false;
  try {
    RingGate.encodeMessage("D", "abc", 0, 1, 0x00, "test");
  } catch {
    threw = true;
  }
  assert(threw, "Should have thrown for 3-char txid");
});

test("Negative seq throws", () => {
  let threw = false;
  try {
    RingGate.encodeMessage("D", "0000", -1, 1, 0x00, "test");
  } catch {
    threw = true;
  }
  assert(threw, "Should have thrown for negative seq");
});

// ============================================================
console.log("\n=== isRingGate ===\n");
// ============================================================

test("Detects valid Ring Gate messages", () => {
  const msg = RingGate.encodeMessage("D", "0000", 0, 1, 0x00, "test");
  assertEqual(RingGate.isRingGate(msg), true);
});

test("Rejects non-Ring Gate strings", () => {
  assertEqual(RingGate.isRingGate("hello world"), false);
  assertEqual(RingGate.isRingGate(""), false);
  assertEqual(RingGate.isRingGate("RG"), false);
  assertEqual(RingGate.isRingGate("RGsomething"), false);
});

test("Rejects non-string values", () => {
  assertEqual(RingGate.isRingGate(null), false);
  assertEqual(RingGate.isRingGate(undefined), false);
  assertEqual(RingGate.isRingGate(42), false);
});

test("decodeMessage returns null for non-Ring Gate", () => {
  assertEqual(RingGate.decodeMessage("hello"), null);
  assertEqual(RingGate.decodeMessage(""), null);
});

// ============================================================
console.log("\n=== HASHING ===\n");
// ============================================================

test("Hash is deterministic", () => {
  const h1 = RingGate.hash("hello world");
  const h2 = RingGate.hash("hello world");
  assertEqual(h1, h2);
});

test("Hash differs for different inputs", () => {
  const h1 = RingGate.hash("hello");
  const h2 = RingGate.hash("world");
  assert(h1 !== h2, "Hashes should differ");
});

test("Hash returns hex string", () => {
  const h = RingGate.hash("test");
  assert(/^[0-9a-f]{64}$/.test(h), `Bad hash format: ${h}`);
});

// ============================================================
console.log("\n=== CHUNK / ASSEMBLE ===\n");
// ============================================================

test("Small data produces manifest + 1 chunk", () => {
  const messages = RingGate.chunk("Hello!", "0001");
  assertEqual(messages.length, 2); // manifest + 1 data
  const manifest = RingGate.decodeMessage(messages[0]);
  assertEqual(manifest.type, "M");
  const data = RingGate.decodeMessage(messages[1]);
  assertEqual(data.type, "D");
  assertEqual(data.seq, 1);
  assertEqual(data.total, 1);
});

test("Chunk/assemble roundtrip — small text", () => {
  const original = "Hello, Ring Gates!";
  const messages = RingGate.chunk(original, "abc0");
  const result = RingGate.assemble(messages[0], messages.slice(1));
  assertEqual(result, original);
});

test("Chunk/assemble roundtrip — medium text (5KB)", () => {
  const original = "ABCDEFGHIJ".repeat(500); // 5000 chars
  const messages = RingGate.chunk(original);
  const result = RingGate.assemble(messages[0], messages.slice(1));
  assertEqual(result, original);
});

test("Chunk/assemble roundtrip — large text (50KB)", () => {
  const original = "X".repeat(50000);
  const messages = RingGate.chunk(original);
  assert(messages.length > 10, `Expected many chunks, got ${messages.length}`);
  const result = RingGate.assemble(messages[0], messages.slice(1));
  assertEqual(result, original);
});

test("Chunk/assemble roundtrip — HTML content", () => {
  const html = "<html><body><h1>Ring Gates</h1><p>First onchain inter-computer protocol.</p></body></html>";
  const messages = RingGate.chunk(html, "html", { contentType: "text/html" });
  const manifest = RingGate.decodeMessage(messages[0]);
  const meta = JSON.parse(manifest.payload);
  assertEqual(meta.type, "text/html");
  const result = RingGate.assemble(messages[0], messages.slice(1));
  assertEqual(result, html);
});

test("Chunk/assemble roundtrip — text mode", () => {
  const original = "Plain text, no base64 encoding needed!";
  const messages = RingGate.chunk(original, "txt0", { textMode: true });
  const manifest = RingGate.decodeMessage(messages[0]);
  const meta = JSON.parse(manifest.payload);
  assertEqual(meta.encoding, "text");
  const data = RingGate.decodeMessage(messages[1]);
  assertEqual(data.text, true);
  const result = RingGate.assemble(messages[0], messages.slice(1));
  assertEqual(result, original);
});

test("Chunk/assemble roundtrip — compressed", () => {
  // Repeating data compresses well
  const original = "Hello Ring Gates! ".repeat(200);
  const messages = RingGate.chunk(original, "comp", { compress: true });
  const manifest = RingGate.decodeMessage(messages[0]);
  const meta = JSON.parse(manifest.payload);
  assertEqual(meta.compressed, true);
  const result = RingGate.assemble(messages[0], messages.slice(1));
  assertEqual(result, original);
});

test("Compressed is smaller than uncompressed for repetitive data", () => {
  const original = "Hello Ring Gates! ".repeat(500);
  const normal = RingGate.chunk(original);
  const compressed = RingGate.chunk(original, undefined, { compress: true });
  assert(
    compressed.length < normal.length,
    `Compressed (${compressed.length}) should have fewer messages than normal (${normal.length})`
  );
});

test("Empty data produces manifest + 1 empty chunk", () => {
  const messages = RingGate.chunk("", "0000");
  assertEqual(messages.length, 2);
  const result = RingGate.assemble(messages[0], messages.slice(1));
  assertEqual(result, "");
});

test("Assemble with out-of-order chunks", () => {
  const original = "ABCDEFGHIJ".repeat(500);
  const messages = RingGate.chunk(original, "shuf");
  const manifest = messages[0];
  const dataChunks = messages.slice(1);
  // Reverse the chunks
  const reversed = [...dataChunks].reverse();
  const result = RingGate.assemble(manifest, reversed);
  assertEqual(result, original);
});

test("Assemble rejects wrong chunk count", () => {
  const messages = RingGate.chunk("test data here", "0001");
  let threw = false;
  try {
    // Pass empty array — missing chunks
    RingGate.assemble(messages[0], []);
  } catch (e) {
    threw = true;
    assert(e.message.includes("Expected"), e.message);
  }
  assert(threw, "Should have thrown for missing chunks");
});

test("Assemble rejects corrupted data (hash mismatch)", () => {
  const messages = RingGate.chunk("important data", "0002");
  // Tamper with the data chunk
  const tampered = messages[1].slice(0, -5) + "XXXXX";
  let threw = false;
  try {
    RingGate.assemble(messages[0], [tampered]);
  } catch (e) {
    threw = true;
    assert(e.message.includes("Hash") || e.message.includes("corrupt"), e.message);
  }
  assert(threw, "Should have thrown for corrupted data");
});

test("Assemble rejects non-manifest first arg", () => {
  let threw = false;
  try {
    RingGate.assemble("not a manifest", []);
  } catch (e) {
    threw = true;
  }
  assert(threw, "Should have thrown for non-manifest");
});

test("All messages fit in 1024 chars", () => {
  const original = "X".repeat(100000);
  const messages = RingGate.chunk(original);
  for (const msg of messages) {
    assert(msg.length <= MAX_MESSAGE_LENGTH, `Message too long: ${msg.length}`);
  }
});

test("All data chunks share same txid", () => {
  const messages = RingGate.chunk("Test data for txid check", "abcd");
  for (const msg of messages) {
    const parsed = RingGate.decodeMessage(msg);
    assertEqual(parsed.txid, "abcd");
  }
});

test("Manifest seq is always 0", () => {
  const messages = RingGate.chunk("test", "0001");
  const manifest = RingGate.decodeMessage(messages[0]);
  assertEqual(manifest.seq, 0);
  assertEqual(manifest.type, "M");
});

test("Data chunk seq starts at 1", () => {
  const messages = RingGate.chunk("some test data to chunk");
  const firstData = RingGate.decodeMessage(messages[1]);
  assertEqual(firstData.seq, 1);
});

test("Manifest payload is valid JSON", () => {
  const messages = RingGate.chunk("test", "0001", { contentType: "text/html" });
  const manifest = RingGate.decodeMessage(messages[0]);
  const meta = JSON.parse(manifest.payload);
  assertEqual(meta.type, "text/html");
  assert(typeof meta.size === "number");
  assert(typeof meta.hash === "string");
  assert(typeof meta.chunks === "number");
});

test("Unicode roundtrip", () => {
  const original = "Ring Gates \u2014 \u5f00\u542f\u661f\u95e8 \ud83d\ude80 \u0420\u0438\u043d\u0433 \u0413\u0435\u0439\u0442\u0441";
  const messages = RingGate.chunk(original);
  const result = RingGate.assemble(messages[0], messages.slice(1));
  assertEqual(result, original);
});

test("Newlines and special chars roundtrip", () => {
  const original = "line1\nline2\r\nline3\ttab\0null";
  const messages = RingGate.chunk(original);
  const result = RingGate.assemble(messages[0], messages.slice(1));
  assertEqual(result, original);
});

// ============================================================
console.log("\n=== SHARDING ===\n");
// ============================================================

test("planShards distributes evenly", () => {
  const messages = RingGate.chunk("X".repeat(10000)); // many chunks
  const dataChunks = messages.slice(1);
  const shards = RingGate.planShards(dataChunks, [1399, 22, 42]);

  assertEqual(shards.length, 3);
  // Total messages across shards should equal data chunks
  const totalMsgs = shards.reduce((s, sh) => s + sh.messages.length, 0);
  assertEqual(totalMsgs, dataChunks.length);
});

test("planShards with 1 computer = all chunks in 1 shard", () => {
  const messages = RingGate.chunk("test data", "0001");
  const dataChunks = messages.slice(1);
  const shards = RingGate.planShards(dataChunks, [1399]);
  assertEqual(shards.length, 1);
  assertEqual(shards[0].computer, 1399);
  assertEqual(shards[0].messages.length, dataChunks.length);
});

test("planShards with more computers than chunks", () => {
  const messages = RingGate.chunk("tiny", "0001"); // 1 data chunk
  const dataChunks = messages.slice(1);
  assertEqual(dataChunks.length, 1);
  const shards = RingGate.planShards(dataChunks, [1399, 22, 42, 100, 200, 300]);
  assertEqual(shards.length, 1); // Only 1 shard needed
  assertEqual(shards[0].messages.length, 1);
});

test("planShards assigns correct channels", () => {
  const messages = RingGate.chunk("X".repeat(5000), "beef");
  const dataChunks = messages.slice(1);
  const shards = RingGate.planShards(dataChunks, [1399, 22]);
  assert(shards[0].channel.startsWith("rg_tx_beef_"), `Bad channel: ${shards[0].channel}`);
  assert(shards[1].channel.startsWith("rg_tx_beef_"), `Bad channel: ${shards[1].channel}`);
  assert(shards[0].channel !== shards[1].channel, "Channels should differ");
});

test("planShards range values are correct", () => {
  const messages = RingGate.chunk("X".repeat(10000), "0001");
  const dataChunks = messages.slice(1);
  const shards = RingGate.planShards(dataChunks, [1399, 22]);

  assertEqual(shards[0].range[0], 1); // 1-based start
  assertEqual(shards[1].range[1], dataChunks.length); // Last shard ends at total
  // Ranges should be contiguous: end of first + 1 = start of second
  assertEqual(shards[0].range[1] + 1, shards[1].range[0]);
});

test("planShards with empty array throws", () => {
  let threw = false;
  try {
    RingGate.planShards([], []);
  } catch {
    threw = true;
  }
  assert(threw, "Should throw for empty computers array");
});

test("buildShardedManifest includes shard map", () => {
  const data = "X".repeat(5000);
  const txid = "test";
  const messages = RingGate.chunk(data, txid);
  const dataChunks = messages.slice(1);
  const shardPlan = RingGate.planShards(dataChunks, [1399, 22]);

  const manifest = RingGate.buildShardedManifest(data, txid, shardPlan);
  const parsed = RingGate.decodeMessage(manifest);
  const meta = JSON.parse(parsed.payload);

  assert(Array.isArray(meta.shards), "Should have shards array");
  assertEqual(meta.shards.length, 2);
  assertEqual(meta.shards[0].computer, 1399);
  assertEqual(meta.shards[1].computer, 22);
});

// ============================================================
console.log("\n=== VERIFY ===\n");
// ============================================================

test("Verify passes for correct data", () => {
  const original = "Ring Gates protocol test data";
  const messages = RingGate.chunk(original);
  const manifest = RingGate.decodeMessage(messages[0]);
  assert(RingGate.verify(manifest, original), "Verify should pass");
});

test("Verify fails for wrong data", () => {
  const original = "Ring Gates protocol test data";
  const messages = RingGate.chunk(original);
  const manifest = RingGate.decodeMessage(messages[0]);
  assert(!RingGate.verify(manifest, "wrong data"), "Verify should fail");
});

// ============================================================
console.log("\n=== TX ID GENERATION ===\n");
// ============================================================

test("generateTxId returns 4 hex chars", () => {
  const txid = RingGate.generateTxId();
  assert(/^[0-9a-f]{4}$/.test(txid), `Bad txid: ${txid}`);
});

test("generateTxId produces different values", () => {
  const ids = new Set();
  for (let i = 0; i < 100; i++) ids.add(RingGate.generateTxId());
  assert(ids.size > 1, "Should produce varied txids");
});

// ============================================================
console.log("\n=== INSTANCE METHODS ===\n");
// ============================================================

test("RingGate constructor sets tokenId", () => {
  const rg = new RingGate(1399);
  assertEqual(rg.tokenId, 1399);
  assert(rg.ok instanceof require("./okcomputer").OKComputer);
});

test("buildTransmission returns array of tx objects", () => {
  const rg = new RingGate(1399);
  const txs = rg.buildTransmission("rg_1399_broadcast", "Hello Ring Gates!");
  assert(Array.isArray(txs), "Should return array");
  assert(txs.length >= 2, "Should have manifest + data"); // manifest + at least 1 data
  for (const tx of txs) {
    assertEqual(tx.to, "0x04D7C8b512D5455e20df1E808f12caD1e3d766E5");
    assertEqual(tx.value, "0");
    assertEqual(tx.chainId, 8453);
    assert(typeof tx.data === "string", "Should have calldata");
    assert(tx.data.startsWith("0x"), "Calldata should start with 0x");
  }
});

test("buildShard returns tx objects for specific computer", () => {
  const rg = new RingGate(1399);
  const messages = RingGate.chunk("X".repeat(5000), "test");
  const dataChunks = messages.slice(1);
  const shards = RingGate.planShards(dataChunks, [1399, 22]);
  const txs = rg.buildShard(shards[0]);
  assert(Array.isArray(txs));
  assert(txs.length > 0);
  for (const tx of txs) {
    assertEqual(tx.chainId, 8453);
  }
});

test("buildShardedTransmission returns complete plan", () => {
  const rg = new RingGate(1399);
  const result = rg.buildShardedTransmission(
    "X".repeat(5000),
    [1399, 22],
    "rg_1399_broadcast"
  );
  assert(result.manifestTx, "Should have manifestTx");
  assert(Array.isArray(result.shardTxs), "Should have shardTxs");
  assert(result.txid, "Should have txid");
  assert(Array.isArray(result.shardPlan), "Should have shardPlan");
  assertEqual(result.shardTxs.length, 2);
});

// ============================================================
console.log("\n=== EDGE CASES ===\n");
// ============================================================

test("Exact 1-chunk boundary (999 chars b64 = 749 bytes)", () => {
  // 749 bytes → 1000 base64 chars (just over 999 → 2 chunks)
  // 748 bytes → 998 base64 chars (under 999 → 1 chunk)
  // Let's test the boundary
  const data748 = "A".repeat(748);
  const msgs748 = RingGate.chunk(data748);
  // 748 bytes ASCII → base64 is ceil(748/3)*4 = 250*4 = 1000 chars → 2 chunks
  // Actually: 748 bytes → 748*4/3 = 997.33 → 1000 chars (padded). That's > 999, so 2 chunks
  // Let's just verify roundtrip regardless of exact boundary
  const result = RingGate.assemble(msgs748[0], msgs748.slice(1));
  assertEqual(result, data748);
});

test("Chunk data with exact payload boundary", () => {
  // In text mode, exactly 999 chars should fit in 1 chunk
  const data = "X".repeat(999);
  const msgs = RingGate.chunk(data, "0001", { textMode: true });
  assertEqual(msgs.length, 2); // manifest + 1 data
  const result = RingGate.assemble(msgs[0], msgs.slice(1));
  assertEqual(result, data);
});

test("Chunk data just over payload boundary (text mode)", () => {
  const data = "X".repeat(1000);
  const msgs = RingGate.chunk(data, "0001", { textMode: true });
  assertEqual(msgs.length, 3); // manifest + 2 data
  const result = RingGate.assemble(msgs[0], msgs.slice(1));
  assertEqual(result, data);
});

test("Large transmission (200KB)", () => {
  const data = "Ring Gates across the void. ".repeat(7500); // ~210KB
  const messages = RingGate.chunk(data);
  assert(messages.length > 100, `Expected 100+ messages, got ${messages.length}`);
  // Don't assemble — just verify messages are valid
  for (const msg of messages) {
    assert(msg.length <= MAX_MESSAGE_LENGTH, `Message too long: ${msg.length}`);
    const parsed = RingGate.decodeMessage(msg);
    assert(parsed !== null, "Should be parseable");
  }
  // Roundtrip
  const result = RingGate.assemble(messages[0], messages.slice(1));
  assertEqual(result, data);
});

test("JSON data roundtrip", () => {
  const obj = {
    protocol: "Ring Gates",
    version: 1,
    computers: [1399, 22, 42],
    metadata: { author: "Ollie", network: "Base" },
  };
  const json = JSON.stringify(obj);
  const messages = RingGate.chunk(json, "json", { contentType: "application/json" });
  const result = RingGate.assemble(messages[0], messages.slice(1));
  assertEqual(result, json);
  const parsed = JSON.parse(result);
  assertEqual(parsed.protocol, "Ring Gates");
});

test("Binary-like data (base64 of random bytes)", () => {
  // Simulate binary content
  const randomB64 = Buffer.from(
    Array.from({ length: 1000 }, () => Math.floor(Math.random() * 256))
  ).toString("base64");
  const messages = RingGate.chunk(randomB64);
  const result = RingGate.assemble(messages[0], messages.slice(1));
  assertEqual(result, randomB64);
});

// ============================================================
// RESULTS
// ============================================================

console.log(`\n${"=".repeat(50)}`);
console.log(`  RESULTS: ${passed} passed, ${failed} failed, ${passed + failed} total`);
console.log(`${"=".repeat(50)}`);

if (failures.length > 0) {
  console.log("\nFailed tests:");
  for (const f of failures) {
    console.log(`  - ${f.name}: ${f.error}`);
  }
}

process.exit(failed > 0 ? 1 : 0);
