import type { PluginConfig } from "../config.js";
import type { PluginLogger } from "../types.js";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type BufferEntry = {
  role: "user" | "assistant";
  content: string;
  timestamp: number;
  messageId?: string;
  /** Channel ID this message arrived on / was sent via */
  channel: string;
};

export type SessionBuffer = {
  sessionKey: string;
  entries: BufferEntry[];
  /** Timer handle for pause-timeout flush */
  timer: ReturnType<typeof setTimeout> | null;
  startedAt: number;
  lastActivityAt: number;
};

export type FlushHandler = (
  sessionKey: string,
  buf: SessionBuffer,
) => Promise<void>;

// ---------------------------------------------------------------------------
// ConversationBuffer
// ---------------------------------------------------------------------------

/**
 * In-memory buffer that groups messages by session key.
 * Auto-flushes when:
 *   • Pause timeout exceeded (no new messages for `pauseTimeoutMs`)
 *   • Max buffer turns reached (`maxBufferTurns`)
 *   • Caller requests an explicit flush (session end / reset)
 */
export class ConversationBuffer {
  private readonly buffers = new Map<string, SessionBuffer>();

  constructor(
    private readonly cfg: PluginConfig,
    private readonly onFlush: FlushHandler,
    private readonly logger: PluginLogger,
  ) {}

  // ---- Public API ---------------------------------------------------------

  /** Add a message to the buffer for the given session key. */
  async addMessage(sessionKey: string, entry: BufferEntry): Promise<void> {
    let buf = this.buffers.get(sessionKey);

    if (!buf) {
      buf = {
        sessionKey,
        entries: [],
        timer: null,
        startedAt: entry.timestamp,
        lastActivityAt: entry.timestamp,
      };
      this.buffers.set(sessionKey, buf);
    }

    // Reset the pause timer each time a message arrives
    this.resetTimer(buf);

    buf.entries.push(entry);
    buf.lastActivityAt = entry.timestamp;

    // Auto-flush when max turns is reached
    if (buf.entries.length >= this.cfg.maxBufferTurns) {
      await this.flushSession(sessionKey);
    }
  }

  /** Flush a specific session's buffer. No-op if empty or unknown. */
  async flushSession(sessionKey: string): Promise<void> {
    const buf = this.buffers.get(sessionKey);
    if (!buf) return;

    // Cancel pending timer so it does not double-fire
    this.clearTimer(buf);

    // Remove from map before flushing so concurrent flushes are not duped
    this.buffers.delete(sessionKey);

    if (buf.entries.length === 0) return;

    try {
      await this.onFlush(sessionKey, buf);
    } catch (err) {
      this.logger.warn(
        `memento: flush error for session "${sessionKey}": ${String(err)}`,
      );
    }
  }

  /** Flush all active session buffers in parallel (sessions are independent). */
  async flushAll(): Promise<void> {
    const keys = Array.from(this.buffers.keys());
    await Promise.all(keys.map((key) => this.flushSession(key)));
  }

  /** Number of sessions currently buffered. */
  get size(): number {
    return this.buffers.size;
  }

  // ---- Internals ----------------------------------------------------------

  private resetTimer(buf: SessionBuffer): void {
    this.clearTimer(buf);
    buf.timer = setTimeout(() => {
      this.flushSession(buf.sessionKey).catch((err) => {
        this.logger.warn(
          `memento: timer flush error for session "${buf.sessionKey}": ${String(err)}`,
        );
      });
    }, this.cfg.pauseTimeoutMs);
  }

  private clearTimer(buf: SessionBuffer): void {
    if (buf.timer !== null) {
      clearTimeout(buf.timer);
      buf.timer = null;
    }
  }
}
