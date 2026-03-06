import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { HubClient } from './hub-client.js';
import { createPullTool, createProposeTool } from './tools.js';

describe('Tools', () => {
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

  describe('personal_data_pull tool', () => {
    it('has correct name and description', () => {
      const tool = createPullTool(client);
      expect(tool.name).toBe('personal_data_pull');
      expect(tool.label).toBe('Pull Personal Data');
      expect(tool.description).toContain('PersonalDataHub');
      expect(tool.parameters.required).toContain('source');
      expect(tool.parameters.required).toContain('purpose');
    });

    it('calls client.pull with correct params and returns formatted result', async () => {
      const pullData = {
        ok: true,
        data: [
          {
            source: 'gmail',
            source_item_id: 'msg_1',
            type: 'email',
            timestamp: '2026-01-15T10:00:00Z',
            data: { title: 'Test', body: 'Hello world' },
          },
        ],
      };

      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(pullData),
      });

      const tool = createPullTool(client);
      const result = await tool.execute('call_1', {
        source: 'gmail',
        type: 'email',
        query: 'is:unread from:alice',
        limit: 10,
        purpose: 'Find emails from Alice',
      });

      // Verify the HTTP call
      const body = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(body.source).toBe('gmail');
      expect(body.type).toBe('email');
      expect(body.params).toEqual({ query: 'is:unread from:alice', limit: 10 });
      expect(body.purpose).toBe('Find emails from Alice');

      // Verify tool return format
      expect(result.content).toHaveLength(1);
      expect(result.content[0].type).toBe('text');
      const parsed = JSON.parse(result.content[0].text!);
      expect(parsed.ok).toBe(true);
      expect(parsed.data).toHaveLength(1);
    });

    it('omits params when no query or limit provided', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ ok: true, data: [] }),
      });

      const tool = createPullTool(client);
      await tool.execute('call_2', {
        source: 'gmail',
        purpose: 'Fetch recent emails',
      });

      const body = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(body.params).toBeUndefined();
    });
  });

  describe('personal_data_propose tool', () => {
    it('has correct name and description', () => {
      const tool = createProposeTool(client);
      expect(tool.name).toBe('personal_data_propose');
      expect(tool.label).toBe('Propose Personal Data Action');
      expect(tool.description).toContain('staged');
      expect(tool.parameters.required).toContain('source');
      expect(tool.parameters.required).toContain('action_type');
      expect(tool.parameters.required).toContain('purpose');
    });

    it('calls client.propose with correct params', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ ok: true, actionId: 'act_456', status: 'pending_review' }),
      });

      const tool = createProposeTool(client);
      const result = await tool.execute('call_3', {
        source: 'gmail',
        action_type: 'draft_email',
        to: 'alice@company.com',
        subject: 'Re: Q4 Report',
        body: 'Looks good!',
        in_reply_to: 'msg_abc',
        purpose: 'Draft reply to Alice',
      });

      const body = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(body.source).toBe('gmail');
      expect(body.action_type).toBe('draft_email');
      expect(body.action_data).toEqual({
        to: 'alice@company.com',
        subject: 'Re: Q4 Report',
        body: 'Looks good!',
        in_reply_to: 'msg_abc',
      });
      expect(body.purpose).toBe('Draft reply to Alice');

      const parsed = JSON.parse(result.content[0].text!);
      expect(parsed.actionId).toBe('act_456');
      expect(parsed.status).toBe('pending_review');
    });

    it('omits in_reply_to when not provided', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ ok: true, actionId: 'act_789', status: 'pending_review' }),
      });

      const tool = createProposeTool(client);
      await tool.execute('call_4', {
        source: 'gmail',
        action_type: 'send_email',
        to: 'bob@co.com',
        subject: 'Hello',
        body: 'Hi Bob',
        purpose: 'Send greeting',
      });

      const body = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(body.action_data.in_reply_to).toBeUndefined();
    });
  });
});
