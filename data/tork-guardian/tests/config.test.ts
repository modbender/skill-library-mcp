import { describe, it, expect } from 'vitest';
import { TorkConfigSchema } from '../dist/config';
import { DEFAULT_NETWORK_POLICY } from '../dist/policies/network-default';
import { STRICT_NETWORK_POLICY } from '../dist/policies/network-strict';
import { DEVELOPMENT_CONFIG } from '../dist/examples/development';
import { PRODUCTION_CONFIG } from '../dist/examples/production';
import { ENTERPRISE_CONFIG } from '../dist/examples/enterprise';
import { MINIMAL_CONFIG } from '../dist/examples/minimal';

describe('TorkConfigSchema', () => {
  it('parses a minimal config with just an API key', () => {
    const config = TorkConfigSchema.parse({ apiKey: 'tork_test_123' });
    expect(config.apiKey).toBe('tork_test_123');
    expect(config.policy).toBe('standard');
    expect(config.redactPII).toBe(true);
    expect(config.networkPolicy).toBe('default');
  });

  it('applies correct defaults', () => {
    const config = TorkConfigSchema.parse({ apiKey: 'key' });
    expect(config.baseUrl).toBe('https://tork.network');
    expect(config.blockShellCommands).toContain('rm -rf');
    expect(config.blockedPaths).toContain('.env');
    expect(config.allowedPaths).toEqual([]);
  });

  it('rejects empty API key', () => {
    expect(() => TorkConfigSchema.parse({ apiKey: '' })).toThrow();
  });

  it('accepts custom overrides', () => {
    const config = TorkConfigSchema.parse({
      apiKey: 'key',
      policy: 'strict',
      networkPolicy: 'strict',
      maxConnectionsPerMinute: 10,
      allowedDomains: ['api.openai.com'],
    });
    expect(config.policy).toBe('strict');
    expect(config.networkPolicy).toBe('strict');
    expect(config.maxConnectionsPerMinute).toBe(10);
    expect(config.allowedDomains).toEqual(['api.openai.com']);
  });
});

describe('Network Policy Presets', () => {
  describe('DEFAULT_NETWORK_POLICY', () => {
    it('uses "default" as network policy', () => {
      expect(DEFAULT_NETWORK_POLICY.networkPolicy).toBe('default');
    });

    it('allows ports 3000-3999 inbound', () => {
      expect(DEFAULT_NETWORK_POLICY.allowedInboundPorts).toContain(3000);
      expect(DEFAULT_NETWORK_POLICY.allowedInboundPorts).toContain(3999);
    });

    it('allows ports 8000-8999 inbound', () => {
      expect(DEFAULT_NETWORK_POLICY.allowedInboundPorts).toContain(8000);
      expect(DEFAULT_NETWORK_POLICY.allowedInboundPorts).toContain(8999);
    });

    it('allows ports 80, 443, 8080 outbound', () => {
      expect(DEFAULT_NETWORK_POLICY.allowedOutboundPorts).toEqual([80, 443, 8080]);
    });

    it('has no domain restrictions', () => {
      expect(DEFAULT_NETWORK_POLICY.allowedDomains).toEqual([]);
    });

    it('rate limits at 60 connections/min', () => {
      expect(DEFAULT_NETWORK_POLICY.maxConnectionsPerMinute).toBe(60);
    });

    it('has all detection enabled', () => {
      expect(DEFAULT_NETWORK_POLICY.detectPortHijacking).toBe(true);
      expect(DEFAULT_NETWORK_POLICY.detectReverseShells).toBe(true);
      expect(DEFAULT_NETWORK_POLICY.blockPrivilegedPorts).toBe(true);
      expect(DEFAULT_NETWORK_POLICY.blockPrivateNetworks).toBe(true);
      expect(DEFAULT_NETWORK_POLICY.logAllActivity).toBe(true);
    });
  });

  describe('STRICT_NETWORK_POLICY', () => {
    it('uses "strict" as network policy', () => {
      expect(STRICT_NETWORK_POLICY.networkPolicy).toBe('strict');
    });

    it('only allows ports 3000-3010 inbound', () => {
      expect(STRICT_NETWORK_POLICY.allowedInboundPorts).toContain(3000);
      expect(STRICT_NETWORK_POLICY.allowedInboundPorts).toContain(3010);
      expect(STRICT_NETWORK_POLICY.allowedInboundPorts).not.toContain(3011);
    });

    it('only allows port 443 outbound (TLS only)', () => {
      expect(STRICT_NETWORK_POLICY.allowedOutboundPorts).toEqual([443]);
    });

    it('has explicit domain allowlist', () => {
      expect(STRICT_NETWORK_POLICY.allowedDomains.length).toBeGreaterThan(0);
      expect(STRICT_NETWORK_POLICY.allowedDomains).toContain('api.openai.com');
      expect(STRICT_NETWORK_POLICY.allowedDomains).toContain('api.anthropic.com');
      expect(STRICT_NETWORK_POLICY.allowedDomains).toContain('tork.network');
    });

    it('rate limits at 20 connections/min', () => {
      expect(STRICT_NETWORK_POLICY.maxConnectionsPerMinute).toBe(20);
    });
  });
});

describe('Example Configs', () => {
  it('MINIMAL_CONFIG has only an API key placeholder', () => {
    expect(MINIMAL_CONFIG.apiKey).toBeDefined();
  });

  it('DEVELOPMENT_CONFIG uses minimal policy', () => {
    expect(DEVELOPMENT_CONFIG.policy).toBe('minimal');
    expect(DEVELOPMENT_CONFIG.networkPolicy).toBe('default');
  });

  it('PRODUCTION_CONFIG uses standard policy with blocked domains', () => {
    expect(PRODUCTION_CONFIG.policy).toBe('standard');
    expect(PRODUCTION_CONFIG.blockedDomains).toContain('pastebin.com');
    expect(PRODUCTION_CONFIG.blockedDomains).toContain('ngrok.io');
    expect(PRODUCTION_CONFIG.blockedDomains).toContain('webhook.site');
  });

  it('ENTERPRISE_CONFIG uses strict policy with strict network', () => {
    expect(ENTERPRISE_CONFIG.policy).toBe('strict');
    expect(ENTERPRISE_CONFIG.networkPolicy).toBe('strict');
    expect(ENTERPRISE_CONFIG.maxConnectionsPerMinute).toBe(20);
    expect(ENTERPRISE_CONFIG.allowedDomains).toContain('api.openai.com');
  });
});
