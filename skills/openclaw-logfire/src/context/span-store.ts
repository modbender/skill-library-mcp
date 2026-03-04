// SPDX-License-Identifier: MIT
/**
 * In-memory store mapping OpenClaw session keys to active OTEL spans.
 *
 * Tool spans use a stack (LIFO) so nested tool calls close in the
 * correct order.  A TTL-based cleanup prevents memory leaks from
 * sessions that never fire agent_end (e.g. gateway crash).
 */

import type { Span, Context } from '@opentelemetry/api';

export interface ToolSpanEntry {
  span: Span;
  ctx: Context;
  name: string;
  callId: string;
  startTime: number;
}

export interface SessionSpanContext {
  /** Root span: invoke_agent */
  agentSpan: Span;
  agentCtx: Context;

  /** Tool call stack (LIFO for correct nesting) */
  toolStack: ToolSpanEntry[];

  /** Monotonic tool call counter for sequencing */
  toolSequence: number;

  /** Whether any tool errored (propagated to agent span) */
  hasError: boolean;

  /** Request start timestamp */
  startTime: number;
}

/** Max age before a session is considered orphaned and cleaned up. */
const MAX_AGE_MS = 30 * 60 * 1000; // 30 minutes

class SpanStore {
  private sessions = new Map<string, SessionSpanContext>();

  set(sessionKey: string, ctx: SessionSpanContext): void {
    this.sessions.set(sessionKey, ctx);
    this.cleanup();
  }

  get(sessionKey: string): SessionSpanContext | undefined {
    return this.sessions.get(sessionKey);
  }

  delete(sessionKey: string): void {
    this.sessions.delete(sessionKey);
  }

  /** Push a tool span onto the session's stack. */
  pushTool(sessionKey: string, entry: ToolSpanEntry): void {
    const session = this.sessions.get(sessionKey);
    if (!session) return;
    session.toolStack.push(entry);
  }

  /** Pop the most recent tool span (LIFO). */
  popTool(sessionKey: string): ToolSpanEntry | undefined {
    const session = this.sessions.get(sessionKey);
    if (!session) return undefined;
    return session.toolStack.pop();
  }

  /** Peek at the top of the tool stack without removing. */
  peekTool(sessionKey: string): ToolSpanEntry | undefined {
    const session = this.sessions.get(sessionKey);
    if (!session || session.toolStack.length === 0) return undefined;
    return session.toolStack[session.toolStack.length - 1];
  }

  get size(): number {
    return this.sessions.size;
  }

  /** End orphaned spans and remove stale sessions. */
  private cleanup(): void {
    const now = Date.now();
    for (const [key, session] of this.sessions) {
      if (now - session.startTime > MAX_AGE_MS) {
        // End any orphaned tool spans
        for (const tool of session.toolStack) {
          tool.span.end();
        }
        session.agentSpan.end();
        this.sessions.delete(key);
      }
    }
  }
}

export const spanStore = new SpanStore();
