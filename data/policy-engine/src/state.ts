/**
 * Session policy state manager.
 *
 * Tracks per-session block counts, tool call history, escalation level,
 * and dry-run overrides. Cleans up entries older than the configured TTL.
 */

export type ToolCallRecord = {
  tool: string;
  allowed: boolean;
  timestamp: number;
};

export type SessionPolicyState = {
  blockedCount: number;
  toolCallHistory: ToolCallRecord[];
  escalationLevel: number;
  dryRun: boolean;
};

const SESSION_TTL_MS = 60 * 60 * 1000; // 1 hour

export class StateManager {
  private sessions = new Map<string, SessionPolicyState>();
  private lastAccess = new Map<string, number>();

  /**
   * Get or create the policy state for a session.
   */
  get(sessionKey: string): SessionPolicyState {
    this.cleanup();
    let state = this.sessions.get(sessionKey);
    if (!state) {
      state = {
        blockedCount: 0,
        toolCallHistory: [],
        escalationLevel: 0,
        dryRun: false,
      };
      this.sessions.set(sessionKey, state);
    }
    this.lastAccess.set(sessionKey, Date.now());
    return state;
  }

  /**
   * Record a tool call outcome.
   */
  recordToolCall(sessionKey: string, tool: string, allowed: boolean): void {
    const state = this.get(sessionKey);
    state.toolCallHistory.push({ tool, allowed, timestamp: Date.now() });
    if (!allowed) {
      state.blockedCount++;
    }
  }

  /**
   * Increment escalation level for a session.
   */
  escalate(sessionKey: string): number {
    const state = this.get(sessionKey);
    state.escalationLevel++;
    return state.escalationLevel;
  }

  /**
   * Get total number of tracked sessions (for diagnostics).
   */
  get size(): number {
    return this.sessions.size;
  }

  /**
   * Remove sessions that haven't been accessed within the TTL.
   */
  private cleanup(): void {
    const now = Date.now();
    for (const [key, lastAccess] of this.lastAccess) {
      if (now - lastAccess > SESSION_TTL_MS) {
        this.sessions.delete(key);
        this.lastAccess.delete(key);
      }
    }
  }

  /**
   * Clear all state (used in tests).
   */
  clear(): void {
    this.sessions.clear();
    this.lastAccess.clear();
  }
}
