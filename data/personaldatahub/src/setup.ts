/**
 * Hub discovery and setup utilities.
 *
 * Used by the skill to detect a running PersonalDataHub.
 * All communication is over HTTP — no dependency on the main
 * PersonalDataHub source.
 */

import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { homedir } from 'node:os';

export interface HealthCheckResult {
  ok: boolean;
  version?: string;
}

export interface HubConfig {
  hubUrl: string;
  hubDir?: string;
}

/** Path to the config file written by `npx pdh init`. */
export const CONFIG_PATH = join(homedir(), '.pdh', 'config.json');

/**
 * Read config from ~/.pdh/config.json.
 * Returns null if the file doesn't exist or is malformed.
 */
export function readConfig(): HubConfig | null {
  try {
    if (!existsSync(CONFIG_PATH)) return null;
    const raw = readFileSync(CONFIG_PATH, 'utf-8');
    const parsed = JSON.parse(raw);
    if (parsed.hubUrl) return parsed as HubConfig;
    return null;
  } catch {
    return null;
  }
}

/**
 * Check if a PersonalDataHub is reachable at the given URL.
 * Hits GET /health and returns the result.
 */
export async function checkHub(hubUrl: string, timeoutMs = 3000): Promise<HealthCheckResult> {
  const url = hubUrl.replace(/\/+$/, '');
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);

    const res = await fetch(`${url}/health`, {
      signal: controller.signal,
    });
    clearTimeout(timer);

    if (!res.ok) {
      return { ok: false };
    }

    const body = await res.json() as { ok?: boolean; version?: string };
    return {
      ok: body.ok === true,
      version: body.version,
    };
  } catch {
    return { ok: false };
  }
}

/** Common default hub URLs to probe during discovery. */
export const DEFAULT_HUB_URLS = [
  'http://localhost:3000',
  'http://localhost:7007',
  'http://127.0.0.1:3000',
  'http://127.0.0.1:7007',
];

/**
 * Try to discover a running PersonalDataHub by probing common URLs.
 * Returns the first URL that responds to /health, or null.
 */
export async function discoverHub(): Promise<string | null> {
  for (const url of DEFAULT_HUB_URLS) {
    const result = await checkHub(url, 2000);
    if (result.ok) {
      return url;
    }
  }
  return null;
}
