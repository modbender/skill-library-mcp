// SPDX-License-Identifier: MIT
/**
 * W3C trace context propagation for distributed tracing.
 *
 * - Outbound: Injects traceparent into exec/Bash tool arguments
 *   when they contain HTTP calls matching configured URL patterns.
 * - Inbound: Extracts traceparent from webhook headers for span linking.
 */

import {
  context,
  propagation,
  trace,
  type Span,
  type SpanContext,
} from '@opentelemetry/api';
import picomatch from 'picomatch';
import type { BeforeToolCallEvent } from '../hooks/before-tool-call.js';

/**
 * Inject W3C traceparent into exec/Bash tool arguments.
 *
 * Detects curl/wget/httpie commands and appends trace headers.
 * Only injects if the target URL matches one of the configured patterns.
 */
export function injectTraceContext(
  event: BeforeToolCallEvent,
  parentSpan: Span,
  urlPatterns: string[],
): void {
  const args = event.tool?.args;
  if (!args) return;

  const command =
    typeof args === 'string'
      ? args
      : (args as Record<string, unknown>).command ??
        (args as Record<string, unknown>).cmd ??
        '';
  if (typeof command !== 'string') return;

  // Only inject into HTTP client commands
  if (!isHttpCommand(command)) return;

  // Check if the URL matches configured patterns
  const url = extractUrlFromCommand(command);
  if (!url || !matchesPatterns(url, urlPatterns)) return;

  // Build the traceparent/tracestate headers
  const carrier: Record<string, string> = {};
  const ctx = trace.setSpan(context.active(), parentSpan);
  propagation.inject(ctx, carrier);

  if (!carrier.traceparent) return;

  // Append -H flags to the command
  let headerFlags = ` -H "traceparent: ${carrier.traceparent}"`;
  if (carrier.tracestate) {
    headerFlags += ` -H "tracestate: ${carrier.tracestate}"`;
  }

  // Mutate the event's tool args to include trace headers
  if (typeof args === 'string') {
    event.tool!.args = args + headerFlags;
  } else if (typeof (args as Record<string, unknown>).command === 'string') {
    (args as Record<string, string>).command += headerFlags;
  } else if (typeof (args as Record<string, unknown>).cmd === 'string') {
    (args as Record<string, string>).cmd += headerFlags;
  }
}

/**
 * Extract W3C trace context from inbound webhook headers.
 * Returns a SpanContext for adding as a span link, or null.
 */
export function extractW3CContext(
  headers: Record<string, string>,
): SpanContext | null {
  const traceparent =
    headers.traceparent ?? headers.Traceparent ?? headers.TRACEPARENT;
  if (!traceparent) return null;

  const carrier: Record<string, string> = { traceparent };
  const tracestate =
    headers.tracestate ?? headers.Tracestate ?? headers.TRACESTATE;
  if (tracestate) carrier.tracestate = tracestate;

  const extractedCtx = propagation.extract(context.active(), carrier);
  const span = trace.getSpan(extractedCtx);
  return span?.spanContext() ?? null;
}

// --- internal helpers ---

function isHttpCommand(cmd: string): boolean {
  return /\b(curl|wget|httpie|http)\b/i.test(cmd);
}

/**
 * Best-effort URL extraction from a shell command string.
 * Handles common patterns: curl URL, curl -X POST URL, etc.
 */
function extractUrlFromCommand(cmd: string): string | null {
  // Match URLs (http:// or https://) in the command
  const match = cmd.match(/https?:\/\/[^\s"']+/);
  return match ? match[0] : null;
}

function matchesPatterns(url: string, patterns: string[]): boolean {
  if (patterns.length === 0) return false;
  if (patterns.includes('*')) return true;
  return patterns.some((pattern) => picomatch.isMatch(url, pattern));
}
