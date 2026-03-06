/**
 * Memory Multiplexer Plugin for OpenClaw
 *
 * Claims the "memory" slot. Provides:
 * - All honcho_* tools (search, recall, analyze, etc.) for retrieval
 * - memory_get for reading local workspace files
 * - agent_end hook that writes conversations to Honcho
 * - Local markdown files are written by the agent itself (via AGENTS.md behavior)
 *
 * This gives us dual-write (honcho cloud + local files) with honcho-only retrieval.
 * If honcho dies, local files are the backup. If we ditch honcho, swap this plugin
 * for memory-core and everything works.
 */

import { Type } from "@sinclair/typebox";
import { Honcho } from "@honcho-ai/sdk";

// ============================================================================
// Config
// ============================================================================

interface PluginConfig {
  apiKey?: string;
  baseUrl: string;
  workspaceId: string;
}

function resolveConfig(pluginConfig: Record<string, unknown>): PluginConfig {
  return {
    apiKey:
      (pluginConfig.apiKey as string) || process.env.HONCHO_API_KEY || "",
    baseUrl:
      (pluginConfig.baseUrl as string) || "https://api.honcho.dev",
    workspaceId:
      (pluginConfig.workspaceId as string) || "openclaw",
  };
}

// ============================================================================
// Constants
// ============================================================================

const OWNER_ID = "owner";
const OPENCLAW_ID = "openclaw";

// ============================================================================
// Helpers
// ============================================================================

function buildSessionKey(ctx: { sessionKey?: string; messageProvider?: string }): string {
  const base = ctx?.sessionKey ?? "default";
  const provider = ctx?.messageProvider ?? "unknown";
  return `${base}-${provider}`.replace(/[^a-zA-Z0-9-]/g, "-");
}

function cleanMessageContent(content: string): string {
  let cleaned = content;
  cleaned = cleaned.replace(/<honcho-memory[^>]*>[\s\S]*?<\/honcho-memory>\s*/gi, "");
  cleaned = cleaned.replace(/<!--[^>]*honcho[^>]*-->\s*/gi, "");
  cleaned = cleaned.replace(/^\[\w+\s+.+?\s+id:\d+\s+[^\]]+\]\s*/, "");
  cleaned = cleaned.replace(/\s*\[message_id:\s*[^\]]+\]\s*$/, "");
  return cleaned.trim();
}

function extractMessages(rawMessages: unknown[], ownerPeer: any, openclawPeer: any) {
  const result: any[] = [];
  for (const msg of rawMessages) {
    if (!msg || typeof msg !== "object") continue;
    const m = msg as any;
    if (m.role !== "user" && m.role !== "assistant") continue;

    let content = "";
    if (typeof m.content === "string") {
      content = m.content;
    } else if (Array.isArray(m.content)) {
      content = m.content
        .filter((b: any) => b?.type === "text")
        .map((b: any) => b.text)
        .filter((t: any) => typeof t === "string")
        .join("\n");
    }

    if (m.role === "user") content = cleanMessageContent(content);
    content = content.trim();

    if (content) {
      const peer = m.role === "user" ? ownerPeer : openclawPeer;
      result.push(peer.message(content));
    }
  }
  return result;
}

// ============================================================================
// Plugin
// ============================================================================

