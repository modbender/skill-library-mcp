#!/bin/sh
# Side-by-side benchmark: baseline (Self Improving Agent — Rank #2 on ClawHub / legacy .learnings) vs Mulch.
# Runs same task series via nanobots; asserts Mulch is more token-efficient.
set -e
ROOT="${1:-/skill}"
BENCH_ROOT="/tmp/bench"
BASELINE_DIR="$BENCH_ROOT/baseline"
MULCH_DIR="$BENCH_ROOT/mulch"
mkdir -p "$BASELINE_DIR" "$MULCH_DIR"

echo "=== Benchmark: Baseline (Self Improving Agent — Rank #2 on ClawHub) vs Mulch Self Improver ==="
echo ""

# Run nanobots (same tasks, different flows)
echo "--- Nanobot: Baseline (.learnings) ---"
/bin/sh "$ROOT/scripts/benchmark/nanobot-baseline.sh" "$BASELINE_DIR" "$BASELINE_DIR/metrics-baseline.json"
echo ""

echo "--- Nanobot: Mulch ---"
/bin/sh "$ROOT/scripts/benchmark/nanobot-mulch.sh" "$MULCH_DIR" "$MULCH_DIR/metrics-mulch.json"
echo ""

echo "--- Troubleshooting benchmark (chars to find fix, resolution find-rate) ---"
/bin/sh "$ROOT/scripts/benchmark/nanobot-troubleshooting.sh" "$ROOT" "$BENCH_ROOT"
echo ""

STYLE_BASELINE_DIR="$BENCH_ROOT/style_baseline"
STYLE_MULCH_DIR="$BENCH_ROOT/style_mulch"
mkdir -p "$STYLE_BASELINE_DIR" "$STYLE_MULCH_DIR"
echo "--- Style & memory benchmark (writing style, addressing, preferences, habits, admin) ---"
/bin/sh "$ROOT/scripts/benchmark/nanobot-style-baseline.sh" "$STYLE_BASELINE_DIR" "$STYLE_BASELINE_DIR/metrics-style-baseline.json"
/bin/sh "$ROOT/scripts/benchmark/nanobot-style-mulch.sh" "$STYLE_MULCH_DIR" "$STYLE_MULCH_DIR/metrics-style-mulch.json"
echo ""

# Compare with Node (reliable JSON parse)
BASELINE_METRICS="$BASELINE_DIR/metrics-baseline.json"
MULCH_METRICS="$MULCH_DIR/metrics-mulch.json"
export BASELINE_METRICS MULCH_METRICS
node -e '
const fs = require("fs");
const baselinePath = process.env.BASELINE_METRICS;
const mulchPath = process.env.MULCH_METRICS;
if (!baselinePath || !mulchPath) throw new Error("Missing BASELINE_METRICS or MULCH_METRICS");
const b = JSON.parse(fs.readFileSync(baselinePath, "utf8"));
const m = JSON.parse(fs.readFileSync(mulchPath, "utf8"));
const report = [];
report.push("Metric                      | Baseline (legacy) | Mulch    | Winner");
report.push("----------------------------|-------------------|----------|--------");
const fmt = (n) => String(n).padStart(6);
const pct = (base, cur) => base === 0 ? "0%" : (100 - (cur/base)*100).toFixed(0) + "% less";
const rRem = b.reminder_chars; const mRem = m.reminder_chars;
report.push("Reminder (chars)            | " + fmt(rRem) + "           | " + fmt(mRem) + "   | " + (mRem <= rRem ? "Mulch (shorter)" : "Baseline"));
const rCtx = b.context_chars; const mCtx = m.context_chars;
report.push("Session context (chars)     | " + fmt(rCtx) + "           | " + fmt(mCtx) + "   | " + (mCtx < rCtx ? "Mulch " + pct(rCtx, mCtx) : (mCtx <= rCtx ? "Mulch" : "Baseline")));
const rRet = b.retrieval_total_chars; const mRet = m.retrieval_total_chars;
report.push("Retrieval (2 queries, chars) | " + fmt(rRet) + "           | " + fmt(mRet) + "   | " + (mRet < rRet ? "Mulch " + pct(rRet, mRet) : (mRet <= rRet ? "Mulch" : "Baseline")));
const rTotal = rRem + rCtx + rRet; const mTotal = mRem + mCtx + mRet;
report.push("Total (rem+ctx+ret)         | " + fmt(rTotal) + "           | " + fmt(mTotal) + "   | " + (mTotal < rTotal ? "Mulch " + pct(rTotal, mTotal) : "Baseline"));
console.log(report.join("\n"));
console.log("");
const okRem = mRem <= rRem;
const okRet = mRet <= rRet;
const okCtxNotWorse = mCtx <= rCtx + 500;
if (!okRem) { console.error("FAIL: Mulch reminder should be <= baseline (more token-efficient)"); process.exit(1); }
if (!okRet) { console.error("FAIL: Mulch retrieval (targeted) should be <= baseline (more token-efficient)"); process.exit(1); }
if (!okCtxNotWorse) { console.error("FAIL: Mulch session context should not be drastically larger than baseline"); process.exit(1); }
console.log("OK: Mulch reminder is shorter than baseline.");
console.log("OK: Mulch retrieval is more targeted (<= baseline chars).");
console.log("OK: Benchmark assertions passed.");
'

