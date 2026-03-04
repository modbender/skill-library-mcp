import test from "node:test";
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const SKILL_ROOT = path.resolve(__dirname, "..");
const SCRIPT_FILE = path.join(SKILL_ROOT, "scripts", "stock_copilot_pro.mjs");

function runCli(args, timeoutMs = 300_000) {
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

test("compare US stocks (AAPL vs MSFT) should return two reports in JSON", async (t) => {
  if (!process.env.QVERIS_API_KEY) {
    t.skip("QVERIS_API_KEY not set, skip live compare e2e");
    return;
  }
  const run = await runCli([
    "compare",
    "--symbols", "AAPL,MSFT",
    "--market", "US",
    "--format", "json",
    "--mode", "basic",
    "--timeout", "20",
    "--skip-questionnaire",
    "--no-evolution",
  ]);
  assert.equal(run.ok, true, `compare AAPL,MSFT failed: ${run.stderr}`);
  const result = parseJsonFromOutput(run.stdout);
  assert.ok(result && typeof result === "object", "compare output should be valid JSON");
  assert.equal(result.mode, "compare", "mode should be 'compare'");
  assert.ok(Array.isArray(result.reports), "reports should be an array");
  assert.equal(result.reports.length, 2, "should have exactly 2 reports");
  for (const report of result.reports) {
    assert.ok(report.symbol, `each report should have symbol, got: ${JSON.stringify(report)}`);
    assert.ok(report.market, "each report should have market");
    assert.ok(report.data && typeof report.data === "object", "each report should have data block");
  }
  const symbols = result.reports.map((r) => r.symbol.toUpperCase());
  assert.ok(symbols.some((s) => s.includes("AAPL")), `reports should contain AAPL, got: ${symbols}`);
  assert.ok(symbols.some((s) => s.includes("MSFT")), `reports should contain MSFT, got: ${symbols}`);
});

test("compare --format chat should return structured chat comparison", async (t) => {
  if (!process.env.QVERIS_API_KEY) {
    t.skip("QVERIS_API_KEY not set, skip live compare e2e");
    return;
  }
  const run = await runCli([
    "compare",
    "--symbols", "NVDA,AMD",
    "--market", "US",
    "--format", "chat",
    "--mode", "basic",
    "--timeout", "20",
    "--skip-questionnaire",
    "--no-evolution",
  ]);
  assert.equal(run.ok, true, `compare --format chat failed: ${run.stderr}`);
  const result = parseJsonFromOutput(run.stdout);
  assert.ok(result && typeof result === "object", "chat compare output should be valid JSON");
  assert.equal(result.mode, "compare-chat", "mode should be 'compare-chat'");
  assert.ok(Array.isArray(result.reports), "reports should be an array");
  assert.equal(result.reports.length, 2, "should have exactly 2 reports");
  for (const report of result.reports) {
    assert.ok(report.symbol, "each chat report should have symbol");
    assert.ok(report.decisionCard, "each chat report should have decisionCard");
    assert.ok(report.chat && Array.isArray(report.chat.segments), "each chat report should have chat.segments");
  }
});
