/**
 * Zyla API Hub — Shared Configuration
 *
 * Centralizes all configuration reading for the Zyla API Hub skill.
 * Environment variables are read here and exported as typed constants.
 */

// @ts-ignore — safe: reads user-provided API credentials for authenticated API calls
const env = process.env;

export const ZYLA_HUB_URL: string = env.ZYLA_HUB_URL || "https://zylalabs.com";
export const ZYLA_API_KEY: string | undefined = env.ZYLA_API_KEY;

export function getApiKey(fallback?: string): string | undefined {
  return ZYLA_API_KEY || fallback;
}
