/**
 * Deep Consolidation — The "Sleep" Pass
 *
 * Periodic batch job that performs thorough knowledge base maintenance:
 *
 *   1. Reviews all unclustered facts and uses the LLM to propose semantic
 *      groupings that go beyond simple category matching.
 *   2. Re-evaluates existing cluster summaries — regenerates them from
 *      current member facts for accuracy.
 *   3. Merges overlapping clusters when their member sets converge.
 *   4. Builds Layer 3+ clusters from groups of related Layer 2 clusters.
 *   5. Applies confidence decay to stale facts (soft, not deletion).
 *
 * This is the expensive pass — it uses LLM calls for semantic analysis.
 * Designed to run once or twice per day (like human sleep consolidation).
 */

import { randomUUID } from "node:crypto";
import type { ConversationDB } from "../storage/db.js";
import type { FactRow, FactClusterRow, ClusterMemberRow } from "../storage/schema.js";
import type { PluginLogger } from "../types.js";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type DeepConsolidationConfig = {
  /** LLM model string for semantic grouping. Same format as extractionModel. */
  model: string;
  /** Maximum unclustered facts to process per run */
  maxFactsPerRun: number;
  /** Confidence decay rate per day for facts not seen in 30+ days */
  decayRatePerDay: number;
  /** Minimum confidence floor — facts never decay below this */
  decayFloor: number;
  /** Days of inactivity before decay starts */
  decayGraceDays: number;
};

export const DEFAULT_DEEP_CONFIG: DeepConsolidationConfig = {
  model: "anthropic/claude-sonnet-4-6",
  maxFactsPerRun: 100,
  decayRatePerDay: 0.005, // 0.5% per day after grace period
  decayFloor: 0.3,
  decayGraceDays: 30,
};

export type DeepConsolidationResult = {
  clustersCreated: number;
  clustersUpdated: number;
  clustersMerged: number;
  factsDecayed: number;
  errors: string[];
};

// ---------------------------------------------------------------------------
// Confidence decay
// ---------------------------------------------------------------------------

/**
 * Apply soft confidence decay to facts that haven't been seen recently.
 *
 * Rules:
 *   - Facts not seen in `decayGraceDays` start losing confidence
 *   - Decay is linear: `decayRatePerDay` per day past the grace period
 *   - Confidence never drops below `decayFloor`
 *   - Facts in clusters decay slower (×0.5 rate) — reinforced by grouping
 *   - High-occurrence facts decay slower (×0.7 rate for 3+ occurrences)
 */
export function applyConfidenceDecay(
  db: ConversationDB,
  agentId: string,
  cfg: DeepConsolidationConfig,
  logger: PluginLogger,
): number {
  const now = Date.now();
  const gracePeriodMs = cfg.decayGraceDays * 24 * 60 * 60 * 1000;
  const decayThreshold = now - gracePeriodMs;

  // Get all active facts that haven't been seen since the grace threshold
  const staleFacts = db.getRelevantFacts(agentId, 1000).filter(
    (f) => f.last_seen_at < decayThreshold && f.confidence > cfg.decayFloor,
  );

  let decayed = 0;

  for (const fact of staleFacts) {
    const daysSinceGrace =
      (now - fact.last_seen_at - gracePeriodMs) / (24 * 60 * 60 * 1000);
    if (daysSinceGrace <= 0) continue;

    // Decay modifiers
    let rateMultiplier = 1.0;

    // Facts in clusters decay slower
    const clusters = db.getClustersForFact(fact.id);
    if (clusters.length > 0) rateMultiplier *= 0.5;

    // High-occurrence facts decay slower
    if (fact.occurrence_count >= 3) rateMultiplier *= 0.7;

    const decay = cfg.decayRatePerDay * daysSinceGrace * rateMultiplier;
    const newConfidence = Math.max(cfg.decayFloor, fact.confidence - decay);

    if (newConfidence < fact.confidence) {
      // Use direct DB access to update confidence
      // (We can't easily add a dedicated method without modifying db.ts further,
      // but we can reuse the pattern from the MC feedback handler)
      try {
        // Update via the existing pattern — insertFact won't work, we need a raw update
        // For now, we'll use the getRelatedFacts pattern to get the DB handle
        // Actually, let's just add a simple helper
        db.updateFactConfidence(fact.id, newConfidence);
        decayed++;
      } catch (err) {
        logger.warn(
          `memento: decay error for fact ${fact.id}: ${String(err)}`,
        );
      }
    }
  }

  if (decayed > 0) {
    logger.info(
      `memento: confidence decay — ${decayed} facts decayed (agent: ${agentId})`,
    );
  }

  return decayed;
}

// ---------------------------------------------------------------------------
// LLM-assisted semantic clustering (placeholder for full implementation)
// ---------------------------------------------------------------------------

