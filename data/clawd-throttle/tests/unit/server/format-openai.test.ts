import { describe, it, expect } from 'vitest';
import {
  parseOpenAiRequest,
  formatOpenAiResponse,
  transformAnthropicSseToOpenAi,
  transformGoogleSseToOpenAi,
  extractAnthropicTokens,
  extractGoogleTokens,
} from '../../../src/server/format-openai.js';
import type { ProxyResponse } from '../../../src/proxy/types.js';

describe('parseOpenAiRequest', () => {
  it('extracts system messages into systemPrompt', () => {
    const result = parseOpenAiRequest({
      messages: [
        { role: 'system', content: 'You are helpful.' },
        { role: 'user', content: 'Hello' },
      ],
      max_tokens: 100,
    });
    expect(result.systemPrompt).toBe('You are helpful.');
    expect(result.messages).toHaveLength(1);
    expect(result.messages[0]!.role).toBe('user');
    expect(result.messages[0]!.content).toBe('Hello');
  });

  it('concatenates multiple system messages', () => {
    const result = parseOpenAiRequest({
      messages: [
        { role: 'system', content: 'Be helpful.' },
        { role: 'system', content: 'Be concise.' },
        { role: 'user', content: 'Hi' },
      ],
    });
    expect(result.systemPrompt).toBe('Be helpful.\nBe concise.');
  });

  it('handles no system messages', () => {
    const result = parseOpenAiRequest({
      messages: [{ role: 'user', content: 'Hi' }],
    });
    expect(result.systemPrompt).toBeUndefined();
  });

  it('defaults max_tokens to 4096', () => {
    const result = parseOpenAiRequest({
      messages: [{ role: 'user', content: 'Hi' }],
    });
    expect(result.maxTokens).toBe(4096);
  });

  it('parses stream flag', () => {
    const result = parseOpenAiRequest({
      messages: [{ role: 'user', content: 'Hi' }],
      stream: true,
    });
    expect(result.stream).toBe(true);
  });

  it('defaults stream to false', () => {
    const result = parseOpenAiRequest({
      messages: [{ role: 'user', content: 'Hi' }],
    });
    expect(result.stream).toBe(false);
  });

  it('throws on empty messages', () => {
    expect(() => parseOpenAiRequest({ messages: [] })).toThrow('Missing or empty');
  });

  it('throws on only system messages', () => {
    expect(() => parseOpenAiRequest({
      messages: [{ role: 'system', content: 'Be helpful.' }],
    })).toThrow('No user or assistant messages');
  });

  it('passes temperature through', () => {
    const result = parseOpenAiRequest({
      messages: [{ role: 'user', content: 'Hi' }],
      temperature: 0.3,
    });
    expect(result.temperature).toBe(0.3);
  });
});

describe('formatOpenAiResponse', () => {
  const mockResponse: ProxyResponse = {
    content: 'Hello there!',
    inputTokens: 10,
    outputTokens: 5,
    modelId: 'gemini-2.5-flash',
    provider: 'google',
    latencyMs: 300,
    finishReason: 'end_turn',
  };

  it('formats correct OpenAI shape', () => {
    const result = formatOpenAiResponse(mockResponse, 'test-123');
    expect(result.id).toBe('chatcmpl-test-123');
    expect(result.object).toBe('chat.completion');
    expect(result.model).toBe('gemini-2.5-flash');
  });

  it('includes choices with message', () => {
    const result = formatOpenAiResponse(mockResponse, 'test-123') as any;
    expect(result.choices).toHaveLength(1);
    expect(result.choices[0].message.role).toBe('assistant');
    expect(result.choices[0].message.content).toBe('Hello there!');
    expect(result.choices[0].finish_reason).toBe('stop');
  });

  it('includes usage totals', () => {
    const result = formatOpenAiResponse(mockResponse, 'test-123') as any;
    expect(result.usage.prompt_tokens).toBe(10);
    expect(result.usage.completion_tokens).toBe(5);
    expect(result.usage.total_tokens).toBe(15);
  });

  it('maps max_tokens finish reason to length', () => {
    const resp = { ...mockResponse, finishReason: 'max_tokens' };
    const result = formatOpenAiResponse(resp, 'id') as any;
    expect(result.choices[0].finish_reason).toBe('length');
  });
});

