/**
 * Configuration loader for OpenClaw Avatar
 *
 * Loads configuration from:
 * 1. Environment variables (.env) for secrets
 * 2. avatar.config.json for user configuration
 * 3. Default values for anything not specified
 */

import { readFileSync, existsSync } from 'fs';
import { resolve } from 'path';
import type { Config, ClientConfig } from './schema.js';
import { validateConfig } from './schema.js';
import { DEFAULT_CONFIG, DEFAULT_FILLERS, DEFAULT_STREAMDECK_COLORS, DEFAULT_BUTTON_PROMPTS } from './defaults.js';

// Load dotenv if available
try {
  const dotenv = await import('dotenv');
  dotenv.config();
} catch {
  // dotenv not installed, use process.env directly
}

function loadConfigFile(configPath: string): Partial<Config> {
  if (!existsSync(configPath)) {
    return {};
  }

  try {
    const content = readFileSync(configPath, 'utf8');
    return JSON.parse(content);
  } catch (err) {
    console.warn(`Warning: Failed to parse ${configPath}:`, (err as Error).message);
    return {};
  }
}

function deepMerge<T extends Record<string, unknown>>(target: T, source: Partial<T>): T {
  const result = { ...target };

  for (const key of Object.keys(source) as Array<keyof T>) {
    const sourceValue = source[key];
    const targetValue = target[key];

    if (sourceValue !== undefined) {
      if (
        typeof sourceValue === 'object' &&
        sourceValue !== null &&
        !Array.isArray(sourceValue) &&
        typeof targetValue === 'object' &&
        targetValue !== null &&
        !Array.isArray(targetValue)
      ) {
        result[key] = deepMerge(
          targetValue as Record<string, unknown>,
          sourceValue as Record<string, unknown>
        ) as T[keyof T];
      } else {
        result[key] = sourceValue as T[keyof T];
      }
    }
  }

  return result;
}

export function loadConfig(configPath?: string): Config {
  // Determine config file path
  const configFilePath = configPath || resolve(process.cwd(), 'avatar.config.json');

  // Load user config file
  const userConfig = loadConfigFile(configFilePath);

  // Build secrets from environment variables
  const secrets = {
    simliApiKey: process.env.SIMLI_API_KEY || '',
    elevenLabsApiKey: process.env.ELEVENLABS_API_KEY || '',
    elevenLabsVoiceId: process.env.ELEVENLABS_VOICE_ID,
    slackBotToken: process.env.SLACK_BOT_TOKEN,
    openclawToken: process.env.OPENCLAW_TOKEN,
  };

  // Merge configs: defaults <- user config <- secrets
  const config: Config = {
    ...deepMerge(DEFAULT_CONFIG, userConfig as Partial<typeof DEFAULT_CONFIG>),
    secrets,
  };

  // Apply default fillers if not provided
  if (!userConfig.fillers) {
    config.fillers = DEFAULT_FILLERS;
  }

  // Apply default StreamDeck colors and prompts
  if (config.integrations.streamDeck.enabled) {
    config.integrations.streamDeck.colors = {
      ...DEFAULT_STREAMDECK_COLORS,
      ...config.integrations.streamDeck.colors,
    };
    config.integrations.streamDeck.buttonPrompts = {
      ...DEFAULT_BUTTON_PROMPTS,
      ...config.integrations.streamDeck.buttonPrompts,
    };
  }

  // Validate configuration
  validateConfig(config);

  return config;
}

/**
 * Get configuration safe to send to the client (no secrets)
 */
export function getClientConfig(config: Config): ClientConfig {
  return {
    app: config.app,
    avatars: config.avatars,
    languages: config.languages,
    fillers: config.fillers,
    simliApiKey: config.secrets.simliApiKey,
  };
}

// Export types
export * from './schema.js';
export { DEFAULT_CONFIG, DEFAULT_FILLERS, DEFAULT_STREAMDECK_COLORS, DEFAULT_BUTTON_PROMPTS } from './defaults.js';
