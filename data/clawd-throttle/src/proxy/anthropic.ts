import type { ProxyRequest, ProxyResponse } from './types.js';
import type { ThrottleConfig } from '../config/types.js';
import { performance } from 'node:perf_hooks';
import { buildAnthropicAuthHeaders } from './anthropic-auth.js';

export async function callAnthropic(
  request: ProxyRequest,
  config: ThrottleConfig,
): Promise<ProxyResponse> {
  const url = `${config.anthropic.baseUrl}/v1/messages`;
  const startMs = performance.now();

  const body: Record<string, unknown> = {
    model: request.modelId,
    max_tokens: request.maxTokens,
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

  const data = await response.json() as {
    content: Array<{ type: string; text: string }>;
    usage: { input_tokens: number; output_tokens: number };
    stop_reason: string;
  };

  const latencyMs = performance.now() - startMs;

  const textContent = data.content
    .filter(c => c.type === 'text')
    .map(c => c.text)
    .join('');

  return {
    content: textContent,
    inputTokens: data.usage.input_tokens,
    outputTokens: data.usage.output_tokens,
    modelId: request.modelId,
    provider: 'anthropic',
    latencyMs: Math.round(latencyMs),
    finishReason: data.stop_reason,
  };
}
