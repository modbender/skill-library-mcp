#!/usr/bin/env node
/**
 * Import Apollo CSV export → Hunter verify → Instantly campaign
 * Usage: node import-csv.js leads.csv
 */

const https = require("https");
const fs = require("fs");
const path = require("path");
const config = require("./config");

const CAMPAIGN_ID = config.sequence.campaignId; // already created

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function request(options, body) {
  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let data = "";
      res.on("data", c => data += c);
      res.on("end", () => {
        try { resolve({ status: res.statusCode, body: JSON.parse(data) }); }
        catch { resolve({ status: res.statusCode, body: data }); }
      });
    });
    req.on("error", reject);
    if (body) req.write(typeof body === "string" ? body : JSON.stringify(body));
    req.end();
  });
}

// Parse Apollo CSV (handles quoted fields)
function parseCSV(content) {
  const lines = content.trim().split("\n");
  const headers = lines[0].split(",").map(h => h.replace(/"/g, "").trim().toLowerCase());
  return lines.slice(1).map(line => {
    const values = [];
    let current = "", inQuotes = false;
    for (const char of line) {
      if (char === '"') { inQuotes = !inQuotes; continue; }
      if (char === "," && !inQuotes) { values.push(current.trim()); current = ""; continue; }
      current += char;
    }
    values.push(current.trim());
    const obj = {};
    headers.forEach((h, i) => obj[h] = values[i] || "");
    return obj;
  }).filter(r => r["email"] || r["work email"] || r["email address"]);
}

function getEmail(row) {
  return row["email"] || row["work email"] || row["email address"] || row["corporate email"] || "";
}

function getField(row, ...keys) {
  for (const k of keys) if (row[k]) return row[k];
  return "";
}

async function verifyEmail(email) {
  if (!email || !email.includes("@")) return false;
  const res = await request({
    hostname: "api.hunter.io",
    path: `/v2/email-verifier?email=${encodeURIComponent(email)}&api_key=${config.hunter.apiKey}`,
    method: "GET",
  });
  if (res.status !== 200) return true;
  const status = res.body?.data?.status;
  return ["valid", "accept_all"].includes(status);
}

function personalizeFirstLine(row) {
  const company = getField(row, "company", "company name", "organization name", "account name") || "your store";
  const country = getField(row, "country", "location") || "UAE";
  const lines = [
    `Noticed ${company} is scaling in ${country} — curious if the ops side is keeping up with growth.`,
    `${company} caught my eye — you're building something real in the GCC e-commerce space.`,
    `Saw ${company} in the ${country} market — stores at your stage usually have processes ready to automate.`,
    `Running ${company} in the GCC — you're probably the one feeling the manual ops pain most.`,
  ];
  return lines[Math.floor(Math.random() * lines.length)];
}

async function uploadLead(lead) {
  const body = JSON.stringify({
    email: lead.email,
    first_name: lead.firstName,
    last_name: lead.lastName,
    company_name: lead.company,
    personalization: lead.firstLine,
    campaign_id: CAMPAIGN_ID,
  });
  return request(
    {
      hostname: "api.instantly.ai",
      path: `/api/v2/leads`,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${config.instantly.apiKey}`,
        "Content-Length": Buffer.byteLength(body),
      },
    },
    body
  );
}

async function run() {
  const csvPath = process.argv[2];
  if (!csvPath) {
    console.error("Usage: node import-csv.js <path-to-apollo-export.csv>");
    process.exit(1);
  }

  if (!fs.existsSync(csvPath)) {
    console.error(`File not found: ${csvPath}`);
    process.exit(1);
  }

  console.log(`⚡ Importing ${path.basename(csvPath)} into Instantly...\n`);

  const content = fs.readFileSync(csvPath, "utf8");
  const rows = parseCSV(content);
  console.log(`📋 Parsed ${rows.length} rows from CSV`);

  if (rows.length > 0) {
    console.log(`   Columns detected: ${Object.keys(rows[0]).slice(0, 8).join(", ")}...\n`);
  }

  const verifiedLeads = [];
  console.log("🔍 Verifying emails with Hunter...");

  for (const row of rows) {
    const email = getEmail(row);
    if (!email) continue;

    const valid = await verifyEmail(email);
    if (!valid) {
      console.log(`  ✗ ${email} — invalid`);
      continue;
    }

    const firstName = getField(row, "first name", "firstname", "first_name") || "there";
    const lastName = getField(row, "last name", "lastname", "last_name") || "";
    const company = getField(row, "company", "company name", "organization name", "account name") || "";

    verifiedLeads.push({ email, firstName, lastName, company, firstLine: personalizeFirstLine(row) });
    console.log(`  ✓ ${email} — ${firstName} @ ${company}`);
    await sleep(250);
  }

  console.log(`\n✅ Verified: ${verifiedLeads.length} / ${rows.length} leads\n`);

  if (!verifiedLeads.length) {
    console.log("No valid leads to upload.");
    return;
  }

  console.log(`📤 Uploading leads to Instantly campaign...`);
  let uploaded = 0;
  let failed = 0;

  for (const lead of verifiedLeads) {
    try {
      const res = await uploadLead(lead);
      if (res.status === 200 || res.status === 201) {
        uploaded++;
        console.log(`  ✓ ${lead.email}`);
      } else {
        failed++;
        console.log(`  ✗ ${lead.email} — ${res.status} ${JSON.stringify(res.body).slice(0, 80)}`);
      }
    } catch (e) {
      failed++;
      console.log(`  ✗ ${lead.email} — ${e.message}`);
    }
    await sleep(300);
  }

  console.log(`\n╔══════════════════════════════════╗`);
  console.log(`║  IMPORT COMPLETE ⚡               ║`);
  console.log(`║  Uploaded: ${String(uploaded).padEnd(23)}║`);
  console.log(`║  Failed:   ${String(failed).padEnd(23)}║`);
  console.log(`║  Campaign: Zeerotoai Outreach    ║`);
  console.log(`║                                  ║`);
  console.log(`║  NEXT: Connect inboxes in        ║`);
  console.log(`║  Instantly → hit Launch 🚀       ║`);
  console.log(`╚══════════════════════════════════╝`);
}

run().catch(console.error);
