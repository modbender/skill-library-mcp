/**
 * Recall Context Builder
 *
 * Transforms scored facts from the search engine into a formatted
 * context block suitable for injection via `prependContext` in the
 * `before_prompt_build` hook.
 *
 * Design goals:
 *   - Compact but readable — every token costs money
 *   - Temporal awareness — include when facts were last seen
 *   - Pattern signals — flag recurring topics
 *   - Structured grouping — decisions first, then preferences, etc.
 */

import type { ScoredFact } from "./search.js";

// ---------------------------------------------------------------------------
// Category display order — most actionable first
// ---------------------------------------------------------------------------

const CATEGORY_ORDER: string[] = [
  "decision",
  "correction",
  "action_item",
  "preference",
  "person",
  "technical",
  "emotional",
  "routine",
];

// ---------------------------------------------------------------------------
// Formatting helpers
// ---------------------------------------------------------------------------

function formatRelativeTime(timestampMs: number): string {
  const diffMs = Date.now() - timestampMs;
  const mins = Math.floor(diffMs / 60_000);
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;
  const weeks = Math.floor(days / 7);
  if (weeks < 5) return `${weeks}w ago`;
  const months = Math.floor(days / 30);
  return `${months}mo ago`;
}

function categoryLabel(cat: string): string {
  const labels: Record<string, string> = {
    decision: "📌 Decision",
    correction: "✏️ Correction",
    action_item: "📋 Action Item",
    preference: "⭐ Preference",
    person: "👤 Person",
    technical: "🔧 Technical",
    emotional: "💭 Emotional",
    routine: "📎 Routine",
  };
  return labels[cat] ?? `📎 ${cat}`;
}

/**
 * Recurring topic marker — flags facts that keep coming up.
 */
function recurrenceTag(occurrences: number): string {
  if (occurrences >= 5) return " 🔴 (recurring ×" + occurrences + ")";
  if (occurrences >= 3) return " 🟡 (mentioned ×" + occurrences + ")";
  return "";
}

/**
 * Resolve a human-readable label for an agent ID.
 * Falls back to the raw agentId if no display name is configured.
 */
function agentLabel(agentId: string, agentDisplay: Record<string, string>): string {
  return agentDisplay[agentId] ?? agentId;
}

// ---------------------------------------------------------------------------
// Builder
// ---------------------------------------------------------------------------

/**
 * Build the context block to inject before the AI turn.
 *
 * Returns an empty string if there are no facts to inject (the hook
 * should return `undefined` for prependContext in that case).
 */
export function buildRecallContext(
  facts: ScoredFact[],
  maxChars: number = 4000,
  agentDisplay: Record<string, string> = {},
): string {
  if (facts.length === 0) return "";

  // Group by category
  const grouped = new Map<string, ScoredFact[]>();
  for (const fact of facts) {
    const list = grouped.get(fact.category) ?? [];
    list.push(fact);
    grouped.set(fact.category, list);
  }

  const hasCrossAgent = facts.some((f) => f.isCrossAgent);

  const lines: string[] = [
    "## 🧠 Memento — Recalled Memory",
    hasCrossAgent
      ? "_Relevant facts from your knowledge base + shared knowledge (auto-injected):_"
      : "_Relevant facts from your knowledge base (auto-injected):_",
    "",
  ];

  let totalChars = lines.join("\n").length;

  // Iterate in priority order
  for (const cat of CATEGORY_ORDER) {
    const catFacts = grouped.get(cat);
    if (!catFacts || catFacts.length === 0) continue;

    const header = `### ${categoryLabel(cat)}`;
    if (totalChars + header.length + 2 > maxChars) break;
    lines.push(header);
    totalChars += header.length + 1;

    for (const fact of catFacts) {
      const when = formatRelativeTime(fact.last_seen_at);
      const recurrence = recurrenceTag(fact.occurrence_count);
      const source = fact.isCrossAgent ? ` [via ${agentLabel(fact.agent_id, agentDisplay)}]` : "";
      const graphTag = fact.matchSource === "graph" && fact.graphParentSummary
        ? ` 🔗 _(related to: ${fact.graphParentSummary.slice(0, 60)})_`
        : "";
      const previousTag = fact.previous_value
        ? ` _(previously: ${fact.previous_value.slice(0, 60)}${fact.previous_value.length > 60 ? "..." : ""})_`
        : "";
      const line = `- ${fact.summary ?? fact.content.slice(0, 120)} _(${when})_${recurrence}${source}${graphTag}${previousTag}`;

      if (totalChars + line.length + 1 > maxChars) break;
      lines.push(line);
      totalChars += line.length + 1;
    }

    lines.push("");
    totalChars += 1;
  }

  // Handle any categories not in CATEGORY_ORDER
  for (const [cat, catFacts] of grouped) {
    if (CATEGORY_ORDER.includes(cat)) continue;
    if (catFacts.length === 0) continue;

    const header = `### ${categoryLabel(cat)}`;
    if (totalChars + header.length + 2 > maxChars) break;
    lines.push(header);
    totalChars += header.length + 1;

    for (const fact of catFacts) {
      const when = formatRelativeTime(fact.last_seen_at);
      const recurrence = recurrenceTag(fact.occurrence_count);
      const source = fact.isCrossAgent ? ` [via ${agentLabel(fact.agent_id, agentDisplay)}]` : "";
      const graphTag = fact.matchSource === "graph" && fact.graphParentSummary
        ? ` 🔗 _(related to: ${fact.graphParentSummary.slice(0, 60)})_`
        : "";
      const previousTag = fact.previous_value
        ? ` _(previously: ${fact.previous_value.slice(0, 60)}${fact.previous_value.length > 60 ? "..." : ""})_`
        : "";
      const line = `- ${fact.summary ?? fact.content.slice(0, 120)} _(${when})_${recurrence}${source}${graphTag}${previousTag}`;

      if (totalChars + line.length + 1 > maxChars) break;
      lines.push(line);
      totalChars += line.length + 1;
    }

    lines.push("");
    totalChars += 1;
  }

  const result = lines.join("\n").trim();
  return result.length > 80 ? result : ""; // Don't inject just headers
}
