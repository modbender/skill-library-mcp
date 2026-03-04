#!/usr/bin/env node
// setup.js — บันทึก Azure credentials สำหรับ ms-graph-calendar
// ใช้: node setup.js --tenant-id xxx --client-id yyy --client-secret zzz

const fs = require("fs");
const os = require("os");
const path = require("path");

const args = process.argv.slice(2);
const get = (flag) => {
  const i = args.indexOf(flag);
  return i !== -1 ? args[i + 1] : null;
};

const tenantId = get("--tenant-id");
const clientId = get("--client-id");
const clientSecret = get("--client-secret");

if (!tenantId || !clientId || !clientSecret) {
  console.error("❌ Usage: node setup.js --tenant-id <id> --client-id <id> --client-secret <secret>");
  process.exit(1);
}

const configDir = path.join(os.homedir(), ".openclaw");
const configPath = path.join(configDir, "ms-graph-calendar.json");

if (!fs.existsSync(configDir)) fs.mkdirSync(configDir, { recursive: true });

fs.writeFileSync(configPath, JSON.stringify({
  AZURE_TENANT_ID: tenantId,
  AZURE_CLIENT_ID: clientId,
  AZURE_CLIENT_SECRET: clientSecret,
}, null, 2), { mode: 0o600 });

console.log("✅ Credentials saved to", configPath);
