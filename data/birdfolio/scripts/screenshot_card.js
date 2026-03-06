#!/usr/bin/env node
/**
 * screenshot_card.js — Screenshot a card HTML file and save it as PNG.
 *
 * Uses playwright-core from OpenClaw's node_modules + its bundled Chromium.
 * No separate install required.
 *
 * Usage:
 *   node screenshot_card.js <cardPath> [outputPath]
 *
 * If outputPath is omitted, saves to the same location with .png extension.
 *
 * Output (JSON to stdout):
 *   {"status":"ok","pngPath":"..."}
 */

const path = require("path");
const fs   = require("fs");

// ── Resolve playwright-core from OpenClaw's node_modules ──────────────────────
const OPENCLAW_MODULES = path.join(
  process.env.APPDATA || "",
  "npm/node_modules/openclaw/node_modules"
);
const PW_PATH = path.join(OPENCLAW_MODULES, "playwright-core");

let pw;
try {
  pw = require(PW_PATH);
} catch (e) {
  console.log(JSON.stringify({ status: "error", message: `Cannot load playwright-core at ${PW_PATH}: ${e.message}` }));
  process.exit(1);
}

// Prefer system Chrome/Edge over playwright-managed binary (which may not be installed)
const SYSTEM_BROWSERS = [
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
  "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
];
const CHROMIUM_EXE = SYSTEM_BROWSERS.find(p => fs.existsSync(p)) || pw.chromium.executablePath();

async function run() {
  const cardPath   = process.argv[2];
  const outputPath = process.argv[3] || cardPath.replace(/\.html?$/i, ".png");

  if (!cardPath) {
    console.log(JSON.stringify({ status: "error", message: "Usage: node screenshot_card.js <cardPath> [outputPath]" }));
    process.exit(1);
  }

  if (!fs.existsSync(cardPath)) {
    console.log(JSON.stringify({ status: "error", message: `Card not found: ${cardPath}` }));
    process.exit(1);
  }

  const fileUrl = "file:///" + cardPath.replace(/\\/g, "/");

  const browser = await pw.chromium.launch({
    executablePath: CHROMIUM_EXE,
    headless: true,
  });

  try {
    const page = await browser.newPage();
    await page.setViewportSize({ width: 600, height: 400 });
    await page.goto(fileUrl, { waitUntil: "networkidle" });
    await page.screenshot({ path: outputPath, type: "png" });

    console.log(JSON.stringify({ status: "ok", pngPath: outputPath }));
  } finally {
    await browser.close();
  }
}

run().catch(e => {
  console.log(JSON.stringify({ status: "error", message: e.message }));
  process.exit(1);
});
