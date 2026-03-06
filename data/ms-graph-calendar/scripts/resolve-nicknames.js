#!/usr/bin/env node
// resolve-nicknames.js — แปลงชื่อเล่นเป็น email โดยอ่านจาก nicknames.md
//
// ใช้: node resolve-nicknames.js --names "แบงค์,มิ้ว,โบ้"
// Output: alice@company.com,bob@company.com,carol@company.com

const fs = require("fs");
const path = require("path");

const argv = process.argv.slice(2);
const args = {};
for (let i = 0; i < argv.length; i += 2) {
  args[argv[i].replace("--", "")] = argv[i + 1];
}

const namesRaw = args.names || "";
if (!namesRaw) {
  console.error("❌ Usage: --names 'แบงค์,มิ้ว,โบ้'");
  process.exit(1);
}

// ── อ่าน nicknames.md ─────────────────────────────────────
const mdPath = path.join(__dirname, "..", "nicknames.md");
if (!fs.existsSync(mdPath)) {
  console.error("❌ nicknames.md not found at:", mdPath);
  process.exit(1);
}

const md = fs.readFileSync(mdPath, "utf-8");

// parse ตาราง markdown
const mapping = {};
for (const line of md.split("\n")) {
  const cols = line.split("|").map((c) => c.trim()).filter(Boolean);
  if (cols.length === 2 && cols[0] !== "nickname" && !cols[0].startsWith("-")) {
    mapping[cols[0].toLowerCase()] = cols[1];
  }
}

// ── resolve ───────────────────────────────────────────────
const names = namesRaw.split(",").map((n) => n.trim());
const resolved = [];
const notFound = [];

for (const name of names) {
  const email = mapping[name.toLowerCase()];
  if (email) {
    resolved.push({ name, email });
  } else {
    notFound.push(name);
  }
}

if (notFound.length) {
  console.warn(`⚠️  ไม่พบชื่อเล่นเหล่านี้ใน nicknames.md: ${notFound.join(", ")}`);
  console.warn(`   → ลองใช้ list-users.js --search แทน หรือเพิ่มใน nicknames.md`);
}

if (resolved.length) {
  console.log("✅ Resolved:");
  resolved.forEach((r) => console.log(`  ${r.name} → ${r.email}`));

  // output comma-separated emails สำหรับส่งต่อให้ scripts อื่น
  console.log("\n---EMAILS---");
  console.log(resolved.map((r) => r.email).join(","));
}

if (!resolved.length) {
  process.exit(1);
}
