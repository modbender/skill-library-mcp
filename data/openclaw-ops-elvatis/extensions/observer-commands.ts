/**
 * openclaw-ops-elvatis: Session Observer (Phase 2)
 *
 * Observes AI agent conversations across all sessions:
 * - Hooks into message_received to build a live event log
 * - Reads brain/docs memory JSONL files to surface memory writes per session
 *
 * Event log: ~/.openclaw/workspace/observer/events.jsonl
 *
 * Commands: /sessions, /activity, /session-tail, /session-stats, /session-clear
 */

import fs from "node:fs";
import path from "node:path";
import { expandHome } from "../src/utils.js";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type EventType = "message" | "tool_call" | "command" | "memory_write";

interface EventLogEntry {
  ts: string;
  type: EventType;
  sessionId: string;
  from?: string;
  channel?: string;
  /** Tool name (tool_call events) */
  tool?: string;
  /** Command name (command events) */
  command?: string;
  /** Truncated content preview (all types) */
  preview?: string;
  /** Memory item kind (memory_write events) */
  memoryKind?: string;
  /** Memory item id (memory_write events) */
  memoryId?: string;
  /** Plugin tags (memory_write events) */
  tags?: string[];
}

interface MemoryItem {
  id: string;
  kind: string;
  text: string;
  createdAt: string;
  tags?: string[];
  source?: {
    channel?: string;
    from?: string;
    conversationId?: string;
    messageId?: string;
  };
}

// ---------------------------------------------------------------------------
// Event log helpers
// ---------------------------------------------------------------------------

const MAX_EVENTS = 5000;

function openEventLog(observerDir: string): string {
  fs.mkdirSync(observerDir, { recursive: true });
  const logPath = path.join(observerDir, "events.jsonl");
  if (!fs.existsSync(logPath)) fs.writeFileSync(logPath, "", "utf-8");
  return logPath;
}

function readEventLog(logPath: string): EventLogEntry[] {
  try {
    const raw = fs.readFileSync(logPath, "utf-8");
    const entries: EventLogEntry[] = [];
    for (const line of raw.split("\n")) {
      if (!line.trim()) continue;
      try {
        entries.push(JSON.parse(line) as EventLogEntry);
      } catch {
        // skip malformed
      }
    }
    return entries;
  } catch {
    return [];
  }
}

function appendEvent(logPath: string, entry: EventLogEntry): void {
  try {
    // Rotate if at limit
    const existing = readEventLog(logPath);
    if (existing.length >= MAX_EVENTS) {
      const trimmed = existing.slice(existing.length - MAX_EVENTS + 1);
      fs.writeFileSync(
        logPath,
        trimmed.map((e) => JSON.stringify(e)).join("\n") + "\n",
        "utf-8",
      );
    }
    fs.appendFileSync(logPath, JSON.stringify(entry) + "\n", "utf-8");
  } catch {
    // best-effort
  }
}

// ---------------------------------------------------------------------------
// Memory JSONL helpers (reads brain + docs stores)
// ---------------------------------------------------------------------------

function readMemoryFiles(workspace: string): EventLogEntry[] {
  const memDir = path.join(workspace, "memory");
  const results: EventLogEntry[] = [];
  if (!fs.existsSync(memDir)) return results;

  let files: string[];
  try {
    files = fs.readdirSync(memDir).filter((f) => f.endsWith(".jsonl"));
  } catch {
    return results;
  }

  for (const file of files) {
    try {
      const raw = fs.readFileSync(path.join(memDir, file), "utf-8");
      for (const line of raw.split("\n")) {
        if (!line.trim()) continue;
        try {
          const parsed = JSON.parse(line) as { item?: MemoryItem; embedding?: unknown };
          const item = parsed.item;
          if (!item?.id || !item.createdAt || !item.text) continue;
          results.push({
            ts: item.createdAt,
            type: "memory_write",
            sessionId: item.source?.conversationId ?? "unknown",
            from: item.source?.from,
            channel: item.source?.channel,
            memoryId: item.id,
            memoryKind: item.kind,
            tags: item.tags,
            preview: item.text.slice(0, 80) + (item.text.length > 80 ? "…" : ""),
          });
        } catch {
          // skip
        }
      }
    } catch {
      // skip
    }
  }

  return results;
}

// ---------------------------------------------------------------------------
// Formatting helpers
// ---------------------------------------------------------------------------

