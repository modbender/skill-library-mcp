// SPDX-License-Identifier: MIT
/**
 * OTEL GenAI semantic convention metrics.
 *
 * gen_ai.client.token.usage     — Histogram of token counts
 * gen_ai.client.operation.duration — Histogram of operation latency
 *
 * Bucket boundaries follow the spec recommendations.
 */

import { metrics } from '@opentelemetry/api';

const meter = metrics.getMeter('@ultrathink-solutions/openclaw-logfire', '0.1.0');

/** Spec bucket boundaries for token usage. */
const TOKEN_BUCKETS = [
  1, 4, 16, 64, 256, 1024, 4096, 16384, 65536, 262144, 1048576, 4194304,
  16777216, 67108864,
];

/** Spec bucket boundaries for operation duration (seconds). */
const DURATION_BUCKETS = [
  0.01, 0.02, 0.04, 0.08, 0.16, 0.32, 0.64, 1.28, 2.56, 5.12, 10.24, 20.48,
  40.96, 81.92,
];

const tokenHistogram = meter.createHistogram('gen_ai.client.token.usage', {
  description: 'Number of input and output tokens used',
  unit: '{token}',
  advice: { explicitBucketBoundaries: TOKEN_BUCKETS },
});

const durationHistogram = meter.createHistogram(
  'gen_ai.client.operation.duration',
  {
    description: 'GenAI operation duration',
    unit: 's',
    advice: { explicitBucketBoundaries: DURATION_BUCKETS },
  },
);

export interface MetricAttributes {
  agentName: string;
  workspace: string;
  providerName: string;
  requestModel: string;
  responseModel: string;
  hasError: boolean;
  errorType?: string;
}

export function recordTokenUsage(
  tokens: number,
  tokenType: 'input' | 'output',
  attrs: MetricAttributes,
): void {
  tokenHistogram.record(tokens, {
    'gen_ai.operation.name': 'invoke_agent',
    'gen_ai.provider.name': attrs.providerName,
    'gen_ai.token.type': tokenType,
    'gen_ai.request.model': attrs.requestModel,
    'gen_ai.response.model': attrs.responseModel,
    'openclaw.agent_name': attrs.agentName,
    'openclaw.workspace': attrs.workspace,
  });
}

export function recordOperationDuration(
  durationSeconds: number,
  attrs: MetricAttributes,
): void {
  durationHistogram.record(durationSeconds, {
    'gen_ai.operation.name': 'invoke_agent',
    'gen_ai.provider.name': attrs.providerName,
    'gen_ai.request.model': attrs.requestModel,
    'gen_ai.response.model': attrs.responseModel,
    'openclaw.agent_name': attrs.agentName,
    'openclaw.workspace': attrs.workspace,
    ...(attrs.hasError && attrs.errorType
      ? { 'error.type': attrs.errorType }
      : {}),
  });
}
