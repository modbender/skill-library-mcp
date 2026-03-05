import test from "node:test";
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { promises as fs } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const SKILL_ROOT = path.resolve(__dirname, "..");
const SCRIPT_FILE = path.join(SKILL_ROOT, "scripts", "stock_copilot_pro.mjs");
const WATCHLIST_FILE = path.join(SKILL_ROOT, "config", "watchlist.json");

function runCli(args, timeoutMs = 150_000) {
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

test("brief e2e should satisfy acceptance criteria", async (t) => {
  if (!process.env.QVERIS_API_KEY) {
    t.skip("QVERIS_API_KEY not set, skip live brief e2e");
    return;
  }
  const original = await fs.readFile(WATCHLIST_FILE, "utf-8");
  const fixture = {
    updatedAt: new Date().toISOString(),
    holdings: [{ symbol: "AAPL", market: "US" }],
    watchlist: [
      { symbol: "NVDA", market: "US" },
      { symbol: "0700.HK", market: "HK" },
    ],
  };
  await fs.writeFile(WATCHLIST_FILE, JSON.stringify(fixture, null, 2), "utf-8");
  t.after(async () => {
    await fs.writeFile(WATCHLIST_FILE, original, "utf-8");
  });

  const run = await runCli(
    ["brief", "--type", "morning", "--market", "GLOBAL", "--max-items", "3", "--format", "json", "--timeout", "25", "--no-evolution"],
    240_000,
  );
  assert.equal(run.ok, true, `brief command failed: ${run.stderr}`);
  const result = parseJsonFromOutput(run.stdout);
  assert.ok(result && typeof result === "object", "brief output should be valid json");
  assert.equal(result.mode, "brief");
  assert.ok(Array.isArray(result.marketOverview?.indices), "marketOverview.indices should exist");
  assert.ok(result.marketOverview.indices.length >= 1, "marketOverview.indices should not be empty");
  // Each index should have at minimum a name and symbol; price may be null when market is closed or API degrades
  const firstIndex = result.marketOverview.indices[0];
  assert.ok(firstIndex.name || firstIndex.symbol, "each index entry should have name or symbol");

  assert.ok(Array.isArray(result.reports) && result.reports.length >= 1, "reports should not be empty");
  const successfulReports = result.reports.filter((x) => !x.error);
  assert.ok(successfulReports.length >= 1, "should have at least one successful report");
  assert.ok(successfulReports.some((x) => x.grade && x.grade !== "N/A"), "at least one report should contain valid grade");
  assert.ok(successfulReports.some((x) => x.price != null), "at least one report should contain current price");

  assert.ok(Array.isArray(result.highlights), "highlights should exist");
  assert.ok(result.highlights.length >= 1, "highlights should not be empty");
  assert.ok(result.meta?.note, "brief meta.note should exist for OpenClaw guidance");
  assert.equal(result.meta?.guide, "Daily Brief Analysis Guide");
});
