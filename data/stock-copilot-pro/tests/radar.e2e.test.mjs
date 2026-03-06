import test from "node:test";
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const SKILL_ROOT = path.resolve(__dirname, "..");
const SCRIPT_FILE = path.join(SKILL_ROOT, "scripts", "stock_copilot_pro.mjs");

function runCli(args, timeoutMs = 120_000) {
  return new Promise((resolve) => {
    const child = spawn("node", [SCRIPT_FILE, ...args], {
      cwd: SKILL_ROOT,
      env: process.env,
      stdio: ["ignore", "pipe", "pipe"],
    });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });
    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });
    const timer = setTimeout(() => {
      child.kill("SIGTERM");
      resolve({ ok: false, code: -1, stdout, stderr: `${stderr}\nTIMEOUT` });
    }, timeoutMs);
    child.on("close", (code) => {
      clearTimeout(timer);
      resolve({ ok: code === 0, code, stdout, stderr });
    });
    child.on("error", (error) => {
      clearTimeout(timer);
      resolve({ ok: false, code: -1, stdout, stderr: error.message });
    });
  });
}

function parseJsonFromOutput(output) {
  const start = output.indexOf("{");
  const end = output.lastIndexOf("}");
  if (start === -1 || end === -1 || end < start) return null;
  try {
    return JSON.parse(output.slice(start, end + 1));
  } catch {
    return null;
  }
}

test("radar e2e should satisfy acceptance criteria", async (t) => {
  if (!process.env.QVERIS_API_KEY) {
    t.skip("QVERIS_API_KEY not set, skip live radar e2e");
    return;
  }
  const run = await runCli(
    ["radar", "--market", "GLOBAL", "--limit", "10", "--format", "json", "--timeout", "25", "--no-evolution"],
    180_000,
  );
  assert.equal(run.ok, true, `radar command failed: ${run.stderr}`);
  const result = parseJsonFromOutput(run.stdout);
  assert.ok(result && typeof result === "object", "radar output should be valid json");
  assert.equal(result.mode, "radar");
  assert.ok(result.topicCount >= 1, "topicCount should be >= 1");
  assert.ok(Array.isArray(result.topics) && result.topics.length >= 1, "topics should not be empty");
  // Verify topic structure contains required fields for OpenClaw analysis
  const firstTopic = result.topics[0];
  assert.ok(firstTopic.title, "topic should have title");
  assert.ok(firstTopic.source, "topic should have source");
  // category may be null when source doesn't provide classification, but the field must exist
  assert.ok("category" in firstTopic, "topic should have category field (may be null)");
  // sentiment and tickers may be null for some sources but keys must be present
  assert.ok("sentiment" in firstTopic, "topic should have sentiment field (may be null)");
  assert.ok("tickers" in firstTopic, "topic should have tickers field (may be null)");
  // Verify meta structure
  assert.ok(Array.isArray(result.meta?.sourceStats), "meta.sourceStats should exist");
  // At least one source must have been attempted
  assert.ok(result.meta.sourceStats.length >= 1, "should attempt at least one source");
  assert.ok(result.meta.note, "meta should contain note about OpenClaw analysis");
});
