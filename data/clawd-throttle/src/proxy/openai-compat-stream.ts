import type { ProxyRequest, StreamingProxyResult, ProviderConfig } from './types.js';
import { performance } from 'node:perf_hooks';

/**
 * Generic streaming proxy for OpenAI Chat Completions-compatible APIs.
 * Returns the raw Response with SSE body — caller owns parsing.
 */
export async function callOpenAiCompatStream(
  request: ProxyRequest,
  providerConfig: ProviderConfig,
): Promise<StreamingProxyResult> {
  const url = `${providerConfig.baseUrl}/chat/completions`;
  const startMs = performance.now();

  // Build messages array with system prompt as first message
  const messages: Array<{ role: string; content: string }> = [];
  if (request.systemPrompt) {
    messages.push({ role: 'system', content: request.systemPrompt });
  }
  for (const m of request.messages) {
    messages.push({ role: m.role, content: m.content });
  }

  const body: Record<string, unknown> = {
    model: request.modelId,
    messages,
    max_tokens: request.maxTokens,
    stream: true,
  };

  if (request.temperature !== undefined) {
    body.temperature = request.temperature;
  }

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (providerConfig.apiKey) {
    headers['Authorization'] = `Bearer ${providerConfig.apiKey}`;
  }

  const response = await fetch(url, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`OpenAI-compat streaming API error (${response.status}): ${errorText}`);
  }

  return {
    response,
    modelId: request.modelId,
    provider: request.provider,
    startMs,
  };
}
