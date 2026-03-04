/**
 * Deduplication Engine — Phase 2: Embedding-Based
 *
 * Processes an array of ExtractedFacts from the LLM, applying one of three
 * outcomes for each fact based on cosine similarity against existing embeddings:
 *
 *   1. Duplicate   (sim >= DUPLICATE_THRESHOLD)  — fact already exists; increment occurrence_count
 *   2. Update      (sim >= UPDATE_THRESHOLD)      — fact supersedes an older one; mark old inactive, insert new
 *   3. New         (sim <  UPDATE_THRESHOLD)      — genuinely new fact; insert + log first occurrence
 *
 * The LLM no longer provides `duplicate_of` / `supersedes` hints — those were
 * unreliable due to the windowed context. Cosine similarity over BGE-M3 embeddings
 * is more consistent and doesn't depend on history quality.
 *
 * Thresholds (tunable via config):
 *   DUPLICATE_THRESHOLD = 0.97  — near-identical wording, same meaning
 *   UPDATE_THRESHOLD    = 0.82  — same topic, different value (e.g. FTP changed)
 *
 * Facts without embeddings (model unavailable) fall back to new-fact insertion.
 */

import { randomUUID } from "node:crypto";
import type { ConversationDB } from "../storage/db.js";
import type { EmbeddingEngine } from "../storage/embeddings.js";
import type { ExtractedFact } from "./extractor.js";
import type { FactRow, FactRelationRow } from "../storage/schema.js";
import type { PluginLogger } from "../types.js";

// ---------------------------------------------------------------------------
// Thresholds
// ---------------------------------------------------------------------------

/** Cosine similarity >= this → treat as duplicate (same fact seen again) */
const DUPLICATE_THRESHOLD = 0.97;

/** Cosine similarity >= this (but < DUPLICATE_THRESHOLD) → treat as update (supersede) */
const UPDATE_THRESHOLD = 0.82;

/** Only compare against facts in the same category (reduces false positives) */
const SAME_CATEGORY_ONLY = true;

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type DeduplicationResult = {
  factsExtracted: number;      // genuinely new facts inserted
  factsUpdated: number;        // facts that superseded an older fact
  factsDeduplicated: number;   // facts identified as duplicates (occurrence incremented)
};

type FactWithVector = FactRow & { embeddingVector: number[] };

// ---------------------------------------------------------------------------
// Cosine similarity (inline — no dep on EmbeddingEngine internals)
// ---------------------------------------------------------------------------

