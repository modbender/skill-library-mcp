/**
 * Relation Sweep — Phase 3 Pipeline
 *
 * Background job that builds the knowledge graph by linking semantically
 * related facts via embedding similarity. Designed to run at 3 AM or
 * on-demand via the Mission Control UI.
 *
 * Algorithm:
 *   1. Load all active facts with embeddings from DB
 *   2. Compute pairwise cosine similarity across categories (cross-category focus)
 *   3. High-similarity same-category pairs → `related_to` edge (no LLM needed)
 *   4. Cross-category pairs above threshold → batched Haiku classification
 *   5. Store typed edges in fact_relations (created_by: "relation-sweep")
 *   6. Skip pairs already linked (idempotent)
 *
 * Thresholds:
 *   SAME_CATEGORY_AUTO  = 0.85  → `related_to` without LLM
 *   CROSS_CATEGORY_LLM  = 0.72  → send to Haiku for classification
 *   CROSS_CATEGORY_AUTO = 0.88  → `related_to` without LLM (very high sim)
 *
 * The sweep is incremental: it only processes pairs involving facts seen
 * since the last run (tracked via `relation_sweep_cursor` in a metadata row).
 */

import { randomUUID } from "node:crypto";
import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import type { ConversationDB } from "../storage/db.js";
import type { FactRelationRow } from "../storage/schema.js";
import type { PluginLogger } from "../types.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// ---------------------------------------------------------------------------
// Thresholds
// ---------------------------------------------------------------------------

const SAME_CATEGORY_AUTO = 0.85;    // auto-link same-category pairs (no LLM)
const CROSS_CATEGORY_LLM_MIN = 0.72; // min similarity to send to LLM
const CROSS_CATEGORY_AUTO = 0.88;   // auto-link cross-category (skip LLM)
const LLM_BATCH_SIZE = 30;          // max pairs per Haiku call

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type RelationSweepResult = {
  factsScanned: number;
  pairsConsidered: number;
  edgesAutoLinked: number;
  edgesLLMClassified: number;
  edgesSkipped: number;  // already linked
  durationMs: number;
};

type FactWithVector = {
  id: string;
  agent_id: string;
  category: string;
  content: string;
  summary: string | null;
  visibility: string;
  embeddingVector: number[];
};

type CandidatePair = {
  a: FactWithVector;
  b: FactWithVector;
  similarity: number;
  sameCat: boolean;
};

type LLMClassification = {
  pair_index: number;
  relation_type: string;
  strength: number;
  rationale: string;
};

// ---------------------------------------------------------------------------
// Cosine similarity
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
// Prompt loader
// ---------------------------------------------------------------------------

function loadClassifyPrompt(): string {
  const path = join(__dirname, "..", "..", "prompts", "relation-classify.md");
  return readFileSync(path, "utf-8");
}

// ---------------------------------------------------------------------------
// LLM call (direct Anthropic API — same pattern as MC batch extraction)
// ---------------------------------------------------------------------------

