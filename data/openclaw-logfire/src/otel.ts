// SPDX-License-Identifier: MIT
/**
 * OpenTelemetry SDK initialization targeting Logfire's OTLP endpoint.
 *
 * Logfire accepts traces and metrics over HTTP/protobuf (not gRPC).
 * Authentication is a write token passed as the Authorization header.
 */

import { NodeSDK } from '@opentelemetry/sdk-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-proto';
import { OTLPMetricExporter } from '@opentelemetry/exporter-metrics-otlp-proto';
import { PeriodicExportingMetricReader } from '@opentelemetry/sdk-metrics';
import {
  BatchSpanProcessor,
  SimpleSpanProcessor,
} from '@opentelemetry/sdk-trace-base';
import { Resource } from '@opentelemetry/resources';
import {
  ATTR_SERVICE_NAME,
  SEMRESATTRS_DEPLOYMENT_ENVIRONMENT,
} from '@opentelemetry/semantic-conventions';
import type { LogfirePluginConfig } from './config.js';

const LOGFIRE_ENDPOINTS: Record<string, string> = {
  us: 'https://logfire-us.pydantic.dev',
  eu: 'https://logfire-eu.pydantic.dev',
};

export function initializeOtel(config: LogfirePluginConfig): NodeSDK {
  const token = config.token;
  if (!token) {
    throw new Error(
      '@ultrathink-solutions/openclaw-logfire: LOGFIRE_TOKEN is required. ' +
        'Set it as an environment variable or in plugins.entries.logfire.config.token',
    );
  }

  const baseEndpoint = LOGFIRE_ENDPOINTS[config.region] ?? LOGFIRE_ENDPOINTS.us;
  const authHeaders = { Authorization: `Bearer ${token}` };

  // Trace exporter
  const traceExporter = new OTLPTraceExporter({
    url: `${baseEndpoint}/v1/traces`,
    headers: authHeaders,
  });

  // Resource attributes
  const resourceAttrs: Record<string, string> = {
    [ATTR_SERVICE_NAME]: config.serviceName,
    [SEMRESATTRS_DEPLOYMENT_ENVIRONMENT]: config.environment,
    ...config.resourceAttributes,
  };
  if (config.projectUrl) {
    resourceAttrs['logfire.project_url'] = config.projectUrl;
  }

  const resource = new Resource(resourceAttrs);

  // Span processor
  const spanProcessor =
    config.spanProcessorType === 'simple'
      ? new SimpleSpanProcessor(traceExporter)
      : new BatchSpanProcessor(traceExporter, {
          maxQueueSize: config.batchConfig.maxQueueSize,
          maxExportBatchSize: config.batchConfig.maxExportBatchSize,
          scheduledDelayMillis: config.batchConfig.scheduledDelayMs,
        });

  // SDK config
  const sdkConfig: ConstructorParameters<typeof NodeSDK>[0] = {
    resource,
    spanProcessors: [spanProcessor],
  };

  // Metrics exporter (optional)
  if (config.enableMetrics) {
    const metricExporter = new OTLPMetricExporter({
      url: `${baseEndpoint}/v1/metrics`,
      headers: authHeaders,
    });
    sdkConfig.metricReader = new PeriodicExportingMetricReader({
      exporter: metricExporter,
      exportIntervalMillis: config.metricsIntervalMs,
    });
  }

  const sdk = new NodeSDK(sdkConfig);
  sdk.start();
  return sdk;
}
