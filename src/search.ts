import type { SearchIndex, SearchResult } from "./types.js";

const STOP_WORDS = new Set([
  "a", "an", "the", "build", "write", "create", "use", "using", "when",
  "this", "for", "from", "with", "that", "are", "has", "its", "was",
  "will", "your", "you", "is", "it", "in", "on", "of", "to", "be",
  "by", "at", "as", "and", "help", "need", "want", "how", "do", "can",
  "me", "i", "my", "show", "about", "what", "should", "please",
]);

function tokenize(text: string): string[] {
  return text.toLowerCase().replace(/[^a-z0-9\-]/g, " ").split(/\s+/).filter(Boolean);
}

export function searchSkills(
  index: SearchIndex,
  query: string,
  limit: number = 20,
): SearchResult[] {
  const rawTokens = tokenize(query);
  if (rawTokens.length === 0) return [];

  // Filter stop-words, but keep all if every token is a stop-word
  const filtered = rawTokens.filter((t) => !STOP_WORDS.has(t));
  const meaningful = filtered.length > 0 ? filtered : rawTokens;

  // Deduplicate query tokens
  const queryTokens = [...new Set(meaningful)];

  const queryLower = query.toLowerCase();
  const results: SearchResult[] = [];

  // Default IDF for tokens not in the index (treat as very rare)
  const defaultIdf = Math.log((index.totalDocs || 1) + 1);

  for (const entry of index.entries) {
    let score = 0;

    let matchedTokens = 0;

    for (const qt of queryTokens) {
      const idfWeight = index.idfScores.get(qt) ?? defaultIdf;
      let bestTokenScore = 0;

      for (const st of entry.searchTokens) {
        if (st === qt) {
          bestTokenScore = Math.max(bestTokenScore, idfWeight);
        } else if (qt.length >= 2 && st.length >= 2 && (st.includes(qt) || qt.includes(st))) {
          bestTokenScore = Math.max(bestTokenScore, idfWeight * 0.5);
        }
      }

      if (bestTokenScore > 0) matchedTokens++;
      score += bestTokenScore;
    }

    // Bonus for exact substring match in name
    if (entry.frontmatter.name.toLowerCase().includes(queryLower)) {
      score += 2.0;
    }

    // Bonus for exact substring match in description
    if (entry.frontmatter.description.toLowerCase().includes(queryLower)) {
      score += 1.0;
    }

    // Normalize by matched token count (unmatched tokens don't dilute score)
    score = score / Math.max(matchedTokens, 1);

    if (score >= 0.5) {
      results.push({
        name: entry.frontmatter.name,
        dirName: entry.dirName,
        description: entry.frontmatter.description,
        score: Math.round(score * 100) / 100,
        hasResources: entry.hasResources,
      });
    }
  }

  results.sort((a, b) => b.score - a.score);
  return results.slice(0, limit);
}
