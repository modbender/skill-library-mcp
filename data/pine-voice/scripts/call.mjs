#!/usr/bin/env node

import { readFileSync } from "node:fs";
import { join } from "node:path";
import { homedir } from "node:os";

const GATEWAY = "https://agent3-api-gateway-staging.19pine.ai";

function loadCredentials() {
  const credPath = join(homedir(), ".pine-voice", "credentials.json");
  try {
    return JSON.parse(readFileSync(credPath, "utf-8"));
  } catch {
    console.error("Not authenticated. Run auth-request.mjs and auth-verify.mjs first.");
    process.exit(1);
  }
}

function readStdin() {
  return new Promise((resolve) => {
    let data = "";
    process.stdin.setEncoding("utf-8");
    process.stdin.on("data", (chunk) => (data += chunk));
    process.stdin.on("end", () => resolve(data));
    if (process.stdin.isTTY) resolve("");
  });
}

const input = await readStdin();
if (!input.trim()) {
  console.error("Usage: echo '{...}' | node call.mjs");
  console.error("Pass call parameters as JSON via stdin.");
  console.error("Required: dialed_number, callee_name, callee_context, call_objective");
  process.exit(2);
}

let params;
try {
  params = JSON.parse(input);
} catch (e) {
  console.error(`Invalid JSON: ${e.message}`);
  process.exit(2);
}

const required = ["dialed_number", "callee_name", "callee_context", "call_objective"];
for (const field of required) {
  if (!params[field]) {
    console.error(`Missing required field: ${field}`);
    process.exit(2);
  }
}

const allowed = [
  "dialed_number", "callee_name", "callee_context", "call_objective",
  "detailed_instructions", "caller", "voice", "max_duration_minutes", "enable_summary",
];
const body = {};
for (const key of allowed) {
  if (params[key] !== undefined) body[key] = params[key];
}

const creds = loadCredentials();

const resp = await fetch(`${GATEWAY}/api/v2/voice/call`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${creds.access_token}`,
    "X-Pine-User-Id": creds.user_id,
  },
  body: JSON.stringify(body),
});

if (!resp.ok) {
  const text = await resp.text().catch(() => "");
  console.error(`Call failed (${resp.status}): ${text}`);
  process.exit(1);
}

const data = await resp.json();
console.log(JSON.stringify(data, null, 2));
