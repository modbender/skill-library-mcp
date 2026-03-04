/**
 * Consolidation Engine — Multi-Layer Memory
 *
 * Groups related facts into clusters (Layer 2), and clusters into
 * higher-level clusters (Layer 3+). Operates in two modes:
 *
 *   1. **Incremental** — called after each extraction to quickly assign
 *      new facts to existing clusters or create small new ones based on
 *      category proximity and graph edges. Cheap, fast, real-time.
 *
 *   2. **Deep ("sleep")** — periodic batch job that reviews all unclustered
 *      facts, re-evaluates cluster boundaries, merges related clusters,
 *      generates richer summaries, and builds higher-layer abstractions.
 *      Uses the LLM for semantic grouping. Expensive, thorough.
 *
 * Visibility rule: a cluster inherits the most restrictive visibility
 * of any of its members (shared < private < secret).
 */

import { randomUUID } from "node:crypto";
import type { ConversationDB } from "../storage/db.js";
import type { FactRow, FactClusterRow, ClusterMemberRow } from "../storage/schema.js";
import type { PluginLogger } from "../types.js";

// ---------------------------------------------------------------------------
// Visibility helpers
// ---------------------------------------------------------------------------

function visibilityLevel(vis: string): number {
  switch (vis) {
    case "shared": return 0;
    case "private": return 1;
    case "secret": return 2;
    default: return 0;
  }
}

function visibilityFromLevel(level: number): "shared" | "private" | "secret" {
  switch (level) {
    case 2: return "secret";
    case 1: return "private";
    default: return "shared";
  }
}

/**
 * Determine the most restrictive visibility across a set of facts.
 */
function inheritVisibility(facts: FactRow[]): "shared" | "private" | "secret" {
  let maxLevel = 0;
  for (const f of facts) {
    maxLevel = Math.max(maxLevel, visibilityLevel(f.visibility));
  }
  return visibilityFromLevel(maxLevel);
}

// ---------------------------------------------------------------------------
// Incremental consolidation
// ---------------------------------------------------------------------------

export type IncrementalConsolidationResult = {
  /** Number of facts assigned to existing clusters */
  assignedToExisting: number;
  /** Number of new clusters created */
  newClusters: number;
  /** IDs of affected clusters (new or updated) */
  affectedClusterIds: string[];
};

/**
 * Incremental consolidation — run after each extraction.
 *
 * Strategy:
 *   1. Get unclustered facts for this agent
 *   2. For each unclustered fact, check if it has graph edges to any
 *      already-clustered facts → assign to that cluster
 *   3. Group remaining unclustered facts by category
 *   4. If a category group has ≥ 3 facts, create a new cluster
 *
 * This is intentionally simple and fast — no LLM calls.
 */
export function incrementalConsolidate(
  db: ConversationDB,
  agentId: string,
  logger: PluginLogger,
): IncrementalConsolidationResult {
  const now = Date.now();
  let assignedToExisting = 0;
  let newClusters = 0;
  const affectedClusterIds: string[] = [];

  const unclustered = db.getUnclusteredFacts(agentId, 200);
  if (unclustered.length === 0) {
    return { assignedToExisting: 0, newClusters: 0, affectedClusterIds: [] };
  }

  logger.debug?.(
    `memento: incremental consolidation — ${unclustered.length} unclustered facts for agent ${agentId}`,
  );

  const remaining: FactRow[] = [];

  // Pass 1: Assign facts to existing clusters via graph edges
  for (const fact of unclustered) {
    const relations = db.getRelationsForFact(fact.id);
    let bestCluster: FactClusterRow | null = null;
    let bestStrength = 0;

    for (const rel of relations) {
      const neighborId = rel.source_id === fact.id ? rel.target_id : rel.source_id;
      const clusters = db.getClustersForFact(neighborId);

      for (const cluster of clusters) {
        // Only join clusters from the same agent
        if (cluster.agent_id !== agentId) continue;
        // Only join Layer 2 clusters (don't skip levels)
        if (cluster.layer !== 2) continue;

        if (rel.strength > bestStrength) {
          bestStrength = rel.strength;
          bestCluster = cluster;
        }
      }
    }

    if (bestCluster && bestStrength >= 0.5) {
      // Assign to existing cluster
      db.addClusterMember({
        cluster_id: bestCluster.id,
        member_id: fact.id,
        member_type: "fact",
        added_at: now,
      });

      // Update cluster visibility (may become more restrictive)
      const clusterFacts = db.getClusterFacts(bestCluster.id);
      const newVis = inheritVisibility([...clusterFacts, fact]);
      if (newVis !== bestCluster.visibility) {
        db.updateCluster(bestCluster.id, { visibility: newVis });
      }

      if (!affectedClusterIds.includes(bestCluster.id)) {
        affectedClusterIds.push(bestCluster.id);
      }
      assignedToExisting++;
      logger.debug?.(
        `memento: assigned fact ${fact.id} to cluster ${bestCluster.id} (strength: ${bestStrength})`,
      );
    } else {
      remaining.push(fact);
    }
  }

  // Pass 2: Group remaining unclustered facts by category
  // Create new clusters when a category has ≥ 3 unclustered facts
  const byCategory = new Map<string, FactRow[]>();
  for (const fact of remaining) {
    const list = byCategory.get(fact.category) ?? [];
    list.push(fact);
    byCategory.set(fact.category, list);
  }

  for (const [category, facts] of byCategory) {
    if (facts.length < 3) continue;

    const clusterId = randomUUID();
    const visibility = inheritVisibility(facts);
    const avgConfidence =
      facts.reduce((sum, f) => sum + f.confidence, 0) / facts.length;

    // Generate a simple summary from the category + fact summaries
    const factSummaries = facts
      .map((f) => f.summary ?? f.content.slice(0, 60))
      .slice(0, 5)
      .join("; ");

    const cluster: FactClusterRow = {
      id: clusterId,
      agent_id: agentId,
      summary: `${categoryLabel(category)} — ${facts.length} facts`,
      description: `Auto-clustered from category "${category}": ${factSummaries}`,
      layer: 2,
      visibility,
      confidence: avgConfidence,
      created_at: now,
      updated_at: now,
      is_active: 1,
      metadata: JSON.stringify({ source: "incremental", category }),
    };

    db.insertCluster(cluster);

    const members: ClusterMemberRow[] = facts.map((f) => ({
      cluster_id: clusterId,
      member_id: f.id,
      member_type: "fact" as const,
      added_at: now,
    }));

    db.addClusterMembersBatch(members);
    affectedClusterIds.push(clusterId);
    newClusters++;

    logger.debug?.(
      `memento: created cluster ${clusterId} for category "${category}" with ${facts.length} facts`,
    );
  }

  if (assignedToExisting > 0 || newClusters > 0) {
    logger.info(
      `memento: incremental consolidation — assigned ${assignedToExisting} to existing, ` +
        `created ${newClusters} new clusters (agent: ${agentId})`,
    );
  }

  return { assignedToExisting, newClusters, affectedClusterIds };
}

// ---------------------------------------------------------------------------
// Category display label (reused from context-builder pattern)
// ---------------------------------------------------------------------------

function categoryLabel(cat: string): string {
  const labels: Record<string, string> = {
    decision: "Decisions",
    correction: "Corrections",
    action_item: "Action Items",
    preference: "Preferences",
    person: "People",
    technical: "Technical",
    emotional: "Emotional Context",
    routine: "Routines",
  };
  return labels[cat] ?? cat.charAt(0).toUpperCase() + cat.slice(1);
}
