import { describe, it, expect } from 'vitest';
import { buildAnthropicAuthHeaders } from '../../../src/proxy/anthropic-auth.js';
import type { ThrottleConfig } from '../../../src/config/types.js';

function makeConfig(overrides: { apiKey?: string; baseUrl?: string; authType?: 'api-key' | 'bearer' | 'auto' } = {}): ThrottleConfig {
  return {
    mode: 'standard',
    anthropic: {
      apiKey: overrides.apiKey ?? '',
      baseUrl: overrides.baseUrl ?? 'https://api.anthropic.com',
      authType: overrides.authType ?? 'auto',
    },
    google: { apiKey: '', baseUrl: '' },
    openai: { apiKey: '', baseUrl: '' },
    deepseek: { apiKey: '', baseUrl: '' },
    xai: { apiKey: '', baseUrl: '' },
    moonshot: { apiKey: '', baseUrl: '' },
    mistral: { apiKey: '', baseUrl: '' },
    ollama: { apiKey: '', baseUrl: '' },
    logging: { level: 'info', logFilePath: '' },
    classifier: { weightsPath: '', thresholds: { simpleMax: 0.3, complexMin: 0.65 } },
    modelCatalogPath: '',
    routingTablePath: '',
    http: { port: 8484, enabled: false },
  } as ThrottleConfig;
}

describe('buildAnthropicAuthHeaders', () => {
  describe('explicit api-key mode', () => {
    it('always uses x-api-key header regardless of key format', () => {
      const config = makeConfig({ apiKey: 'eyJhbGciOiJSUz', authType: 'api-key' });
      const headers = buildAnthropicAuthHeaders(config);
      expect(headers).toEqual({ 'x-api-key': 'eyJhbGciOiJSUz' });
    });

    it('uses x-api-key for standard API keys', () => {
      const config = makeConfig({ apiKey: 'sk-ant-abc123', authType: 'api-key' });
      const headers = buildAnthropicAuthHeaders(config);
      expect(headers).toEqual({ 'x-api-key': 'sk-ant-abc123' });
    });
  });

  describe('explicit bearer mode', () => {
    it('always uses Authorization Bearer header regardless of key format', () => {
      const config = makeConfig({ apiKey: 'sk-ant-abc123', authType: 'bearer', baseUrl: 'http://localhost:3456' });
      const headers = buildAnthropicAuthHeaders(config);
      expect(headers).toEqual({ 'Authorization': 'Bearer sk-ant-abc123' });
    });

    it('uses Bearer for OAuth tokens', () => {
      const config = makeConfig({ apiKey: 'eyJhbGciOiJSUz', authType: 'bearer', baseUrl: 'http://localhost:3456' });
      const headers = buildAnthropicAuthHeaders(config);
      expect(headers).toEqual({ 'Authorization': 'Bearer eyJhbGciOiJSUz' });
    });
  });

  describe('auto mode', () => {
    it('detects sk-ant- prefix as API key', () => {
      const config = makeConfig({ apiKey: 'sk-ant-api03-abc123def456', authType: 'auto' });
      const headers = buildAnthropicAuthHeaders(config);
      expect(headers).toEqual({ 'x-api-key': 'sk-ant-api03-abc123def456' });
    });

    it('detects non-sk-ant token as Bearer', () => {
      const config = makeConfig({ apiKey: 'eyJhbGciOiJSUzI1NiJ9', authType: 'auto', baseUrl: 'http://localhost:3456' });
      const headers = buildAnthropicAuthHeaders(config);
      expect(headers).toEqual({ 'Authorization': 'Bearer eyJhbGciOiJSUzI1NiJ9' });
    });

    it('treats empty string as Bearer', () => {
      const config = makeConfig({ apiKey: '', authType: 'auto', baseUrl: 'http://localhost:3456' });
      const headers = buildAnthropicAuthHeaders(config);
      expect(headers).toEqual({ 'Authorization': 'Bearer ' });
    });
  });
});
