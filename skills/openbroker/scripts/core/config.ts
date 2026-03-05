// Configuration loader for Open Broker

import { config as loadDotenv } from 'dotenv';
import { resolve, join } from 'path';
import { existsSync, mkdirSync } from 'fs';
import { homedir } from 'os';
import { privateKeyToAccount } from 'viem/accounts';
import type { OpenBrokerConfig } from './types.js';

// Config locations (in order of priority)
// 1. Environment variables (always checked first by process.env)
// 2. Local .env in current working directory
// 3. Global config at ~/.openbroker/.env

export const GLOBAL_CONFIG_DIR = join(homedir(), '.openbroker');
export const GLOBAL_ENV_PATH = join(GLOBAL_CONFIG_DIR, '.env');
// Use OPENBROKER_CWD if set (from CLI wrapper), otherwise use process.cwd()
const userCwd = process.env.OPENBROKER_CWD || process.cwd();
export const LOCAL_ENV_PATH = resolve(userCwd, '.env');

// Package root (for reference, not config loading)
export const PROJECT_ROOT = resolve(import.meta.dirname, '../..');

const MAINNET_URL = 'https://api.hyperliquid.xyz';
const TESTNET_URL = 'https://api.hyperliquid-testnet.xyz';

// Open Broker builder address - receives builder fees on all trades
export const OPEN_BROKER_BUILDER_ADDRESS = '0xbb67021fA3e62ab4DA985bb5a55c5c1884381068';

// Default read-only key (for info commands that don't need authentication)
// This is a valid but essentially useless private key
const DEFAULT_READ_ONLY_KEY = '0x0000000000000000000000000000000000000000000000000000000000000001' as const;

// Track if we've shown the read-only warning
let readOnlyWarningShown = false;

/**
 * Find and load the config file from multiple locations
 * Priority: env vars > local .env > global ~/.openbroker/.env > project .env
 */
function loadEnvFile(): string | null {
  const verbose = process.env.VERBOSE === '1' || process.env.VERBOSE === 'true';
  process.env.DOTENV_CONFIG_QUIET = 'true';

  // Check locations in order of priority
  const locations = [
    { path: LOCAL_ENV_PATH, name: 'local (.env)' },
    { path: GLOBAL_ENV_PATH, name: 'global (~/.openbroker/.env)' },
  ];

  for (const { path, name } of locations) {
    if (existsSync(path)) {
      const result = loadDotenv({ path });
      if (verbose) {
        console.log(`[DEBUG] Loaded config from ${name}: ${path}`);
      }
      return path;
    }
  }

  if (verbose) {
    console.log('[DEBUG] No config file found in any location');
    console.log('[DEBUG] Run "openbroker setup" to configure');
  }

  return null;
}

// Load config on module import
const loadedConfigPath = loadEnvFile();

/**
 * Ensure the global config directory exists
 */
export function ensureConfigDir(): string {
  if (!existsSync(GLOBAL_CONFIG_DIR)) {
    mkdirSync(GLOBAL_CONFIG_DIR, { recursive: true, mode: 0o700 });
  }
  return GLOBAL_CONFIG_DIR;
}

/**
 * Get the path where config was loaded from, or where it should be saved
 */
export function getConfigPath(): string {
  return loadedConfigPath || GLOBAL_ENV_PATH;
}

export function loadConfig(): OpenBrokerConfig {
  let privateKey = process.env.HYPERLIQUID_PRIVATE_KEY;
  let isReadOnly = false;

  if (!privateKey) {
    // Use default read-only key for info commands
    privateKey = DEFAULT_READ_ONLY_KEY;
    isReadOnly = true;

    // Show warning once
    if (!readOnlyWarningShown) {
      readOnlyWarningShown = true;
      console.log('\x1b[33m⚠️  Not configured for trading. Run "openbroker setup" to enable trades.\x1b[0m\n');
    }
  }

  if (!privateKey.startsWith('0x') || privateKey.length !== 66) {
    throw new Error('HYPERLIQUID_PRIVATE_KEY must be a 64-character hex string with 0x prefix');
  }

  const network = process.env.HYPERLIQUID_NETWORK || 'mainnet';
  const baseUrl = network === 'testnet' ? TESTNET_URL : MAINNET_URL;

  // Use open-broker address by default, but allow override for custom builders
  const builderAddress = (process.env.BUILDER_ADDRESS || OPEN_BROKER_BUILDER_ADDRESS).toLowerCase();
  const builderFee = parseInt(process.env.BUILDER_FEE || '10', 10); // default 1 bps
  const slippageBps = parseInt(process.env.SLIPPAGE_BPS || '50', 10); // default 0.5%

  // Derive the wallet address from private key
  const wallet = privateKeyToAccount(privateKey as `0x${string}`);
  const walletAddress = wallet.address.toLowerCase();

  // Account address can be different if using an API wallet
  const accountAddress = process.env.HYPERLIQUID_ACCOUNT_ADDRESS?.toLowerCase();

  // Determine if this is an API wallet setup
  const isApiWallet = accountAddress !== undefined && accountAddress !== walletAddress;

  return {
    baseUrl,
    privateKey: privateKey as `0x${string}`,
    walletAddress,
    accountAddress: accountAddress || walletAddress,
    isApiWallet,
    isReadOnly,
    builderAddress,
    builderFee,
    slippageBps,
  };
}

/**
 * Check if the current config is read-only (no trading capability)
 */
export function isConfigured(): boolean {
  return !!process.env.HYPERLIQUID_PRIVATE_KEY;
}

export function getNetwork(): 'mainnet' | 'testnet' {
  const network = process.env.HYPERLIQUID_NETWORK || 'mainnet';
  return network === 'testnet' ? 'testnet' : 'mainnet';
}

export function isMainnet(): boolean {
  return getNetwork() === 'mainnet';
}
