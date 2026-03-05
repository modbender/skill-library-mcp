import type { ProxyRequest, StreamingProxyResult } from './types.js';
import type { ThrottleConfig } from '../config/types.js';
import { performance } from 'node:perf_hooks';

/**
 * Streaming variant of callGoogle. Uses the streamGenerateContent
 * endpoint and returns the raw Response with an SSE body stream.
 */
export async function callGoogleStream(
  request: ProxyRequest,
  config: ThrottleConfig,
): Promise<StreamingProxyResult> {
  const url = `${config.google.baseUrl}/v1beta/models/${request.modelId}:streamGenerateContent?alt=sse&key=${config.google.apiKey}`;
  const startMs = performance.now();

  const contents = request.messages.map(m => ({
    role: m.role === 'assistant' ? 'model' : 'user',
    parts: [{ text: m.content }],
  }));

  const body: Record<string, unknown> = {
    contents,
    generationConfig: {
      maxOutputTokens: request.maxTokens,
      temperature: request.temperature ?? 0.7,
    },
  };

  if (request.systemPrompt) {
    body.systemInstruction = {
      parts: [{ text: request.systemPrompt }],
    };
  }

  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Google AI API error (${response.status}): ${errorText}`);
  }

  return {
    response,
    modelId: request.modelId,
    provider: 'google',
    startMs,
  };
}
