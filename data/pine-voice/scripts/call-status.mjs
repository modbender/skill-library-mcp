#!/usr/bin/env node

import { readFileSync } from "node:fs";
import { join } from "node:path";
import { homedir } from "node:os";

const GATEWAY = "https://agent3-api-gateway-staging.19pine.ai";

const TERMINAL_STATUSES = new Set([
  "completed", "Completed",
  "HungupByPeer", "HungupByLocal",
  "Timeout", "TooLongSilence",
  "failed", "Failed", "DialFailed", "NoAnswer", "Declined",
  "cancelled",
]);

function loadCredentials() {
  const credPath = join(homedir(), ".pine-voice", "credentials.json");
  try {
    return JSON.parse(readFileSync(credPath, "utf-8"));
  } catch {
    console.error("Not authenticated. Run auth-request.mjs and auth-verify.mjs first.");
    process.exit(1);
  }
}

const callId = (process.argv[2] ?? "").trim();
if (!callId) {
  console.error("Usage: call-status.mjs <call_id>");
  process.exit(2);
}

const creds = loadCredentials();

const resp = await fetch(`${GATEWAY}/api/v2/voice/call/${encodeURIComponent(callId)}`, {
  headers: {
    "Authorization": `Bearer ${creds.access_token}`,
    "X-Pine-User-Id": creds.user_id,
  },
});

if (!resp.ok) {
  const text = await resp.text().catch(() => "");
  console.error(`Status check failed (${resp.status}): ${text}`);
  process.exit(1);
}

const data = await resp.json();
const status = data?.status ?? "unknown";
const isTerminal = TERMINAL_STATUSES.has(status);

console.log(JSON.stringify({ ...data, is_terminal: isTerminal }, null, 2));
