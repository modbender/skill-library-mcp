// SPDX-License-Identifier: MIT
/**
 * Hook: before_tool_call
 *
 * Creates an `execute_tool` child span for each tool invocation,
 * following OTEL GenAI semantic conventions.  Optionally injects
 * W3C traceparent into HTTP commands for distributed tracing.
 */

import { trace, SpanKind } from '@opentelemetry/api';
import { spanStore } from '../context/span-store.js';
import {
  generateCallId,
  prepareForCapture,
} from '../util.js';
import { injectTraceContext } from '../context/propagation.js';
import type { LogfirePluginConfig } from '../config.js';

export interface BeforeToolCallEvent {
  context: {
    sessionKey: string;
  };
  tool?: {
    name?: string;
    description?: string;
    args?: unknown;
  };
}

export function handleBeforeToolCall(
  event: BeforeToolCallEvent,
  config: LogfirePluginConfig,
): void {
  const session = spanStore.get(event.context.sessionKey);
  if (!session) return;

  const tracer = trace.getTracer('@ultrathink-solutions/openclaw-logfire', '0.1.0');
  const toolName = event.tool?.name || 'unknown';
  const callId = generateCallId();

  session.toolSequence++;

  // Span name per spec: "execute_tool {gen_ai.tool.name}"
  const spanName = `execute_tool ${toolName}`;

  const attributes: Record<string, string | number | boolean> = {
    'gen_ai.operation.name': 'execute_tool',
    'gen_ai.tool.name': toolName,
    'gen_ai.tool.call.id': callId,
    'gen_ai.tool.type': 'function',
    'openclaw.tool.sequence': session.toolSequence,
  };

  // Optional tool description
  if (event.tool?.description) {
    attributes['gen_ai.tool.description'] = event.tool.description;
  }

  // Opt-in: capture tool arguments
  if (config.captureToolInput && event.tool?.args !== undefined) {
    attributes['gen_ai.tool.call.arguments'] = prepareForCapture(
      event.tool.args,
      config.toolInputMaxLength,
      config.redactSecrets,
    );
    attributes['openclaw.tool.input_size'] =
      typeof event.tool.args === 'string'
        ? event.tool.args.length
        : JSON.stringify(event.tool.args ?? '').length;
  }

  const toolSpan = tracer.startSpan(
    spanName,
    { kind: SpanKind.INTERNAL, attributes },
    session.agentCtx,
  );

  const toolCtx = trace.setSpan(session.agentCtx, toolSpan);

  spanStore.pushTool(event.context.sessionKey, {
    span: toolSpan,
    ctx: toolCtx,
    name: toolName,
    callId,
    startTime: Date.now(),
  });

  // Distributed tracing: inject traceparent into HTTP calls
  if (
    config.distributedTracing.enabled &&
    config.distributedTracing.injectIntoCommands &&
    event.tool?.args !== undefined
  ) {
    injectTraceContext(event, toolSpan, config.distributedTracing.urlPatterns);
  }
}
