import natural from 'natural';
import type { MemDocument, SearchResult, SearchOptions } from '../types.js';

const { TfIdf } = natural;

export function searchDocuments(
  docs: MemDocument[],
  query: string,
  options: SearchOptions = {},
): SearchResult[] {
  const { limit = 10, minScore = 0.01, category, tags } = options;

  let filtered = docs;
  if (category) {
    filtered = filtered.filter((d) => d.category === category);
  }
  if (tags && tags.length > 0) {
    const lowerTags = tags.map((t) => t.toLowerCase());
    filtered = filtered.filter((d) =>
      lowerTags.some((lt) => d.tags.map((t) => t.toLowerCase()).includes(lt)),
    );
  }

  if (filtered.length === 0) return [];

  const tfidf = new TfIdf();
  for (const doc of filtered) {
    const text = `${doc.title} ${doc.tags.join(' ')} ${doc.content}`;
    tfidf.addDocument(text);
  }

  const scored: { index: number; score: number }[] = [];
  tfidf.tfidfs(query, (i, measure) => {
    if (measure > minScore) {
      scored.push({ index: i, score: measure });
    }
  });

  scored.sort((a, b) => b.score - a.score);

  const maxScore = scored.length > 0 ? scored[0].score : 1;

  return scored.slice(0, limit).map(({ index, score }) => {
    const doc = filtered[index];
    const normalizedScore = maxScore > 0 ? score / maxScore : 0;
    return {
      document: doc,
      score: normalizedScore,
      snippet: extractSnippet(doc.content, query),
    };
  });
}

function extractSnippet(content: string, query: string, maxLen = 150): string {
  const lower = content.toLowerCase();
  const terms = query.toLowerCase().split(/\s+/);

  for (const term of terms) {
    const idx = lower.indexOf(term);
    if (idx !== -1) {
      const start = Math.max(0, idx - 40);
      const end = Math.min(content.length, idx + maxLen - 40);
      let snippet = content.slice(start, end).trim();
      if (start > 0) snippet = '...' + snippet;
      if (end < content.length) snippet = snippet + '...';
      return snippet;
    }
  }

  return content.slice(0, maxLen).trim() + (content.length > maxLen ? '...' : '');
}