const TYPE_ICONS: Record<EventType, string> = {
  message: "💬",
  tool_call: "🔧",
  command: "⌨️",
  memory_write: "🧠",
};

function fmtTs(iso: string): string {
  // Show as "MM-DD HH:MM" for compact output
  try {
    const d = new Date(iso);
    const mm = String(d.getMonth() + 1).padStart(2, "0");
    const dd = String(d.getDate()).padStart(2, "0");
    const hh = String(d.getHours()).padStart(2, "0");
    const min = String(d.getMinutes()).padStart(2, "0");
    return `${mm}-${dd} ${hh}:${min}`;
  } catch {
    return iso.slice(0, 16);
  }
}

function fmtSession(id: string): string {
  if (!id || id === "unknown") return "(no session)";
  return id.length > 16 ? id.slice(0, 8) + "…" + id.slice(-6) : id;
}

// ---------------------------------------------------------------------------
// Main registration
// ---------------------------------------------------------------------------

export function registerObserverCommands(api: any, workspace: string): void {
  const observerDir = path.join(workspace, "observer");
  const logPath = openEventLog(observerDir);

  // ── Hook: capture inbound messages ────────────────────────────────────────
  api.on?.("message_received", async (event: any, ctx: any) => {
    try {
      const content = String(event?.content ?? "").trim();
      if (!content) return;
      const entry: EventLogEntry = {
        ts: new Date().toISOString(),
        type: "message",
        sessionId: ctx?.sessionId ?? ctx?.conversationId ?? "unknown",
        from: event?.from,
        channel: ctx?.messageProvider ?? ctx?.channel,
        preview: content.slice(0, 80) + (content.length > 80 ? "…" : ""),
      };
      appendEvent(logPath, entry);
    } catch {
      // best-effort
    }
  });

  // ── /sessions ──────────────────────────────────────────────────────────────
  api.registerCommand({
    name: "sessions",
    description: "List recent AI agent sessions with activity summary",
    usage: "/sessions [limit]",
    requireAuth: false,
    acceptsArgs: true,
    handler: async (ctx: any) => {
      const limit = Math.min(50, Math.max(1, parseInt(String(ctx?.args ?? "10")) || 10));

      // Merge event log + memory files
      const logEvents = readEventLog(logPath);
      const memEvents = readMemoryFiles(workspace);
      const allEvents = [...logEvents, ...memEvents].sort(
        (a, b) => new Date(a.ts).getTime() - new Date(b.ts).getTime(),
      );

      // Group by sessionId
      const sessions = new Map<
        string,
        { firstSeen: string; lastSeen: string; messages: number; memoryWrites: number; channels: Set<string> }
      >();

      for (const e of allEvents) {
        const sid = e.sessionId || "unknown";
        if (!sessions.has(sid)) {
          sessions.set(sid, {
            firstSeen: e.ts,
            lastSeen: e.ts,
            messages: 0,
            memoryWrites: 0,
            channels: new Set(),
          });
        }
        const s = sessions.get(sid)!;
        if (e.ts > s.lastSeen) s.lastSeen = e.ts;
        if (e.ts < s.firstSeen) s.firstSeen = e.ts;
        if (e.type === "message") s.messages++;
        if (e.type === "memory_write") s.memoryWrites++;
        if (e.channel) s.channels.add(e.channel);
      }

      // Sort by lastSeen descending, take limit
      const sorted = [...sessions.entries()]
        .sort((a, b) => new Date(b[1].lastSeen).getTime() - new Date(a[1].lastSeen).getTime())
        .slice(0, limit);

      const lines: string[] = [];
      lines.push(`Sessions (${sessions.size} total, showing ${sorted.length})`);
      lines.push("");

      if (sorted.length === 0) {
        lines.push("No sessions observed yet.");
        lines.push("Memory items will appear here once brain/docs plugins write entries.");
        lines.push("Inbound messages will appear once message_received events fire.");
        return { text: lines.join("\n") };
      }

      for (const [sid, s] of sorted) {
        const channels = [...s.channels].join(", ") || "-";
        lines.push(`Session: ${fmtSession(sid)}`);
        lines.push(`  Last seen:  ${fmtTs(s.lastSeen)}`);
        lines.push(`  First seen: ${fmtTs(s.firstSeen)}`);
        lines.push(`  💬 Messages:      ${s.messages}`);
        lines.push(`  🧠 Memory writes: ${s.memoryWrites}`);
        lines.push(`  Channel: ${channels}`);
        lines.push("");
      }

      return { text: lines.join("\n").trim() };
    },
  });

  // ── /activity ──────────────────────────────────────────────────────────────
  api.registerCommand({
    name: "activity",
    description: "Show recent agent activity (all or by session). Usage: /activity [sessionId] [limit]",
    usage: "/activity [sessionId] [limit]",
    requireAuth: false,
    acceptsArgs: true,
    handler: async (ctx: any) => {
      const parts = String(ctx?.args ?? "").trim().split(/\s+/).filter(Boolean);

      // Detect if first arg is a limit (pure number) or a sessionId
      let sessionFilter: string | undefined;
      let limit = 20;

      if (parts.length === 0) {
        // defaults
      } else if (parts.length === 1) {
        const n = parseInt(parts[0]!);
        if (!isNaN(n) && n > 0) {
          limit = Math.min(100, n);
        } else {
          sessionFilter = parts[0];
        }
      } else {
        sessionFilter = parts[0];
        const n = parseInt(parts[1]!);
        if (!isNaN(n) && n > 0) limit = Math.min(100, n);
      }

      const logEvents = readEventLog(logPath);
      const memEvents = readMemoryFiles(workspace);
      let events = [...logEvents, ...memEvents].sort(
        (a, b) => new Date(b.ts).getTime() - new Date(a.ts).getTime(),
      );

      if (sessionFilter) {
        events = events.filter((e) => e.sessionId?.includes(sessionFilter!));
      }

      events = events.slice(0, limit);

      const header = sessionFilter
        ? `Activity for session: ${fmtSession(sessionFilter)} (last ${events.length})`
        : `Activity: all sessions (last ${events.length})`;

      const lines: string[] = [header, ""];

      if (events.length === 0) {
        lines.push(sessionFilter ? "No activity found for that session." : "No activity recorded yet.");
        return { text: lines.join("\n") };
      }

      for (const e of events) {
        const icon = TYPE_ICONS[e.type] ?? "•";
        const ts = fmtTs(e.ts);
        const sid = fmtSession(e.sessionId);
        let detail = "";
        if (e.type === "tool_call" && e.tool) detail = `[${e.tool}] `;
        if (e.type === "command" && e.command) detail = `[/${e.command}] `;
        if (e.type === "memory_write" && e.memoryKind) detail = `[${e.memoryKind}] `;
        const tags = e.tags?.length ? ` (${e.tags.join(",")})` : "";
        lines.push(`${icon} ${ts}  ${sid}${tags}`);
        if (e.preview) lines.push(`   ${detail}${e.preview}`);
        lines.push("");
      }

      return { text: lines.join("\n").trim() };
    },
  });

  // ── /session-tail ─────────────────────────────────────────────────────────
  api.registerCommand({
    name: "session-tail",
    description: "Tail the most recent agent events across all sessions",
    usage: "/session-tail [limit]",
    requireAuth: false,
    acceptsArgs: true,
    handler: async (ctx: any) => {
      const n = parseInt(String(ctx?.args ?? "30").trim()) || 30;
      const limit = Math.min(100, Math.max(1, n));

      const logEvents = readEventLog(logPath);
      const memEvents = readMemoryFiles(workspace);
      const events = [...logEvents, ...memEvents]
        .sort((a, b) => new Date(b.ts).getTime() - new Date(a.ts).getTime())
        .slice(0, limit)
        .reverse(); // oldest first for tail feel

      const lines: string[] = [`Session tail (last ${events.length} events)`, ""];

      if (events.length === 0) {
        lines.push("No events recorded yet.");
        return { text: lines.join("\n") };
      }

      for (const e of events) {
        const icon = TYPE_ICONS[e.type] ?? "•";
        const ts = fmtTs(e.ts);
        const sid = fmtSession(e.sessionId);
        const kindBadge = e.memoryKind ? `[${e.memoryKind}] ` : e.tool ? `[${e.tool}] ` : "";
        lines.push(`${icon} ${ts} ${sid}  ${kindBadge}${e.preview ?? ""}`);
      }

      return { text: lines.join("\n") };
    },
  });

  // ── /session-stats ────────────────────────────────────────────────────────
  api.registerCommand({
    name: "session-stats",
    description: "Aggregate statistics for all observed agent sessions",
    usage: "/session-stats",
    requireAuth: false,
    acceptsArgs: false,
    handler: async (_ctx: any) => {
      const logEvents = readEventLog(logPath);
      const memEvents = readMemoryFiles(workspace);
      const all = [...logEvents, ...memEvents];

      if (all.length === 0) {
        return { text: "Session stats\n\nNo data yet. Stats populate as sessions run." };
      }

      // Per-session aggregation
      const sessionMap = new Map<string, { messages: number; memWrites: number; toolCalls: number; commands: number; lastSeen: string }>();
      const channelCounts = new Map<string, number>();
      const toolCounts = new Map<string, number>();
      const tagCounts = new Map<string, number>();

      for (const e of all) {
        const sid = e.sessionId || "unknown";
        if (!sessionMap.has(sid)) {
          sessionMap.set(sid, { messages: 0, memWrites: 0, toolCalls: 0, commands: 0, lastSeen: e.ts });
        }
        const s = sessionMap.get(sid)!;
        if (e.ts > s.lastSeen) s.lastSeen = e.ts;
        if (e.type === "message") s.messages++;
        if (e.type === "memory_write") s.memWrites++;
        if (e.type === "tool_call") { s.toolCalls++; if (e.tool) toolCounts.set(e.tool, (toolCounts.get(e.tool) ?? 0) + 1); }
        if (e.type === "command") s.commands++;
        if (e.channel) channelCounts.set(e.channel, (channelCounts.get(e.channel) ?? 0) + 1);
        for (const tag of e.tags ?? []) tagCounts.set(tag, (tagCounts.get(tag) ?? 0) + 1);
      }

      const totalMessages = all.filter((e) => e.type === "message").length;
      const totalMemWrites = all.filter((e) => e.type === "memory_write").length;
      const totalToolCalls = all.filter((e) => e.type === "tool_call").length;

      // Top sessions by activity
      const topSessions = [...sessionMap.entries()]
        .sort((a, b) => (b[1].messages + b[1].memWrites) - (a[1].messages + a[1].memWrites))
        .slice(0, 5);

      const lines: string[] = ["Session stats", ""];
      lines.push("OVERVIEW");
      lines.push(`- Total sessions:     ${sessionMap.size}`);
      lines.push(`- Total events:       ${all.length}`);
      lines.push(`- Messages received:  ${totalMessages}`);
      lines.push(`- Memory writes:      ${totalMemWrites}`);
      lines.push(`- Tool calls:         ${totalToolCalls}`);

      if (channelCounts.size > 0) {
        lines.push("");
        lines.push("TOP CHANNELS");
        for (const [ch, count] of [...channelCounts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 3)) {
          lines.push(`- ${ch}: ${count}`);
        }
      }

      if (toolCounts.size > 0) {
        lines.push("");
        lines.push("TOP TOOLS");
        for (const [tool, count] of [...toolCounts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 5)) {
          lines.push(`- ${tool}: ${count}x`);
        }
      }

      if (tagCounts.size > 0) {
        lines.push("");
        lines.push("MEMORY TAGS");
        for (const [tag, count] of [...tagCounts.entries()].sort((a, b) => b[1] - a[1])) {
          lines.push(`- ${tag}: ${count}`);
        }
      }

      lines.push("");
      lines.push("MOST ACTIVE SESSIONS");
      for (const [sid, s] of topSessions) {
        const activity = s.messages + s.memWrites + s.toolCalls;
        lines.push(`- ${fmtSession(sid)}`);
        lines.push(`  💬 ${s.messages} msg  🧠 ${s.memWrites} mem  🔧 ${s.toolCalls} tools  (${activity} total)`);
        lines.push(`  Last: ${fmtTs(s.lastSeen)}`);
      }

      return { text: lines.join("\n") };
    },
  });

  // ── /session-clear ────────────────────────────────────────────────────────
  api.registerCommand({
    name: "session-clear",
    description: "Clear the observer event log (destructive)",
    usage: "/session-clear",
    requireAuth: true,
    acceptsArgs: false,
    handler: async (_ctx: any) => {
      try {
        const existing = readEventLog(logPath);
        const count = existing.length;
        fs.writeFileSync(logPath, "", "utf-8");
        return { text: `Observer event log cleared. Removed ${count} entries.` };
      } catch (err: unknown) {
        return { text: `Failed to clear log: ${(err as Error).message}` };
      }
    },
  });

  api.logger?.info?.(`[observer] enabled. log=${logPath}`);
}
