import { describe, it, expect } from 'vitest';

// Import everything from the main package entry
import * as guardian from '../dist/index';

describe('Package exports', () => {
  it('exports TorkGuardian class', () => {
    expect(guardian.TorkGuardian).toBeDefined();
    expect(typeof guardian.TorkGuardian).toBe('function');
  });

  it('exports TorkClient class', () => {
    expect(guardian.TorkClient).toBeDefined();
    expect(typeof guardian.TorkClient).toBe('function');
  });

  it('exports NetworkAccessHandler class', () => {
    expect(guardian.NetworkAccessHandler).toBeDefined();
    expect(typeof guardian.NetworkAccessHandler).toBe('function');
  });

  it('exports NetworkMonitor class', () => {
    expect(guardian.NetworkMonitor).toBeDefined();
    expect(typeof guardian.NetworkMonitor).toBe('function');
  });

  it('exports GovernanceDeniedError class', () => {
    expect(guardian.GovernanceDeniedError).toBeDefined();
    expect(typeof guardian.GovernanceDeniedError).toBe('function');
  });

  it('exports standalone governance functions', () => {
    expect(typeof guardian.governLLMRequest).toBe('function');
    expect(typeof guardian.governToolCall).toBe('function');
    expect(typeof guardian.redactPII).toBe('function');
    expect(typeof guardian.generateReceipt).toBe('function');
  });

  it('exports network standalone functions', () => {
    expect(typeof guardian.validatePortBind).toBe('function');
    expect(typeof guardian.validateEgress).toBe('function');
    expect(typeof guardian.validateDNS).toBe('function');
  });

  it('exports network policy presets', () => {
    expect(guardian.DEFAULT_NETWORK_POLICY).toBeDefined();
    expect(guardian.STRICT_NETWORK_POLICY).toBeDefined();
    expect(guardian.DEFAULT_NETWORK_POLICY.networkPolicy).toBe('default');
    expect(guardian.STRICT_NETWORK_POLICY.networkPolicy).toBe('strict');
  });

  it('exports example configs', () => {
    expect(guardian.MINIMAL_CONFIG).toBeDefined();
    expect(guardian.DEVELOPMENT_CONFIG).toBeDefined();
    expect(guardian.PRODUCTION_CONFIG).toBeDefined();
    expect(guardian.ENTERPRISE_CONFIG).toBeDefined();
  });

  it('exports scanner classes and functions', () => {
    expect(guardian.SkillScanner).toBeDefined();
    expect(typeof guardian.SkillScanner).toBe('function');
    expect(typeof guardian.scanFromSource).toBe('function');
    expect(typeof guardian.scanFromURL).toBe('function');
    expect(typeof guardian.formatReportForAPI).toBe('function');
  });

  it('exports badge functions', () => {
    expect(typeof guardian.generateBadge).toBe('function');
    expect(typeof guardian.generateBadgeMarkdown).toBe('function');
    expect(typeof guardian.generateBadgeJSON).toBe('function');
  });

  it('exports scan rules', () => {
    expect(guardian.SCAN_RULES).toBeDefined();
    expect(Array.isArray(guardian.SCAN_RULES)).toBe(true);
    expect(guardian.SCAN_RULES.length).toBe(14);
  });

  it('exports ReportStore', () => {
    expect(guardian.ReportStore).toBeDefined();
  });
});

describe('TorkGuardian class', () => {
  it('constructs with API key', () => {
    const g = new guardian.TorkGuardian({ apiKey: 'test-key' });
    expect(g).toBeDefined();
  });

  it('has governLLM method', () => {
    const g = new guardian.TorkGuardian({ apiKey: 'test-key' });
    expect(typeof g.governLLM).toBe('function');
  });

  it('has governTool method', () => {
    const g = new guardian.TorkGuardian({ apiKey: 'test-key' });
    expect(typeof g.governTool).toBe('function');
  });

  it('has redactPII method', () => {
    const g = new guardian.TorkGuardian({ apiKey: 'test-key' });
    expect(typeof g.redactPII).toBe('function');
  });

  it('has generateReceipt method', () => {
    const g = new guardian.TorkGuardian({ apiKey: 'test-key' });
    expect(typeof g.generateReceipt).toBe('function');
  });

  it('has getNetworkHandler method', () => {
    const g = new guardian.TorkGuardian({ apiKey: 'test-key' });
    expect(typeof g.getNetworkHandler).toBe('function');
    expect(g.getNetworkHandler()).toBeInstanceOf(guardian.NetworkAccessHandler);
  });

  it('getConfig returns parsed config', () => {
    const g = new guardian.TorkGuardian({ apiKey: 'test-key', policy: 'strict' });
    const config = g.getConfig();
    expect(config.apiKey).toBe('test-key');
    expect(config.policy).toBe('strict');
  });
});
