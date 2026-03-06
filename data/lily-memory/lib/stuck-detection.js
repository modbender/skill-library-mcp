import { sqliteQuery } from "./sqlite.js";
import fs from "node:fs";
import path from "node:path";

export const MAX_TOPIC_HISTORY = 10;
export const STUCK_THRESHOLD = 3;

export const STOP_WORDS = new Set([
  "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
  "have", "has", "had", "do", "does", "did", "will", "would", "could",
  "should", "may", "might", "shall", "can", "need", "dare", "ought",
  "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
  "as", "into", "through", "during", "before", "after", "above", "below",
  "between", "out", "off", "over", "under", "again", "further", "then",
  "once", "here", "there", "when", "where", "why", "how", "all", "both",
  "each", "few", "more", "most", "other", "some", "such", "no", "nor",
  "not", "only", "own", "same", "so", "than", "too", "very", "just",
  "don", "now", "and", "but", "or", "if", "while", "that", "this",
  "it", "i", "you", "we", "they", "he", "she", "my", "your", "his",
  "her", "its", "our", "their", "what", "which", "who", "whom",
]);

/**
 * Extract a topic signature from text — top 5 significant words.
 * @param {string} text
 * @returns {string|null}
 */
export function extractTopicSignature(text) {
  if (!text || text.length < 30) return null;

  const words = text
    .toLowerCase()
    .replace(/[^\w\s]/g, " ")
    .split(/\s+/)
    .filter(w => w.length > 3 && !STOP_WORDS.has(w));

  const freq = {};
  for (const w of words) {
    freq[w] = (freq[w] || 0) + 1;
  }

  const top = Object.entries(freq)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([w]) => w)
    .sort()
    .join(",");

  // Return null if we got fewer than 2 significant words
  if (!top || top.split(",").filter(Boolean).length < 2) return null;

  return top;
}

/**
 * Load topic history from a JSON file.
 * @param {string} topicHistoryPath
 * @returns {string[]}
 */
export function loadTopicHistory(topicHistoryPath) {
  try {
    if (fs.existsSync(topicHistoryPath)) {
      return JSON.parse(fs.readFileSync(topicHistoryPath, "utf-8"));
    }
  } catch { /* ignore */ }
  return [];
}

/**
 * Save topic history to a JSON file, trimmed to MAX_TOPIC_HISTORY entries.
 * @param {string} topicHistoryPath
 * @param {string[]} history
 */
export function saveTopicHistory(topicHistoryPath, history) {
  try {
    const dir = path.dirname(topicHistoryPath);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(
      topicHistoryPath,
      JSON.stringify(history.slice(-MAX_TOPIC_HISTORY)),
      "utf-8"
    );
  } catch { /* ignore */ }
}

/**
 * Build a Reflexion-enhanced stuck nudge.
 * @param {string} dbPath
 * @param {string} repeatingSignature
 * @param {string} [userName]
 * @returns {string}
 */
export function buildReflexionNudge(dbPath, repeatingSignature, userName = "the user") {
  const repeatingWords = new Set(repeatingSignature.split(","));

  const allFacts = sqliteQuery(dbPath, `
    SELECT DISTINCT entity, fact_key, category FROM decisions
    WHERE ttl_class IN ('permanent', 'stable')
      AND entity IS NOT NULL AND fact_key IS NOT NULL
    ORDER BY importance DESC
    LIMIT 20
  `);

  const alternatives = allFacts.filter(f => {
    const words = `${f.entity} ${f.fact_key} ${f.category}`.toLowerCase().split(/\W+/);
    const overlap = words.filter(w => repeatingWords.has(w)).length;
    return overlap === 0;
  });

  const suggestions = alternatives.slice(0, 3).map(f => `${f.entity}.${f.fact_key}`);

  const lines = [
    "<lily-memory-nudge type=\"reflexion\">",
    "SELF-REFLECTION: Stuck-detection triggered. Analysis:",
    `- Repeating topic words: ${[...repeatingWords].join(", ")}`,
    "- Pattern: You are giving unsolicited status updates or repeating the same information",
    "- Root cause: Likely defaulting to project summaries when no specific task is given",
    "",
    "BREAK THE LOOP:",
    `1. Ask ${userName} a direct question about what they want to work on`,
    `2. Wait for ${userName}'s input instead of volunteering information`,
  ];

  if (suggestions.length > 0) {
    lines.push(`3. If you must speak, try a DIFFERENT topic: ${suggestions.join(", ")}`);
  } else {
    lines.push("3. If you must speak, try an entirely different subject");
  }

  lines.push(`4. Do NOT give a project status update unless ${userName} explicitly asks for one`);
  lines.push("</lily-memory-nudge>");

  return lines.join("\n");
}

/**
 * Check if the agent is stuck on the same topic.
 * Returns a nudge string if stuck, null otherwise.
 * @param {string} dbPath
 * @param {string} topicHistoryPath
 * @param {string|null} currentSignature
 * @param {{ userName?: string }} [cfg]
 * @returns {string|null}
 */
export function checkStuck(dbPath, topicHistoryPath, currentSignature, cfg = {}) {
  if (!currentSignature) return null;

  const userName = cfg.userName || "the user";

  const history = loadTopicHistory(topicHistoryPath);
  history.push(currentSignature);
  saveTopicHistory(topicHistoryPath, history);

  if (history.length < STUCK_THRESHOLD) return null;

  const recent = history.slice(-STUCK_THRESHOLD);
  const currentWords = new Set(currentSignature.split(","));

  let similarCount = 0;
  for (const sig of recent) {
    const sigWords = new Set(sig.split(","));
    const intersection = [...currentWords].filter(w => sigWords.has(w)).length;
    const union = new Set([...currentWords, ...sigWords]).size;
    if (union > 0 && intersection / union > 0.6) {
      similarCount++;
    }
  }

  if (similarCount >= STUCK_THRESHOLD) {
    return buildReflexionNudge(dbPath, currentSignature, userName);
  }

  return null;
}
