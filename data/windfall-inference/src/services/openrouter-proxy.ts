import { config } from '../config';
import { InferenceRequest } from '../types';

const OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions';

// Models that cost more — charge premium price
const PREMIUM_MODELS = [
  'anthropic/claude',
  'openai/gpt-4',
  'openai/o1',
  'google/gemini-2',
];

export function isPremiumModel(model: string): boolean {
  return PREMIUM_MODELS.some(prefix => model.startsWith(prefix));
}

export function getModelPrice(model: string): number {
  if (isPremiumModel(model)) return config.premiumPricePerRequest;
  return config.pricePerRequest;
}

export interface OpenRouterResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: Array<{
    index: number;
    message: { role: string; content: string };
    finish_reason: string;
  }>;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

export async function callOpenRouter(
  request: InferenceRequest
): Promise<{ response: OpenRouterResponse; latencyMs: number }> {
  const model = request.model || config.defaultModel;

  const body: any = {
    model,
    messages: request.messages,
  };

  if (request.temperature !== undefined) body.temperature = request.temperature;
  if (request.max_tokens !== undefined) body.max_tokens = request.max_tokens;

  const start = Date.now();

  const res = await fetch(OPENROUTER_URL, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${config.openrouterApiKey}`,
      'Content-Type': 'application/json',
      'HTTP-Referer': 'https://windfall.ecofrontiers.xyz',
      'X-Title': 'Windfall Inference Gateway',
    },
    body: JSON.stringify(body),
  });

  const latencyMs = Date.now() - start;

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`OpenRouter ${res.status}: ${errorText}`);
  }

  const response = (await res.json()) as OpenRouterResponse;

  return { response, latencyMs };
}

// Stream support (for future use)
export async function callOpenRouterStream(
  request: InferenceRequest
): Promise<ReadableStream> {
  const model = request.model || config.defaultModel;

  const body: any = {
    model,
    messages: request.messages,
    stream: true,
  };

  if (request.temperature !== undefined) body.temperature = request.temperature;
  if (request.max_tokens !== undefined) body.max_tokens = request.max_tokens;

  const res = await fetch(OPENROUTER_URL, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${config.openrouterApiKey}`,
      'Content-Type': 'application/json',
      'HTTP-Referer': 'https://windfall.ecofrontiers.xyz',
      'X-Title': 'Windfall Inference Gateway',
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`OpenRouter stream ${res.status}: ${errorText}`);
  }

  return res.body!;
}
