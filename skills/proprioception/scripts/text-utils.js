/**
 * TEXT UTILITIES
 * Lightweight NLP primitives for proprioceptive analysis.
 * Zero dependencies — pure string math.
 */

// ---------------------------------------------------------------------------
// Tokenisation
// ---------------------------------------------------------------------------

/**
 * Simple whitespace + punctuation tokeniser.
 * Lowercases, strips common punctuation, removes empty tokens.
 */
function tokenize(text) {
  return text
    .toLowerCase()
    .replace(/[^\w\s'-]/g, " ")
    .split(/\s+/)
    .filter((t) => t.length > 0);
}

// ---------------------------------------------------------------------------
// Stop-word set (lightweight — covers the 80/20)
// ---------------------------------------------------------------------------

const STOP_WORDS = new Set([
  "a","an","the","and","or","but","in","on","at","to","for","of","with",
  "by","from","is","it","its","this","that","was","are","were","be","been",
  "being","have","has","had","do","does","did","will","would","shall",
  "should","may","might","can","could","i","you","he","she","we","they",
  "me","him","her","us","them","my","your","his","our","their","what",
  "which","who","whom","when","where","why","how","not","no","nor","so",
  "if","then","than","too","very","just","about","up","out","into","over",
]);

function removeStopWords(tokens) {
  return tokens.filter((t) => !STOP_WORDS.has(t));
}

// ---------------------------------------------------------------------------
// Jaccard similarity
// ---------------------------------------------------------------------------

function jaccardSimilarity(tokensA, tokensB) {
  const setA = new Set(tokensA);
  const setB = new Set(tokensB);
  const intersection = new Set([...setA].filter((x) => setB.has(x)));
  const union = new Set([...setA, ...setB]);
  if (union.size === 0) return 0;
  return intersection.size / union.size;
}

// ---------------------------------------------------------------------------
// Cosine similarity on term-frequency vectors
// ---------------------------------------------------------------------------

function termFrequencyVector(tokens) {
  const freq = {};
  for (const t of tokens) {
    freq[t] = (freq[t] || 0) + 1;
  }
  return freq;
}

function cosineSimilarity(tokensA, tokensB) {
  const vecA = termFrequencyVector(tokensA);
  const vecB = termFrequencyVector(tokensB);
  const allTerms = new Set([...Object.keys(vecA), ...Object.keys(vecB)]);

  let dot = 0;
  let magA = 0;
  let magB = 0;

  for (const term of allTerms) {
    const a = vecA[term] || 0;
    const b = vecB[term] || 0;
    dot += a * b;
    magA += a * a;
    magB += b * b;
  }

  if (magA === 0 || magB === 0) return 0;
  return dot / (Math.sqrt(magA) * Math.sqrt(magB));
}

// ---------------------------------------------------------------------------
// Semantic content tokens (stop-words removed, meaningful terms only)
// ---------------------------------------------------------------------------

function semanticTokens(text) {
  return removeStopWords(tokenize(text));
}

// ---------------------------------------------------------------------------
// Sentence splitter (rough but good enough for heuristic analysis)
// ---------------------------------------------------------------------------

function splitSentences(text) {
  return text
    .split(/(?<=[.!?])\s+/)
    .map((s) => s.trim())
    .filter((s) => s.length > 0);
}

// ---------------------------------------------------------------------------
// N-gram generator
// ---------------------------------------------------------------------------

function ngrams(tokens, n) {
  const result = [];
  for (let i = 0; i <= tokens.length - n; i++) {
    result.push(tokens.slice(i, i + n).join(" "));
  }
  return result;
}

// ---------------------------------------------------------------------------
// Pattern frequency counter
// ---------------------------------------------------------------------------

function countPatterns(text, patterns) {
  const lower = text.toLowerCase();
  let count = 0;
  for (const p of patterns) {
    const regex = new RegExp(p, "gi");
    const matches = lower.match(regex);
    if (matches) count += matches.length;
  }
  return count;
}

// ---------------------------------------------------------------------------
// Word count
// ---------------------------------------------------------------------------

function wordCount(text) {
  return tokenize(text).length;
}

// ---------------------------------------------------------------------------
// Lexical diversity (type-token ratio)
// ---------------------------------------------------------------------------

function lexicalDiversity(text) {
  const tokens = tokenize(text);
  if (tokens.length === 0) return 0;
  const types = new Set(tokens);
  return types.size / tokens.length;
}

module.exports = {
  tokenize,
  removeStopWords,
  jaccardSimilarity,
  cosineSimilarity,
  semanticTokens,
  splitSentences,
  ngrams,
  countPatterns,
  wordCount,
  lexicalDiversity,
  termFrequencyVector,
};
