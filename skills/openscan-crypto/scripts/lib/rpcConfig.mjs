/**
 * RPC Configuration persistence layer
 * Manages ~/.config/openscan-crypto/rpc-config.json
 */

import { readFile, writeFile, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { join } from "node:path";
import { homedir } from "node:os";

const CONFIG_DIR = join(homedir(), ".config", "openscan-crypto");
const CONFIG_PATH = join(CONFIG_DIR, "rpc-config.json");

const DEFAULT_CONFIG = {
  version: 1,
  metadataVersion: null,
  lastFetched: null,
  defaults: {
    strategy: "fallback",
    maxRpcs: 5,
    privateOnly: false,
  },
  networks: {},
};

/**
 * Load config from disk. Returns default config if file doesn't exist.
 */
export async function loadConfig() {
  if (!existsSync(CONFIG_PATH)) {
    return structuredClone(DEFAULT_CONFIG);
  }
  try {
    const raw = await readFile(CONFIG_PATH, "utf-8");
    const config = JSON.parse(raw);
    // Ensure all required fields exist (forward compat)
    return {
      ...structuredClone(DEFAULT_CONFIG),
      ...config,
      defaults: { ...DEFAULT_CONFIG.defaults, ...config.defaults },
    };
  } catch {
    return structuredClone(DEFAULT_CONFIG);
  }
}

/**
 * Save config to disk
 */
export async function saveConfig(config) {
  if (!existsSync(CONFIG_DIR)) {
    await mkdir(CONFIG_DIR, { recursive: true });
  }
  await writeFile(CONFIG_PATH, JSON.stringify(config, null, 2));
}

/**
 * Check if config file exists
 */
export function configExists() {
  return existsSync(CONFIG_PATH);
}

/**
 * Get network config. Returns null if network not configured.
 */
export function getNetworkConfig(config, chainId) {
  return config.networks[String(chainId)] || null;
}

/**
 * Set RPCs for a network (replaces existing)
 */
export function setNetworkRpcs(config, chainId, rpcs, strategy) {
  const key = String(chainId);
  if (!config.networks[key]) {
    config.networks[key] = {};
  }
  config.networks[key].rpcs = rpcs;
  if (strategy) {
    config.networks[key].strategy = strategy;
  }
  return config;
}

/**
 * Set strategy for a network
 */
export function setNetworkStrategy(config, chainId, strategy) {
  const key = String(chainId);
  if (!config.networks[key]) {
    config.networks[key] = { rpcs: [] };
  }
  config.networks[key].strategy = strategy;
  return config;
}

/**
 * Add RPCs to a network (append, deduplicate by URL)
 */
export function addNetworkRpcs(config, chainId, newRpcs) {
  const key = String(chainId);
  if (!config.networks[key]) {
    config.networks[key] = { rpcs: [] };
  }
  const existing = config.networks[key].rpcs || [];
  const existingUrls = new Set(existing.map(r => r.url));
  for (const rpc of newRpcs) {
    if (!existingUrls.has(rpc.url)) {
      existing.push(rpc);
      existingUrls.add(rpc.url);
    }
  }
  config.networks[key].rpcs = existing;
  return config;
}

/**
 * Remove an RPC from a network by URL
 */
export function removeNetworkRpc(config, chainId, url) {
  const key = String(chainId);
  const net = config.networks[key];
  if (!net || !net.rpcs) return config;
  net.rpcs = net.rpcs.filter(r => r.url !== url);
  return config;
}

/**
 * Reset a network to empty (will be re-populated from metadata on next use)
 */
export function resetNetwork(config, chainId) {
  delete config.networks[String(chainId)];
  return config;
}

/**
 * Reorder: move RPC at fromIndex to toIndex
 */
export function moveRpc(config, chainId, fromIndex, toIndex) {
  const rpcs = config.networks[String(chainId)]?.rpcs;
  if (!rpcs || fromIndex < 0 || fromIndex >= rpcs.length) return config;
  toIndex = Math.max(0, Math.min(toIndex, rpcs.length - 1));
  const [item] = rpcs.splice(fromIndex, 1);
  rpcs.splice(toIndex, 0, item);
  return config;
}

/**
 * Reorder: swap two positions
 */
export function swapRpcs(config, chainId, posA, posB) {
  const rpcs = config.networks[String(chainId)]?.rpcs;
  if (!rpcs) return config;
  const a = posA - 1, b = posB - 1; // 1-indexed to 0-indexed
  if (a < 0 || a >= rpcs.length || b < 0 || b >= rpcs.length) return config;
  [rpcs[a], rpcs[b]] = [rpcs[b], rpcs[a]];
  return config;
}

/**
 * Get effective RPCs + strategy for a network
 * Returns { rpcs: [...], strategy: "fallback"|"race"|"parallel" } or null if none
 */
export function getEffectiveRpcs(config, chainId) {
  const net = config.networks[String(chainId)];
  if (!net || !net.rpcs || net.rpcs.length === 0) return null;
  return {
    rpcs: net.rpcs,
    strategy: net.strategy || config.defaults.strategy,
  };
}

export { CONFIG_PATH, CONFIG_DIR };
