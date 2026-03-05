import { describe, it, expect } from 'vitest';
import { computeStats, formatStatsTable } from '../../../src/logging/stats.js';
import type { RoutingLogEntry } from '../../../src/logging/types.js';
import type { ModelSpec } from '../../../src/router/types.js';

function makeEntry(overrides: Partial<RoutingLogEntry> = {}): RoutingLogEntry {
  return {
    requestId: 'test-id',
    timestamp: '2026-02-08T12:00:00.000Z',
    promptHash: 'abc123',
    compositeScore: 0.3,
    tier: 'simple',
    selectedModel: 'gemini-2.5-flash',
    provider: 'google',
    mode: 'standard',
    override: 'none',
    inputTokens: 100,
    outputTokens: 200,
    estimatedCostUsd: 0.000135,
    latencyMs: 300,
    ...overrides,
  };
}

const premiumBaseline: ModelSpec = {
  id: 'claude-opus-4-6',
  displayName: 'Claude Opus 4.6',
  provider: 'anthropic',
  inputCostPerMTok: 5.00,
  outputCostPerMTok: 25.00,
  maxContextTokens: 200000,
};

describe('computeStats', () => {
  it('returns zeros for empty entries', () => {
    const stats = computeStats([]);
    expect(stats.totalRequests).toBe(0);
    expect(stats.totalCostUsd).toBe(0);
    expect(stats.estimatedSavingsUsd).toBe(0);
  });

  it('computes correct totals', () => {
    const entries = [
      makeEntry({ estimatedCostUsd: 0.001, inputTokens: 100, outputTokens: 200, latencyMs: 300 }),
      makeEntry({ estimatedCostUsd: 0.002, inputTokens: 200, outputTokens: 400, latencyMs: 500 }),
    ];
    const stats = computeStats(entries);
    expect(stats.totalRequests).toBe(2);
    expect(stats.totalCostUsd).toBeCloseTo(0.003, 4);
  });

  it('computes savings vs default baseline (legacy Opus pricing)', () => {
    const entries = [
      makeEntry({
        selectedModel: 'gemini-2.5-flash',
        inputTokens: 1000,
        outputTokens: 1000,
        estimatedCostUsd: 0.00075, // Flash pricing
      }),
    ];
    const stats = computeStats(entries);
    // Default baseline: Opus pricing (5/25 per MTok)
    // Cost: (1000/1M)*5 + (1000/1M)*25 = 0.005 + 0.025 = 0.030
    expect(stats.costIfAlwaysPremium).toBeCloseTo(0.030, 4);
    expect(stats.estimatedSavingsUsd).toBeGreaterThan(0);
    expect(stats.savingsPercent).toBeGreaterThan(90);
    expect(stats.baselineModel).toBe('claude-opus-4-6');
  });

  it('uses custom baseline model when provided', () => {
    const entries = [
      makeEntry({
        inputTokens: 1000,
        outputTokens: 1000,
        estimatedCostUsd: 0.00075,
      }),
    ];
    const stats = computeStats(entries, premiumBaseline);
    expect(stats.baselineModel).toBe('Claude Opus 4.6');
    expect(stats.costIfAlwaysPremium).toBeCloseTo(0.030, 4);
  });

  it('tracks model distribution', () => {
    const entries = [
      makeEntry({ selectedModel: 'gemini-2.5-flash' }),
      makeEntry({ selectedModel: 'gemini-2.5-flash' }),
      makeEntry({ selectedModel: 'claude-sonnet-4-5' }),
    ];
    const stats = computeStats(entries);
    expect(stats.modelDistribution['gemini-2.5-flash']?.count).toBe(2);
    expect(stats.modelDistribution['claude-sonnet-4-5']?.count).toBe(1);
    expect(stats.modelDistribution['gemini-2.5-flash']?.percentOfRequests).toBeCloseTo(66.67, 0);
  });

  it('tracks tier distribution', () => {
    const entries = [
      makeEntry({ tier: 'simple' }),
      makeEntry({ tier: 'simple' }),
      makeEntry({ tier: 'complex' }),
    ];
    const stats = computeStats(entries);
    expect(stats.tierDistribution.simple).toBe(2);
    expect(stats.tierDistribution.complex).toBe(1);
    expect(stats.tierDistribution.standard).toBe(0);
  });
});

describe('formatStatsTable', () => {
  it('formats stats as readable table', () => {
    const entries = [
      makeEntry({ timestamp: '2026-02-01T00:00:00Z' }),
      makeEntry({ timestamp: '2026-02-08T00:00:00Z' }),
    ];
    const stats = computeStats(entries);
    const output = formatStatsTable(stats, 30);
    expect(output).toContain('Clawd Throttle');
    expect(output).toContain('Total requests:');
    expect(output).toContain('Model Distribution:');
    expect(output).toContain('Complexity Distribution:');
  });

  it('shows baseline model name in output', () => {
    const entries = [makeEntry()];
    const stats = computeStats(entries, premiumBaseline);
    const output = formatStatsTable(stats, 30);
    expect(output).toContain('Claude Opus 4.6');
  });
});
