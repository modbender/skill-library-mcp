/**
 * Configuration Schema for Memory-as-Tools v2
 *
 * v2 uses QMD for search - no OpenAI API key required!
 */

import { Type, type Static } from '@sinclair/typebox';
import { MEMORY_CATEGORIES } from './types.js';

export const memoryToolsConfigSchema = Type.Object({
  // Path to store memories (markdown files)
  memoriesPath: Type.Optional(Type.String()),

  // Legacy v1 database path (for migration detection)
  legacyDbPath: Type.Optional(Type.String()),

  // Auto-inject standing instructions at conversation start
  autoInjectInstructions: Type.Optional(Type.Boolean()),

  // Auto-migrate legacy v1 database on startup
  autoMigrateLegacy: Type.Optional(Type.Boolean()),

  // QMD collection name
  qmdCollection: Type.Optional(Type.String()),
});

export type MemoryToolsConfig = Static<typeof memoryToolsConfigSchema>;

/**
 * Expand environment variables in a string.
 * Supports ${VAR_NAME} syntax.
 */
function expandEnvVars(value: string): string {
  return value.replace(/\$\{([^}]+)\}/g, (_, varName) => {
    return process.env[varName] ?? '';
  });
}

/**
 * Expand ~ to home directory
 */
function expandPath(p: string): string {
  if (p.startsWith('~/')) {
    return p.replace('~', process.env.HOME || process.env.USERPROFILE || '');
  }
  return p;
}

export function parseConfig(raw: unknown): MemoryToolsConfig {
  const config = (raw ?? {}) as Record<string, unknown>;

  // Default paths
  let memoriesPath = (config.memoriesPath as string) || '~/.openclaw/memories';
  let legacyDbPath = (config.legacyDbPath as string) || (config.dbPath as string) || '~/.openclaw/memory/tools';

  // Expand environment variables and paths
  memoriesPath = expandPath(expandEnvVars(memoriesPath));
  legacyDbPath = expandPath(expandEnvVars(legacyDbPath));

  return {
    memoriesPath,
    legacyDbPath,
    autoInjectInstructions: config.autoInjectInstructions === true,
    autoMigrateLegacy: config.autoMigrateLegacy === true,
    qmdCollection: (config.qmdCollection as string) || 'memories',
  };
}

export { MEMORY_CATEGORIES };
