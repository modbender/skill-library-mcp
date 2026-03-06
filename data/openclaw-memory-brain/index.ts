import {
  DefaultRedactor,
  HashEmbedder,
  JsonlMemoryStore,
  uuid,
  expandHome,
  safePath,
  safeLimit,
  ttlMs,
  type MemoryItem,
  type PluginApi,
  type CommandContext,
  type ToolCallParams,
  type MessageEvent,
  type MessageEventContext,
} from "@elvatis_com/openclaw-memory-core";

/** Internal counters for /brain-status. */
interface CaptureStats {
  explicitCaptures: number;
  topicCaptures: number;
  skippedShort: number;
  skippedChannel: number;
  skippedDuplicate: number;
  totalMessages: number;
}

export default function register(api: PluginApi) {
  const cfg = (api.pluginConfig ?? {}) as {
    enabled?: boolean;
    storePath?: string;
    dims?: number;
    redactSecrets?: boolean;
    defaultTags?: string[];
    maxItems?: number;
    capture?: {
      minChars?: number;
      requireExplicit?: boolean;
      explicitTriggers?: string[];
      autoTopics?: string[];
      channels?: {
        allow?: string[];
        deny?: string[];
        defaultPolicy?: "capture" | "skip";
      };
      dedupeThreshold?: number;
      defaultTtlMs?: number;
    };
    retention?: {
      maxAgeDays?: number;
    };
  };
  if (cfg.enabled === false) return;

  let storePath: string;
  try {
    storePath = safePath(expandHome(cfg.storePath ?? "~/.openclaw/workspace/memory/brain-memory.jsonl"), "[memory-brain] storePath");
  } catch (err: unknown) {
    api.logger?.error?.(`[memory-brain] ${(err as Error).message}`);
    return;
  }

  const embedder = new HashEmbedder(cfg.dims ?? 256);
  const store = new JsonlMemoryStore({ filePath: storePath, embedder, maxItems: cfg.maxItems ?? 5000 });
  const redactor = new DefaultRedactor();

  const captureCfg = cfg.capture ?? {};
  const minChars: number = captureCfg.minChars ?? 80;
  const requireExplicit: boolean = captureCfg.requireExplicit === true;
  const explicitTriggers: string[] = captureCfg.explicitTriggers ?? ["merke dir", "remember this", "notiere", "keep this"];
  const autoTopics: string[] = captureCfg.autoTopics ?? ["entscheidung", "decision"];
  const defaultTags: string[] = cfg.defaultTags ?? ["brain"];
  const redactSecrets: boolean = cfg.redactSecrets !== false;

  // Issue #1: Per-channel capture policy
  const channelsCfg = captureCfg.channels ?? {};
  const channelAllow: string[] = channelsCfg.allow ?? [];
  const channelDeny: string[] = channelsCfg.deny ?? [];
  const channelDefaultPolicy: "capture" | "skip" = channelsCfg.defaultPolicy ?? "capture";

  // Issue #2: Dedupe + TTL
  const dedupeThreshold: number = captureCfg.dedupeThreshold ?? 0;
  const defaultTtlMs: number = captureCfg.defaultTtlMs ?? 0;

  // Issue #3: Capture stats for /brain-status
  const stats: CaptureStats = {
    explicitCaptures: 0,
    topicCaptures: 0,
    skippedShort: 0,
    skippedChannel: 0,
    skippedDuplicate: 0,
    totalMessages: 0,
  };

  function includesAny(hay: string, needles: string[]): boolean {
    const s = hay.toLowerCase();
    return needles.some((n) => s.includes(n.toLowerCase()));
  }

  function parseTags(raw: string): { tags: string[]; rest: string } {
    const match = raw.match(/--tags\s+(\S+)/);
    if (!match) return { tags: [], rest: raw };
    const tags = match[1]!.split(",").map((t) => t.trim()).filter(Boolean);
    const rest = raw.replace(/--tags\s+\S+/, "").replace(/\s+/g, " ").trim();
    return { tags, rest };
  }

  /** Issue #1: Check if capture is allowed for the given channel/provider. */
  function isChannelAllowed(channel: string | undefined): boolean {
    const ch = (channel ?? "").toLowerCase();
    // If the deny list contains this channel, block it
    if (channelDeny.length > 0 && channelDeny.some((d) => d.toLowerCase() === ch)) return false;
    // If an allow list is set, only allow listed channels
    if (channelAllow.length > 0) return channelAllow.some((a) => a.toLowerCase() === ch);
    // Fall back to default policy
    return channelDefaultPolicy === "capture";
  }

  /** Issue #3: Strip explicit trigger prefixes from captured text. */
  function stripTriggerPrefix(text: string): string {
    const lower = text.toLowerCase();
    for (const trigger of explicitTriggers) {
      const tLower = trigger.toLowerCase();
      const idx = lower.indexOf(tLower);
      if (idx !== -1) {
        // Remove the trigger and any following colon/whitespace
        let stripped = text.slice(0, idx) + text.slice(idx + trigger.length);
        stripped = stripped.replace(/^\s*[:]\s*/, "").trim();
        if (stripped) return stripped;
      }
    }
    return text;
  }

  /** Issue #2: Check if content is a near-duplicate of an existing memory. */
  async function isDuplicate(text: string): Promise<boolean> {
    if (dedupeThreshold <= 0) return false;
    const hits = await store.search(text, { limit: 1 });
    if (hits.length === 0) return false;
    return hits[0]!.score >= dedupeThreshold;
  }

  const maxAgeDays: number = cfg.retention?.maxAgeDays ?? 0;

  async function runRetention(dryRun = false): Promise<{ deleted: number; total: number }> {
    if (maxAgeDays <= 0) return { deleted: 0, total: 0 };
    const cutoff = Date.now() - maxAgeDays * 86_400_000;
    const items = await store.list({ limit: 5000 });
    let deleted = 0;
    for (const item of items) {
      const ts = new Date(item.createdAt).getTime();
      if (!isNaN(ts) && ts < cutoff) {
        if (!dryRun) await store.delete(item.id);
        deleted++;
      }
    }
    return { deleted, total: items.length };
  }

  api.logger?.info?.(`[memory-brain] enabled. store=${storePath}`);

  // Run retention on startup if configured
  if (maxAgeDays > 0) {
    runRetention().then((r) => {
      if (r.deleted > 0) {
        api.logger?.info?.(`[memory-brain] retention: deleted ${r.deleted} expired item(s) older than ${maxAgeDays} day(s)`);
      }
    }).catch((err: unknown) => {
      api.logger?.error?.(`[memory-brain] retention startup error: ${(err as Error).message}`);
    });
  }

  // Purge TTL-expired items on startup
  store.purgeExpired().then((n) => {
    if (n > 0) api.logger?.info?.(`[memory-brain] TTL purge: removed ${n} expired item(s) on startup`);
  }).catch((err: unknown) => {
    api.logger?.error?.(`[memory-brain] TTL purge startup error: ${(err as Error).message}`);
  });

  // Tool: brain_memory_search
  api.registerTool({
    name: "brain_memory_search",
    description: "Search personal brain memory items (local JSONL store). Optionally filter by tags (AND logic).",
    parameters: {
      type: "object",
      additionalProperties: false,
      properties: {
        query: { type: "string" },
        limit: { type: "number", minimum: 1, maximum: 20, default: 5 },
        tags: { type: "array", items: { type: "string" }, description: "Filter results to items that have ALL of these tags" }
      },
      required: ["query"]
    },
    async execute(params: ToolCallParams) {
      const q = String(params['query'] ?? "").trim();
      const limit = safeLimit(params['limit'], 5, 20);
      const tags = Array.isArray(params['tags']) ? (params['tags'] as string[]).filter(Boolean) : [];
      if (!q) return { hits: [] };
      const hits = await store.search(q, { limit, ...(tags.length > 0 ? { tags } : {}) });
      return {
        hits: hits.map((h) => ({
          score: h.score,
          id: h.item.id,
          createdAt: h.item.createdAt,
          tags: h.item.tags,
          text: h.item.text
        }))
      };
    }
  });

  // Command: /remember-brain <text> [--tags tag1,tag2]
  api.registerCommand({
    name: "remember-brain",
    description: "Save a personal brain memory item (explicit capture). Use --tags tag1,tag2 to add custom tags.",
    usage: "/remember-brain <text> [--tags tag1,tag2]",
    requireAuth: false,
    acceptsArgs: true,
    handler: async (ctx: CommandContext) => {
      const raw = String(ctx?.args ?? "").trim();
      if (!raw) return { text: "Usage: /remember-brain <text> [--tags tag1,tag2]" };

      const { tags: extraTags, rest: text } = parseTags(raw);
      if (!text) return { text: "Usage: /remember-brain <text> [--tags tag1,tag2]" };

      const mergedTags = [...defaultTags, ...extraTags.filter((t) => !defaultTags.includes(t))];
      const r = redactSecrets ? redactor.redact(text) : { redactedText: text, hadSecrets: false, matches: [] };
      const id = uuid();
      const item: MemoryItem = {
        id,
        kind: "note",
        text: r.redactedText,
        createdAt: new Date().toISOString(),
        tags: mergedTags,
        source: {
          channel: ctx?.channel,
          from: ctx?.from,
          conversationId: ctx?.conversationId,
          messageId: ctx?.messageId,
        },
        meta: r.hadSecrets ? { redaction: { hadSecrets: true, matches: r.matches } } : undefined,
      };

      // Issue #2: Apply TTL if configured
      if (defaultTtlMs > 0) {
        item.expiresAt = ttlMs(defaultTtlMs);
      }

      await store.add(item);
      const note = r.hadSecrets ? " (secrets redacted)" : "";
      // Issue #3: Include id in confirmation
      return { text: `Saved brain memory [id=${id}].${note}` };
    },
  });

  // Command: /search-brain <query> [--tags tag1,tag2] [limit]
  api.registerCommand({
    name: "search-brain",
    description: "Search brain memory items by query. Use --tags tag1,tag2 to filter by tags (AND logic).",
    usage: "/search-brain <query> [--tags tag1,tag2] [limit]",
    requireAuth: false,
    acceptsArgs: true,
    handler: async (ctx: CommandContext) => {
      const raw = String(ctx?.args ?? "").trim();
      const { tags, rest } = parseTags(raw);
      const args = rest.split(/\s+/).filter(Boolean);
      // Support optional trailing --limit N or just a bare number as last arg.
      const lastArg = args[args.length - 1] ?? "";
      const maybeLimit = Number(lastArg);
      let query: string;
      let limit: number;
      if (!isNaN(maybeLimit) && maybeLimit >= 1 && args.length > 1) {
        limit = safeLimit(maybeLimit, 5, 20);
        query = args.slice(0, -1).join(" ");
      } else {
        limit = 5;
        query = args.join(" ");
      }
      if (!query) return { text: "Usage: /search-brain <query> [--tags tag1,tag2] [limit]" };
      const hits = await store.search(query, { limit, ...(tags.length > 0 ? { tags } : {}) });
      if (hits.length === 0) return { text: `No brain memories found for: ${query}` };
      const lines = hits.map((h, n) =>
        `${n + 1}. [score:${h.score.toFixed(2)}] ${h.item.text.slice(0, 120)}${h.item.text.length > 120 ? "\u2026" : ""}`
      );
      return { text: `Brain memory results for "${query}":\n${lines.join("\n")}` };
    },
  });

  // Command: /list-brain [--tags tag1,tag2] [limit]
  api.registerCommand({
    name: "list-brain",
    description: "List the most recent brain memory items. Use --tags tag1,tag2 to filter by tags (AND logic).",
    usage: "/list-brain [--tags tag1,tag2] [limit]",
    requireAuth: false,
    acceptsArgs: true,
    handler: async (ctx: CommandContext) => {
      const raw = String(ctx?.args ?? "").trim();
      const { tags, rest } = parseTags(raw);
      const limit = safeLimit(rest, 10, 50);
      const items = await store.list({ limit, ...(tags.length > 0 ? { tags } : {}) });
      if (items.length === 0) return { text: "No brain memories stored yet." };
      const lines = items.map((i, n) =>
        `${n + 1}. [${i.createdAt.slice(0, 10)}] ${i.text.slice(0, 120)}${i.text.length > 120 ? "\u2026" : ""}`
      );
      return { text: `Brain memories (${items.length}):\n${lines.join("\n")}` };
    },
  });

  // Command: /tags-brain
  api.registerCommand({
    name: "tags-brain",
    description: "List all unique tags across all brain memory items",
    usage: "/tags-brain",
    requireAuth: false,
    acceptsArgs: false,
    handler: async () => {
      const items = await store.list({ limit: 5000 });
      const tagSet = new Set<string>();
      for (const item of items) {
        for (const tag of item.tags ?? []) tagSet.add(tag);
      }
      if (tagSet.size === 0) return { text: "No tags found." };
      const sorted = [...tagSet].sort();
      return { text: `Tags (${sorted.length}): ${sorted.join(", ")}` };
    },
  });

  // Command: /forget-brain <id>
  api.registerCommand({
    name: "forget-brain",
    description: "Delete a brain memory item by ID",
    usage: "/forget-brain <id>",
    requireAuth: true,
    acceptsArgs: true,
    handler: async (ctx: CommandContext) => {
      const id = String(ctx?.args ?? "").trim();
      if (!id) return { text: "Usage: /forget-brain <id>" };
      const deleted = await store.delete(id);
      return { text: deleted ? `Deleted brain memory: ${id}` : `No memory found with id: ${id}` };
    },
  });

  // Command: /export-brain [--tags tag1,tag2]
  api.registerCommand({
    name: "export-brain",
    description: "Export brain memory items as JSON for backup or portability. Use --tags tag1,tag2 to filter.",
    usage: "/export-brain [--tags tag1,tag2]",
    requireAuth: false,
    acceptsArgs: true,
    handler: async (ctx: CommandContext) => {
      const raw = String(ctx?.args ?? "").trim();
      const { tags } = parseTags(raw);
      const items = await store.list({ limit: 5000, ...(tags.length > 0 ? { tags } : {}) });
      if (items.length === 0) return { text: "No brain memories to export." };
      const payload = {
        version: 1,
        exportedAt: new Date().toISOString(),
        count: items.length,
        items,
      };
      return { text: JSON.stringify(payload, null, 2) };
    },
  });

  // Command: /purge-brain [--dry-run]
  api.registerCommand({
    name: "purge-brain",
    description: "Delete brain memory items older than the configured retention period (maxAgeDays). Use --dry-run to preview without deleting.",
    usage: "/purge-brain [--dry-run]",
    requireAuth: true,
    acceptsArgs: true,
    handler: async (ctx: CommandContext) => {
      if (maxAgeDays <= 0) return { text: "Retention policy is not configured. Set retention.maxAgeDays in plugin config." };
      const raw = String(ctx?.args ?? "").trim();
      const dryRun = raw === "--dry-run";
      const result = await runRetention(dryRun);
      if (result.deleted === 0) return { text: `No items older than ${maxAgeDays} day(s). ${result.total} item(s) in store.` };
      if (dryRun) return { text: `Dry run: ${result.deleted} of ${result.total} item(s) would be deleted (older than ${maxAgeDays} day(s)).` };
      return { text: `Purged ${result.deleted} item(s) older than ${maxAgeDays} day(s). ${result.total - result.deleted} item(s) remaining.` };
    },
  });

  // Command: /import-brain <json>
  api.registerCommand({
    name: "import-brain",
    description: "Import brain memory items from a JSON export. Skips items that already exist.",
    usage: "/import-brain <json>",
    requireAuth: true,
    acceptsArgs: true,
    handler: async (ctx: CommandContext) => {
      const raw = String(ctx?.args ?? "").trim();
      if (!raw) return { text: "Usage: /import-brain <json>" };

      let payload: unknown;
      try {
        payload = JSON.parse(raw);
      } catch {
        return { text: "Invalid JSON input." };
      }

      let items: unknown[];
      if (Array.isArray(payload)) {
        items = payload;
      } else if (payload && typeof payload === "object" && Array.isArray((payload as Record<string, unknown>).items)) {
        items = (payload as Record<string, unknown>).items as unknown[];
      } else {
        return { text: "Expected a JSON array or an object with an \"items\" array." };
      }

      if (items.length === 0) return { text: "No items to import." };

      let imported = 0;
      let skipped = 0;
      let invalid = 0;

      for (const entry of items) {
        if (!entry || typeof entry !== "object") { invalid++; continue; }
        const obj = entry as Record<string, unknown>;
        if (typeof obj.text !== "string" || !obj.text) { invalid++; continue; }
        if (typeof obj.createdAt !== "string") { invalid++; continue; }

        const id = typeof obj.id === "string" && obj.id ? obj.id : uuid();
        const existing = await store.get(id);
        if (existing) { skipped++; continue; }

        const kind = (["fact", "decision", "doc", "note"].includes(obj.kind as string)
          ? obj.kind : "note") as MemoryItem["kind"];
        const item: MemoryItem = {
          id,
          kind,
          text: obj.text as string,
          createdAt: obj.createdAt as string,
          tags: Array.isArray(obj.tags)
            ? (obj.tags as unknown[]).filter((t): t is string => typeof t === "string")
            : defaultTags,
          source: obj.source && typeof obj.source === "object"
            ? obj.source as MemoryItem["source"] : undefined,
          meta: obj.meta && typeof obj.meta === "object"
            ? obj.meta as Record<string, unknown> : undefined,
        };

        await store.add(item);
        imported++;
      }

      const parts: string[] = [`Imported ${imported} item${imported !== 1 ? "s" : ""}.`];
      if (skipped > 0) parts.push(`${skipped} skipped (already exist).`);
      if (invalid > 0) parts.push(`${invalid} skipped (invalid format).`);
      return { text: parts.join(" ") };
    },
  });

  // Issue #3: Command: /brain-status - show capture stats and config
  api.registerCommand({
    name: "brain-status",
    description: "Show brain memory capture statistics and current configuration.",
    usage: "/brain-status",
    requireAuth: false,
    acceptsArgs: false,
    handler: async () => {
      const items = await store.list({ limit: 5000 });
      const lines: string[] = [
        `Brain Memory Status`,
        `---`,
        `Total stored items: ${items.length}`,
        `Session stats:`,
        `  Messages processed: ${stats.totalMessages}`,
        `  Explicit captures: ${stats.explicitCaptures}`,
        `  Topic captures: ${stats.topicCaptures}`,
        `  Skipped (too short): ${stats.skippedShort}`,
        `  Skipped (channel policy): ${stats.skippedChannel}`,
        `  Skipped (duplicate): ${stats.skippedDuplicate}`,
        `Config:`,
        `  requireExplicit: ${requireExplicit}`,
        `  minChars: ${minChars}`,
        `  dedupeThreshold: ${dedupeThreshold || "disabled"}`,
        `  defaultTtlMs: ${defaultTtlMs || "disabled"}`,
        `  channelPolicy: ${channelAllow.length > 0 ? "allow=" + channelAllow.join(",") : channelDeny.length > 0 ? "deny=" + channelDeny.join(",") : "default=" + channelDefaultPolicy}`,
        `  maxAgeDays: ${maxAgeDays || "disabled"}`,
      ];
      return { text: lines.join("\n") };
    },
  });

  // Auto-capture from inbound messages.
  api.on("message_received", async (event: MessageEvent, ctx: MessageEventContext) => {
    try {
      stats.totalMessages++;
      const content = String(event?.content ?? "").trim();
      if (!content) return;

      if (content.length < minChars) {
        stats.skippedShort++;
        return;
      }

      // Issue #1: Per-channel capture policy
      const channel = ctx?.messageProvider;
      if (!isChannelAllowed(channel)) {
        stats.skippedChannel++;
        api.logger?.info?.(`[memory-brain] skipped capture: channel "${channel}" not allowed by policy`);
        return;
      }

      const isExplicit = includesAny(content, explicitTriggers);
      const isTopic = includesAny(content, autoTopics);

      if (requireExplicit && !isExplicit) return;
      if (!requireExplicit && !isExplicit && !isTopic) return;

      // Issue #3: Strip trigger prefix from captured text
      const cleanedContent = isExplicit ? stripTriggerPrefix(content) : content;
      const textToStore = cleanedContent || content; // fallback if stripping removes everything

      // Issue #2: Dedupe check
      if (await isDuplicate(textToStore)) {
        stats.skippedDuplicate++;
        api.logger?.info?.(`[memory-brain] skipped duplicate capture`);
        return;
      }

      const r = redactSecrets ? redactor.redact(textToStore) : { redactedText: textToStore, hadSecrets: false, matches: [] as Array<{rule: string; count: number}> };
      const item: MemoryItem = {
        id: uuid(),
        kind: "note",
        text: r.redactedText,
        createdAt: new Date().toISOString(),
        tags: defaultTags,
        source: {
          channel: ctx?.messageProvider,
          from: event?.from,
          conversationId: ctx?.sessionId,
        },
        meta: {
          capture: { explicit: isExplicit, topic: isTopic },
          ...(r.hadSecrets ? { redaction: { hadSecrets: true, matches: r.matches } } : {})
        }
      };

      // Issue #2: Apply TTL if configured
      if (defaultTtlMs > 0) {
        item.expiresAt = ttlMs(defaultTtlMs);
      }

      await store.add(item);

      if (isExplicit) stats.explicitCaptures++;
      if (isTopic && !isExplicit) stats.topicCaptures++;

      api.logger?.info?.(`[memory-brain] captured memory (explicit=${isExplicit} topic=${isTopic}) id=${item.id}`);
    } catch (err: unknown) {
      api.logger?.error?.(`[memory-brain] failed to capture message: ${(err as Error).message}`);
    }
  });
}
