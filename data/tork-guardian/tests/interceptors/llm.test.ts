import { describe, it, expect, vi } from 'vitest';
import { governLLMRequest, GovernanceDeniedError } from '../../dist/interceptors/llm';
import { TorkConfigSchema } from '../../dist/config';

function makeConfig(overrides: Record<string, unknown> = {}) {
  return TorkConfigSchema.parse({ apiKey: 'test-key', ...overrides });
}

function makeMockClient(responses: Array<{ action: string; output: string; pii_detected?: any[]; receipt?: any }>) {
  let callIndex = 0;
  return {
    govern: vi.fn(async () => {
      const resp = responses[callIndex] || responses[0];
      callIndex++;
      return resp;
    }),
    redact: vi.fn(),
  } as any;
}

describe('governLLMRequest', () => {
  it('passes clean text through when PII redaction is disabled', async () => {
    const client = makeMockClient([]);
    const config = makeConfig({ redactPII: false });

    const result = await governLLMRequest(client, {
      messages: [{ role: 'user', content: 'Hello world' }],
    }, config);

    expect(result.governed).toBe(false);
    expect(result.request.messages[0].content).toBe('Hello world');
    expect(client.govern).not.toHaveBeenCalled();
  });

  it('redacts PII in messages when action is redact', async () => {
    const client = makeMockClient([{
      action: 'redact',
      output: 'Email [EMAIL_REDACTED] about the project',
      pii_detected: [{ type: 'email', count: 1 }],
    }]);
    const config = makeConfig({ redactPII: true, policy: 'standard' });

    const result = await governLLMRequest(client, {
      messages: [{ role: 'user', content: 'Email john@example.com about the project' }],
    }, config);

    expect(result.governed).toBe(true);
    expect(result.pii_found).toBe(true);
    expect(result.request.messages[0].content).toBe('Email [EMAIL_REDACTED] about the project');
  });

  it('collects compliance receipt IDs', async () => {
    const client = makeMockClient([{
      action: 'allow',
      output: 'clean text',
      receipt: { receipt_id: 'rcpt_123', timestamp: '2026-01-01', policy_version: '1.0' },
    }]);
    const config = makeConfig();

    const result = await governLLMRequest(client, {
      messages: [{ role: 'user', content: 'clean text' }],
    }, config);

    expect(result.receipts).toContain('rcpt_123');
  });

  it('throws GovernanceDeniedError when action is deny', async () => {
    const client = makeMockClient([{
      action: 'deny',
      output: '',
      pii_detected: [{ type: 'ssn', count: 1 }],
    }]);
    const config = makeConfig({ policy: 'strict' });

    await expect(
      governLLMRequest(client, {
        messages: [{ role: 'user', content: 'My SSN is 123-45-6789' }],
      }, config),
    ).rejects.toThrow(GovernanceDeniedError);
  });

  it('handles messages with empty content', async () => {
    const client = makeMockClient([{ action: 'allow', output: '' }]);
    const config = makeConfig();

    const result = await governLLMRequest(client, {
      messages: [{ role: 'system', content: '' }],
    }, config);

    expect(result.governed).toBe(true);
    // Empty string is falsy, so govern should skip it
    expect(client.govern).not.toHaveBeenCalled();
  });

  it('processes multiple messages sequentially', async () => {
    const client = makeMockClient([
      { action: 'allow', output: 'Message one' },
      { action: 'redact', output: 'Call [PHONE_REDACTED]', pii_detected: [{ type: 'phone', count: 1 }] },
    ]);
    const config = makeConfig();

    const result = await governLLMRequest(client, {
      messages: [
        { role: 'user', content: 'Message one' },
        { role: 'user', content: 'Call 555-123-4567' },
      ],
    }, config);

    expect(result.pii_found).toBe(true);
    expect(result.request.messages[1].content).toBe('Call [PHONE_REDACTED]');
    expect(client.govern).toHaveBeenCalledTimes(2);
  });
});

describe('GovernanceDeniedError', () => {
  it('stores the govern response', () => {
    const response = { action: 'deny' as const, output: '' };
    const error = new GovernanceDeniedError('Denied', response);

    expect(error.message).toBe('Denied');
    expect(error.name).toBe('GovernanceDeniedError');
    expect(error.governResponse).toBe(response);
    expect(error).toBeInstanceOf(Error);
  });
});
