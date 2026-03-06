/**
 * Memento — Local Persistent Memory for OpenClaw Agents
 *
 * Phase 1 (Capture): Hooks into message events to buffer all conversations
 * per session, then flushes complete segments to SQLite + JSONL when a pause
 * is detected, the buffer is full, or the session ends.
 *
 * Phase 2 (Extraction): After each segment is captured, asynchronously
 * extracts structured facts using the configured LLM. Facts are deduplicated,
 * classified by visibility, and stored in SQLite with temporal tracking.
 *
 * Phase 3 (Recall): Before each AI turn, searches the knowledge base for
 * facts relevant to the current user message and injects them as context
 * via the `before_prompt_build` hook. Uses FTS5 keyword search + recency/
 * frequency scoring. Semantic embedding search planned for Phase 5.
 *
 * Phase 4 (Master KB): Cross-agent knowledge sharing. Each agent's recall
 * searches its own facts (all visibility levels) plus shared facts from
 * other agents. Private and secret facts never cross agent boundaries.
 * Cross-agent facts are scored lower than own-agent facts and displayed
 * with provenance tags (e.g., "[via agent-id]" or a configured display name).
 */

import { resolveConfig } from "./config.js";
import { ConversationBuffer } from "./capture/buffer.js";
import { SegmentWriter } from "./capture/writer.js";
import { ExtractionTrigger } from "./extraction/trigger.js";
import { searchRelevantFacts } from "./recall/search.js";
import { buildRecallContext } from "./recall/context-builder.js";
import { EmbeddingEngine } from "./storage/embeddings.js";

// ---------------------------------------------------------------------------
// Plugin definition
// ---------------------------------------------------------------------------