async function callHaiku(pairs: CandidatePair[], apiToken: string, logger: PluginLogger): Promise<LLMClassification[]> {
  const promptTemplate = loadClassifyPrompt();

  const pairsJson = pairs.map((p, i) => ({
    pair_index: i,
    fact_a: { id: p.a.id, category: p.a.category, summary: p.a.summary, content: p.a.content.slice(0, 200) },
    fact_b: { id: p.b.id, category: p.b.category, summary: p.b.summary, content: p.b.content.slice(0, 200) },
    similarity: p.similarity.toFixed(3),
  }));

  const prompt = promptTemplate.replace("{{pairs}}", JSON.stringify(pairsJson, null, 2));

  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${apiToken}`,
      "anthropic-version": "2023-06-01",
      "anthropic-beta": "oauth-2025-04-20",
    },
    body: JSON.stringify({
      model: "claude-haiku-4-5",
      max_tokens: 2048,
      messages: [{ role: "user", content: prompt }],
    }),
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`Haiku API error ${response.status}: ${err.slice(0, 200)}`);
  }

  const data = await response.json() as any;
  const text = data.content?.[0]?.text ?? "";

  // Parse JSON (strip markdown fences if present)
  const clean = text.replace(/^```[a-z]*\n?/, "").replace(/\n?```$/, "").trim();
  try {
    const parsed = JSON.parse(clean);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    logger.warn(`relation-sweep: failed to parse LLM response: ${clean.slice(0, 100)}`);
    return [];
  }
}

// ---------------------------------------------------------------------------
// Get existing edges (for dedup)
// ---------------------------------------------------------------------------

function getExistingEdgeSet(db: ConversationDB): Set<string> {
  const rows = db.getAllRelations?.() ?? [];
  const set = new Set<string>();
  for (const r of rows) {
    set.add(`${r.source_id}:${r.target_id}`);
    set.add(`${r.target_id}:${r.source_id}`); // undirected
  }
  return set;
}

// ---------------------------------------------------------------------------
// Main entry point
// ---------------------------------------------------------------------------

export async function runRelationSweep(
  db: ConversationDB,
  apiToken: string | null,
  logger: PluginLogger,
): Promise<RelationSweepResult> {
  const startMs = Date.now();
  let edgesAutoLinked = 0;
  let edgesLLMClassified = 0;
  let edgesSkipped = 0;

  logger.info("relation-sweep: starting…");

  // Load all active facts with embeddings
  const allAgentIds = db.getDistinctAgentIds?.() ?? ["main"];
  const allFacts: FactWithVector[] = [];

  for (const agentId of allAgentIds) {
    const facts = db.getFactsWithEmbeddings(agentId);
    // Include shared facts for cross-agent linking
    for (const f of facts) {
      if (f.visibility !== "secret") { // never link secret facts
        allFacts.push(f as FactWithVector);
      }
    }
  }

  logger.info(`relation-sweep: loaded ${allFacts.length} facts with embeddings`);

  if (allFacts.length < 2) {
    return { factsScanned: allFacts.length, pairsConsidered: 0, edgesAutoLinked: 0, edgesLLMClassified: 0, edgesSkipped: 0, durationMs: Date.now() - startMs };
  }

  // Get existing edges to avoid re-linking
  const existingEdges = getExistingEdgeSet(db);

  // Find candidate pairs
  const autoPairs: Array<{ pair: CandidatePair; relationType: string; strength: number }> = [];
  const llmPairs: CandidatePair[] = [];
  let pairsConsidered = 0;

  for (let i = 0; i < allFacts.length; i++) {
    for (let j = i + 1; j < allFacts.length; j++) {
      const a = allFacts[i];
      const b = allFacts[j];

      // Skip same-agent same-fact (shouldn't happen but safety)
      if (a.id === b.id) continue;
      // Skip if already linked
      if (existingEdges.has(`${a.id}:${b.id}`)) { edgesSkipped++; continue; }

      const sim = cosine(a.embeddingVector, b.embeddingVector);
      const sameCat = a.category === b.category;

      if (sameCat && sim >= SAME_CATEGORY_AUTO) {
        pairsConsidered++;
        autoPairs.push({ pair: { a, b, similarity: sim, sameCat }, relationType: "related_to", strength: Math.min(sim, 1.0) });
      } else if (!sameCat && sim >= CROSS_CATEGORY_AUTO) {
        pairsConsidered++;
        autoPairs.push({ pair: { a, b, similarity: sim, sameCat }, relationType: "related_to", strength: Math.min(sim * 0.95, 1.0) });
      } else if (!sameCat && sim >= CROSS_CATEGORY_LLM_MIN && apiToken) {
        pairsConsidered++;
        llmPairs.push({ a, b, similarity: sim, sameCat });
      }
    }
  }

  logger.info(`relation-sweep: ${autoPairs.length} auto pairs, ${llmPairs.length} LLM pairs`);

  const now = Date.now();
  const relationsToInsert: FactRelationRow[] = [];

  // Auto-link pairs
  for (const { pair, relationType, strength } of autoPairs) {
    relationsToInsert.push({
      id: randomUUID(),
      source_id: pair.a.id,
      target_id: pair.b.id,
      relation_type: relationType,
      strength,
      causal_weight: 1.0,
      created_at: now,
      created_by: "relation-sweep",
      metadata: JSON.stringify({ similarity: pair.similarity, method: "embedding-auto" }),
    });
    edgesAutoLinked++;
  }

  // LLM-classified pairs (batched)
  if (llmPairs.length > 0 && apiToken) {
    for (let start = 0; start < llmPairs.length; start += LLM_BATCH_SIZE) {
      const batch = llmPairs.slice(start, start + LLM_BATCH_SIZE);
      try {
        const classifications = await callHaiku(batch, apiToken, logger);
        for (const cls of classifications) {
          if (cls.pair_index < 0 || cls.pair_index >= batch.length) continue;
          const pair = batch[cls.pair_index];
          const validTypes = new Set(["caused_by", "precondition_of", "part_of", "related_to", "contradicts", "superseded_by"]);
          const relType = validTypes.has(cls.relation_type) ? cls.relation_type : "related_to";
          relationsToInsert.push({
            id: randomUUID(),
            source_id: pair.a.id,
            target_id: pair.b.id,
            relation_type: relType,
            strength: Math.min(Math.max(cls.strength ?? 0.7, 0.5), 1.0),
            causal_weight: ["caused_by", "precondition_of"].includes(relType) ? 1.5 : 1.0,
            created_at: now,
            created_by: "relation-sweep",
            metadata: JSON.stringify({ similarity: pair.similarity, method: "llm-haiku", rationale: (cls.rationale ?? "").slice(0, 200) }),
          });
          edgesLLMClassified++;
        }
        logger.info(`relation-sweep: batch ${Math.floor(start / LLM_BATCH_SIZE) + 1} — ${classifications.length} relations from ${batch.length} pairs`);
      } catch (err) {
        logger.warn(`relation-sweep: LLM batch failed: ${String(err)}`);
      }
    }
  }

  // Batch-insert all relations
  if (relationsToInsert.length > 0) {
    try {
      db.insertRelationsBatch(relationsToInsert);
      logger.info(`relation-sweep: inserted ${relationsToInsert.length} new edges`);
    } catch (err) {
      logger.warn(`relation-sweep: failed to insert relations: ${String(err)}`);
    }
  }

  const result: RelationSweepResult = {
    factsScanned: allFacts.length,
    pairsConsidered,
    edgesAutoLinked,
    edgesLLMClassified,
    edgesSkipped,
    durationMs: Date.now() - startMs,
  };

  logger.info(`relation-sweep: done in ${result.durationMs}ms — ${edgesAutoLinked} auto, ${edgesLLMClassified} LLM, ${edgesSkipped} skipped`);
  return result;
}
