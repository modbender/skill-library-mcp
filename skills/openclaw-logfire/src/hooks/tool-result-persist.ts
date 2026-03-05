// SPDX-License-Identifier: MIT
/**
 * Hook: tool_result_persist (synchronous)
 *
 * Closes the most recent tool span, records result size, duration,
 * and any errors with full stack traces per OTEL exception conventions.
 *
 * This hook is synchronous — it MUST NOT return a Promise.
 * Return undefined to leave the result unmodified.
 */

import { SpanStatusCode } from '@opentelemetry/api';
import { spanStore } from '../context/span-store.js';
import {
  prepareForCapture,
  extractErrorDetails,
  safeJsonStringify,
} from '../util.js';
import type { LogfirePluginConfig } from '../config.js';

export interface ToolResultPersistEvent {
  context: {
    sessionKey: string;
  };
  result?: unknown;
  error?: unknown;
}

export function handleToolResultPersist(
  event: ToolResultPersistEvent,
  config: LogfirePluginConfig,
): void {
  const entry = spanStore.popTool(event.context.sessionKey);
  if (!entry) return;

  const durationMs = Date.now() - entry.startTime;
  entry.span.setAttribute('openclaw.tool.duration_ms', durationMs);

  // Result size
  if (event.result !== undefined) {
    const resultStr =
      typeof event.result === 'string'
        ? event.result
        : safeJsonStringify(event.result);
    entry.span.setAttribute('openclaw.tool.output_size', resultStr.length);

    // Opt-in: capture tool output
    if (config.captureToolOutput) {
      entry.span.setAttribute(
        'gen_ai.tool.call.result',
        prepareForCapture(
          event.result,
          config.toolOutputMaxLength,
          config.redactSecrets,
        ),
      );
    }
  }

  // Error handling with stack traces
  if (event.error) {
    const session = spanStore.get(event.context.sessionKey);
    if (session) session.hasError = true;

    const details = extractErrorDetails(event.error);

    entry.span.setAttribute('error.type', details.type);
    entry.span.setStatus({
      code: SpanStatusCode.ERROR,
      message: details.message,
    });

    // Record exception per OTEL semantic conventions
    if (event.error instanceof Error) {
      entry.span.recordException(event.error);
    } else {
      // Manual exception event for non-Error objects
      entry.span.addEvent('exception', {
        'exception.type': details.type,
        'exception.message': details.message,
        ...(config.captureStackTraces && details.stacktrace
          ? { 'exception.stacktrace': details.stacktrace }
          : {}),
      });
    }
  } else {
    entry.span.setStatus({ code: SpanStatusCode.OK });
  }

  entry.span.end();
}
