import { describe, it, expect, vi, afterEach } from 'vitest';
import { validateApiKey } from '../lib/auth.js';

describe('auth + config', () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.resetModules();
  });

  describe('validateApiKey', () => {
    it('throws when key is missing', () => {
      expect(() => validateApiKey()).toThrow(/Missing Buffer API key/);
    });

    it('throws when key is too short', () => {
      expect(() => validateApiKey('short')).toThrow(/too short/);
    });

    it('returns a trimmed key when valid', () => {
      expect(validateApiKey('  valid_key_123456  ')).toBe('valid_key_123456');
    });
  });

  describe('getConfig', () => {
    it('uses env api url when provided', async () => {
      vi.stubEnv('BUFFER_API_KEY', 'my_api_key_123456');
      vi.stubEnv('BUFFER_API_URL', 'https://custom.example/graphql');
      const { getConfig } = await import('../lib/config.js');

      expect(getConfig()).toEqual({
        apiKey: 'my_api_key_123456',
        apiUrl: 'https://custom.example/graphql',
      });
    });

    it('falls back to default api url when env is missing', async () => {
      vi.stubEnv('BUFFER_API_KEY', 'my_api_key_123456');
      vi.stubEnv('BUFFER_API_URL', '');
      const { getConfig, DEFAULT_API_URL } = await import('../lib/config.js');

      expect(getConfig().apiUrl).toBe(DEFAULT_API_URL);
    });
  });
});
