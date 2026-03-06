import type { RoutingLogEntry, AggregateStats } from './types.js';
import type { ComplexityTier } from '../classifier/types.js';
import type { ModelSpec } from '../router/types.js';

/** Default baseline if none provided (legacy Opus pricing). */
const DEFAULT_BASELINE = { inputCostPerMTok: 5.00, outputCostPerMTok: 25.00, displayName: 'claude-opus-4-6' };

export function computeStats(
  entries: RoutingLogEntry[],
  baselineModel?: ModelSpec,
): AggregateStats {
  const baseline = baselineModel ?? DEFAULT_BASELINE as Pick<ModelSpec, 'inputCostPerMTok' | 'outputCostPerMTok' | 'displayName'>;
  const baselineName = baseline.displayName;

  if (entries.length === 0) {
    return {
      totalRequests: 0,
      totalCostUsd: 0,
      costIfAlwaysPremium: 0,
      baselineModel: baselineName,
      estimatedSavingsUsd: 0,
      savingsPercent: 0,
      modelDistribution: {},
      tierDistribution: { simple: 0, standard: 0, complex: 0 },
      periodStart: new Date().toISOString(),
      periodEnd: new Date().toISOString(),
      avgLatencyMs: 0,
    };
  }

  let totalCostUsd = 0;
  let costIfAlwaysPremium = 0;
  let totalLatencyMs = 0;

  const modelDist: Record<string, { count: number; costUsd: number }> = {};
  const tierDist: Record<ComplexityTier, number> = { simple: 0, standard: 0, complex: 0 };

  for (const entry of entries) {
    totalCostUsd += entry.estimatedCostUsd;
    totalLatencyMs += entry.latencyMs;

    costIfAlwaysPremium +=
      (entry.inputTokens / 1_000_000) * baseline.inputCostPerMTok +
      (entry.outputTokens / 1_000_000) * baseline.outputCostPerMTok;

    if (!modelDist[entry.selectedModel]) {
      modelDist[entry.selectedModel] = { count: 0, costUsd: 0 };
    }
    modelDist[entry.selectedModel]!.count++;
    modelDist[entry.selectedModel]!.costUsd += entry.estimatedCostUsd;

    tierDist[entry.tier]++;
  }

  const estimatedSavingsUsd = costIfAlwaysPremium - totalCostUsd;
  const savingsPercent = costIfAlwaysPremium > 0
    ? (estimatedSavingsUsd / costIfAlwaysPremium) * 100
    : 0;

  const modelDistFull: AggregateStats['modelDistribution'] = {};
  for (const [modelId, data] of Object.entries(modelDist)) {
    modelDistFull[modelId] = {
      count: data.count,
      costUsd: data.costUsd,
      percentOfRequests: (data.count / entries.length) * 100,
    };
  }

  const timestamps = entries.map(e => e.timestamp).sort();

  return {
    totalRequests: entries.length,
    totalCostUsd,
    costIfAlwaysPremium,
    baselineModel: baselineName,
    estimatedSavingsUsd,
    savingsPercent,
    modelDistribution: modelDistFull,
    tierDistribution: tierDist,
    periodStart: timestamps[0]!,
    periodEnd: timestamps[timestamps.length - 1]!,
    avgLatencyMs: Math.round(totalLatencyMs / entries.length),
  };
}

export function formatStatsTable(stats: AggregateStats, days: number): string {
  const lines: string[] = [];

  lines.push('');
  lines.push(`=== Clawd Throttle - Routing Stats (last ${days} days) ===`);
  lines.push('');
  lines.push(`Total requests:       ${stats.totalRequests.toLocaleString()}`);
  lines.push(`Total cost:           $${stats.totalCostUsd.toFixed(2)}`);
  lines.push(`Cost if always ${stats.baselineModel}: $${stats.costIfAlwaysPremium.toFixed(2)}`);
  lines.push(`Estimated savings:    $${stats.estimatedSavingsUsd.toFixed(2)} (${stats.savingsPercent.toFixed(1)}%)`);
  lines.push('');
  lines.push('Model Distribution:');

  for (const [modelId, data] of Object.entries(stats.modelDistribution)) {
    const pct = data.percentOfRequests.toFixed(1);
    lines.push(`  ${modelId.padEnd(30)} ${String(data.count).padStart(6)} requests   $${data.costUsd.toFixed(2).padStart(8)}   (${pct}%)`);
  }

  lines.push('');
  lines.push('Complexity Distribution:');
  for (const [tier, count] of Object.entries(stats.tierDistribution)) {
    const pct = stats.totalRequests > 0 ? ((count / stats.totalRequests) * 100).toFixed(1) : '0.0';
    lines.push(`  ${tier.padEnd(12)} ${String(count).padStart(6)} (${pct}%)`);
  }

  lines.push('');
  lines.push(`Avg latency:          ${stats.avgLatencyMs.toLocaleString()}ms`);
  lines.push(`Period:               ${stats.periodStart.slice(0, 10)} to ${stats.periodEnd.slice(0, 10)}`);
  lines.push('');

  return lines.join('\n');
}
