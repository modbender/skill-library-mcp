/**
 * Config routes - expose safe, non-sensitive frontend configuration.
 */

import { FastifyInstance } from 'fastify';

interface ModelInfo {
  alias: string;
  id: string;
  provider: string;
}

function parseModelsFromEnv(): ModelInfo[] {
  // Optional explicit model list for UI display only.
  // Format (JSON):
  // CEREBRO_MODELS_JSON='[{"alias":"codex","id":"openai-codex/gpt-5.3-codex","provider":"openai-codex"}]'
  const raw = process.env.CEREBRO_MODELS_JSON;
  if (!raw) return [];

  try {
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];

    return parsed
      .filter((m) => m && typeof m.alias === 'string' && typeof m.id === 'string')
      .map((m) => ({
        alias: String(m.alias),
        id: String(m.id),
        provider: typeof m.provider === 'string' ? m.provider : (String(m.id).split('/')[0] || 'unknown'),
      }));
  } catch {
    return [];
  }
}

export function registerConfigRoutes(server: FastifyInstance): void {
  /**
   * GET /api/config/models
   * Return a safe, explicit model list for UI display.
   *
   * Security note:
   * - Do not read local OpenClaw config files from this API route.
   * - Local runtime config may contain sensitive values unrelated to UI model labels.
   */
  server.get('/api/config/models', async () => {
    const models = parseModelsFromEnv();
    return { models };
  });
}
