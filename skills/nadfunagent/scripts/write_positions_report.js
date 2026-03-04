#!/usr/bin/env node
/**
 * Write positions report JSON. Reads one JSON object from stdin and writes to
 * positions_report.json. Data dir: NADFUNAGENT_DATA_DIR or $HOME/nadfunagent.
 * Optional: POSITIONS_REPORT_PATH overrides the file path.
 * Required structure: { timestamp, wallet, cycle?, positionsCount?, positions[], summary? }
 * Usage: echo '{"timestamp":"...","wallet":"0x...","positions":[],"summary":{}}' | node write_positions_report.js
 */
const fs = require('fs');
const path = require('path');
const os = require('os');

const DATA_DIR = process.env.NADFUNAGENT_DATA_DIR || path.join(os.homedir(), 'nadfunagent');
const FILE_PATH = process.env.POSITIONS_REPORT_PATH || path.join(DATA_DIR, 'positions_report.json');

async function main() {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  const raw = Buffer.concat(chunks).toString('utf-8').trim();

  if (!raw) {
    console.error('No JSON input');
    process.exit(1);
  }

  let report;
  try {
    report = JSON.parse(raw);
  } catch (e) {
    console.error('Invalid JSON:', e.message);
    process.exit(1);
  }

  if (!report.positions) report.positions = [];
  if (!report.summary) report.summary = {};
  if (!report.timestamp) report.timestamp = new Date().toISOString().replace(/\.\d{3}Z$/, '.000Z');
  report.positionsCount = report.positions.length;

  const dir = path.dirname(FILE_PATH);
  if (dir) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(FILE_PATH, JSON.stringify(report, null, 2), 'utf-8');

  console.log(`OK written ${report.positionsCount} positions to ${FILE_PATH}`);
}

main().catch(e => {
  console.error(e);
  process.exit(1);
});
