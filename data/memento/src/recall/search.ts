/**
 * Recall Search Engine
 *
 * Searches the knowledge base for facts relevant to the current conversation.
 * Uses a multi-strategy approach:
 *
 *   1. FTS5 keyword search — matches facts by content/summary text
 *   2. Recency boost — recently-seen facts score higher
 *   3. Frequency boost — facts with more occurrences score higher
 *   4. Category priority — decisions and corrections outweigh routine facts
 *
 * Phase 3 uses FTS5 only. Phase 5 will add semantic (embedding) search
 * via BGE-M3 for true "meaning" matching beyond keyword overlap.
 */

import type { ConversationDB } from "../storage/db.js";
import type { FactRow } from "../storage/schema.js";
import type { RecallConfig } from "../config.js";
import { EmbeddingEngine } from "../storage/embeddings.js";
import { runViaOpenClaw } from "../extraction/embedded-runner.js";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type ScoredFact = FactRow & {
  /** Combined relevance score (higher = more relevant) */
  score: number;
  /** How this fact was found */
  matchSource: "fts" | "semantic" | "recency" | "frequency" | "category" | "cross_agent" | "graph";
  /** Whether this fact came from another agent's shared knowledge */
  isCrossAgent: boolean;
  /** For graph-sourced facts: summary of the fact that led here */
  graphParentSummary?: string;
};

// ---------------------------------------------------------------------------
// Category priority weights — decisions & corrections matter most
// ---------------------------------------------------------------------------

const CATEGORY_WEIGHT: Record<string, number> = {
  decision: 1.5,
  correction: 1.4,
  preference: 1.3,
  person: 1.1,
  action_item: 1.2,
  technical: 1.0,
  emotional: 0.9,
  routine: 0.7,
};

// ---------------------------------------------------------------------------
// Query planning (AMA-Agent inspired)
// ---------------------------------------------------------------------------

export type QueryPlan = {
  categories?: string[];
  timeRangeHint?: string;
  entities?: string[];
  expandedQuery?: string;
};

const QUERY_PLAN_PROMPT = `You are a memory retrieval planning system. Given a user query, output a JSON object to guide knowledge base search.

QUERY: {{query}}

Return a JSON object with these optional fields:
- categories: array of relevant fact categories from [preference, decision, person, action_item, correction, technical, routine, emotional]
- timeRangeHint: time range hint like "recent", "last week", "last month", or omit if not relevant
- entities: key named entities, topics, or concepts to search for
- expandedQuery: a richer version of the query with synonyms/related terms for better FTS matching

Respond with ONLY a JSON object, no markdown, no explanation.`;

/**
 * Use LLM to plan a query before retrieval — expands terms and identifies
 * relevant categories/entities for more targeted search.
 *
 * Returns an empty object on any failure (non-fatal, best-effort only).
 */
export async function planQuery(
  query: string,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  config: any,
): Promise<QueryPlan> {
  try {
    const prompt = QUERY_PLAN_PROMPT.replace("{{query}}", query);
    const result = await runViaOpenClaw(prompt, config);
    if (!result) return {};

    const trimmed = result.text.trim();
    const jsonStr = trimmed.startsWith("{") ? trimmed : trimmed.slice(trimmed.indexOf("{"));
    const end = jsonStr.lastIndexOf("}");
    if (end === -1) return {};

    const parsed = JSON.parse(jsonStr.slice(0, end + 1)) as QueryPlan;
    return typeof parsed === "object" && parsed !== null ? parsed : {};
  } catch {
    return {};
  }
}

// ---------------------------------------------------------------------------
// Search implementation
// ---------------------------------------------------------------------------

/**
 * Extract meaningful keywords from the user's message for FTS5 search.
 * Strips common stopwords and very short tokens.
 */
