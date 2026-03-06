import type { ProxyRequest, ProxyResponse, ProviderConfig } from './types.js';
import { performance } from 'node:perf_hooks';

/**
 * Generic proxy for OpenAI Chat Completions-compatible APIs.
 * Works for: OpenAI, DeepSeek, xAI/Grok, Moonshot/Kimi, Mistral, Ollama.
 */
export async function callOpenAiCompat(
  request: ProxyRequest,
  providerConfig: ProviderConfig,
): Promise<ProxyResponse> {
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
  };

  if (request.temperature !== undefined) {
    body.temperature = request.temperature;
  }

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  // Omit Authorization header for Ollama (no auth needed)
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
    throw new Error(`OpenAI-compat API error (${response.status}): ${errorText}`);
  }

  const data = await response.json() as {
    choices: Array<{
      message: { content: string };
      finish_reason: string;
    }>;
    usage: {
      prompt_tokens: number;
      completion_tokens: number;
    };
  };

  const latencyMs = performance.now() - startMs;

  return {
    content: data.choices[0]?.message.content ?? '',
    inputTokens: data.usage?.prompt_tokens ?? 0,
    outputTokens: data.usage?.completion_tokens ?? 0,
    modelId: request.modelId,
    provider: request.provider,
    latencyMs: Math.round(latencyMs),
    finishReason: data.choices[0]?.finish_reason ?? 'stop',
  };
}
