import type { ProxyMessage, ProxyResponse } from '../proxy/types.js';
import type { ApiProvider } from '../router/types.js';

export interface ParsedRequest {
  messages: ProxyMessage[];
  systemPrompt: string | undefined;
  maxTokens: number;
  temperature: number | undefined;
  stream: boolean;
}

/**
 * Parse an OpenAI Chat Completions request body into our internal format.
 * Extracts role:"system" messages into systemPrompt.
 */
export function parseOpenAiRequest(body: Record<string, unknown>): ParsedRequest {
  const rawMessages = body.messages as Array<{ role: string; content: string }>;
  if (!rawMessages || !Array.isArray(rawMessages) || rawMessages.length === 0) {
    throw new Error('Missing or empty messages array');
  }

  const systemMessages: string[] = [];
  const messages: ProxyMessage[] = [];

  for (const m of rawMessages) {
    if (m.role === 'system') {
      systemMessages.push(typeof m.content === 'string' ? m.content : String(m.content));
    } else if (m.role === 'user' || m.role === 'assistant') {
      messages.push({
        role: m.role,
        content: typeof m.content === 'string' ? m.content : String(m.content),
      });
    }
    // skip 'tool', 'function' roles
  }

  if (messages.length === 0) {
    throw new Error('No user or assistant messages found');
  }

  return {
    messages,
    systemPrompt: systemMessages.length > 0 ? systemMessages.join('\n') : undefined,
    maxTokens: typeof body.max_tokens === 'number' ? body.max_tokens : 4096,
    temperature: typeof body.temperature === 'number' ? body.temperature : undefined,
    stream: body.stream === true,
  };
}

/**
 * Format a ProxyResponse into OpenAI Chat Completions response shape.
 */
export function formatOpenAiResponse(
  proxyResponse: ProxyResponse,
  requestId: string,
): Record<string, unknown> {
  return {
    id: `chatcmpl-${requestId}`,
    object: 'chat.completion',
    created: Math.floor(Date.now() / 1000),
    model: proxyResponse.modelId,
    choices: [{
      index: 0,
      message: {
        role: 'assistant',
        content: proxyResponse.content,
      },
      finish_reason: mapFinishReasonToOpenAi(proxyResponse.finishReason),
    }],
    usage: {
      prompt_tokens: proxyResponse.inputTokens,
      completion_tokens: proxyResponse.outputTokens,
      total_tokens: proxyResponse.inputTokens + proxyResponse.outputTokens,
    },
  };
}

/**
 * Transform an Anthropic SSE event into an OpenAI streaming chunk string.
 * Returns null for events that should be skipped (but caller still parses for token accumulation).
 */
export function transformAnthropicSseToOpenAi(
  event: string,
  data: string,
  requestId: string,
  modelId: string,
): string | null {
  try {
    const parsed = JSON.parse(data);

    if (event === 'content_block_delta' && parsed.delta?.type === 'text_delta') {
      return formatOpenAiChunk(requestId, modelId, { content: parsed.delta.text }, null);
    }

    if (event === 'message_delta') {
      const stopReason = parsed.delta?.stop_reason;
      if (stopReason) {
        return formatOpenAiChunk(requestId, modelId, {}, mapFinishReasonToOpenAi(stopReason));
      }
    }

    if (event === 'message_stop') {
      return 'data: [DONE]\n\n';
    }

    return null;
  } catch {
    return null;
  }
}

/**
 * Transform a Google SSE data payload into an OpenAI streaming chunk string.
 */
export function transformGoogleSseToOpenAi(
  data: string,
  requestId: string,
  modelId: string,
): string | null {
  try {
    const parsed = JSON.parse(data);
    const text = parsed?.candidates?.[0]?.content?.parts?.[0]?.text;
    const finishReason = parsed?.candidates?.[0]?.finishReason;

    const events: string[] = [];

    if (text) {
      events.push(formatOpenAiChunk(requestId, modelId, { content: text }, null));
    }

    if (finishReason) {
      events.push(formatOpenAiChunk(requestId, modelId, {}, 'stop'));
      events.push('data: [DONE]\n\n');
    }

    return events.length > 0 ? events.join('') : null;
  } catch {
    return null;
  }
}

function formatOpenAiChunk(
  requestId: string,
  modelId: string,
  delta: Record<string, unknown>,
  finishReason: string | null,
): string {
  const chunk = {
    id: `chatcmpl-${requestId}`,
    object: 'chat.completion.chunk',
    created: Math.floor(Date.now() / 1000),
    model: modelId,
    choices: [{
      index: 0,
      delta,
      finish_reason: finishReason,
    }],
  };
  return `data: ${JSON.stringify(chunk)}\n\n`;
}

function mapFinishReasonToOpenAi(reason: string): string {
  switch (reason) {
    case 'end_turn':
    case 'stop':
    case 'STOP':
      return 'stop';
    case 'max_tokens':
    case 'MAX_TOKENS':
      return 'length';
    default:
      return reason;
  }
}

/**
 * Extract token counts from an Anthropic SSE event for accumulation.
 * Returns partial counts (only the fields present in this event).
 */
export function extractAnthropicTokens(event: string, data: string): {
  inputTokens?: number;
  outputTokens?: number;
} {
  try {
    const parsed = JSON.parse(data);

    if (event === 'message_start') {
      return { inputTokens: parsed.message?.usage?.input_tokens };
    }

    if (event === 'message_delta') {
      return { outputTokens: parsed.usage?.output_tokens };
    }

    return {};
  } catch {
    return {};
  }
}

/**
 * Extract token counts from a Google SSE data payload for accumulation.
 */
export function extractGoogleTokens(data: string): {
  inputTokens?: number;
  outputTokens?: number;
} {
  try {
    const parsed = JSON.parse(data);
    const meta = parsed?.usageMetadata;
    if (meta) {
      return {
        inputTokens: meta.promptTokenCount,
        outputTokens: meta.candidatesTokenCount,
      };
    }
    return {};
  } catch {
    return {};
  }
}

/**
 * Extract token counts from an OpenAI-compatible SSE data payload.
 * OpenAI streaming only includes usage in the final chunk (if stream_options.include_usage is set)
 * or not at all. We parse any chunk that has a usage field.
 */
export function extractOpenAiCompatTokens(data: string): {
  inputTokens?: number;
  outputTokens?: number;
} {
  try {
    if (data === '[DONE]') return {};
    const parsed = JSON.parse(data);
    if (parsed?.usage) {
      return {
        inputTokens: parsed.usage.prompt_tokens,
        outputTokens: parsed.usage.completion_tokens,
      };
    }
    return {};
  } catch {
    return {};
  }
}
