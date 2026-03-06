import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { checkHub, discoverHub, readConfig, DEFAULT_HUB_URLS, CONFIG_PATH } from './setup.js';

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

  describe('readConfig', () => {
    it('returns config from file or null without throwing', () => {
      // This test just verifies readConfig doesn't throw
      const cfg = readConfig();
      expect(cfg === null || (typeof cfg === 'object' && !!cfg.hubUrl)).toBe(true);
    });

    it('exports CONFIG_PATH', () => {
      expect(CONFIG_PATH).toContain('.pdh');
      expect(CONFIG_PATH).toContain('config.json');
    });
  });
});
