/**
 * 🔧 Utility functions
 */

import fs from 'fs/promises';
import path from 'path';
import os from 'os';

/**
 * Load configuration file
 */
export async function loadConfig(configPath) {
  const paths = [
    configPath,
    '.openclaw-guard.json',
    path.join(os.homedir(), '.openclaw-guard.json'),
    path.join(os.homedir(), '.config', 'openclaw-guard', 'config.json')
  ];
  
  for (const p of paths) {
    try {
      const content = await fs.readFile(p, 'utf-8');
      return JSON.parse(content);
    } catch {
      continue;
    }
  }
  
  return {}; // Default empty config
}

/**
 * Get OpenClaw installation path
 */
export async function getOpenClawPath() {
  const candidates = [
    path.join(os.homedir(), '.openclaw'),
    path.join(os.homedir(), '.config', 'openclaw'),
    process.cwd()
  ];
  
  for (const p of candidates) {
    try {
      await fs.access(p);
      return p;
    } catch {
      continue;
    }
  }
  
  return path.join(os.homedir(), '.openclaw');
}

/**
 * Format duration in human readable format
 */
export function formatDuration(ms) {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${(ms / 60000).toFixed(1)}m`;
}

/**
 * Deep merge objects
 */
export function deepMerge(target, source) {
  const result = { ...target };
  
  for (const key of Object.keys(source)) {
    if (source[key] instanceof Object && key in target) {
      result[key] = deepMerge(target[key], source[key]);
    } else {
      result[key] = source[key];
    }
  }
  
  return result;
}