export default {
  id: "honcho-memory-mux",
  name: "Memory (Multiplexer)",
  description: "Dual-write memory: Honcho cloud + local markdown files",
  kind: "memory",

  register(api: any) {
    const cfg = resolveConfig(api.pluginConfig ?? {});

    const honcho = new Honcho({
      apiKey: cfg.apiKey,
      baseURL: cfg.baseUrl,
      workspaceId: cfg.workspaceId,
    });

    let ownerPeer: any = null;
    let openclawPeer: any = null;
    let initialized = false;

    async function ensureInitialized() {
      await honcho.setMetadata({});
      if (initialized) return;
      ownerPeer = await honcho.peer(OWNER_ID, { metadata: {} });
      openclawPeer = await honcho.peer(OPENCLAW_ID, {
        metadata: {},
        config: { observe_me: false },
      });
      initialized = true;
    }

    // ========================================================================
    // HOOK: gateway_start
    // ========================================================================
    api.on("gateway_start", async () => {
      try {
        await ensureInitialized();
        api.logger.info("[mux] Honcho connected");
      } catch (err) {
        api.logger.error(`[mux] Honcho init failed: ${err}`);
      }
    });

    // ========================================================================
    // HOOK: before_agent_start — inject honcho context into system prompt
    // ========================================================================
    api.on("before_agent_start", async (event: any, ctx: any) => {
      if (!event.prompt || event.prompt.length < 5) return;
      const sessionKey = buildSessionKey(ctx);

      try {
        await ensureInitialized();
        const session = await honcho.session(sessionKey, { metadata: {} });

        let context: any;
        try {
          context = await (session as any).context({
            summary: true,
            tokens: 2000,
            peerTarget: ownerPeer,
            peerPerspective: openclawPeer,
          });
        } catch (e: any) {
          if (e?.message?.toLowerCase().includes("not found")) return;
          throw e;
        }

        const sections: string[] = [];
        if (context.peerCard?.length)
          sections.push(`Key facts:\n${context.peerCard.map((f: string) => `• ${f}`).join("\n")}`);
        if (context.peerRepresentation)
          sections.push(`User context:\n${context.peerRepresentation}`);
        if (context.summary?.content)
          sections.push(`Earlier in this conversation:\n${context.summary.content}`);

        if (!sections.length) return;

        return {
          systemPrompt: `## User Memory Context\n\n${sections.join("\n\n")}\n\nUse this context naturally when relevant.`,
        };
      } catch (err) {
        api.logger.warn?.(`[mux] Failed to fetch context: ${err}`);
      }
    });

    // ========================================================================
    // HOOK: agent_end — persist messages to Honcho
    // (local files are written by the agent via normal tool calls)
    // ========================================================================
    api.on("agent_end", async (event: any, ctx: any) => {
      if (!event.success || !event.messages?.length) return;
      const sessionKey = buildSessionKey(ctx);

      try {
        await ensureInitialized();
        const session = await honcho.session(sessionKey, { metadata: {} });

        let meta = await session.getMetadata();
        if (meta.lastSavedIndex === undefined) {
          const startIndex = Math.max(0, event.messages.length - 2);
          await session.setMetadata({ lastSavedIndex: startIndex });
          meta = { lastSavedIndex: startIndex };
        }

        const lastSaved = meta.lastSavedIndex ?? 0;
        await session.addPeers([
          [OWNER_ID, { observe_me: true, observe_others: false }],
          [OPENCLAW_ID, { observe_me: false, observe_others: true }],
        ]);

        if (event.messages.length <= lastSaved) return;

        const newMessages = extractMessages(
          event.messages.slice(lastSaved),
          ownerPeer,
          openclawPeer
        );

        if (newMessages.length > 0) {
          await session.addMessages(newMessages);
        }
        await session.setMetadata({ ...meta, lastSavedIndex: event.messages.length });
      } catch (err) {
        api.logger.error(`[mux] Failed to save to Honcho: ${err}`);
      }
    });

    // ========================================================================
    // TOOL: memory_get — read local workspace files (the backup)
    // ========================================================================
    api.registerTool({
      name: "memory_get",
      label: "Read Memory File",
      description:
        "Safe snippet read from MEMORY.md or memory/*.md with optional from/lines; " +
        "use after memory_search to pull only the needed lines and keep context small.",
      parameters: Type.Object({
        path: Type.String({ description: "Relative path to file (e.g. MEMORY.md, memory/2026-02-12.md)" }),
        from: Type.Optional(Type.Number({ description: "Line to start reading from (1-indexed)" })),
        lines: Type.Optional(Type.Number({ description: "Max lines to read" })),
      }),
      async execute(_id: string, params: { path: string; from?: number; lines?: number }, _signal: any) {
        // Delegate to the builtin helper if available
        const tool = api.runtime.tools.createMemoryGetTool({
          config: api.config,
          agentSessionKey: "main",
        });
        if (tool) {
          return tool.execute(_id, params, _signal);
        }

        // Fallback: direct file read
        const fs = await import("node:fs/promises");
        const pathMod = await import("node:path");
        const workspace = api.config?.agents?.defaults?.workspace ?? process.cwd();
        const fullPath = pathMod.resolve(workspace, params.path);

        // Safety: only allow MEMORY.md and memory/ paths
        const rel = pathMod.relative(workspace, fullPath);
        if (rel.startsWith("..") || (!rel.startsWith("memory") && rel !== "MEMORY.md")) {
          return { content: [{ type: "text", text: `Access denied: ${params.path}` }] };
        }

        try {
          const raw = await fs.readFile(fullPath, "utf-8");
          const allLines = raw.split("\n");
          const start = (params.from ?? 1) - 1;
          const count = params.lines ?? allLines.length;
          const slice = allLines.slice(start, start + count).join("\n");
          return { content: [{ type: "text", text: slice, path: params.path }] };
        } catch {
          return { content: [{ type: "text", text: `File not found: ${params.path}` }] };
        }
      },
    }, { name: "memory_get" });

    // ========================================================================
    // TOOL: honcho_session
    // ========================================================================
    api.registerTool({
      name: "honcho_session",
      label: "Session History",
      description:
        "Retrieve conversation history from THIS SESSION ONLY. Does NOT access cross-session memory.\n\n" +
        "━━━ SCOPE: CURRENT SESSION ━━━\n" +
        "This tool retrieves messages and summaries from the current conversation session.\n" +
        "It does NOT know about previous sessions or long-term user knowledge.\n\n" +
        "━━━ DATA TOOL ━━━\n" +
        "Returns: Recent messages + optional summary of earlier conversation in this session\n" +
        "Cost: Low (database query only, no LLM)\nSpeed: Fast\n\n" +
        "Best for:\n- \"What did we talk about earlier?\" (in this conversation)\n" +
        "- \"What was that thing you just mentioned?\"\n- Recalling recent conversation context\n\n" +
        "NOT for:\n- \"What do you know about me?\" → Use honcho_context instead\n" +
        "- Long-term user preferences → Use honcho_profile or honcho_context",
      parameters: Type.Object({
        includeMessages: Type.Optional(Type.Boolean({ description: "Include recent messages (default: true)" })),
        includeSummary: Type.Optional(Type.Boolean({ description: "Include conversation summary (default: true)" })),
        searchQuery: Type.Optional(Type.String({ description: "Semantic search within this session" })),
        messageLimit: Type.Optional(Type.Number({ description: "Token budget for messages (default: 4000)" })),
      }),
      async execute(_id: string, params: any) {
        await ensureInitialized();
        const { includeMessages = true, includeSummary = true, searchQuery, messageLimit = 4000 } = params;
        try {
          const session = await honcho.session(params.sessionKey ?? "default");
          const context = await (session as any).context({
            summary: includeSummary,
            tokens: messageLimit,
            peerTarget: ownerPeer,
            peerPerspective: openclawPeer,
            searchQuery,
          });

          const sections: string[] = [];
          if (context.summary?.content)
            sections.push(`## Summary\n\n${context.summary.content}`);
          if (context.peerCard?.length)
            sections.push(`## Profile\n\n${context.peerCard.map((f: string) => `• ${f}`).join("\n")}`);
          if (includeMessages && context.messages?.length) {
            const lines = context.messages.map((m: any) => {
              const who = m.peerId === ownerPeer.id ? "User" : "Agent";
              return `**${who}**: ${m.content}`;
            });
            sections.push(`## Messages (${context.messages.length})\n\n${lines.join("\n\n---\n\n")}`);
          }

          return {
            content: [{
              type: "text",
              text: sections.length ? sections.join("\n\n") : "No history for this session yet.",
            }],
          };
        } catch (e: any) {
          if (e?.message?.toLowerCase().includes("not found"))
            return { content: [{ type: "text", text: "New session — no history yet." }] };
          throw e;
        }
      },
    }, { name: "honcho_session" });

    // ========================================================================
    // TOOL: honcho_profile
    // ========================================================================
    api.registerTool({
      name: "honcho_profile",
      label: "User Profile",
      description:
        "Retrieve the user's peer card — a curated list of their most important facts.\n\n" +
        "━━━ DATA TOOL ━━━\nReturns: Raw fact list\nCost: Minimal\nSpeed: Instant\n\n" +
        "Best for: Quick context, core identity, cost-efficient fact lookup.",
      parameters: Type.Object({}),
      async execute() {
        await ensureInitialized();
        const card = await ownerPeer.card().catch(() => null);
        if (!card?.length)
          return { content: [{ type: "text", text: "No profile yet. Builds over time." }] };
        return { content: [{ type: "text", text: card.map((f: string) => `• ${f}`).join("\n") }] };
      },
    }, { name: "honcho_profile" });

    // ========================================================================
    // TOOL: honcho_search
    // ========================================================================
    api.registerTool({
      name: "honcho_search",
      label: "Search Memory",
      description:
        "Semantic search over Honcho's stored observations. Returns raw memories ranked by relevance.\n\n" +
        "━━━ DATA TOOL ━━━\nReturns: Raw observations matching query\nCost: Low\nSpeed: Fast\n\n" +
        "Best for: Finding specific past context, seeing evidence before conclusions.\n" +
        "Parameters: topK (3-5 focused, 10-20 exploratory), maxDistance (0.3 strict, 0.5 balanced, 0.7 loose)",
      parameters: Type.Object({
        query: Type.String({ description: "Semantic search query" }),
        topK: Type.Optional(Type.Number({ description: "Number of results (default: 10)" })),
        maxDistance: Type.Optional(Type.Number({ description: "Semantic distance 0-1 (default: 0.5)" })),
      }),
      async execute(_id: string, params: { query: string; topK?: number; maxDistance?: number }) {
        await ensureInitialized();
        const rep = await ownerPeer.representation({
          searchQuery: params.query,
          searchTopK: params.topK ?? 10,
          searchMaxDistance: params.maxDistance ?? 0.5,
        });
        if (!rep)
          return { content: [{ type: "text", text: `No memories matching: "${params.query}"` }] };
        return { content: [{ type: "text", text: rep }] };
      },
    }, { name: "honcho_search" });

    // ========================================================================
    // TOOL: honcho_context
    // ========================================================================
    api.registerTool({
      name: "honcho_context",
      label: "Broad Context",
      description:
        "Retrieve everything Honcho knows about this user ACROSS ALL SESSIONS.\n\n" +
        "━━━ DATA TOOL ━━━\nReturns: Broad synthesized representation\nCost: Low\nSpeed: Fast\n\n" +
        "Best for: \"What do you know about me?\", holistic understanding, long-term patterns.",
      parameters: Type.Object({
        includeMostFrequent: Type.Optional(Type.Boolean({ description: "Include frequent observations (default: true)" })),
      }),
      async execute(_id: string, params: { includeMostFrequent?: boolean }) {
        await ensureInitialized();
        const rep = await ownerPeer.representation({
          includeMostFrequent: params.includeMostFrequent ?? true,
        });
        if (!rep)
          return { content: [{ type: "text", text: "No context yet. Builds over time." }] };
        return { content: [{ type: "text", text: rep }] };
      },
    }, { name: "honcho_context" });

    // ========================================================================
    // TOOL: honcho_recall — quick factual Q&A
    // ========================================================================
    api.registerTool({
      name: "honcho_recall",
      label: "Quick Recall",
      description:
        "Ask Honcho a simple factual question. Uses minimal LLM reasoning.\n\n" +
        "━━━ Q&A TOOL ━━━\nCost: ~$0.001\nSpeed: Instant\n\n" +
        "Best for: Single data points (name, timezone, preferred language).\n" +
        "Use honcho_profile for raw facts (cheaper). Use this for direct answers.",
      parameters: Type.Object({
        query: Type.String({ description: "Simple factual question" }),
      }),
      async execute(_id: string, params: { query: string }) {
        await ensureInitialized();
        return {
          content: [{
            type: "text",
            text: await openclawPeer.chat(params.query, {
              target: ownerPeer,
              reasoningLevel: "minimal",
            }),
          }],
        };
      },
    }, { name: "honcho_recall" });

    // ========================================================================
    // TOOL: honcho_analyze — complex synthesis Q&A
    // ========================================================================
    api.registerTool({
      name: "honcho_analyze",
      label: "Analyze",
      description:
        "Ask Honcho a complex question requiring synthesis. Uses medium LLM reasoning.\n\n" +
        "━━━ Q&A TOOL ━━━\nCost: ~$0.05\nSpeed: Fast\n\n" +
        "Best for: Synthesizing patterns, communication style, decision summaries.\n" +
        "Use honcho_search for raw evidence (cheaper). Use this for interpreted answers.",
      parameters: Type.Object({
        query: Type.String({ description: "Complex question requiring synthesis" }),
      }),
      async execute(_id: string, params: { query: string }) {
        await ensureInitialized();
        return {
          content: [{
            type: "text",
            text: await openclawPeer.chat(params.query, {
              target: ownerPeer,
              reasoningLevel: "medium",
            }),
          }],
        };
      },
    }, { name: "honcho_analyze" });

    // ========================================================================
    // CLI
    // ========================================================================
    api.registerCli(({ program }: any) => {
      const cmd = program.command("honcho").description("Honcho memory");

      cmd.command("status").action(async () => {
        try {
          await ensureInitialized();
          console.log(`Connected — workspace: ${cfg.workspaceId}`);
        } catch (err) {
          console.error(`Failed: ${err}`);
        }
      });

      cmd.command("ask <question>").action(async (q: string) => {
        try {
          await ensureInitialized();
          console.log(await openclawPeer.chat(q, { target: ownerPeer }) ?? "No info.");
        } catch (err) {
          console.error(`Failed: ${err}`);
        }
      });

      cmd.command("search <query>")
        .option("-k, --top-k <n>", "Results", "10")
        .option("-d, --max-distance <n>", "Distance", "0.5")
        .action(async (q: string, opts: any) => {
          try {
            await ensureInitialized();
            const rep = await ownerPeer.representation({
              searchQuery: q,
              searchTopK: parseInt(opts.topK),
              searchMaxDistance: parseFloat(opts.maxDistance),
            });
            console.log(rep ?? `No results for: "${q}"`);
          } catch (err) {
            console.error(`Failed: ${err}`);
          }
        });
    }, { commands: ["honcho"] });

    api.logger.info("[mux] Memory multiplexer loaded (honcho + local files)");
  },
};
