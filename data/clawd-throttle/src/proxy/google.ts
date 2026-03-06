import type { ProxyRequest, ProxyResponse } from './types.js';
import type { ThrottleConfig } from '../config/types.js';
import { performance } from 'node:perf_hooks';

export async function callGoogle(
  request: ProxyRequest,
  config: ThrottleConfig,
): Promise<ProxyResponse> {
  const url = `${config.google.baseUrl}/v1beta/models/${request.modelId}:generateContent?key=${config.google.apiKey}`;
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

  const data = await response.json() as {
    candidates: Array<{
      content: { parts: Array<{ text: string }> };
      finishReason: string;
    }>;
    usageMetadata: {
      promptTokenCount: number;
      candidatesTokenCount: number;
    };
  };

  const latencyMs = performance.now() - startMs;

  const textContent = data.candidates[0]?.content.parts
    .map(p => p.text)
    .join('') ?? '';

  return {
    content: textContent,
    inputTokens: data.usageMetadata.promptTokenCount,
    outputTokens: data.usageMetadata.candidatesTokenCount,
    modelId: request.modelId,
    provider: 'google',
    latencyMs: Math.round(latencyMs),
    finishReason: data.candidates[0]?.finishReason ?? 'unknown',
  };
}