describe('transformAnthropicSseToOpenAi', () => {
  it('transforms content_block_delta to OpenAI chunk', () => {
    const data = JSON.stringify({
      type: 'content_block_delta',
      delta: { type: 'text_delta', text: 'Hello' },
    });
    const result = transformAnthropicSseToOpenAi('content_block_delta', data, 'req-1', 'model-1');
    expect(result).toContain('"content":"Hello"');
    expect(result).toContain('chatcmpl-req-1');
    expect(result).toStartWith('data: ');
  });

  it('transforms message_delta with stop_reason', () => {
    const data = JSON.stringify({
      type: 'message_delta',
      delta: { stop_reason: 'end_turn' },
      usage: { output_tokens: 42 },
    });
    const result = transformAnthropicSseToOpenAi('message_delta', data, 'req-1', 'model-1');
    expect(result).toContain('"finish_reason":"stop"');
  });

  it('transforms message_stop to [DONE]', () => {
    const data = JSON.stringify({ type: 'message_stop' });
    const result = transformAnthropicSseToOpenAi('message_stop', data, 'req-1', 'model-1');
    expect(result).toBe('data: [DONE]\n\n');
  });

  it('returns null for ping events', () => {
    const result = transformAnthropicSseToOpenAi('ping', '{}', 'req-1', 'model-1');
    expect(result).toBeNull();
  });

  it('returns null for message_start', () => {
    const data = JSON.stringify({
      type: 'message_start',
      message: { usage: { input_tokens: 25 } },
    });
    const result = transformAnthropicSseToOpenAi('message_start', data, 'req-1', 'model-1');
    expect(result).toBeNull();
  });
});

describe('transformGoogleSseToOpenAi', () => {
  it('transforms text content to OpenAI chunk', () => {
    const data = JSON.stringify({
      candidates: [{ content: { parts: [{ text: 'World' }] } }],
    });
    const result = transformGoogleSseToOpenAi(data, 'req-1', 'model-1');
    expect(result).toContain('"content":"World"');
  });

  it('emits [DONE] on finishReason', () => {
    const data = JSON.stringify({
      candidates: [{ content: { parts: [{ text: '' }] }, finishReason: 'STOP' }],
      usageMetadata: { promptTokenCount: 10, candidatesTokenCount: 20 },
    });
    const result = transformGoogleSseToOpenAi(data, 'req-1', 'model-1');
    expect(result).toContain('[DONE]');
  });
});

describe('extractAnthropicTokens', () => {
  it('extracts input tokens from message_start', () => {
    const data = JSON.stringify({
      type: 'message_start',
      message: { usage: { input_tokens: 42 } },
    });
    expect(extractAnthropicTokens('message_start', data)).toEqual({ inputTokens: 42 });
  });

  it('extracts output tokens from message_delta', () => {
    const data = JSON.stringify({
      type: 'message_delta',
      usage: { output_tokens: 15 },
    });
    expect(extractAnthropicTokens('message_delta', data)).toEqual({ outputTokens: 15 });
  });

  it('returns empty for other events', () => {
    expect(extractAnthropicTokens('ping', '{}')).toEqual({});
  });
});

describe('extractGoogleTokens', () => {
  it('extracts token counts from usageMetadata', () => {
    const data = JSON.stringify({
      usageMetadata: { promptTokenCount: 30, candidatesTokenCount: 50 },
    });
    expect(extractGoogleTokens(data)).toEqual({ inputTokens: 30, outputTokens: 50 });
  });

  it('returns empty when no metadata', () => {
    const data = JSON.stringify({ candidates: [] });
    expect(extractGoogleTokens(data)).toEqual({});
  });
});
