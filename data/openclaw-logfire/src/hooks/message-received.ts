// SPDX-License-Identifier: MIT
/**
 * Hook: message_received
 *
 * Enriches the active agent span with channel and sender information.
 * Optionally extracts W3C trace context from inbound webhook headers
 * and adds span links for cross-service correlation.
 */

import { spanStore } from '../context/span-store.js';
import { extractW3CContext } from '../context/propagation.js';
import type { LogfirePluginConfig } from '../config.js';

export interface MessageReceivedEvent {
  context: {
    sessionKey: string;
    commandSource?: string;
    senderId?: string;
    headers?: Record<string, string>;
  };
  messages?: unknown[];
}

export function handleMessageReceived(
  event: MessageReceivedEvent,
  config: LogfirePluginConfig,
): void {
  const session = spanStore.get(event.context.sessionKey);
  if (!session) return;

  // Enrich the agent span with channel info
  if (event.context.commandSource) {
    session.agentSpan.setAttribute(
      'openclaw.channel',
      event.context.commandSource,
    );
  }
  if (event.context.senderId) {
    session.agentSpan.setAttribute(
      'openclaw.sender_id',
      event.context.senderId,
    );
  }
  if (event.messages) {
    session.agentSpan.setAttribute(
      'openclaw.message_count',
      event.messages.length,
    );
  }

  // Extract inbound trace context from webhook headers (distributed tracing)
  if (
    config.distributedTracing.enabled &&
    config.distributedTracing.extractFromWebhooks &&
    event.context.headers
  ) {
    const remoteContext = extractW3CContext(event.context.headers);
    if (remoteContext) {
      session.agentSpan.addLink({ context: remoteContext });
    }
  }
}