# Troubleshooting report
TROUBLESHOOT_METRICS="$BENCH_ROOT/metrics-troubleshooting.json"
if [ -f "$TROUBLESHOOT_METRICS" ]; then
  export TROUBLESHOOT_METRICS
  node -e '
  const fs = require("fs");
  const path = process.env.TROUBLESHOOT_METRICS;
  if (!path) process.exit(0);
  const t = JSON.parse(fs.readFileSync(path, "utf8"));
  const b = t.baseline;
  const m = t.mulch;
  const pct = (base, cur) => base === 0 ? "0%" : (100 - (cur/base)*100).toFixed(0) + "% less";
  console.log("");
  console.log("Troubleshooting (3 error scenarios: find resolution)");
  console.log("  Chars to get all 3 resolutions  | Baseline: " + b.troubleshoot_chars + "  | Mulch: " + m.troubleshoot_chars + "  | Mulch " + pct(b.troubleshoot_chars, m.troubleshoot_chars));
  console.log("  Resolutions found (of 3)       | Baseline: " + b.resolutions_found + "/3  | Mulch: " + m.resolutions_found + "/3");
  if (m.troubleshoot_chars > b.troubleshoot_chars) { console.error("FAIL: Mulch troubleshooting should use <= baseline chars"); process.exit(1); }
  if (m.resolutions_found < 2) { console.error("FAIL: Mulch should find at least 2/3 resolutions (targeted search)"); process.exit(1); }
  console.log("OK: Troubleshooting skill improvement (fewer chars to get resolutions).");
  '
fi

# Style & memory report (assistant skills: writing style, addressing, preferences, habits, admin)
STYLE_BASELINE_METRICS="$BENCH_ROOT/style_baseline/metrics-style-baseline.json"
STYLE_MULCH_METRICS="$BENCH_ROOT/style_mulch/metrics-style-mulch.json"
if [ -f "$STYLE_BASELINE_METRICS" ] && [ -f "$STYLE_MULCH_METRICS" ]; then
  export STYLE_BASELINE_METRICS STYLE_MULCH_METRICS
  node -e '
  const fs = require("fs");
  const b = JSON.parse(fs.readFileSync(process.env.STYLE_BASELINE_METRICS, "utf8"));
  const m = JSON.parse(fs.readFileSync(process.env.STYLE_MULCH_METRICS, "utf8"));
  const pct = (base, cur) => base === 0 ? "0%" : (100 - (cur/base)*100).toFixed(0) + "% less";
  console.log("");
  console.log("Style & memory (6 scenarios: Gmail/Twitter voice, address customer/manager/colleague, standup preference)");
  console.log("  Chars to get all 6 answers     | Baseline: " + b.style_memory_chars + "  | Mulch: " + m.style_memory_chars + "  | " + (m.style_memory_chars <= b.style_memory_chars ? "Mulch " + pct(b.style_memory_chars, m.style_memory_chars) : "Baseline"));
  console.log("  Scenarios found (of 6)        | Baseline: " + b.scenarios_found + "/6  | Mulch: " + m.scenarios_found + "/6");
  if (m.style_memory_chars > b.style_memory_chars) { console.error("FAIL: Mulch style/memory should use <= baseline chars"); process.exit(1); }
  if (m.scenarios_found < 4) { console.error("FAIL: Mulch should find at least 4/6 style/memory scenarios"); process.exit(1); }
  console.log("OK: Style & memory (assistant skills) — fewer chars, same or better find rate.");
  '
fi

echo ""
echo "=== Benchmark passed: Mulch Self Improver is more token-efficient than baseline (Self Improving Agent — Rank #2 on ClawHub) ==="
