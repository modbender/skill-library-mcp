#!/usr/bin/env node
// get-token.js — ดึง App-only Access Token จาก Azure AD
// ใช้: node get-token.js
// Output: พิมพ์ token ออกมา (หรือเก็บไว้ใน /tmp/openclaw-graph-token.json)

const https = require("https");
const querystring = require("querystring");
const fs = require("fs");
const os = require("os");
const path = require("path");

// อ่านจาก config file ก่อน (ถ้ามี) แล้วค่อย fallback ไป process.env
const CONFIG_PATH = path.join(os.homedir(), ".openclaw", "ms-graph-calendar.json");
let config = {};
if (fs.existsSync(CONFIG_PATH)) {
  try { config = JSON.parse(fs.readFileSync(CONFIG_PATH, "utf8")); } catch (e) {}
}

const TENANT_ID = process.env.AZURE_TENANT_ID || config.AZURE_TENANT_ID;
const CLIENT_ID = process.env.AZURE_CLIENT_ID || config.AZURE_CLIENT_ID;
const CLIENT_SECRET = process.env.AZURE_CLIENT_SECRET || config.AZURE_CLIENT_SECRET;

if (!TENANT_ID || !CLIENT_ID || !CLIENT_SECRET) {
  console.error("❌ Missing env vars: AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET");
  console.error("💡 รัน setup: node setup.js");
  process.exit(1);
}

const body = querystring.stringify({
  grant_type: "client_credentials",
  client_id: CLIENT_ID,
  client_secret: CLIENT_SECRET,
  scope: "https://graph.microsoft.com/.default",
});

const options = {
  hostname: "login.microsoftonline.com",
  path: `/${TENANT_ID}/oauth2/v2.0/token`,
  method: "POST",
  headers: {
    "Content-Type": "application/x-www-form-urlencoded",
    "Content-Length": Buffer.byteLength(body),
  },
};

const req = https.request(options, (res) => {
  let data = "";
  res.on("data", (chunk) => (data += chunk));
  res.on("end", () => {
    const json = JSON.parse(data);
    if (json.error) {
      console.error("❌ Token error:", json.error_description);
      process.exit(1);
    }

    const tokenPath = path.join(os.tmpdir(), "openclaw-graph-token.json");
    const tokenData = {
      access_token: json.access_token,
      expires_at: Date.now() + json.expires_in * 1000,
    };
    fs.writeFileSync(tokenPath, JSON.stringify(tokenData));

    console.log("✅ Token acquired. Expires in", Math.round(json.expires_in / 60), "minutes.");
    console.log(json.access_token);
  });
});

req.on("error", (e) => {
  console.error("❌ Request failed:", e.message);
  process.exit(1);
});

req.write(body);
req.end();
