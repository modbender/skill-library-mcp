import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { HubClient, HubApiError } from './hub-client.js';

describe('HubClient', () => {
  let client: HubClient;
  let mockFetch: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockFetch = vi.fn();
    client = new HubClient({
      hubUrl: 'http://localhost:7007',
      apiKey: 'pk_test_abc123',
    });
    vi.stubGlobal('fetch', mockFetch);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('pull', () => {
    it('sends correct HTTP request with purpose field', async () => {
      const mockResponse = {
        ok: true,
        data: [
          {
            source: 'gmail',
            source_item_id: 'msg_1',
            type: 'email',
            timestamp: '2026-01-15T10:00:00Z',
            data: { title: 'Test Email', body: 'Hello' },
          },
        ],
      };

      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await client.pull({
        source: 'gmail',
        type: 'email',
        params: { query: 'is:unread' },
        purpose: 'Collect unanswered emails to draft responses',
      });

      expect(mockFetch).toHaveBeenCalledWith('http://localhost:7007/app/v1/pull', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer pk_test_abc123',
        },
        body: JSON.stringify({
          source: 'gmail',
          type: 'email',
          params: { query: 'is:unread' },
          purpose: 'Collect unanswered emails to draft responses',
        }),
      });

      expect(result.ok).toBe(true);
      expect(result.data).toHaveLength(1);
      expect(result.data[0].data.title).toBe('Test Email');
    });

    it('sends pull request without optional fields', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ ok: true, data: [] }),
      });

      await client.pull({
        source: 'gmail',
        purpose: 'Check for new emails',
      });

      const body = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(body.source).toBe('gmail');
      expect(body.purpose).toBe('Check for new emails');
      expect(body.type).toBeUndefined();
      expect(body.params).toBeUndefined();
    });

    it('throws HubApiError on non-ok response', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 401,
        text: () => Promise.resolve('Unauthorized'),
      });

      await expect(
        client.pull({ source: 'gmail', purpose: 'test' }),
      ).rejects.toThrow(HubApiError);

      try {
        await client.pull({ source: 'gmail', purpose: 'test' });
      } catch (e) {
        const err = e as HubApiError;
        expect(err.endpoint).toBe('pull');
        expect(err.statusCode).toBe(401);
        expect(err.body).toBe('Unauthorized');
      }
    });

    it('strips trailing slash from hub URL', async () => {
      const clientWithSlash = new HubClient({
        hubUrl: 'http://localhost:7007/',
        apiKey: 'pk_test',
      });

      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ ok: true, data: [] }),
      });

      await clientWithSlash.pull({ source: 'gmail', purpose: 'test' });

      expect(mockFetch.mock.calls[0][0]).toBe('http://localhost:7007/app/v1/pull');
    });
  });

  describe('propose', () => {
    it('sends correct HTTP request with purpose field', async () => {
      const mockResponse = {
        ok: true,
        actionId: 'act_123',
        status: 'pending_review',
      };

      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await client.propose({
        source: 'gmail',
        action_type: 'draft_email',
        action_data: {
          to: 'alice@company.com',
          subject: 'Re: Q4 Report',
          body: 'Thanks Alice, the numbers look good.',
          in_reply_to: 'msg_abc123',
        },
        purpose: 'Draft reply to unanswered email from Alice about Q4 report',
      });

      expect(mockFetch).toHaveBeenCalledWith('http://localhost:7007/app/v1/propose', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer pk_test_abc123',
        },
        body: JSON.stringify({
          source: 'gmail',
          action_type: 'draft_email',
          action_data: {
            to: 'alice@company.com',
            subject: 'Re: Q4 Report',
            body: 'Thanks Alice, the numbers look good.',
            in_reply_to: 'msg_abc123',
          },
          purpose: 'Draft reply to unanswered email from Alice about Q4 report',
        }),
      });

      expect(result.ok).toBe(true);
      expect(result.actionId).toBe('act_123');
      expect(result.status).toBe('pending_review');
    });

    it('throws HubApiError on non-ok response', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 403,
        text: () => Promise.resolve('Action type not allowed'),
      });

      await expect(
        client.propose({
          source: 'gmail',
          action_type: 'send_email',
          action_data: { to: 'a@b.com', subject: 'Hi', body: 'Hey' },
          purpose: 'test',
        }),
      ).rejects.toThrow(HubApiError);
    });
  });
});
