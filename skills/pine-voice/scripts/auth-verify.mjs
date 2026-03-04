#!/usr/bin/env node

import { writeFileSync, mkdirSync, chmodSync } from "node:fs";
import { join } from "node:path";
import { homedir } from "node:os";

const email = (process.argv[2] ?? "").trim();
const requestToken = (process.argv[3] ?? "").trim();
const code = (process.argv[4] ?? "").trim();

if (!email || !requestToken || !code) {
  console.error("Usage: auth-verify.mjs <email> <request_token> <code>");
  process.exit(2);
}

const resp = await fetch("https://www.19pine.ai/api/v2/auth/email/verify", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ email, request_token: requestToken, code }),
});

if (!resp.ok) {
  const text = await resp.text().catch(() => "");
  console.error(`Auth verification failed (${resp.status}): ${text}`);
  process.exit(1);
}

const data = await resp.json();
const accessToken = data?.data?.access_token;
const userId = data?.data?.id;

if (!accessToken || !userId) {
  console.error("Unexpected response — missing access_token or id.");
  console.error(JSON.stringify(data, null, 2));
  process.exit(1);
}

const dir = join(homedir(), ".pine-voice");
const credPath = join(dir, "credentials.json");

mkdirSync(dir, { recursive: true });
writeFileSync(credPath, JSON.stringify({ access_token: accessToken, user_id: userId }, null, 2) + "\n");
chmodSync(credPath, 0o600);

console.log(JSON.stringify({
  status: "authenticated",
  credentials_path: credPath,
  user_id: userId,
}));
