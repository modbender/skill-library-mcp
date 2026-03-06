// SPDX-License-Identifier: MIT
/**
 * Hook: agent_end
 *
 * Closes the invoke_agent span, records token usage and duration,
 * emits metrics, and logs the Logfire trace link.
 */

import { SpanStatusCode } from '@opentelemetry/api';
import { spanStore } from '../context/span-store.js';
import { buildLogfireTraceUrl } from '../trace-link.js';
import { recordTokenUsage, recordOperationDuration } from '../metrics/genai-metrics.js';
import { extractWorkspaceName } from '../util.js';
import type { LogfirePluginConfig } from '../config.js';

export interface AgentEndEvent {
  context: {
    sessionKey: string;
    agentId?: string;
    workspaceDir?: string;
    model?: string;
  };
  /** Token usage reported by OpenClaw (structure may vary). */
  usage?: {
    inputTokens?: number;
    outputTokens?: number;
    totalTokens?: number;
    model?: string;
    cost?: number;
  };
  error?: unknown;
}

/** Logger interface — matches OpenClaw plugin api.logger shape. */
export interface Logger {
  info(msg: string): void;
  debug(msg: string): void;
  warn(msg: string): void;
  error(msg: string): void;
}

export function handleAgentEnd(
  event: AgentEndEvent,
  config: LogfirePluginConfig,
  logger: Logger,
): void {
  const session = spanStore.get(event.context.sessionKey);
  if (!session) return;

  const durationMs = Date.now() - session.startTime;
  const durationS = durationMs / 1000;
  const agentName = event.context.agentId || 'agent';
  const workspace = extractWorkspaceName(event.context.workspaceDir);

  // Close any remaining tool spans (shouldn't happen but safety net)
  for (const tool of session.toolStack) {
    tool.span.end();
  }

  // Token usage attributes
  const usage = event.usage;
  if (usage) {
    if (usage.inputTokens !== undefined) {
      session.agentSpan.setAttribute(
        'gen_ai.usage.input_tokens',
        usage.inputTokens,
      );
    }
    if (usage.outputTokens !== undefined) {
      session.agentSpan.setAttribute(
        'gen_ai.usage.output_tokens',
        usage.outputTokens,
      );
    }
    if (usage.model) {
      session.agentSpan.setAttribute('gen_ai.response.model', usage.model);
    }
  }

  // Duration and tool count
  session.agentSpan.setAttribute('openclaw.request.duration_ms', durationMs);
  session.agentSpan.setAttribute(
    'openclaw.request.tool_count',
    session.toolSequence,
  );

  // Error status
  if (event.error || session.hasError) {
    const errorType =
      event.error instanceof Error
        ? event.error.constructor.name
        : session.hasError
          ? 'ToolError'
          : 'Error';
    session.agentSpan.setAttribute('error.type', errorType);
    session.agentSpan.setStatus({
      code: SpanStatusCode.ERROR,
      message: event.error ? String(event.error) : 'Tool error occurred',
    });
  } else {
    session.agentSpan.setStatus({ code: SpanStatusCode.OK });
  }

  // End the agent span
  session.agentSpan.end();

  // Record metrics
  if (config.enableMetrics) {
    const metricAttrs = {
      agentName,
      workspace,
      providerName: config.providerName || 'unknown',
      requestModel: event.context.model || usage?.model || '',
      responseModel: usage?.model || '',
      hasError: !!(event.error || session.hasError),
      errorType: event.error
        ? event.error instanceof Error
          ? event.error.constructor.name
          : 'Error'
        : undefined,
    };

    recordOperationDuration(durationS, metricAttrs);

    if (usage?.inputTokens !== undefined) {
      recordTokenUsage(usage.inputTokens, 'input', metricAttrs);
    }
    if (usage?.outputTokens !== undefined) {
      recordTokenUsage(usage.outputTokens, 'output', metricAttrs);
    }
  }

  // Log trace link
  if (config.enableTraceLinks && config.projectUrl) {
    const traceId = session.agentSpan.spanContext().traceId;
    const url = buildLogfireTraceUrl(config.projectUrl, traceId);
    logger.info(`Logfire trace: ${url}`);
  }

  // Cleanup
  spanStore.delete(event.context.sessionKey);
}
