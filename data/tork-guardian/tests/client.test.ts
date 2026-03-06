import { describe, it, expect, vi } from 'vitest';
import { TorkClient } from '../dist/client';

function makeClientWithMockHttp(mockPost: ReturnType<typeof vi.fn>) {
  const client = new TorkClient('tork_test_key');
  // Replace the internal axios instance with a mock
  (client as any).http = { post: mockPost };
  return client;
}

describe('TorkClient', () => {
  it('initializes with API key', () => {
    const client = new TorkClient('tork_test_key_123');
    expect(client).toBeDefined();
  });

  it('initializes with custom base URL', () => {
    const client = new TorkClient('tork_key', 'https://custom.tork.network');
    expect(client).toBeDefined();
  });

  it('fail-open: returns allow when API is unreachable', async () => {
    const mockPost = vi.fn().mockRejectedValue(new Error('ECONNREFUSED'));
    const client = makeClientWithMockHttp(mockPost);

    const result = await client.govern('test content');

    expect(result.action).toBe('allow');
    expect(result.output).toBe('test content');
    expect(mockPost).toHaveBeenCalledWith('/api/v1/govern', {
      content: 'test content',
      options: undefined,
    });
  });

  it('redact calls govern with redact mode', async () => {
    const mockPost = vi.fn().mockResolvedValue({
      data: { action: 'redact', output: '[REDACTED]' },
    });
    const client = makeClientWithMockHttp(mockPost);

    const result = await client.redact('sensitive data');

    expect(result.action).toBe('redact');
    expect(result.output).toBe('[REDACTED]');
    expect(mockPost).toHaveBeenCalledWith('/api/v1/govern', {
      content: 'sensitive data',
      options: { mode: 'redact' },
    });
  });
});
