import type { ProxyMessage } from '../proxy/types.js';
import type { ProxyResponse } from '../proxy/types.js';

export interface ParsedRequest {
  messages: ProxyMessage[];
  systemPrompt: string | undefined;
  maxTokens: number;
  temperature: number | undefined;
  stream: boolean;
}

/**
 * Parse an Anthropic Messages API request body into our internal format.
 * Handles content as string or Array<{type:"text", text:string}>.
 */
export function parseAnthropicRequest(body: Record<string, unknown>): ParsedRequest {
  const rawMessages = body.messages as Array<{ role: string; content: unknown }>;
  if (!rawMessages || !Array.isArray(rawMessages) || rawMessages.length === 0) {
    throw new Error('Missing or empty messages array');
  }

  const messages: ProxyMessage[] = rawMessages.map(m => ({
    role: m.role as 'user' | 'assistant',
    content: flattenContent(m.content),
  }));

  let systemPrompt: string | undefined;
  if (typeof body.system === 'string') {
    systemPrompt = body.system;
  } else if (Array.isArray(body.system)) {
    // system can also be an array of content blocks
    systemPrompt = (body.system as Array<{ type: string; text: string }>)
      .filter(b => b.type === 'text')
      .map(b => b.text)
      .join('\n');
  }

  return {
    messages,
    systemPrompt,
    maxTokens: typeof body.max_tokens === 'number' ? body.max_tokens : 4096,
    temperature: typeof body.temperature === 'number' ? body.temperature : undefined,
    stream: body.stream === true,
  };
}

/**
 * Format a ProxyResponse into Anthropic Messages API response shape.
 */
export function formatAnthropicResponse(
  proxyResponse: ProxyResponse,
  requestId: string,
): Record<string, unknown> {
  return {
    id: `msg_${requestId}`,
    type: 'message',
    role: 'assistant',
    content: [{ type: 'text', text: proxyResponse.content }],
    model: proxyResponse.modelId,
    stop_reason: mapFinishReason(proxyResponse.finishReason),
    stop_sequence: null,
    usage: {
      input_tokens: proxyResponse.inputTokens,
      output_tokens: proxyResponse.outputTokens,
    },
  };
}

/**
 * Transform a Google SSE data payload into an Anthropic-format SSE event string.
 * Returns null if the chunk should be skipped.
 */
export function transformGoogleSseToAnthropic(
  data: string,
  requestId: string,
  isFirst: boolean,
): string | null {
  try {
    const parsed = JSON.parse(data);
    const text = parsed?.candidates?.[0]?.content?.parts?.[0]?.text;
    const finishReason = parsed?.candidates?.[0]?.finishReason;

    const events: string[] = [];

    if (isFirst) {
      // Emit message_start
      events.push(formatSseEvent('message_start', JSON.stringify({
        type: 'message_start',
        message: {
          id: `msg_${requestId}`,
          type: 'message',
          role: 'assistant',
          content: [],
          model: 'throttle-routed',
          stop_reason: null,
          stop_sequence: null,
          usage: { input_tokens: parsed?.usageMetadata?.promptTokenCount ?? 0, output_tokens: 0 },
        },
      })));
      events.push(formatSseEvent('content_block_start', JSON.stringify({
        type: 'content_block_start',
        index: 0,
        content_block: { type: 'text', text: '' },
      })));
    }

    if (text) {
      events.push(formatSseEvent('content_block_delta', JSON.stringify({
        type: 'content_block_delta',
        index: 0,
        delta: { type: 'text_delta', text },
      })));
    }

    if (finishReason) {
      const outputTokens = parsed?.usageMetadata?.candidatesTokenCount ?? 0;
      events.push(formatSseEvent('content_block_stop', JSON.stringify({
        type: 'content_block_stop',
        index: 0,
      })));
      events.push(formatSseEvent('message_delta', JSON.stringify({
        type: 'message_delta',
        delta: { stop_reason: 'end_turn', stop_sequence: null },
        usage: { output_tokens: outputTokens },
      })));
      events.push(formatSseEvent('message_stop', JSON.stringify({
        type: 'message_stop',
      })));
    }

    return events.length > 0 ? events.join('') : null;
  } catch {
    return null;
  }
}

function formatSseEvent(event: string, data: string): string {
  return `event: ${event}\ndata: ${data}\n\n`;
}

function flattenContent(content: unknown): string {
  if (typeof content === 'string') return content;
  if (Array.isArray(content)) {
    return content
      .filter((b: Record<string, unknown>) => b.type === 'text')
      .map((b: Record<string, unknown>) => b.text as string)
      .join('\n');
  }
  return String(content ?? '');
}

/**
 * Transform an OpenAI-compatible SSE data payload into Anthropic-format SSE events.
 * Used when client wants Anthropic format but upstream is an OpenAI-compat provider.
 */
export function transformOpenAiSseToAnthropic(
  data: string,
  requestId: string,
  isFirst: boolean,
): string | null {
  try {
    if (data === '[DONE]') {
      const events: string[] = [];
      events.push(formatSseEvent('content_block_stop', JSON.stringify({
        type: 'content_block_stop',
        index: 0,
      })));
      events.push(formatSseEvent('message_delta', JSON.stringify({
        type: 'message_delta',
        delta: { stop_reason: 'end_turn', stop_sequence: null },
        usage: { output_tokens: 0 },
      })));
      events.push(formatSseEvent('message_stop', JSON.stringify({
        type: 'message_stop',
      })));
      return events.join('');
    }

    const parsed = JSON.parse(data);
    const events: string[] = [];

    if (isFirst) {
      // Emit message_start and content_block_start
      events.push(formatSseEvent('message_start', JSON.stringify({
        type: 'message_start',
        message: {
          id: `msg_${requestId}`,
          type: 'message',
          role: 'assistant',
          content: [],
          model: parsed.model ?? 'throttle-routed',
          stop_reason: null,
          stop_sequence: null,
          usage: { input_tokens: 0, output_tokens: 0 },
        },
      })));
      events.push(formatSseEvent('content_block_start', JSON.stringify({
        type: 'content_block_start',
        index: 0,
        content_block: { type: 'text', text: '' },
      })));
    }

    // Extract text delta
    const text = parsed?.choices?.[0]?.delta?.content;
    if (text) {
      events.push(formatSseEvent('content_block_delta', JSON.stringify({
        type: 'content_block_delta',
        index: 0,
        delta: { type: 'text_delta', text },
      })));
    }

    // Check for finish_reason (emit stop events)
    const finishReason = parsed?.choices?.[0]?.finish_reason;
    if (finishReason) {
      events.push(formatSseEvent('content_block_stop', JSON.stringify({
        type: 'content_block_stop',
        index: 0,
      })));
      events.push(formatSseEvent('message_delta', JSON.stringify({
        type: 'message_delta',
        delta: { stop_reason: mapFinishReason(finishReason), stop_sequence: null },
        usage: { output_tokens: parsed?.usage?.completion_tokens ?? 0 },
      })));
      events.push(formatSseEvent('message_stop', JSON.stringify({
        type: 'message_stop',
      })));
    }

    return events.length > 0 ? events.join('') : null;
  } catch {
    return null;
  }
}

function mapFinishReason(reason: string): string {
  switch (reason) {
    case 'end_turn':
    case 'stop':
    case 'STOP':
      return 'end_turn';
    case 'max_tokens':
    case 'MAX_TOKENS':
    case 'length':
      return 'max_tokens';
    default:
      return reason;
  }
}
