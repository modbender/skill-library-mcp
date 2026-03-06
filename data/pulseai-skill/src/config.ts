import { createMainnetClient, type PresetPulseClient } from '@pulseai/sdk';
import { privateKeyToAccount } from 'viem/accounts';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

type PulseConfig = {
  privateKey?: `0x${string}`;
};

const CONFIG_PATH = path.join(os.homedir(), '.pulse', 'config.json');

let _client: PresetPulseClient | undefined;

export function loadConfig(): PulseConfig {
  try {
    if (!fs.existsSync(CONFIG_PATH)) {
      return {};
    }

    const raw = fs.readFileSync(CONFIG_PATH, 'utf8').trim();
    if (!raw) {
      return {};
    }

    const parsed = JSON.parse(raw) as unknown;
    if (!parsed || typeof parsed !== 'object') {
      return {};
    }

    const privateKey = (parsed as Record<string, unknown>).privateKey;
    if (typeof privateKey !== 'string' || !privateKey) {
      return {};
    }

    return { privateKey: privateKey as `0x${string}` };
  } catch (e) {
    throw new Error(
      `Failed to load Pulse config from ${CONFIG_PATH}: ${e instanceof Error ? e.message : String(e)}`,
    );
  }
}

export function saveConfig(config: PulseConfig): void {
  try {
    fs.mkdirSync(path.dirname(CONFIG_PATH), { recursive: true });
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2) + '\n', 'utf8');
  } catch (e) {
    throw new Error(
      `Failed to save Pulse config to ${CONFIG_PATH}: ${e instanceof Error ? e.message : String(e)}`,
    );
  }
}

function getPrivateKey(): `0x${string}` | undefined {
  if (process.env.PULSE_PRIVATE_KEY) {
    return process.env.PULSE_PRIVATE_KEY as `0x${string}`;
  }
  return loadConfig().privateKey;
}

/**
 * Create a Pulse client from PULSE_PRIVATE_KEY env var.
 * All contract addresses and indexer URL are embedded in the SDK.
 */
export function getClient(): PresetPulseClient {
  if (_client) return _client;

  const key = getPrivateKey();
  if (!key) {
    throw new Error(
      'No wallet private key found. Set PULSE_PRIVATE_KEY or run `pulse wallet generate`.\n' +
      'Config fallback path: ~/.pulse/config.json',
    );
  }

  const account = privateKeyToAccount(key);
  _client = createMainnetClient({ account });
  return _client;
}

/** Get a read-only client (no private key needed). */
export function getReadClient(): PresetPulseClient {
  if (_client) return _client;

  // Try with key first, fall back to read-only
  const key = getPrivateKey();
  if (key) {
    return getClient();
  }

  _client = createMainnetClient();
  return _client;
}

/** Get the wallet address from the configured private key. */
export function getAddress(): `0x${string}` {
  const key = getPrivateKey();
  if (!key) {
    throw new Error('No wallet private key found. Set PULSE_PRIVATE_KEY or run `pulse wallet generate`.');
  }
  return privateKeyToAccount(key).address;
}
