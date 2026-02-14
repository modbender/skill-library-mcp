import type { SkillEntry, SearchResult } from "./types.js";

function tokenize(text: string): string[] {
  return text.toLowerCase().replace(/[^a-z0-9\-]/g, " ").split(/\s+/).filter(Boolean);
}

export function searchSkills(
  index: SkillEntry[],
  query: string,
  limit: number = 20,
): SearchResult[] {
  const queryTokens = tokenize(query);
  if (queryTokens.length === 0) return [];

  const queryLower = query.toLowerCase();
  const results: SearchResult[] = [];

  for (const entry of index) {
    let score = 0;

    // Token overlap scoring
    for (const qt of queryTokens) {
      for (const st of entry.searchTokens) {
        if (st === qt) {
          score += 1;
        } else if (st.includes(qt) || qt.includes(st)) {
          score += 0.5;
        }
      }
    }

    // Bonus for exact substring match in name
    if (entry.frontmatter.name.toLowerCase().includes(queryLower)) {
      score += 0.5;
    }

    // Bonus for exact substring match in description
    if (entry.frontmatter.description.toLowerCase().includes(queryLower)) {
      score += 0.3;
    }

    // Normalize by query token count
    score = score / queryTokens.length;

    if (score >= 0.2) {
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
