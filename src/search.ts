import type { SearchIndex, SearchResult } from "./types.js";
import { tokenize } from "./tokenize.js";

const STOP_WORDS = new Set([
  "a", "an", "the", "build", "write", "create", "use", "using", "when",
  "this", "for", "from", "with", "that", "are", "has", "its", "was",
  "will", "your", "you", "is", "it", "in", "on", "of", "to", "be",
  "by", "at", "as", "and", "help", "need", "want", "how", "do", "can",
  "me", "i", "my", "show", "about", "what", "should", "please",
]);

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
    const nameLower = entry.frontmatter.name.toLowerCase();
    const descLower = entry.frontmatter.description.toLowerCase();

    for (const qt of queryTokens) {
      const idfWeight = index.idfScores.get(qt) ?? defaultIdf;
      let bestTokenScore = 0;

      for (const st of entry.searchTokens) {
        if (st === qt) {
          // Exact token match — full IDF weight
          bestTokenScore = Math.max(bestTokenScore, idfWeight);
        } else if (qt.length >= 3 && st.length >= 3) {
          // Substring match — require min 3 chars and scale by overlap ratio
          if (st.includes(qt)) {
            const overlap = qt.length / st.length;
            bestTokenScore = Math.max(bestTokenScore, idfWeight * overlap * 0.5);
          } else if (qt.includes(st)) {
            const overlap = st.length / qt.length;
            bestTokenScore = Math.max(bestTokenScore, idfWeight * overlap * 0.5);
          }
        }
      }

      if (bestTokenScore > 0) matchedTokens++;
      score += bestTokenScore;
    }

    // Bonus for exact phrase match in name (strongest signal)
    if (nameLower.includes(queryLower)) {
      score += 3.0;
    }
    // Bonus for individual query tokens appearing in name
    for (const qt of queryTokens) {
      if (nameLower.includes(qt)) score += 1.0;
    }

    // Bonus for exact phrase match in description
    if (descLower.includes(queryLower)) {
      score += 1.5;
    }

    // Coverage bonus: reward matching more query tokens
    const coverage = matchedTokens / queryTokens.length;
    score *= 1 + coverage;

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