function cosine(a: number[], b: number[]): number {
  let dot = 0, normA = 0, normB = 0;
  const len = Math.min(a.length, b.length);
  for (let i = 0; i < len; i++) {
    dot += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  const denom = Math.sqrt(normA) * Math.sqrt(normB);
  return denom === 0 ? 0 : dot / denom;
}

// ---------------------------------------------------------------------------
// Main entry point
// ---------------------------------------------------------------------------

/**
 * Process extracted facts against the database, applying dedup/supersede/insert logic
 * using embedding cosine similarity (Phase 2 pipeline).
 *
 * @param facts           - Facts extracted by the LLM (history-agnostic, no duplicate_of hints)
 * @param conversationId  - Current conversation ID (for occurrence logging)
 * @param agentId         - Agent owning these facts
 * @param db              - ConversationDB instance
 * @param embeddingEngine - Optional: if provided, new facts get embedded immediately
 * @param logger          - Plugin logger
 */
export async function processExtractedFacts(
  facts: ExtractedFact[],
  conversationId: string,
  agentId: string,
  db: ConversationDB,
  embeddingEngine: EmbeddingEngine | null,
  logger: PluginLogger,
): Promise<DeduplicationResult> {
  const now = Date.now();
  let factsExtracted = 0;
  let factsUpdated = 0;
  let factsDeduplicated = 0;

  // Load existing facts with embeddings for this agent (once, for all comparisons)
  const existingFacts: FactWithVector[] = db.getFactsWithEmbeddings(agentId);

  logger.debug?.(
    `memento: deduplicator loaded ${existingFacts.length} existing facts with embeddings`,
  );

  for (const fact of facts) {
    try {
      let persistedFactId: string | null = null;

      // ── Step 1: Embed the incoming fact ──────────────────────────────────
      let incomingVector: number[] | null = null;
      if (embeddingEngine) {
        const text = `${fact.summary ? fact.summary + ". " : ""}${fact.content}`.slice(0, 2000);
        incomingVector = await embeddingEngine.embed(text);
      }

      // ── Step 2: Find best match via cosine similarity ─────────────────────
      let bestSim = 0;
      let bestMatch: FactWithVector | null = null;

      if (incomingVector && existingFacts.length > 0) {
        const candidates = SAME_CATEGORY_ONLY
          ? existingFacts.filter(f => f.category === fact.category)
          : existingFacts;

        for (const existing of candidates) {
          const sim = cosine(incomingVector, existing.embeddingVector);
          if (sim > bestSim) {
            bestSim = sim;
            bestMatch = existing;
          }
        }
      }

      logger.debug?.(
        `memento: best match sim=${bestSim.toFixed(4)} for "${fact.content.slice(0, 50)}"` +
        (bestMatch ? ` → "${bestMatch.summary?.slice(0, 50)}"` : " (no match)"),
      );

      // ── Step 3: Apply outcome based on similarity ─────────────────────────

      if (bestMatch && bestSim >= DUPLICATE_THRESHOLD) {
        // DUPLICATE — increment occurrence, update last_seen_at
        db.updateFactOccurrence(
          bestMatch.id,
          conversationId,
          fact.content,
          fact.sentiment ?? "neutral",
          now,
        );
        persistedFactId = bestMatch.id;
        factsDeduplicated++;
        logger.debug?.(
          `memento: duplicate (sim=${bestSim.toFixed(3)}) of ${bestMatch.id}: ${fact.content.slice(0, 60)}`,
        );

      } else if (bestMatch && bestSim >= UPDATE_THRESHOLD) {
        // UPDATE — supersede the existing fact with the new one
        const newFact: FactRow = buildFactRow(fact, agentId, now);
        db.supersedeFact(bestMatch.id, newFact);
        db.updateFactOccurrence(
          newFact.id,
          conversationId,
          fact.content,
          fact.sentiment ?? "update",
          now,
        );
        // Store embedding for the new fact
        if (incomingVector) {
          db.setFactEmbedding(newFact.id, incomingVector);
          // Update the in-memory list so subsequent facts can match against this new one
          existingFacts.push({ ...newFact, embeddingVector: incomingVector });
        }
        persistedFactId = newFact.id;
        factsUpdated++;
        logger.debug?.(
          `memento: superseded (sim=${bestSim.toFixed(3)}) ${bestMatch.id} → ${newFact.id}: ${fact.content.slice(0, 60)}`,
        );

      } else {
        // NEW FACT — insert and embed
        const newFact: FactRow = buildFactRow(fact, agentId, now);
        db.insertFact(newFact);
        db.updateFactOccurrence(
          newFact.id,
          conversationId,
          fact.content,
          fact.sentiment ?? "neutral",
          now,
        );
        if (incomingVector) {
          db.setFactEmbedding(newFact.id, incomingVector);
          existingFacts.push({ ...newFact, embeddingVector: incomingVector });
        }
        persistedFactId = newFact.id;
        factsExtracted++;
        logger.debug?.(
          `memento: new fact ${newFact.id} [${fact.category}]: ${fact.content.slice(0, 60)}`,
        );
      }

      // ── Step 4: Store graph relations (if any provided by LLM) ───────────
      // Relations are still accepted from the LLM if present, but no longer required.
      // Phase 3 (async background job) will build relations from embedding similarity.
      if (persistedFactId && fact.relations && fact.relations.length > 0) {
        const CAUSAL_TYPES = new Set(["caused_by", "precondition_of"]);
        const relations: FactRelationRow[] = fact.relations
          .filter((r) => r.target_id !== persistedFactId)
          .map((r) => ({
            id: randomUUID(),
            source_id: persistedFactId!,
            target_id: r.target_id,
            relation_type: r.relation_type,
            strength: r.strength ?? 0.8,
            causal_weight: CAUSAL_TYPES.has(r.relation_type) ? 1.5 : 1.0,
            created_at: now,
            created_by: "extraction",
            metadata: null,
          }));

        if (relations.length > 0) {
          try {
            db.insertRelationsBatch(relations);
          } catch (relErr) {
            logger.warn(`memento: failed to store relations for ${persistedFactId}: ${String(relErr)}`);
          }
        }
      }

    } catch (err) {
      logger.warn(
        `memento: deduplicator error processing fact "${fact.content.slice(0, 60)}": ${String(err)}`,
      );
    }
  }

  return { factsExtracted, factsUpdated, factsDeduplicated };
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

function buildFactRow(fact: ExtractedFact, agentId: string, now: number): FactRow {
  return {
    id: randomUUID(),
    agent_id: agentId,
    category: fact.category,
    content: fact.content,
    summary: fact.summary ?? null,
    visibility: fact.visibility ?? "shared",
    confidence: fact.confidence ?? 1.0,
    first_seen_at: now,
    last_seen_at: now,
    occurrence_count: 0, // updateFactOccurrence will increment to 1
    supersedes: fact.supersedes ?? null,
    is_active: 1,
    metadata: null,
    embedding: null, // set immediately after insert via setFactEmbedding
    previous_value: null, // set by supersedeFact in db.ts
  };
}