const mementoPlugin = {
  id: "memento",
  name: "Memento",
  description:
    "Memento — Local persistent memory with temporal intelligence for OpenClaw agents.",

  register(api: any): void {
    const cfg = resolveConfig(api.pluginConfig);

    if (!cfg.autoCapture) {
      api.logger.info(
        "memento: autoCapture is disabled — hooks not registered",
      );
      return;
    }

    // Resolve the data directory from the plugin config.
    // resolvePath expands ~ and resolves relative paths against workspace.
    const dataDir = api.resolvePath(cfg.dataDir);

    const writer = new SegmentWriter(dataDir, api.logger);

    // ── Embedding engine (lazy-loaded on first recall) ─────────────────────
    const embeddingEngine = new EmbeddingEngine(
      cfg.embeddingModel,
      api.logger,
    );

    // ── Phase 2: extraction trigger ─────────────────────────────────────────
    // Created unconditionally (the trigger checks cfg.extraction.autoExtract).
    // Shares the same DB connection as the writer to avoid opening a second handle.
    let trigger: ExtractionTrigger | null = null;

    if (cfg.extraction.autoExtract) {
      trigger = new ExtractionTrigger(
        writer.getDb(),
        cfg.extraction,
        cfg.extractionModel,
        api.logger,
        api.config,  // Pass OpenClaw config for model routing
        embeddingEngine, // Phase 2: embedding-based dedup
      );

      api.logger.info(
        `memento: extraction enabled (model: ${cfg.extractionModel}, ` +
          `minTurns: ${cfg.extraction.minTurnsForExtraction}, ` +
          `maxPerMin: ${cfg.extraction.maxExtractionsPerMinute})`,
      );
    } else {
      api.logger.info("memento: extraction disabled (autoExtract=false)");
    }

    const buffer = new ConversationBuffer(
      cfg,
      // flush handler — called by buffer whenever a segment is complete
      async (sessionKey, buf) => {
        const conversation = writer.writeSegment(sessionKey, buf);
        // Trigger extraction async — never awaited, never blocks capture
        if (conversation && trigger) {
          trigger.triggerAsync(conversation);
        }
      },
      api.logger,
    );

    api.logger.info(
      `memento: registered (dataDir: ${dataDir}, ` +
        `pauseTimeout: ${cfg.pauseTimeoutMs}ms, maxTurns: ${cfg.maxBufferTurns})`,
    );

    // -----------------------------------------------------------------------
    // Hook: message:received  — user message arriving via a channel
    // -----------------------------------------------------------------------
    api.on("message_received", async (event: any, ctx: any) => {
      try {
        // Key the buffer by conversationId when available; fall back to channelId.
        // conversationId typically maps to a Telegram chat / Discord thread / etc.
        const sessionKey = ctx.conversationId ?? ctx.channelId;

        await buffer.addMessage(sessionKey, {
          role: "user",
          content: event.content,
          timestamp: event.timestamp ?? Date.now(),
          messageId: undefined,
          channel: ctx.channelId,
        });
      } catch (err) {
        // Never propagate — capture failures must not disrupt the agent
        api.logger.warn(
          `memento: message_received error: ${String(err)}`,
        );
      }
    });

    // -----------------------------------------------------------------------
    // Hook: message:sent  — assistant response delivered to the channel
    // -----------------------------------------------------------------------
    api.on("message_sent", async (event: any, ctx: any) => {
      // Skip failed deliveries — nothing useful to capture
      if (!event.success) return;

      try {
        const sessionKey = ctx.conversationId ?? ctx.channelId;

        await buffer.addMessage(sessionKey, {
          role: "assistant",
          content: event.content,
          timestamp: Date.now(),
          messageId: undefined,
          channel: ctx.channelId,
        });
      } catch (err) {
        api.logger.warn(
          `memento: message_sent error: ${String(err)}`,
        );
      }
    });

    // -----------------------------------------------------------------------
    // Hook: before_reset  — user typed /new (or equivalent session reset)
    // Flush all active buffers so nothing is lost when the session clears.
    // -----------------------------------------------------------------------
    api.on("before_reset", async (_event: any, _ctx: any) => {
      try {
        await buffer.flushAll();
      } catch (err) {
        api.logger.warn(
          `memento: before_reset flush error: ${String(err)}`,
        );
      }
    });

    // -----------------------------------------------------------------------
    // Hook: session_end  — belt-and-suspenders flush when a session closes
    // -----------------------------------------------------------------------
    api.on("session_end", async (_event: any, _ctx: any) => {
      try {
        await buffer.flushAll();
      } catch (err) {
        api.logger.warn(
          `memento: session_end flush error: ${String(err)}`,
        );
      }
    });

    // -----------------------------------------------------------------------
    // Hook: before_prompt_build — Phase 3: Auto-Recall + Semantic Search
    // Injects relevant facts from the knowledge base before each AI turn.
    // Uses FTS5 keyword search + embedding cosine similarity when available.
    // -----------------------------------------------------------------------
    if (cfg.recall.autoRecall) {
      api.on("before_prompt_build", async (event: any, ctx: any) => {
        try {
          // Extract the latest user message from the conversation messages
          const messages: any[] = event.messages ?? [];
          const lastUserMsg = [...messages]
            .reverse()
            .find((m: any) => m.role === "user");

          if (!lastUserMsg) return {};

          // Get the text content from the message
          let queryText = "";
          if (typeof lastUserMsg.content === "string") {
            queryText = lastUserMsg.content;
          } else if (Array.isArray(lastUserMsg.content)) {
            // Multi-part content (text + images, etc.)
            queryText = lastUserMsg.content
              .filter((p: any) => p.type === "text")
              .map((p: any) => p.text)
              .join(" ");
          }

          if (queryText.length < cfg.recall.minQueryLength) return {};

          // Resolve agent ID from hook context
          const agentId = ctx.agentId ?? "unknown";

          // Generate query embedding (async, may return null if model not loaded).
          // ensureInit is lazy — first call loads the model; subsequent calls are instant.
          const queryEmbedding: number[] | null = await embeddingEngine.embed(queryText);

          // Search for relevant facts (FTS5 + semantic when embedding available)
          const scoredFacts = await searchRelevantFacts(
            writer.getDb(),
            agentId,
            queryText,
            cfg.recall,
            embeddingEngine.isReady ? embeddingEngine : null,
            queryEmbedding,
            api.config, // OpenClaw config for query planning (autoQueryPlanning)
          );

          if (scoredFacts.length === 0) return {};

          // Build the context block
          const contextBlock = buildRecallContext(
            scoredFacts,
            cfg.recall.maxContextChars,
            cfg.agentDisplay,
          );

          if (!contextBlock) return {};

          api.logger.debug?.(
            `memento: recall injecting ${scoredFacts.length} facts ` +
              `(${contextBlock.length} chars, semantic: ${queryEmbedding ? "yes" : "no"}) ` +
              `for agent ${agentId}`,
          );

          return { prependContext: contextBlock };
        } catch (err) {
          // Recall failures must never block the AI turn
          api.logger.warn(
            `memento: before_prompt_build recall error: ${String(err)}`,
          );
          return {};
        }
      });

      api.logger.info(
        `memento: recall enabled (maxFacts: ${cfg.recall.maxFacts}, ` +
          `maxChars: ${cfg.recall.maxContextChars}, ` +
          `embeddings: ${cfg.embeddingModel})`,
      );
    } else {
      api.logger.info("memento: recall disabled (autoRecall=false)");
    }

    // -----------------------------------------------------------------------
    // Service lifecycle — flush + close DB cleanly on gateway shutdown
    // -----------------------------------------------------------------------
    api.registerService({
      id: "memento",

      start: (ctx: any) => {
        api.logger.info(
          `memento: service started` +
            (ctx.workspaceDir ? ` (workspace: ${ctx.workspaceDir})` : ""),
        );
      },

      stop: async () => {
        try {
          if (buffer.size > 0) {
            api.logger.info(
              `memento: flushing ${buffer.size} active session(s) before shutdown`,
            );
            await buffer.flushAll();
          }
          await embeddingEngine.dispose();
          writer.close();
        } catch (err) {
          api.logger.warn(
            `memento: stop flush error: ${String(err)}`,
          );
        }
        api.logger.info("memento: service stopped");
      },
    });
  },
};

export default mementoPlugin;
