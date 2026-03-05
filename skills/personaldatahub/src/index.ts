/**
 * PersonalDataHub — OpenClaw skill for interacting with PersonalDataHub.
 *
 * Registers tools that let the agent pull personal data and propose
 * outbound actions through the PersonalDataHub access control gateway.
 *
 * Config resolution order:
 *   1. Plugin config (hubUrl passed directly)
 *   2. Environment variable (PDH_HUB_URL)
 *   3. Config file (~/.pdh/config.json, written by npx pdh init)
 *   4. Auto-discovery (probe localhost)
 */

import { HubClient } from './hub-client.js';
import { createPullTool, createProposeTool } from './tools.js';
import { PERSONAL_DATA_SYSTEM_PROMPT } from './prompts.js';
import { discoverHub, readConfig } from './setup.js';

export interface PersonalDataHubPluginConfig {
  hubUrl: string;
}

export default {
  id: 'personaldatahub',
  name: 'Personal Data Hub',
  description: 'Unified interface to personal data through PersonalDataHub access control gateway',

  configSchema: {
    safeParse(value: unknown) {
      if (!value || typeof value !== 'object' || Array.isArray(value)) {
        return {
          success: false as const,
          error: { issues: [{ path: [], message: 'expected config object' }] },
        };
      }
      const cfg = value as Record<string, unknown>;
      if (!cfg.hubUrl || typeof cfg.hubUrl !== 'string') {
        return {
          success: false as const,
          error: { issues: [{ path: ['hubUrl'], message: 'hubUrl is required and must be a string' }] },
        };
      }
      return { success: true as const, data: value };
    },
    jsonSchema: {
      type: 'object',
      additionalProperties: false,
      properties: {
        hubUrl: { type: 'string' },
      },
      required: ['hubUrl'],
    },
  },

  async register(api: {
    pluginConfig?: Record<string, unknown>;
    logger: { info: (msg: string) => void; warn: (msg: string) => void; error: (msg: string) => void };
    registerTool: (tool: unknown) => void;
    on: (hook: string, handler: (event: unknown) => Promise<unknown>) => void;
  }) {
    let config = api.pluginConfig as PersonalDataHubPluginConfig | undefined;

    // Step 2: Check environment variable
    if (!config?.hubUrl) {
      const envHubUrl = process.env.PDH_HUB_URL;
      if (envHubUrl) {
        config = { hubUrl: envHubUrl };
        api.logger.info(`PersonalDataHub: Configured from environment variables (hub: ${envHubUrl})`);
      }
    }

    // Step 3: Check config file (~/.pdh/config.json)
    if (!config?.hubUrl) {
      const cfg = readConfig();
      if (cfg) {
        config = { hubUrl: cfg.hubUrl };
        api.logger.info(`PersonalDataHub: Configured from config file (hub: ${cfg.hubUrl})`);
      }
    }

    // Step 4: Auto-discovery — probe localhost
    if (!config?.hubUrl) {
      api.logger.info('PersonalDataHub: Config incomplete, attempting auto-discovery...');

      try {
        const hubUrl = await discoverHub();
        if (hubUrl) {
          config = { hubUrl };
          api.logger.info(`PersonalDataHub: Discovered hub at ${hubUrl}`);
        }
      } catch (err) {
        api.logger.warn(
          `PersonalDataHub: Auto-discovery failed: ${(err as Error).message}`,
        );
      }
    }

    if (!config?.hubUrl) {
      api.logger.warn(
        'PersonalDataHub: Missing hubUrl. Could not find a running hub.\n' +
        '  To set up PersonalDataHub:\n' +
        '  1. Run: npx pdh init\n' +
        '  2. Run: npx pdh start\n' +
        '  3. Restart the agent — it will auto-connect.\n' +
        '  Or configure manually: { "hubUrl": "http://localhost:3000" }',
      );
      return;
    }

    const client = new HubClient({
      hubUrl: config.hubUrl,
    });

    api.logger.info(`PersonalDataHub: Registering tools (hub: ${config.hubUrl})`);

    api.registerTool(createPullTool(client));
    api.registerTool(createProposeTool(client));

    api.on('before_agent_start', async (_event: unknown) => {
      return { systemPromptAppend: PERSONAL_DATA_SYSTEM_PROMPT };
    });
  },
};

// Re-export for direct usage
export { HubClient, HubApiError } from './hub-client.js';
export type { HubClientConfig, PullParams, ProposeParams, PullResult, ProposeResult } from './hub-client.js';
export { createPullTool, createProposeTool } from './tools.js';
export { PERSONAL_DATA_SYSTEM_PROMPT } from './prompts.js';
export { checkHub, discoverHub, readConfig } from './setup.js';
