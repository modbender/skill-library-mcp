// SPDX-License-Identifier: MIT
/**
 * @ultrathink-solutions/openclaw-logfire
 *
 * Pydantic Logfire observability plugin for OpenClaw.
 * OTEL GenAI semantic convention compliant.
 *
 * Minimal setup:
 *   1. Set LOGFIRE_TOKEN env var
 *   2. Add to openclaw.json:
 *      { "plugins": { "entries": { "openclaw-logfire": { "enabled": true, "config": {} } } } }
 *   3. Restart OpenClaw
 */

import { resolveConfig } from './config.js';
import { initializeOtel } from './otel.js';
import { handleBeforeAgentStart } from './hooks/before-agent-start.js';
import { handleBeforeToolCall } from './hooks/before-tool-call.js';
import { handleToolResultPersist } from './hooks/tool-result-persist.js';
import { handleAgentEnd } from './hooks/agent-end.js';
import { handleMessageReceived } from './hooks/message-received.js';
import type { NodeSDK } from '@opentelemetry/sdk-node';

/**
 * Minimal OpenClaw plugin API contract.
 * We type only what we actually use to avoid tight coupling
 * to a specific OpenClaw version.
 */
interface PluginApi {
  /** Full application config (openclaw.json). */
  config?: Record<string, unknown>;
  /** Plugin-specific config from plugins.entries.<id>.config. */
  pluginConfig?: Record<string, unknown>;
  logger: {
    info(msg: string): void;
    debug(msg: string): void;
    warn(msg: string): void;
    error(msg: string): void;
  };
  on(event: string, handler: (event: never) => void): void;
  registerService(service: {
    id: string;
    start: () => void;
    stop: () => void | Promise<void>;
  }): void;
}

let sdk: NodeSDK | null = null;

export default function register(api: PluginApi): void {
  // pluginConfig is the plugin-specific config from plugins.entries.<id>.config.
  // api.config is the full openclaw.json — DO NOT use it for plugin settings.
  const config = resolveConfig(api.pluginConfig);

  // Validate token
  if (!config.token) {
    api.logger.error(
      'Logfire plugin disabled: LOGFIRE_TOKEN not set. ' +
        'Export it as an env var or set plugins.entries.openclaw-logfire.config.token',
    );
    return;
  }

  // Initialize OTEL SDK
  try {
    sdk = initializeOtel(config);
  } catch (err) {
    api.logger.error(`Logfire plugin init failed: ${err}`);
    return;
  }

  // Register lifecycle hooks
  api.on('before_agent_start', ((event: never) => {
    try {
      handleBeforeAgentStart(event, config);
    } catch (err) {
      api.logger.warn(`Logfire before_agent_start error: ${err}`);
    }
  }) as (event: never) => void);

  api.on('before_tool_call', ((event: never) => {
    try {
      handleBeforeToolCall(event, config);
    } catch (err) {
      api.logger.warn(`Logfire before_tool_call error: ${err}`);
    }
  }) as (event: never) => void);

  api.on('tool_result_persist', ((event: never) => {
    try {
      handleToolResultPersist(event, config);
    } catch (err) {
      api.logger.warn(`Logfire tool_result_persist error: ${err}`);
    }
  }) as (event: never) => void);

  api.on('agent_end', ((event: never) => {
    try {
      handleAgentEnd(event, config, api.logger);
    } catch (err) {
      api.logger.warn(`Logfire agent_end error: ${err}`);
    }
  }) as (event: never) => void);

  api.on('message_received', ((event: never) => {
    try {
      handleMessageReceived(event, config);
    } catch (err) {
      api.logger.warn(`Logfire message_received error: ${err}`);
    }
  }) as (event: never) => void);

  // Register service for clean shutdown
  api.registerService({
    id: 'logfire-otel',
    start: () => {
      const region = config.region === 'eu' ? 'EU' : 'US';
      api.logger.info(
        `Logfire: exporting to ${region} (service: ${config.serviceName}, env: ${config.environment})`,
      );
    },
    stop: async () => {
      if (sdk) {
        await sdk.shutdown();
        api.logger.info('Logfire: OTEL SDK shut down');
      }
    },
  });
}
