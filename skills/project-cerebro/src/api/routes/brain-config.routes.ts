/**
 * Brain config routes
 */

import { FastifyInstance } from 'fastify';
import { BrainConfigRepository } from '../../data/repositories/brain-config.repository';

function getDefaultBrainConfig(brainId: string): Record<string, any> {
  const base = {
    systemPrompt: '',
    defaultModel: '',
    tools: { enabled: {}, config: {} },
    skills: [],
    reportTemplate: '',
    reportFormat: 'json',
  } as any;

  switch (brainId) {
    case 'school':
      return {
        ...base,
        tools: {
          enabled: { calendar: true, todoist: true },
          // Configure merged calendar ids in the UI or via env-driven schedule script.
          config: { calendar: { mergedCalendars: 'primary' } },
        },
      };
    case 'personal':
      return {
        ...base,
        tools: {
          enabled: { calendar: true, weather: true },
          config: { calendar: { mergedCalendars: 'primary' } },
        },
      };
    case 'research':
      return {
        ...base,
        tools: { enabled: { web_search: true, research_storage: true }, config: {} },
      };
    case 'money':
      return {
        ...base,
        tools: { enabled: { web_search: true, email: true }, config: { email: { defaultAccount: 'office' } } },
      };
    case 'job':
      return {
        ...base,
        tools: { enabled: { jobspy: true, agent_browser: true, email: true }, config: { email: { defaultAccount: 'office' } } },
      };
    default:
      return base;
  }
}

export function registerBrainConfigRoutes(
  server: FastifyInstance,
  brainConfigRepo: BrainConfigRepository
): void {
  /**
   * GET /api/brains/:brainId/config
   * Get brain config
   */
  server.get<{ Params: { brainId: string } }>(
    '/api/brains/:brainId/config',
    async (request, reply) => {
      const { brainId } = request.params;
      const config = brainConfigRepo.get(brainId) || getDefaultBrainConfig(brainId);
      return { config: JSON.stringify(config) };
    }
  );

  /**
   * POST /api/brains/:brainId/config
   * Save brain config
   */
  server.post<{
    Params: { brainId: string };
    Body: { config: string };
  }>(
    '/api/brains/:brainId/config',
    async (request, reply) => {
      const { brainId } = request.params;
      const { config } = request.body;

      let parsed: Record<string, any> = {};
      try {
        parsed = JSON.parse(config || '{}');
      } catch {
        reply.code(400);
        return { error: 'Invalid JSON config' };
      }

      brainConfigRepo.set(brainId, parsed);
      return { success: true };
    }
  );
}
