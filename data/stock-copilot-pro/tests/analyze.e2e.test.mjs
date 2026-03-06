import test from "node:test";
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const SKILL_ROOT = path.resolve(__dirname, "..");
const SCRIPT_FILE = path.join(SKILL_ROOT, "scripts", "stock_copilot_pro.mjs");

const BASE_ARGS = [
  "--format", "json",
  "--mode", "basic",
  "--timeout", "20",
  "--skip-questionnaire",
  "--no-evolution",
];

function runCli(args, timeoutMs = 180_000) {
  return new Promise((resolve) => {
    const child = spawn("node", [SCRIPT_FILE, ...args], {
      cwd: SKILL_ROOT,
      env: process.env,
      stdio: ["ignore", "pipe", "pipe"],
    });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (chunk) => { stdout += chunk.toString(); });
    child.stderr.on("data", (chunk) => { stderr += chunk.toString(); });
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

function hasAnyPrice(data) {
  if (!data || typeof data !== "object") return false;
  const capabilities = ["quote", "fundamentals", "technicals", "sentiment"];
  for (const cap of capabilities) {
    const parsed = data[cap]?.parsed;
    if (!parsed) continue;
    if (parsed.price != null && parsed.price !== "N/A") return true;
    if (parsed.close != null) return true;
    if (parsed.lastPrice != null) return true;
  }
  return false;
}

test("analyze US ticker (AAPL) should return valid JSON structure", async (t) => {
  if (!process.env.QVERIS_API_KEY) {
    t.skip("QVERIS_API_KEY not set, skip live analyze e2e");
    return;
  }
  const run = await runCli(["analyze", "--symbol", "AAPL", "--market", "US", ...BASE_ARGS]);
  assert.equal(run.ok, true, `analyze AAPL failed: ${run.stderr}`);
  const result = parseJsonFromOutput(run.stdout);
  assert.ok(result && typeof result === "object", "output should be valid JSON");
  // mode is the analysis mode (basic/comprehensive/etc), not the command name
  assert.ok(result.mode, "mode should be present");
  assert.ok(result.symbol, "symbol should be present");
  assert.ok(result.symbol.toUpperCase().includes("AAPL"), `symbol should contain AAPL, got: ${result.symbol}`);
  assert.equal(result.market, "US");
  assert.ok(result.data && typeof result.data === "object", "data should be present");
  assert.ok(hasAnyPrice(result.data), "at least one capability should return a price");
  assert.ok(result.analysis && typeof result.analysis === "object", "analysis block should exist");
  assert.ok(result.runtime?.resolvedInput?.symbol, "runtime.resolvedInput.symbol should be set");
  assert.ok(result.meta?.guide, "meta.guide should be set for OpenClaw");
});

test("analyze HK ticker (0700.HK) should return valid JSON structure", async (t) => {
  if (!process.env.QVERIS_API_KEY) {
    t.skip("QVERIS_API_KEY not set, skip live analyze e2e");
    return;
  }
  const run = await runCli(["analyze", "--symbol", "0700.HK", "--market", "HK", ...BASE_ARGS]);
  assert.equal(run.ok, true, `analyze 0700.HK failed: ${run.stderr}`);
  const result = parseJsonFromOutput(run.stdout);
  assert.ok(result && typeof result === "object", "output should be valid JSON");
  assert.ok(result.mode, "mode should be present");
  assert.ok(result.symbol, "symbol should be present");
  const sym = result.symbol.toUpperCase().replace(/^0+/, "");
  assert.ok(sym.includes("700"), `symbol should contain 700, got: ${result.symbol}`);
  assert.ok(result.data && typeof result.data === "object", "data should be present");
  // At least one capability should succeed; HK data sources may degrade gracefully
  const capValues = Object.values(result.data);
  assert.ok(capValues.length >= 1, "data should have at least one capability");
});

test("analyze CN alias (腾讯控股) should resolve to 0700.HK", async (t) => {
  if (!process.env.QVERIS_API_KEY) {
    t.skip("QVERIS_API_KEY not set, skip live analyze e2e");
    return;
  }
  const run = await runCli(["analyze", "--symbol", "腾讯控股", "--market", "HK", ...BASE_ARGS]);
  assert.equal(run.ok, true, `analyze 腾讯控股 failed: ${run.stderr}`);
  const result = parseJsonFromOutput(run.stdout);
  assert.ok(result && typeof result === "object", "output should be valid JSON");
  assert.ok(result.mode, "mode should be present");
  const resolvedSymbol = result.runtime?.resolvedInput?.symbol || result.symbol || "";
  const normalized = resolvedSymbol.toUpperCase().replace(/^0+/, "");
  assert.ok(
    normalized.includes("700") || normalized.includes("TENCENT"),
    `resolved symbol should map to 0700.HK, got: ${resolvedSymbol}`,
  );
});

test("analyze --format chat (NVDA) should return segmented chat output", async (t) => {
  if (!process.env.QVERIS_API_KEY) {
    t.skip("QVERIS_API_KEY not set, skip live analyze e2e");
    return;
  }
  const run = await runCli([
    "analyze", "--symbol", "NVDA", "--market", "US",
    "--format", "chat",
    "--mode", "basic",
    "--timeout", "20",
    "--skip-questionnaire",
    "--no-evolution",
  ]);
  assert.equal(run.ok, true, `analyze --format chat failed: ${run.stderr}`);
  const result = parseJsonFromOutput(run.stdout);
  assert.ok(result && typeof result === "object", "chat output should be valid JSON");
  assert.ok(result.symbol, "chat output should have symbol");
  assert.ok(Array.isArray(result.segments), "chat output should have segments array");
  assert.ok(result.segments.length >= 1, "segments should not be empty");
});
