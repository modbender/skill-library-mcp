import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { checkHub, createApiKey, autoSetup, discoverHub, readCredentials, DEFAULT_HUB_URLS, CREDENTIALS_PATH } from './setup.js';

describe('Setup Module', () => {
  let mockFetch: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockFetch = vi.fn();
    vi.stubGlobal('fetch', mockFetch);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('checkHub', () => {
    it('returns ok:true when hub responds with {ok:true}', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ ok: true, version: '0.1.0' }),
      });

      const result = await checkHub('http://localhost:3000');
      expect(result.ok).toBe(true);
      expect(result.version).toBe('0.1.0');
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:3000/health',
        expect.objectContaining({ signal: expect.any(AbortSignal) }),
      );
    });

    it('returns ok:false when hub returns non-ok HTTP status', async () => {
      mockFetch.mockResolvedValue({ ok: false });
      const result = await checkHub('http://localhost:3000');
      expect(result.ok).toBe(false);
    });

    it('returns ok:false when fetch throws (hub unreachable)', async () => {
      mockFetch.mockRejectedValue(new Error('ECONNREFUSED'));
      const result = await checkHub('http://localhost:3000');
      expect(result.ok).toBe(false);
    });

    it('strips trailing slash from hubUrl', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ ok: true }),
      });
      await checkHub('http://localhost:3000/');
      expect(mockFetch.mock.calls[0][0]).toBe('http://localhost:3000/health');
    });
  });

  describe('createApiKey', () => {
    it('sends POST /api/keys and returns the key', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ ok: true, id: 'openclaw-agent', key: 'pk_abc123' }),
      });

      const result = await createApiKey('http://localhost:3000', 'OpenClaw Agent');
      expect(result.ok).toBe(true);
      expect(result.key).toBe('pk_abc123');

      const body = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(body.name).toBe('OpenClaw Agent');
    });

    it('throws on non-ok response', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 500,
        text: () => Promise.resolve('Internal error'),
      });

      await expect(createApiKey('http://localhost:3000', 'Test')).rejects.toThrow(
        'Failed to create API key: 500 Internal error',
      );
    });
  });

  describe('autoSetup', () => {
    it('returns hubUrl and apiKey when hub is reachable', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ ok: true, version: '0.1.0' }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ ok: true, id: 'openclaw', key: 'pk_xyz789' }),
        });

      const result = await autoSetup('http://localhost:3000', 'OpenClaw');
      expect(result).toEqual({
        hubUrl: 'http://localhost:3000',
        apiKey: 'pk_xyz789',
      });
    });

    it('returns null when hub is not reachable', async () => {
      mockFetch.mockRejectedValue(new Error('ECONNREFUSED'));
      const result = await autoSetup('http://localhost:3000', 'OpenClaw');
      expect(result).toBeNull();
    });
  });

  describe('discoverHub', () => {
    it('returns the first URL that responds', async () => {
      mockFetch
        .mockRejectedValueOnce(new Error('ECONNREFUSED'))
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ ok: true }),
        });

      const url = await discoverHub();
      expect(url).toBe('http://localhost:7007');
    });

    it('returns null when no hub found', async () => {
      mockFetch.mockRejectedValue(new Error('ECONNREFUSED'));
      const url = await discoverHub();
      expect(url).toBeNull();
    });

    it('probes expected default URLs', () => {
      expect(DEFAULT_HUB_URLS).toContain('http://localhost:3000');
      expect(DEFAULT_HUB_URLS).toContain('http://localhost:7007');
    });
  });

  describe('readCredentials', () => {
    it('returns credentials from file or null without throwing', () => {
      // This test just verifies readCredentials doesn't throw
      const creds = readCredentials();
      expect(creds === null || (typeof creds === 'object' && !!creds.hubUrl && !!creds.apiKey)).toBe(true);
    });

    it('exports CREDENTIALS_PATH', () => {
      expect(CREDENTIALS_PATH).toContain('.pdh');
      expect(CREDENTIALS_PATH).toContain('credentials.json');
    });
  });
});
