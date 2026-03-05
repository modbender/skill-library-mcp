#!/usr/bin/env node
/**
 * RMN Soul Heartbeat — Decay tick + auto-anchor check
 */

const fs = require('fs');
const path = require('path');
const { RecursiveMemoryNetwork, computeMemoryMerkle } = require('./rmn-engine');

const WORKSPACE = process.env.OPENCLAW_WORKSPACE || path.resolve(__dirname, '../../../');
const DATA_DIR = path.join(WORKSPACE, 'rmn-soul-data');
const DB_PATH = path.join(DATA_DIR, 'memory.json');
const CONFIG_PATH = path.join(DATA_DIR, 'config.json');

if (!fs.existsSync(DB_PATH)) {
  console.log(JSON.stringify({ status: 'not_initialized' }));
  process.exit(0);
}

const rmn = new RecursiveMemoryNetwork(DB_PATH);
const decay = rmn.decayTick();
const merkle = computeMemoryMerkle(rmn);
const stats = rmn.stats();

// Check if auto-anchor is due
let anchorDue = false;
try {
  const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'));
  if (config.autoAnchorDays > 0 && config.lastAnchor) {
    const daysSince = (Date.now() - new Date(config.lastAnchor).getTime()) / (1000 * 60 * 60 * 24);
    anchorDue = daysSince >= config.autoAnchorDays;
  }
} catch {}

const report = {
  timestamp: new Date().toISOString(),
  pruned: decay.pruned,
  remaining: decay.remaining,
  memoryRoot: merkle.memoryRoot.slice(0, 16),
  soulHash: merkle.soulHash.slice(0, 16),
  stats,
  anchorDue,
};

console.log(JSON.stringify(report));

if (anchorDue) {
  console.error('⚠️ Auto-anchor is due! Run: node scripts/anchor.js');
}
