import type { ProxyRequest, StreamingProxyResult } from './types.js';
import type { ThrottleConfig } from '../config/types.js';
import { performance } from 'node:perf_hooks';
import { buildAnthropicAuthHeaders } from './anthropic-auth.js';

/**
 * Streaming variant of callAnthropic. Returns the raw Response
 * with an SSE body stream instead of parsing it.
 */
export async function callAnthropicStream(
  request: ProxyRequest,
  config: ThrottleConfig,
): Promise<StreamingProxyResult> {
  const url = `${config.anthropic.baseUrl}/v1/messages`;
  const startMs = performance.now();

  const body: Record<string, unknown> = {
    model: request.modelId,
    max_tokens: request.maxTokens,
    stream: true,
    messages: request.messages.map(m => ({
      role: m.role,
      content: m.content,
    })),
  };

  if (request.systemPrompt) {
    body.system = request.systemPrompt;
  }
  if (request.temperature !== undefined) {
    body.temperature = request.temperature;
  }

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...buildAnthropicAuthHeaders(config),
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Anthropic API error (${response.status}): ${errorText}`);
  }

  return {
    response,
    modelId: request.modelId,
    provider: 'anthropic',
    startMs,
  };
}
