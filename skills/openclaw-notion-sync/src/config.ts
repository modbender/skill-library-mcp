import fs from 'fs';
import path from 'path';
import type { NotionSyncConfig } from './types.js';

const CONFIG_FILE = '.notion-sync.json';

export function findConfig(dir: string): string | null {
  const file = path.join(dir, CONFIG_FILE);
  return fs.existsSync(file) ? file : null;
}

export function loadConfig(dir: string): NotionSyncConfig {
  const file = findConfig(dir);
  if (!file) throw new Error(`No ${CONFIG_FILE} found. Run: notion-sync init`);
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

export function saveConfig(dir: string, config: NotionSyncConfig): void {
  const file = path.join(dir, CONFIG_FILE);
  fs.writeFileSync(file, JSON.stringify(config, null, 2));
}

export function initConfig(dir: string, token: string, rootPageId: string): NotionSyncConfig {
  const config: NotionSyncConfig = {
    path: dir,
    notion: { token, rootPageId },
    ignore: ['node_modules', '.git', 'dist', '.notion-sync.json', '*.lock', '*.log'],
    checksums: {}
  };
  saveConfig(dir, config);
  return config;
}
