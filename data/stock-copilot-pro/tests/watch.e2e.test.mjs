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

function runCli(args, timeoutMs = 30_000) {
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

test("watch list should return JSON with holdings and watchlist arrays", async (t) => {
  const run = await runCli(["watch", "--action", "list", "--format", "json"]);
  assert.equal(run.ok, true, `watch list failed: ${run.stderr}`);
  const result = parseJsonFromOutput(run.stdout);
  assert.ok(result && typeof result === "object", "watch list output should be valid JSON");
  assert.equal(result.mode, "watch", "mode should be 'watch'");
  assert.equal(result.action, "list", "action should be 'list'");
  assert.ok(result.watchlist && typeof result.watchlist === "object", "watchlist state should exist");
  assert.ok(Array.isArray(result.watchlist.holdings), "watchlist.holdings should be an array");
  assert.ok(Array.isArray(result.watchlist.watchlist), "watchlist.watchlist should be an array");
});

test("watch add + remove lifecycle should maintain consistency", async (t) => {
  const original = await fs.readFile(WATCHLIST_FILE, "utf-8");
  t.after(async () => {
    await fs.writeFile(WATCHLIST_FILE, original, "utf-8");
  });

  const testSymbol = "TSLA";
  const testMarket = "US";

  // Add TSLA to watchlist
  const addRun = await runCli([
    "watch", "--action", "add",
    "--symbol", testSymbol,
    "--market", testMarket,
    "--bucket", "watchlist",
    "--format", "json",
  ]);
  assert.equal(addRun.ok, true, `watch add failed: ${addRun.stderr}`);
  const addResult = parseJsonFromOutput(addRun.stdout);
  assert.ok(addResult && typeof addResult === "object", "add result should be valid JSON");
  assert.equal(addResult.mode, "watch");
  assert.equal(addResult.action, "add");
  assert.equal(addResult.symbol, testSymbol);

  // Verify the symbol is now present in the watchlist
  const afterAdd = addResult.watchlist?.watchlist || [];
  const found = afterAdd.some(
    (item) => item.symbol.toUpperCase() === testSymbol && item.market === testMarket,
  );
  assert.ok(found, `${testSymbol} should appear in watchlist after add`);

  // Remove TSLA from watchlist
  const removeRun = await runCli([
    "watch", "--action", "remove",
    "--symbol", testSymbol,
    "--market", testMarket,
    "--bucket", "watchlist",
    "--format", "json",
  ]);
  assert.equal(removeRun.ok, true, `watch remove failed: ${removeRun.stderr}`);
  const removeResult = parseJsonFromOutput(removeRun.stdout);
  assert.ok(removeResult && typeof removeResult === "object", "remove result should be valid JSON");
  assert.equal(removeResult.mode, "watch");
  assert.equal(removeResult.action, "remove");

  // Verify the symbol is gone
  const afterRemove = removeResult.watchlist?.watchlist || [];
  const stillPresent = afterRemove.some(
    (item) => item.symbol.toUpperCase() === testSymbol && item.market === testMarket,
  );
  assert.ok(!stillPresent, `${testSymbol} should be removed from watchlist after remove`);
});

test("watch add to holdings bucket should persist separately from watchlist", async (t) => {
  const original = await fs.readFile(WATCHLIST_FILE, "utf-8");
  t.after(async () => {
    await fs.writeFile(WATCHLIST_FILE, original, "utf-8");
  });

  const testSymbol = "AAPL";
  const testMarket = "US";

  const addRun = await runCli([
    "watch", "--action", "add",
    "--symbol", testSymbol,
    "--market", testMarket,
    "--bucket", "holdings",
    "--format", "json",
  ]);
  assert.equal(addRun.ok, true, `watch add to holdings failed: ${addRun.stderr}`);
  const addResult = parseJsonFromOutput(addRun.stdout);
  assert.ok(addResult && typeof addResult === "object", "result should be valid JSON");
  assert.equal(addResult.bucket, "holdings");

  const holdingsList = addResult.watchlist?.holdings || [];
  const found = holdingsList.some(
    (item) => item.symbol.toUpperCase() === testSymbol,
  );
  assert.ok(found, `${testSymbol} should appear in holdings after add`);
});
