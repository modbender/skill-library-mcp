import { randomUUID } from "node:crypto";
import { existsSync, mkdirSync, appendFileSync } from "node:fs";
import { join } from "node:path";
import type { PluginLogger } from "../types.js";
import { ConversationDB } from "../storage/db.js";
import type { ConversationRow, MessageRow } from "../storage/schema.js";
import type { SessionBuffer } from "./buffer.js";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Extract agentId from a session key of the form "agent:<agentId>:<sessionName>".
 * Falls back to the raw session key if it does not match the expected format.
 */
function parseAgentId(sessionKey: string): string {
  const parts = sessionKey.split(":");
  if (parts[0] === "agent" && parts.length >= 2 && parts[1]) {
    return parts[1];
  }
  return sessionKey;
}

/**
 * Format a Date as "YYYY-MM-DD-HHMM" for use in filenames.
 * All components are zero-padded to fixed width.
 */
function formatDateForFilename(d: Date): string {
  const pad = (n: number, w = 2) => String(n).padStart(w, "0");
  return [
    d.getFullYear(),
    "-",
    pad(d.getMonth() + 1),
    "-",
    pad(d.getDate()),
    "-",
    pad(d.getHours()),
    pad(d.getMinutes()),
  ].join("");
}

// ---------------------------------------------------------------------------
// SegmentWriter
// ---------------------------------------------------------------------------

/**
 * Persists a flushed conversation buffer as:
 *   • A row + child rows in SQLite (`<dataDir>/conversations.sqlite`)
 *   • A JSONL line appended to `<dataDir>/conversations/YYYY-MM-DD-HHMM.jsonl`
 *
 * Both writes are best-effort: failures are logged but never propagated so
 * that a write error never disrupts the agent.
 *
 * `writeSegment` returns the ConversationRow that was written (or null if the
 * buffer was empty), so the caller can pass it to the extraction trigger.
 */
export class SegmentWriter {
  private _db: ConversationDB | null = null;

  constructor(
    /** Resolved absolute path to the data directory (e.g. /home/user/.engram/) */
    private readonly dataDir: string,
    private readonly logger: PluginLogger,
  ) {}

  // ---- Public API ---------------------------------------------------------

  /**
   * Persist a conversation segment to SQLite + JSONL.
   * Returns the written ConversationRow, or null if the buffer was empty.
   */
  writeSegment(sessionKey: string, buf: SessionBuffer): ConversationRow | null {
    if (buf.entries.length === 0) return null;

    const segmentId = randomUUID();
    const agentId = parseAgentId(sessionKey);
    const channel = buf.entries[0]?.channel ?? "unknown";

    const rawText = buf.entries
      .map((e) => `[${e.role}] ${e.content}`)
      .join("\n\n---\n\n");

    const conversationRow: ConversationRow = {
      id: segmentId,
      agent_id: agentId,
      session_key: sessionKey,
      channel,
      started_at: buf.startedAt,
      ended_at: buf.lastActivityAt,
      turn_count: buf.entries.length,
      raw_text: rawText,
      metadata: null,
    };

    const messageRows: MessageRow[] = buf.entries.map((entry) => ({
      id: randomUUID(),
      conversation_id: segmentId,
      role: entry.role,
      content: entry.content,
      timestamp: entry.timestamp,
      message_id: entry.messageId ?? null,
      metadata: null,
    }));

    // Write to SQLite (synchronous better-sqlite3 under the hood)
    try {
      this.getDb().insertConversationWithMessages(conversationRow, messageRows);
    } catch (err) {
      this.logger.warn(
        `memento: SQLite write failed for segment ${segmentId}: ${String(err)}`,
      );
    }

    // Write human-readable JSONL backup
    try {
      this.writeJsonlBackup(segmentId, sessionKey, conversationRow, messageRows, buf);
    } catch (err) {
      this.logger.warn(
        `memento: JSONL write failed for segment ${segmentId}: ${String(err)}`,
      );
    }

    this.logger.info(
      `memento: captured segment ${segmentId} ` +
        `(${buf.entries.length} turns, ${buf.lastActivityAt - buf.startedAt}ms, ` +
        `session: ${sessionKey}, channel: ${channel})`,
    );

    return conversationRow;
  }

  /**
   * Expose the underlying DB so other components (e.g. ExtractionTrigger)
   * can share the same connection without opening a second file handle.
   */
  getDb(): ConversationDB {
    if (!this._db) {
      const dbPath = join(this.dataDir, "conversations.sqlite");
      this._db = new ConversationDB(dbPath);
    }
    return this._db;
  }

  close(): void {
    this._db?.close();
    this._db = null;
  }

  // ---- Internals ----------------------------------------------------------

  private writeJsonlBackup(
    segmentId: string,
    sessionKey: string,
    conversation: ConversationRow,
    messages: MessageRow[],
    buf: SessionBuffer,
  ): void {
    const dir = join(this.dataDir, "conversations");
    if (!existsSync(dir)) {
      mkdirSync(dir, { recursive: true });
    }

    const dateStr = formatDateForFilename(new Date(buf.startedAt));
    const filePath = join(dir, `${dateStr}.jsonl`);

    // Write one JSON object per message, each on its own line
    const lines = messages.map((msg) =>
      JSON.stringify({
        segmentId,
        sessionKey,
        agentId: conversation.agent_id,
        channel: conversation.channel,
        turnCount: conversation.turn_count,
        segmentStartedAt: conversation.started_at,
        segmentEndedAt: conversation.ended_at,
        messageId: msg.id,
        role: msg.role,
        content: msg.content,
        timestamp: msg.timestamp,
        providerMessageId: msg.message_id,
      }),
    );

    appendFileSync(filePath, lines.join("\n") + "\n", "utf8");
  }
}
