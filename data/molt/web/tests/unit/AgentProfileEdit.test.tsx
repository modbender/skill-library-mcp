import { describe, it, expect, beforeEach, vi } from 'vitest';
import { api } from '../../src/lib/api';

const fetchMock = vi.fn();

beforeEach(() => {
  global.fetch = fetchMock;
  vi.clearAllMocks();
  api.setTokenGetter(() => null);
  api.setAgentApiKeyGetter(() => 'test-agent-api-key');
});

describe('Agent profile API', () => {
  describe('uploadAgentAvatar', () => {
    it('should POST to /api/agents/me/avatar with FormData', async () => {
      const mockAgent = {
        id: 'agent-1',
        name: 'test-agent',
        avatar_url: '/api/uploads/agents/agent-1/avatar.jpg',
        karma: 10,
        created_at: '2026-01-01T00:00:00Z',
      };

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAgent,
      });

      const file = new File(['image content'], 'avatar.jpg', { type: 'image/jpeg' });
      const result = await api.uploadAgentAvatar(file);

      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining('/api/agents/me/avatar'),
        expect.objectContaining({
          method: 'POST',
          body: expect.any(FormData),
        })
      );
      const callBody = fetchMock.mock.calls[0][1].body as FormData;
      expect(callBody.get('avatar')).toBe(file);
      expect(fetchMock.mock.calls[0][1].headers?.['X-Agent-API-Key']).toBe('test-agent-api-key');
      expect(result.avatar_url).toBe('/api/uploads/agents/agent-1/avatar.jpg');
    });
  });

  describe('updateAgentProfile', () => {
    it('should PATCH /api/agents/me with description', async () => {
      const mockAgent = {
        id: 'agent-1',
        name: 'test-agent',
        description: 'Updated description',
        karma: 10,
        created_at: '2026-01-01T00:00:00Z',
      };

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAgent,
      });

      const result = await api.updateAgentProfile({ description: 'Updated description' });

      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining('/api/agents/me'),
        expect.objectContaining({
          method: 'PATCH',
          body: JSON.stringify({ description: 'Updated description' }),
        })
      );
      expect(result.description).toBe('Updated description');
    });
  });

  describe('getCurrentAgent', () => {
    it('should GET /api/agents/me with agent API key', async () => {
      const mockAgent = {
        id: 'agent-1',
        name: 'test-agent',
        karma: 10,
        created_at: '2026-01-01T00:00:00Z',
      };

      fetchMock.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAgent,
      });

      const result = await api.getCurrentAgent();

      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining('/api/agents/me'),
        expect.any(Object)
      );
      expect(fetchMock.mock.calls[0][1].headers?.['X-Agent-API-Key']).toBe('test-agent-api-key');
      expect(result.name).toBe('test-agent');
    });
  });
});
