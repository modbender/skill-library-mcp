import { describe, it, expect } from 'vitest';
import {
  safeJsonStringify,
  truncate,
  redactSecrets,
  prepareForCapture,
  extractWorkspaceName,
  generateCallId,
  extractErrorDetails,
} from './util.js';

describe('safeJsonStringify', () => {
  it('serializes objects', () => {
    expect(safeJsonStringify({ a: 1 })).toBe('{"a":1}');
  });

  it('handles circular references', () => {
    const obj: Record<string, unknown> = { a: 1 };
    obj.self = obj;
    const result = safeJsonStringify(obj);
    expect(result).toContain('"a":1');
    expect(result).toContain('[Circular]');
  });

  it('handles BigInt', () => {
    expect(safeJsonStringify({ n: BigInt(42) })).toBe('{"n":"42"}');
  });
});

describe('truncate', () => {
  it('does not truncate short strings', () => {
    expect(truncate('hello', 10)).toBe('hello');
  });

  it('truncates and adds marker', () => {
    expect(truncate('hello world', 5)).toBe('hello...[truncated]');
  });
});

describe('redactSecrets', () => {
  it('redacts API keys', () => {
    const input = 'curl -H "api_key: sk_live_abc123defgh456"';
    const result = redactSecrets(input);
    expect(result).not.toContain('sk_live_abc123defgh456');
    expect(result).toContain('[REDACTED]');
  });

  it('redacts bearer tokens', () => {
    const input = 'Authorization: Bearer ghp_abcdef1234567890abcdef';
    const result = redactSecrets(input);
    expect(result).not.toContain('ghp_abcdef1234567890abcdef');
  });

  it('redacts JWTs', () => {
    const input =
      'token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0';
    const result = redactSecrets(input);
    expect(result).toContain('[REDACTED]');
  });

  it('leaves non-secret content alone', () => {
    const input = 'curl https://api.example.com/data -d \'{"name":"test"}\'';
    expect(redactSecrets(input)).toBe(input);
  });
});

describe('prepareForCapture', () => {
  it('serializes, redacts, and truncates', () => {
    const result = prepareForCapture(
      { key: 'api_key: secret123456789012' },
      50,
      true,
    );
    expect(result).toContain('[REDACTED]');
    expect(result.length).toBeLessThanOrEqual(50 + '...[truncated]'.length);
  });

  it('skips redaction when disabled', () => {
    const result = prepareForCapture('api_key: mysecret12345678', 200, false);
    expect(result).toContain('mysecret12345678');
  });
});

describe('extractWorkspaceName', () => {
  it('extracts last path segment', () => {
    expect(extractWorkspaceName('/path/to/workspaces/chief-of-staff')).toBe(
      'chief-of-staff',
    );
  });

  it('handles trailing slash', () => {
    expect(extractWorkspaceName('/workspaces/marketing/')).toBe('marketing');
  });

  it('returns unknown for undefined', () => {
    expect(extractWorkspaceName(undefined)).toBe('unknown');
  });
});

describe('generateCallId', () => {
  it('generates unique IDs', () => {
    const ids = new Set(Array.from({ length: 100 }, () => generateCallId()));
    expect(ids.size).toBe(100);
  });

  it('returns string format', () => {
    const id = generateCallId();
    expect(typeof id).toBe('string');
    expect(id).toMatch(/.+-[a-z0-9]+/);
  });
});

describe('extractErrorDetails', () => {
  it('extracts from Error objects', () => {
    const err = new TypeError('bad input');
    const details = extractErrorDetails(err);
    expect(details.type).toBe('TypeError');
    expect(details.message).toBe('bad input');
    expect(details.stacktrace).toContain('TypeError');
  });

  it('handles string errors', () => {
    const details = extractErrorDetails('something failed');
    expect(details.type).toBe('Error');
    expect(details.message).toBe('something failed');
  });

  it('handles unknown error types', () => {
    const details = extractErrorDetails({ code: 42 });
    expect(details.type).toBe('Error');
    expect(details.message).toContain('42');
  });
});
