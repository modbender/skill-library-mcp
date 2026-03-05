import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { resolveConfig } from './config.js';

describe('resolveConfig', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    process.env = { ...originalEnv };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  it('returns sensible defaults when no config provided', () => {
    const config = resolveConfig(undefined);
    expect(config.serviceName).toBe('openclaw-agent');
    expect(config.region).toBe('us');
    expect(config.environment).toBe('development');
    expect(config.captureToolInput).toBe(true);
    expect(config.captureToolOutput).toBe(false);
    expect(config.captureMessageContent).toBe(false);
    expect(config.redactSecrets).toBe(true);
    expect(config.distributedTracing.enabled).toBe(false);
    expect(config.enableMetrics).toBe(true);
    expect(config.spanProcessorType).toBe('batch');
  });

  it('reads LOGFIRE_TOKEN from env', () => {
    process.env.LOGFIRE_TOKEN = 'test-token-123';
    const config = resolveConfig({});
    expect(config.token).toBe('test-token-123');
  });

  it('explicit config overrides env vars', () => {
    process.env.LOGFIRE_TOKEN = 'env-token';
    const config = resolveConfig({ token: 'explicit-token' });
    expect(config.token).toBe('explicit-token');
  });

  it('reads LOGFIRE_ENVIRONMENT from env', () => {
    process.env.LOGFIRE_ENVIRONMENT = 'production';
    const config = resolveConfig({});
    expect(config.environment).toBe('production');
  });

  it('merges partial distributedTracing config with defaults', () => {
    const config = resolveConfig({
      distributedTracing: { enabled: true },
    });
    expect(config.distributedTracing.enabled).toBe(true);
    expect(config.distributedTracing.injectIntoCommands).toBe(true);
    expect(config.distributedTracing.urlPatterns).toEqual(['*']);
  });

  it('validates enum values and falls back to defaults', () => {
    const config = resolveConfig({
      region: 'invalid',
      logLevel: 'verbose',
      spanProcessorType: 'turbo',
    });
    expect(config.region).toBe('us');
    expect(config.logLevel).toBe('info');
    expect(config.spanProcessorType).toBe('batch');
  });

  it('accepts valid enum values', () => {
    const config = resolveConfig({
      region: 'eu',
      logLevel: 'debug',
      spanProcessorType: 'simple',
    });
    expect(config.region).toBe('eu');
    expect(config.logLevel).toBe('debug');
    expect(config.spanProcessorType).toBe('simple');
  });

  it('merges batchConfig with defaults', () => {
    const config = resolveConfig({
      batchConfig: { maxQueueSize: 4096 },
    });
    expect(config.batchConfig.maxQueueSize).toBe(4096);
    expect(config.batchConfig.maxExportBatchSize).toBe(512);
    expect(config.batchConfig.scheduledDelayMs).toBe(5000);
  });

  it('accepts resourceAttributes as string record', () => {
    const config = resolveConfig({
      resourceAttributes: { 'custom.team': 'platform', 'custom.version': '2.0' },
    });
    expect(config.resourceAttributes).toEqual({
      'custom.team': 'platform',
      'custom.version': '2.0',
    });
  });
});
