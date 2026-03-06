import { describe, it, expect } from 'vitest';
import { buildLogfireTraceUrl } from './trace-link.js';

describe('buildLogfireTraceUrl', () => {
  it('builds a basic trace URL', () => {
    const url = buildLogfireTraceUrl(
      'https://logfire.pydantic.dev/myorg/myproject',
      'abc123def456',
    );
    expect(url).toBe(
      'https://logfire.pydantic.dev/myorg/myproject/explore?traceId=abc123def456',
    );
  });

  it('includes spanId when provided', () => {
    const url = buildLogfireTraceUrl(
      'https://logfire.pydantic.dev/myorg/myproject',
      'abc123',
      'span456',
    );
    expect(url).toContain('traceId=abc123');
    expect(url).toContain('spanId=span456');
  });

  it('strips trailing slash from project URL', () => {
    const url = buildLogfireTraceUrl(
      'https://logfire.pydantic.dev/myorg/myproject/',
      'trace1',
    );
    expect(url.startsWith(
      'https://logfire.pydantic.dev/myorg/myproject/explore',
    )).toBe(true);
  });
});
