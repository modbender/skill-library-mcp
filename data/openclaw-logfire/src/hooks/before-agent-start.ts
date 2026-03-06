// SPDX-License-Identifier: MIT
/**
 * Hook: before_agent_start
 *
 * Creates the root `invoke_agent` span following OTEL GenAI semantic
 * conventions.  This span parents all tool call spans and is closed
 * in agent-end.ts.
 */

import { trace, context, SpanKind } from '@opentelemetry/api';
import { spanStore, type SessionSpanContext } from '../context/span-store.js';
import { extractWorkspaceName } from '../util.js';
import type { LogfirePluginConfig } from '../config.js';

/** Minimal contract for the hook event — we only access what we need. */
export interface BeforeAgentStartEvent {
  context: {
    sessionKey: string;
    agentId?: string;
    workspaceDir?: string;
    commandSource?: string;
    senderId?: string;
    model?: string;
    messages?: unknown[];
  };
}

export function handleBeforeAgentStart(
  event: BeforeAgentStartEvent,
  config: LogfirePluginConfig,
): void {
  const tracer = trace.getTracer('@ultrathink-solutions/openclaw-logfire', '0.1.0');
  const agentName = event.context.agentId || 'agent';
  const workspace = extractWorkspaceName(event.context.workspaceDir);

  // Span name per spec: "invoke_agent {gen_ai.agent.name}"
  const spanName = `invoke_agent ${agentName}`;

  const agentSpan = tracer.startSpan(
    spanName,
    {
      kind: SpanKind.INTERNAL,
      attributes: {
        // Required GenAI attributes
        'gen_ai.operation.name': 'invoke_agent',
        'gen_ai.provider.name': config.providerName || 'unknown',

        // Agent attributes
        'gen_ai.agent.name': agentName,
        'gen_ai.agent.id': event.context.agentId || '',
        'gen_ai.conversation.id': event.context.sessionKey,

        // Model (if known at start)
        ...(event.context.model
          ? { 'gen_ai.request.model': event.context.model }
          : {}),

        // OpenClaw-specific context
        'openclaw.session_key': event.context.sessionKey,
        'openclaw.workspace': workspace,
        'openclaw.channel': event.context.commandSource || 'unknown',
        'openclaw.sender_id': event.context.senderId || '',
      },
    },
    context.active(),
  );

  const agentCtx = trace.setSpan(context.active(), agentSpan);

  const session: SessionSpanContext = {
    agentSpan,
    agentCtx,
    toolStack: [],
    toolSequence: 0,
    hasError: false,
    startTime: Date.now(),
  };

  spanStore.set(event.context.sessionKey, session);
}
