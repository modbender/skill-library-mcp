"use strict";

/**
 * BM25 + Keyword Matching Search Engine for Agent Registry.
 *
 * Extracted from hooks/user_prompt_search.js so both the hook and
 * the CLI scripts share a single implementation.
 */

function tokenize(text) {
  return text.toLowerCase().match(/\b[a-z0-9]+\b/g) || [];
}

class BM25 {
  constructor(k1 = 1.5, b = 0.75) {
    this.k1 = k1;
    this.b = b;
    this.corpus = [];
    this.docLengths = [];
    this.avgdl = 0;
    this.idf = {};
    this.N = 0;
  }

  fit(documents) {
    this.corpus = [];
    this.docLengths = [];
    const docFreqs = {};

    for (const doc of documents) {
      const tokens = tokenize(doc);
      this.corpus.push(tokens);
      this.docLengths.push(tokens.length);

      const seen = new Set(tokens);
      for (const term of seen) {
        docFreqs[term] = (docFreqs[term] || 0) + 1;
      }
    }

    this.N = documents.length;
    this.avgdl =
      this.N > 0
        ? this.docLengths.reduce((a, b) => a + b, 0) / this.N
        : 0;

    this.idf = {};
    for (const [term, df] of Object.entries(docFreqs)) {
      this.idf[term] = Math.log((this.N - df + 0.5) / (df + 0.5) + 1);
    }
  }

  score(query, docIdx) {
    const queryTokens = tokenize(query);
    const docTokens = this.corpus[docIdx];
    const docLen = this.docLengths[docIdx];

    const tf = {};
    for (const t of docTokens) {
      tf[t] = (tf[t] || 0) + 1;
    }

    let s = 0;
    for (const term of queryTokens) {
      if (!(term in this.idf)) continue;
      const freq = tf[term] || 0;
      if (freq === 0) continue;

      const num = this.idf[term] * freq * (this.k1 + 1);
      const den =
        freq + this.k1 * (1 - this.b + (this.b * docLen) / this.avgdl);
      s += num / den;
    }
    return s;
  }

  search(query, topK) {
    const scores = [];
    for (let i = 0; i < this.corpus.length; i++) {
      const s = this.score(query, i);
      if (s > 0) scores.push([i, s]);
    }
    scores.sort((a, b) => b[1] - a[1]);
    return scores.slice(0, topK);
  }
}

function keywordMatchScore(query, agent) {
  const queryTerms = new Set(tokenize(query));
  if (queryTerms.size === 0) return 0;

  let matches = 0;
  let totalWeight = 0;

  // Name (highest weight)
  const nameTerms = new Set(tokenize(agent.name || ""));
  let nameMatches = 0;
  for (const t of queryTerms) {
    if (nameTerms.has(t)) nameMatches++;
  }
  matches += nameMatches * 3;
  totalWeight += queryTerms.size * 3;

  // Keywords (medium weight)
  const agentKeywords = new Set(
    (agent.keywords || []).map((k) => k.toLowerCase())
  );
  let kwMatches = 0;
  for (const t of queryTerms) {
    if (agentKeywords.has(t)) kwMatches++;
  }
  matches += kwMatches * 2;
  totalWeight += queryTerms.size * 2;

  // Summary (lower weight)
  const summaryTerms = new Set(tokenize(agent.summary || ""));
  let sumMatches = 0;
  for (const t of queryTerms) {
    if (summaryTerms.has(t)) sumMatches++;
  }
  matches += sumMatches;
  totalWeight += queryTerms.size;

  // Partial matches in summary
  const summaryLower = (agent.summary || "").toLowerCase();
  for (const term of queryTerms) {
    if (term.length >= 3 && summaryLower.includes(term)) {
      matches += 0.5;
    }
  }

  return totalWeight > 0 ? matches / totalWeight : 0;
}

function _searchCore(query, registry) {
  const agents = registry.agents || [];
  if (agents.length === 0) return [];

  const corpus = agents.map(
    (a) => `${a.name} ${a.summary || ""} ${(a.keywords || []).join(" ")}`
  );

  const bm25 = new BM25();
  bm25.fit(corpus);
  const bm25Results = bm25.search(query, agents.length);

  const bm25Scores = {};
  for (const [idx, score] of bm25Results) {
    bm25Scores[idx] = score;
  }

  // Normalize BM25 scores to 0-1
  const vals = Object.values(bm25Scores);
  const maxBm25 = vals.length > 0 ? Math.max(...vals) : 1;
  if (maxBm25 > 0) {
    for (const idx in bm25Scores) {
      bm25Scores[idx] /= maxBm25;
    }
  }

  const results = [];
  for (let i = 0; i < agents.length; i++) {
    const bm25Score = bm25Scores[i] || 0;
    const kwScore = keywordMatchScore(query, agents[i]);
    const combined = 0.6 * bm25Score + 0.4 * kwScore;

    if (combined > 0.05) {
      results.push({
        name: agents[i].name,
        summary: agents[i].summary,
        score: Math.round(combined * 1000) / 1000,
        bm25_score: Math.round(bm25Score * 1000) / 1000,
        keyword_score: Math.round(kwScore * 1000) / 1000,
        token_estimate: agents[i].token_estimate || 0,
        keywords: (agents[i].keywords || []).slice(0, 5),
      });
    }
  }

  results.sort((a, b) => b.score - a.score);
  return results;
}

function searchAgents(query, registry, topK = 5) {
  return _searchCore(query, registry).slice(0, topK);
}

function searchAgentsAll(query, registry) {
  return _searchCore(query, registry);
}

module.exports = {
  tokenize,
  BM25,
  keywordMatchScore,
  searchAgents,
  searchAgentsAll,
};
