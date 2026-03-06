#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import os from 'os';

function configPath() { return path.join(os.homedir(), '.config', 'soul-in-sapphire', 'config.json'); }

function loadConfig() {
  const p = configPath();
  if (!fs.existsSync(p)) throw new Error(`Missing config: ${p}`);
  return JSON.parse(fs.readFileSync(p, 'utf-8'));
}

function saveConfig(cfg) {
  const p = configPath();
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, JSON.stringify(cfg, null, 2) + '\n', 'utf-8');
}

function requirePaths(cfg, keys) {
  const missing = [];
  for (const k of keys) if (!cfg?.[k]) missing.push(k);
  if (missing.length) throw new Error(`Config missing keys: ${missing.join(', ')}`);
}

export { configPath, loadConfig, saveConfig, requirePaths };
