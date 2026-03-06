#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const os = require('node:os');

const DATA_DIR = path.resolve(__dirname, '..', 'data');
const BASELINE_FILE = path.join(DATA_DIR, 'baselines.json');

function expandPath(p) {
  if (p.startsWith('~/')) return path.join(os.homedir(), p.slice(2));
  return p;
}

function hashFile(filePath) {
  try {
    const content = fs.readFileSync(expandPath(filePath));
    return crypto.createHash('sha256').update(content).digest('hex');
  } catch (e) {
    return e.code === 'ENOENT' ? 'FILE_NOT_FOUND' : `ERROR:${e.code}`;
  }
}

function loadBaselines() {
  try { return JSON.parse(fs.readFileSync(BASELINE_FILE, 'utf8')); }
  catch { return {}; }
}

function saveBaselines(baselines) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.writeFileSync(BASELINE_FILE, JSON.stringify(baselines, null, 2));
}

function init(files) {
  const baselines = {};
  for (const f of files) {
    baselines[f] = { hash: hashFile(f), timestamp: new Date().toISOString() };
  }
  saveBaselines(baselines);
  return baselines;
}

function check(files) {
  const baselines = loadBaselines();
  const results = [];
  for (const f of files) {
    const currentHash = hashFile(f);
    const baseline = baselines[f];
    if (!baseline) {
      results.push({ file: f, status: 'NEW', hash: currentHash });
    } else if (baseline.hash !== currentHash) {
      results.push({ file: f, status: 'CHANGED', oldHash: baseline.hash.substring(0, 12), newHash: currentHash.substring(0, 12) });
    } else {
      results.push({ file: f, status: 'OK' });
    }
  }
  return results;
}

module.exports = { init, check, hashFile, loadBaselines };
