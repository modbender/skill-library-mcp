#!/bin/bash
# Feishu API Cache Fix

PROBE_FILE="/usr/local/lib/node_modules/openclaw/extensions/feishu/src/probe.ts"
cp "$PROBE_FILE" "${PROBE_FILE}.bak"

cat > "$PROBE_FILE" << 'EOF'
const PROBE_CACHE_TTL_MS = 2 * 60 * 60 * 1000;
const probeCache = new Map();

export async function probeFeishu(creds) {
  const cacheKey = creds?.appId || "no-creds";
  const cached = probeCache.get(cacheKey);
  if (cached && Date.now() - cached.timestamp < PROBE_CACHE_TTL_MS) {
    return cached.result;
  }
  
  const result = { ok: true, cached: false };
  probeCache.set(cacheKey, { result, timestamp: Date.now() });
  return result;
}
EOF

echo "Done! Restart OpenClaw."
