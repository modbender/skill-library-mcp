import { z } from 'zod';
import crypto from 'node:crypto';
import type { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import type { ThrottleConfig } from '../config/types.js';
import type { DimensionWeights } from '../classifier/types.js';
import type { ModelRegistry, RoutingTable } from '../router/model-registry.js';
import type { LogWriter } from '../logging/writer.js';
import type { LogReader } from '../logging/reader.js';
import { classifyPrompt } from '../classifier/engine.js';
import { routeRequest } from '../router/engine.js';
import { detectOverrides, FORCE_MODEL_MAP } from '../router/overrides.js';
import { dispatch } from '../proxy/dispatcher.js';
import { estimateCost } from '../logging/writer.js';
import { computeStats } from '../logging/stats.js';
import { hashPrompt } from '../utils/hash.js';
import { saveConfig } from '../config/index.js';
import { createLogger } from '../utils/logger.js';

const log = createLogger('tools');

// Build the forceModel enum from FORCE_MODEL_MAP keys
const forceModelKeys = Object.keys(FORCE_MODEL_MAP) as [string, ...string[]];

export function registerTools(
  server: McpServer,
  config: ThrottleConfig,
  registry: ModelRegistry,
  weights: DimensionWeights,
  logWriter: LogWriter,
  logReader: LogReader,
  routingTable: RoutingTable,
): void {
  // Tool 1: route_request - Primary routing proxy
  server.tool(
    'route_request',
    'Send a prompt to the cheapest capable LLM model based on complexity classification. Returns the LLM response plus routing metadata.',
    {
      messages: z.array(z.object({
        role: z.enum(['user', 'assistant']),
        content: z.string(),
      })).min(1).describe('Conversation messages in chronological order'),

      systemPrompt: z.string().optional()
        .describe('System prompt to prepend to the conversation'),

      maxTokens: z.number().int().positive().optional().default(4096)
        .describe('Maximum tokens to generate'),

      temperature: z.number().min(0).max(1).optional().default(0.7)
        .describe('Sampling temperature'),

      forceModel: z.enum(forceModelKeys).optional()
        .describe('Force routing to a specific model, bypassing classification. Accepts aliases like "opus", "gpt-5", "deepseek", "grok", "kimi", "mistral", "local", etc.'),

      parentRequestId: z.string().optional()
        .describe('Parent request ID for sub-agent tier inheritance'),
    },
    async ({ messages, systemPrompt, maxTokens, temperature, forceModel, parentRequestId }) => {
      try {
        const lastUserMsg = messages.filter(m => m.role === 'user').pop();
        if (!lastUserMsg) {
          return { content: [{ type: 'text' as const, text: 'No user message found' }], isError: true };
        }

        const override = detectOverrides(messages, forceModel, parentRequestId, logReader);
        const classification = classifyPrompt(lastUserMsg.content, {
          messageCount: messages.length,
          systemPrompt,
        }, weights, config.classifier.thresholds);

        const decision = routeRequest(classification, config.mode, override, registry, config, routingTable);

        const proxyResponse = await dispatch({
          provider: decision.model.provider,
          modelId: decision.model.id,
          messages: messages.map(m => ({ role: m.role, content: m.content })),
          systemPrompt,
          maxTokens,
          temperature,
        }, config);

        const requestId = crypto.randomUUID();
        const cost = estimateCost(decision.model, proxyResponse.inputTokens, proxyResponse.outputTokens);

        logWriter.append({
          requestId,
          timestamp: new Date().toISOString(),
          promptHash: hashPrompt(lastUserMsg.content),
          compositeScore: classification.score,
          tier: classification.tier,
          selectedModel: decision.model.id,
          provider: decision.model.provider,
          mode: config.mode,
          override: decision.override,
          inputTokens: proxyResponse.inputTokens,
          outputTokens: proxyResponse.outputTokens,
          estimatedCostUsd: cost,
          latencyMs: proxyResponse.latencyMs,
          parentRequestId,
        });

        return {
          content: [{
            type: 'text' as const,
            text: JSON.stringify({
              response: proxyResponse.content,
              routing: {
                requestId,
                model: decision.model.displayName,
                tier: decision.tier,
                score: classification.score,
                mode: decision.mode,
                override: decision.override,
                reasoning: decision.reasoning,
                inputTokens: proxyResponse.inputTokens,
                outputTokens: proxyResponse.outputTokens,
                estimatedCostUsd: cost,
                latencyMs: proxyResponse.latencyMs,
              },
            }, null, 2),
          }],
        };
      } catch (err) {
        log.error('route_request failed', err);
        return {
          content: [{ type: 'text' as const, text: `Routing error: ${err instanceof Error ? err.message : String(err)}` }],
          isError: true,
        };
      }
    },
  );

  // Tool 2: classify_prompt - Diagnostic (no API call)
  server.tool(
    'classify_prompt',
    'Analyze prompt complexity and return classification scores without making an LLM call. Useful for understanding routing behavior.',
    {
      text: z.string().min(1).describe('The prompt text to classify'),
      messageCount: z.number().int().optional().default(1)
        .describe('Total messages in conversation for depth scoring'),
      systemPrompt: z.string().optional()
        .describe('System prompt content for signal scoring'),
    },
    async ({ text, messageCount, systemPrompt }) => {
      const classification = classifyPrompt(text, {
        messageCount,
        systemPrompt,
      }, weights, config.classifier.thresholds);

      const routingPreview: Record<string, string> = {};
      for (const mode of ['eco', 'standard', 'gigachad'] as const) {
        const decision = routeRequest(
          classification, mode,
          { kind: 'none' },
          registry,
          config,
          routingTable,
        );
        routingPreview[mode] = decision.model.displayName;
      }

      return {
        content: [{
          type: 'text' as const,
          text: JSON.stringify({
            tier: classification.tier,
            compositeScore: classification.score,
            classifiedInMs: classification.classifiedInMs,
            dimensions: classification.dimensions,
            routingPreview,
            thresholds: config.classifier.thresholds,
          }, null, 2),
        }],
      };
    },
  );

  // Tool 3: get_routing_stats - Cost tracking
  server.tool(
    'get_routing_stats',
    'Get routing statistics: total cost, estimated savings vs most-expensive model, and model/tier distribution for a time period.',
    {
      days: z.number().int().positive().optional().default(30)
        .describe('Lookback period in days'),
    },
    async ({ days }) => {
      const since = new Date();
      since.setDate(since.getDate() - days);
      const entries = logReader.readSince(since.toISOString());

      const baseline = registry.getMostExpensive();
      const stats = computeStats(entries, baseline);

      return {
        content: [{
          type: 'text' as const,
          text: JSON.stringify(stats, null, 2),
        }],
      };
    },
  );

  // Tool 4: get_config - Show current config (keys redacted)
  server.tool(
    'get_config',
    'View the current Clawd Throttle configuration. API keys are redacted for safety.',
    {},
    async () => {
      const redactKey = (key: string): string =>
        key ? '***' + key.slice(-4) : '(not set)';

      const safe = {
        mode: config.mode,
        configuredProviders: registry.getConfiguredProviders(config),
        anthropic: {
          apiKey: redactKey(config.anthropic.apiKey),
          baseUrl: config.anthropic.baseUrl,
          authType: config.anthropic.authType,
        },
        google: {
          apiKey: redactKey(config.google.apiKey),
          baseUrl: config.google.baseUrl,
        },
        openai: {
          apiKey: redactKey(config.openai.apiKey),
          baseUrl: config.openai.baseUrl,
        },
        deepseek: {
          apiKey: redactKey(config.deepseek.apiKey),
          baseUrl: config.deepseek.baseUrl,
        },
        xai: {
          apiKey: redactKey(config.xai.apiKey),
          baseUrl: config.xai.baseUrl,
        },
        moonshot: {
          apiKey: redactKey(config.moonshot.apiKey),
          baseUrl: config.moonshot.baseUrl,
        },
        mistral: {
          apiKey: redactKey(config.mistral.apiKey),
          baseUrl: config.mistral.baseUrl,
        },
        ollama: {
          apiKey: '(none required)',
          baseUrl: config.ollama.baseUrl,
        },
        logging: config.logging,
        classifier: config.classifier,
      };
      return {
        content: [{ type: 'text' as const, text: JSON.stringify(safe, null, 2) }],
      };
    },
  );

  // Tool 5: set_mode - Change routing mode at runtime
  server.tool(
    'set_mode',
    'Change the active routing mode. eco=cheapest, standard=balanced, gigachad=highest quality.',
    {
      mode: z.enum(['eco', 'standard', 'gigachad'])
        .describe('The routing mode to activate'),
    },
    async ({ mode }) => {
      const previousMode = config.mode;
      config.mode = mode;
      saveConfig({ mode });
      return {
        content: [{
          type: 'text' as const,
          text: `Routing mode changed from "${previousMode}" to "${mode}".`,
        }],
      };
    },
  );

  // Tool 6: get_recent_routing_log - Inspect recent decisions
  server.tool(
    'get_recent_routing_log',
    'View the most recent routing decisions. Shows which model was selected and why for each request.',
    {
      limit: z.number().int().positive().optional().default(10)
        .describe('Number of recent entries to return'),
    },
    async ({ limit }) => {
      const entries = logReader.tail(limit);
      const formatted = entries.map(e => ({
        requestId: e.requestId,
        timestamp: e.timestamp,
        tier: e.tier,
        score: e.compositeScore,
        model: e.selectedModel,
        mode: e.mode,
        override: e.override,
        tokens: { input: e.inputTokens, output: e.outputTokens },
        cost: `$${e.estimatedCostUsd.toFixed(4)}`,
        latency: `${e.latencyMs}ms`,
        parentRequestId: e.parentRequestId || null,
      }));

      return {
        content: [{
          type: 'text' as const,
          text: JSON.stringify({ entries: formatted, count: formatted.length }, null, 2),
        }],
      };
    },
  );
}