function extractSearchTerms(text: string): string[] {
  const STOPWORDS = new Set([
    // English
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
    "as", "into", "through", "during", "before", "after", "above",
    "below", "between", "out", "off", "over", "under", "again",
    "further", "then", "once", "here", "there", "when", "where",
    "why", "how", "all", "both", "each", "few", "more", "most",
    "other", "some", "such", "no", "nor", "not", "only", "own",
    "same", "so", "than", "too", "very", "just", "don", "now",
    "it", "its", "i", "me", "my", "we", "our", "you", "your",
    "he", "him", "his", "she", "her", "they", "them", "their",
    "what", "which", "who", "whom", "this", "that", "these", "those",
    "am", "but", "if", "or", "because", "until", "while", "about",
    "and", "also", "get", "got", "let", "ok", "okay", "yes", "yeah",
    "sure", "please", "thanks", "thank", "hi", "hello", "hey",
    // French
    "le", "la", "les", "un", "une", "des", "du", "de", "et", "en",
    "est", "sont", "a", "ont", "il", "elle", "nous", "vous", "ils",
    "je", "tu", "ce", "se", "qui", "que", "dans", "pour", "pas",
    "sur", "avec", "plus", "ne", "au", "aux", "par", "son", "sa",
    "ses", "mais", "ou", "si", "bien", "tout", "fait", "comme",
    "été", "être", "avoir", "faire", "dit", "ça", "oui", "non",
  ]);

  return text
    .toLowerCase()
    .replace(/[^\w\s\-'àâäéèêëïîôùûüçæœ]/g, " ")
    .split(/\s+/)
    .filter((w) => w.length >= 3 && !STOPWORDS.has(w));
}

/**
 * Search the knowledge base for facts relevant to the current user message
 * and recent conversation context.
 *
 * Returns scored facts sorted by relevance (descending).
 */
export async function searchRelevantFacts(
  db: ConversationDB,
  agentId: string,
  userMessage: string,
  cfg: RecallConfig,
  embeddingEngine?: EmbeddingEngine | null,
  queryEmbedding?: number[] | null,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  openClawConfig?: any,
): Promise<ScoredFact[]> {
  const now = Date.now();
  const seenIds = new Set<string>();
  const results: ScoredFact[] = [];

  // ── Query planning (optional, AMA-Agent inspired) ─────────────────────
  let effectiveQuery = userMessage;
  if (cfg.autoQueryPlanning && openClawConfig) {
    const plan = await planQuery(userMessage, openClawConfig);
    if (plan.expandedQuery) {
      effectiveQuery = `${userMessage} ${plan.expandedQuery}`;
    }
  }

  // ── Strategy 1: FTS5 keyword search ─────────────────────────────────────
  const terms = extractSearchTerms(effectiveQuery);

  if (terms.length > 0) {
    // Build OR query for broader matching, limit to reasonable chunk
    const ftsQuery = terms.slice(0, 12).join(" OR ");
    try {
      const ftsResults = db.searchFacts(agentId, ftsQuery);
      for (const fact of ftsResults) {
        if (seenIds.has(fact.id)) continue;
        seenIds.add(fact.id);

        const catWeight = CATEGORY_WEIGHT[fact.category] ?? 1.0;
        const recencyMs = now - fact.last_seen_at;
        const recencyBoost = Math.max(0.5, 1.0 - recencyMs / (30 * 24 * 60 * 60 * 1000)); // decay over 30 days
        const freqBoost = Math.min(2.0, 1.0 + Math.log2(Math.max(1, fact.occurrence_count)));

        results.push({
          ...fact,
          score: catWeight * recencyBoost * freqBoost,
          matchSource: "fts",
          isCrossAgent: false,
        });
      }
    } catch (_err) {
      // FTS errors are non-fatal
    }
  }

  // ── Strategy 1b: Semantic (embedding) search ─────────────────────────────
  // When embeddings are available, find facts by meaning similarity.
  // This catches relevant facts even when keywords don't overlap.
  //
  // To avoid O(n) cost over the full knowledge base, we pre-filter via FTS first
  // and only run semantic scoring over the FTS candidates + a capped fallback set.
  if (queryEmbedding && embeddingEngine) {
    try {
      // Cap: use FTS results already seen + up to 200 additional facts with embeddings.
      // This keeps the semantic pass bounded even as the KB grows.
      const SEMANTIC_CANDIDATE_CAP = 200;
      const factsWithEmb = db.getFactsWithEmbeddings(agentId, SEMANTIC_CANDIDATE_CAP);

      for (const fact of factsWithEmb) {
        if (seenIds.has(fact.id)) continue;

        const similarity = EmbeddingEngine.cosineSimilarity(
          queryEmbedding,
          fact.embeddingVector,
        );

        // Only include facts with meaningful similarity
        if (similarity < 0.45) continue;

        seenIds.add(fact.id);

        const catWeight = CATEGORY_WEIGHT[fact.category] ?? 1.0;
        const recencyMs = now - fact.last_seen_at;
        const recencyBoost = Math.max(0.5, 1.0 - recencyMs / (30 * 24 * 60 * 60 * 1000));
        const freqBoost = Math.min(2.0, 1.0 + Math.log2(Math.max(1, fact.occurrence_count)));

        // Similarity is in [0.45, 1.0]; normalize to a score
        const simScore = (similarity - 0.3) / 0.7; // map 0.3-1.0 → 0-1

        results.push({
          ...fact,
          score: simScore * catWeight * recencyBoost * freqBoost * 1.2, // Slight boost over FTS
          matchSource: "semantic",
          isCrossAgent: false,
        });
      }
    } catch (_err) {
      // Embedding search failures are non-fatal
    }
  }

  // ── Strategy 2: Recent high-importance facts ────────────────────────────
  // Always include very recent facts (last 7 days) with high occurrence
  const recentFacts = db.getRelevantFacts(agentId, cfg.maxFacts * 2);
  const sevenDaysAgo = now - 7 * 24 * 60 * 60 * 1000;

  for (const fact of recentFacts) {
    if (seenIds.has(fact.id)) continue;

    // Include if: seen in last 7 days, OR high occurrence count
    const isRecent = fact.last_seen_at >= sevenDaysAgo;
    const isFrequent = fact.occurrence_count >= 3;

    if (!isRecent && !isFrequent) continue;

    seenIds.add(fact.id);

    const catWeight = CATEGORY_WEIGHT[fact.category] ?? 1.0;
    const recencyMs = now - fact.last_seen_at;
    const recencyBoost = Math.max(0.3, 1.0 - recencyMs / (30 * 24 * 60 * 60 * 1000));
    const freqBoost = Math.min(2.0, 1.0 + Math.log2(Math.max(1, fact.occurrence_count)));

    // Lower base score than FTS matches (contextual relevance vs background knowledge)
    results.push({
      ...fact,
      score: catWeight * recencyBoost * freqBoost * 0.6,
      matchSource: isRecent ? "recency" : "frequency",
      isCrossAgent: false,
    });
  }

  // ── Strategy 3: Cross-agent shared facts (Master KB) ─────────────────
  // Search shared facts from other agents for broader context.
  // These get a lower base score since the agent's own knowledge is primary.
  if (cfg.crossAgentRecall && terms.length > 0) {
    const ftsQuery = terms.slice(0, 12).join(" OR ");
    try {
      const crossAgentFts = db.searchSharedFacts(agentId, ftsQuery);
      for (const fact of crossAgentFts) {
        if (seenIds.has(fact.id)) continue;
        seenIds.add(fact.id);

        const catWeight = CATEGORY_WEIGHT[fact.category] ?? 1.0;
        const recencyMs = now - fact.last_seen_at;
        const recencyBoost = Math.max(0.5, 1.0 - recencyMs / (30 * 24 * 60 * 60 * 1000));
        const freqBoost = Math.min(2.0, 1.0 + Math.log2(Math.max(1, fact.occurrence_count)));

        // Cross-agent facts score lower (0.5 multiplier) — own knowledge is primary
        results.push({
          ...fact,
          score: catWeight * recencyBoost * freqBoost * 0.5,
          matchSource: "cross_agent",
          isCrossAgent: true,
        });
      }
    } catch (_err) {
      // Non-fatal
    }
  }

  // Cross-agent semantic search (capped to avoid full-scan over large shared KBs)
  if (cfg.crossAgentRecall && queryEmbedding && embeddingEngine) {
    try {
      const SHARED_SEMANTIC_CAP = 200;
      const sharedWithEmb = db.getSharedFactsWithEmbeddings(agentId, SHARED_SEMANTIC_CAP);
      for (const fact of sharedWithEmb) {
        if (seenIds.has(fact.id)) continue;

        const similarity = EmbeddingEngine.cosineSimilarity(
          queryEmbedding,
          fact.embeddingVector,
        );

        if (similarity < 0.50) continue; // Slightly higher threshold for cross-agent

        seenIds.add(fact.id);

        const catWeight = CATEGORY_WEIGHT[fact.category] ?? 1.0;
        const recencyMs = now - fact.last_seen_at;
        const recencyBoost = Math.max(0.5, 1.0 - recencyMs / (30 * 24 * 60 * 60 * 1000));
        const simScore = (similarity - 0.3) / 0.7;

        results.push({
          ...fact,
          score: simScore * catWeight * recencyBoost * 0.5,
          matchSource: "cross_agent",
          isCrossAgent: true,
        });
      }
    } catch (_err) {
      // Non-fatal
    }
  }

  // Also include recent high-value shared facts from other agents
  if (!cfg.crossAgentRecall) {
    results.sort((a, b) => b.score - a.score);
    return results.slice(0, cfg.maxFacts);
  }

  const crossAgentRecent = db.getSharedFactsFromOtherAgents(agentId, cfg.maxFacts);
  for (const fact of crossAgentRecent) {
    if (seenIds.has(fact.id)) continue;

    const isRecent = fact.last_seen_at >= sevenDaysAgo;
    const isFrequent = fact.occurrence_count >= 4; // Slightly higher threshold for cross-agent

    if (!isRecent && !isFrequent) continue;

    seenIds.add(fact.id);

    const catWeight = CATEGORY_WEIGHT[fact.category] ?? 1.0;
    const recencyMs = now - fact.last_seen_at;
    const recencyBoost = Math.max(0.3, 1.0 - recencyMs / (30 * 24 * 60 * 60 * 1000));
    const freqBoost = Math.min(2.0, 1.0 + Math.log2(Math.max(1, fact.occurrence_count)));

    results.push({
      ...fact,
      score: catWeight * recencyBoost * freqBoost * 0.35,
      matchSource: "cross_agent",
      isCrossAgent: true,
    });
  }

  // ── Strategy 4: Knowledge Graph traversal ────────────────────────────
  // For the top-scoring facts, follow 1-hop graph edges to pull in
  // semantically related facts that wouldn't match keyword/embedding search.
  {
    // Take the top 10 facts so far as graph seeds
    const sorted = [...results].sort((a, b) => b.score - a.score);
    const seeds = sorted.slice(0, 10);

    // Determine visibility ceiling for graph traversal
    // Own-agent: can see up to private; cross-agent: only shared
    const maxVis: "shared" | "private" | "secret" = "private";

    for (const seed of seeds) {
      try {
        const related = db.getRelatedFactsWithVisibility(seed.id, maxVis);
        for (const relFact of related) {
          if (seenIds.has(relFact.id)) continue;
          seenIds.add(relFact.id);

          // Get the relation edge to determine strength
          const edges = db.getRelationBetween(seed.id, relFact.id);
          const bestEdge = edges.reduce(
            (best, e) => (e.strength > best.strength ? e : best),
            { strength: 0.5, relation_type: "related_to" } as { strength: number; relation_type: string },
          );

          // Causal edges (caused_by, precondition_of) get a 1.5x boost instead of 0.4 reduction
          const isCausal = bestEdge.relation_type === "caused_by" || bestEdge.relation_type === "precondition_of";
          const graphMultiplier = isCausal ? 1.5 : 0.4;
          const graphScore = seed.score * bestEdge.strength * graphMultiplier;

          results.push({
            ...relFact,
            score: graphScore,
            matchSource: "graph",
            isCrossAgent: relFact.agent_id !== agentId,
            graphParentSummary: seed.summary ?? seed.content.slice(0, 80),
          });
        }
      } catch (_err) {
        // Graph traversal errors are non-fatal
      }
    }
  }

  // ── Sort by score and cap at maxFacts ───────────────────────────────────
  results.sort((a, b) => b.score - a.score);
  return results.slice(0, cfg.maxFacts);
}
