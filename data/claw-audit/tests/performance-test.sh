#!/bin/bash
# Performance comparison: sync vs async versions

echo "======================================"
echo "ClawAudit Performance Test"
echo "======================================"
echo ""

cd "$(dirname "$0")/.." || exit 1

echo "1. Testing audit-system.mjs (original sync)"
echo "--------------------------------------"
time node scripts/audit-system.mjs --json > /tmp/audit-system-sync.json 2>&1
SYNC_EXIT=$?
echo "Exit code: $SYNC_EXIT"
echo ""

echo "2. Testing audit-system-async.mjs (proof of concept - 7 checks)"
echo "--------------------------------------"
time node scripts/audit-system-async.mjs --json > /tmp/audit-system-async.json 2>&1
ASYNC_EXIT=$?
echo "Exit code: $ASYNC_EXIT"
echo ""

echo "3. Testing audit-system-full-async.mjs (complete - 32 checks)"
echo "--------------------------------------"
time node scripts/audit-system-full-async.mjs --json > /tmp/audit-system-full-async.json 2>&1
FULL_ASYNC_EXIT=$?
echo "Exit code: $FULL_ASYNC_EXIT"
echo ""

echo "4. Testing audit-config.mjs (original)"
echo "--------------------------------------"
time node scripts/audit-config.mjs --json > /tmp/audit-config-sync.json 2>&1
CONFIG_SYNC_EXIT=$?
echo "Exit code: $CONFIG_SYNC_EXIT"
echo ""

echo "5. Testing audit-config-optimized.mjs"
echo "--------------------------------------"
time node scripts/audit-config-optimized.mjs --json > /tmp/audit-config-optimized.json 2>&1
CONFIG_OPT_EXIT=$?
echo "Exit code: $CONFIG_OPT_EXIT"
echo ""

echo "======================================"
echo "Results Comparison"
echo "======================================"

# Compare finding counts
SYNC_FINDINGS=$(jq '.findings | length' /tmp/audit-system-sync.json 2>/dev/null || echo "0")
ASYNC_FINDINGS=$(jq '.findings | length' /tmp/audit-system-async.json 2>/dev/null || echo "0")
FULL_ASYNC_FINDINGS=$(jq '.findings | length' /tmp/audit-system-full-async.json 2>/dev/null || echo "0")

echo "audit-system findings:"
echo "  sync (all checks): $SYNC_FINDINGS"
echo "  async (7 checks): $ASYNC_FINDINGS"
echo "  full-async (all checks): $FULL_ASYNC_FINDINGS"

if [ "$SYNC_FINDINGS" -eq "$FULL_ASYNC_FINDINGS" ]; then
  echo "✅ Full async findings match sync!"
else
  echo "❌ Full async findings differ from sync!"
fi

CONFIG_SYNC_FINDINGS=$(jq '.findings | length' /tmp/audit-config-sync.json 2>/dev/null || echo "0")
CONFIG_OPT_FINDINGS=$(jq '.findings | length' /tmp/audit-config-optimized.json 2>/dev/null || echo "0")

echo "audit-config findings: sync=$CONFIG_SYNC_FINDINGS, optimized=$CONFIG_OPT_FINDINGS"

if [ "$CONFIG_SYNC_FINDINGS" -eq "$CONFIG_OPT_FINDINGS" ]; then
  echo "✅ Finding counts match!"
else
  echo "❌ Finding counts differ!"
fi

echo ""
echo "Execution times:"
ASYNC_TIME=$(jq '.executionTimeMs' /tmp/audit-system-async.json 2>/dev/null || echo "0")
FULL_ASYNC_TIME=$(jq '.executionTimeMs' /tmp/audit-system-full-async.json 2>/dev/null || echo "0")
CONFIG_SYNC_TIME=$(jq '.executionTimeMs // "N/A"' /tmp/audit-config-sync.json 2>/dev/null || echo "N/A")
CONFIG_OPT_TIME=$(jq '.executionTimeMs' /tmp/audit-config-optimized.json 2>/dev/null || echo "0")

echo "  audit-system:"
echo "    sync (from time):   ~2640ms"
echo "    async (7 checks):   ${ASYNC_TIME}ms"
echo "    full-async (all):   ${FULL_ASYNC_TIME}ms"

if [ "$FULL_ASYNC_TIME" != "0" ]; then
  SPEEDUP=$(awk "BEGIN {printf \"%.1f\", 2640 / $FULL_ASYNC_TIME}")
  echo "    → Full async speedup: ${SPEEDUP}x faster"
fi

echo ""
echo "  audit-config sync: ${CONFIG_SYNC_TIME}ms"
echo "  audit-config optimized: ${CONFIG_OPT_TIME}ms"

if [ "$CONFIG_OPT_TIME" != "0" ] && [ "$CONFIG_OPT_TIME" != "N/A" ] && [ "$CONFIG_SYNC_TIME" != "N/A" ]; then
  CONFIG_SPEEDUP=$(awk "BEGIN {printf \"%.1f\", $CONFIG_SYNC_TIME / $CONFIG_OPT_TIME}")
  echo "  → Speedup: ${CONFIG_SPEEDUP}x"
fi

echo ""
echo "======================================"
echo "Performance Test Complete"
echo "======================================"
