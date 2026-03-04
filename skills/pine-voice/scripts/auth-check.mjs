#!/usr/bin/env node

import { readFileSync } from "node:fs";
import { join } from "node:path";
import { homedir } from "node:os";

const credPath = join(homedir(), ".pine-voice", "credentials.json");

try {
  const creds = JSON.parse(readFileSync(credPath, "utf-8"));
  if (!creds.access_token || !creds.user_id) {
    console.log(JSON.stringify({ authenticated: false, reason: "incomplete credentials" }));
    process.exit(1);
  }
  console.log(JSON.stringify({ authenticated: true, user_id: creds.user_id, credentials_path: credPath }));
} catch {
  console.log(JSON.stringify({ authenticated: false, reason: "no credentials file" }));
  process.exit(1);
}