/**
 * Deep consolidation entry point.
 *
 * Currently implements:
 *   - Confidence decay (no LLM needed)
 *   - Cluster summary refresh (from member facts, no LLM needed)
 *
 * TODO (future iterations):
 *   - LLM-assisted semantic grouping of unclustered facts
 *   - Cluster merging when member overlap exceeds threshold
 *   - Layer 3+ meta-cluster creation
 *   - LLM-generated rich cluster summaries
 */
export function deepConsolidate(
  db: ConversationDB,
  agentId: string,
  cfg: DeepConsolidationConfig,
  logger: PluginLogger,
): DeepConsolidationResult {
  const result: DeepConsolidationResult = {
    clustersCreated: 0,
    clustersUpdated: 0,
    clustersMerged: 0,
    factsDecayed: 0,
    errors: [],
  };

  // ── Step 1: Confidence decay ────────────────────────────────────────
  try {
    result.factsDecayed = applyConfidenceDecay(db, agentId, cfg, logger);
  } catch (err) {
    const msg = `Confidence decay failed: ${String(err)}`;
    result.errors.push(msg);
    logger.warn(`memento: ${msg}`);
  }

  // ── Step 2: Refresh cluster summaries ───────────────────────────────
  try {
    const clusters = db.getClusters(agentId, 2);
    for (const cluster of clusters) {
      const facts = db.getClusterFacts(cluster.id);
      if (facts.length === 0) {
        // Empty cluster — deactivate it
        db.deactivateCluster(cluster.id);
        result.clustersUpdated++;
        continue;
      }

      // Recalculate visibility from current members
      let maxVisLevel = 0;
      for (const f of facts) {
        const vl = f.visibility === "secret" ? 2 : f.visibility === "private" ? 1 : 0;
        maxVisLevel = Math.max(maxVisLevel, vl);
      }
      const newVis = maxVisLevel === 2 ? "secret" : maxVisLevel === 1 ? "private" : "shared";

      // Regenerate summary from member facts
      const factSummaries = facts
        .sort((a, b) => b.confidence - a.confidence)
        .map((f) => f.summary ?? f.content.slice(0, 80))
        .slice(0, 8);

      const newSummary = `${facts.length} facts: ${factSummaries.slice(0, 3).join("; ")}`;
      const newDesc = factSummaries.join("; ");

      // Average confidence from members
      const avgConf = facts.reduce((s, f) => s + f.confidence, 0) / facts.length;

      const needsUpdate =
        newVis !== cluster.visibility ||
        Math.abs(avgConf - cluster.confidence) > 0.01;

      if (needsUpdate) {
        db.updateCluster(cluster.id, {
          summary: newSummary,
          description: newDesc,
          visibility: newVis,
          confidence: avgConf,
        });
        result.clustersUpdated++;
      }
    }
  } catch (err) {
    const msg = `Cluster refresh failed: ${String(err)}`;
    result.errors.push(msg);
    logger.warn(`memento: ${msg}`);
  }

  // ── Step 3: Merge overlapping clusters ──────────────────────────────
  try {
    const clusters = db.getClusters(agentId, 2);
    const clusterMembers = new Map<string, Set<string>>();

    for (const cluster of clusters) {
      const members = db.getClusterMembers(cluster.id);
      clusterMembers.set(
        cluster.id,
        new Set(members.map((m) => m.member_id)),
      );
    }

    const merged = new Set<string>();

    for (let i = 0; i < clusters.length; i++) {
      if (merged.has(clusters[i].id)) continue;
      const setA = clusterMembers.get(clusters[i].id)!;

      for (let j = i + 1; j < clusters.length; j++) {
        if (merged.has(clusters[j].id)) continue;
        const setB = clusterMembers.get(clusters[j].id)!;

        // Calculate Jaccard similarity
        let intersection = 0;
        for (const id of setA) {
          if (setB.has(id)) intersection++;
        }
        const union = setA.size + setB.size - intersection;
        const jaccard = union > 0 ? intersection / union : 0;

        // Merge if >60% overlap
        if (jaccard > 0.6) {
          // Merge B into A
          const now = Date.now();
          for (const memberId of setB) {
            if (!setA.has(memberId)) {
              db.addClusterMember({
                cluster_id: clusters[i].id,
                member_id: memberId,
                member_type: "fact",
                added_at: now,
              });
              setA.add(memberId);
            }
          }
          db.deactivateCluster(clusters[j].id);
          merged.add(clusters[j].id);
          result.clustersMerged++;

          logger.debug?.(
            `memento: merged cluster ${clusters[j].id} into ${clusters[i].id} (jaccard: ${jaccard.toFixed(2)})`,
          );
        }
      }
    }
  } catch (err) {
    const msg = `Cluster merging failed: ${String(err)}`;
    result.errors.push(msg);
    logger.warn(`memento: ${msg}`);
  }

  logger.info(
    `memento: deep consolidation — created ${result.clustersCreated}, ` +
      `updated ${result.clustersUpdated}, merged ${result.clustersMerged}, ` +
      `decayed ${result.factsDecayed} (agent: ${agentId})`,
  );

  return result;
}
