#!/usr/bin/env node

const email = (process.argv[2] ?? "").trim();
if (!email) {
  console.error("Usage: auth-request.mjs <email>");
  process.exit(2);
}

const resp = await fetch("https://www.19pine.ai/api/v2/auth/email/request", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ email }),
});

if (!resp.ok) {
  const text = await resp.text().catch(() => "");
  console.error(`Auth request failed (${resp.status}): ${text}`);
  process.exit(1);
}

const data = await resp.json();
const requestToken = data?.data?.request_token;

if (!requestToken) {
  console.error("Unexpected response — no request_token returned.");
  console.error(JSON.stringify(data, null, 2));
  process.exit(1);
}

console.log(JSON.stringify({ request_token: requestToken, email }));
