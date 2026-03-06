// lib/search.js – Hybrid search: FTS5 keyword + LLM reranking
const { getDb } = require('./db');
const { rerankResults } = require('./extractor');

async function search(query, { limit = 10, rerank = true, tier = 'all' } = {}) {
  const db = getDb();
  let results = [];

  if (tier === 'all' || tier === 'midterm') {
    try {
      const midterm = db.prepare(`
        SELECT ke.*, 'midterm' as tier, rank
        FROM knowledge_fts fts
        JOIN knowledge_entries ke ON ke.id = fts.rowid
        WHERE knowledge_fts MATCH ?
        ORDER BY rank LIMIT ?
      `).all(ftsEscape(query), limit);
      results.push(...midterm);
    } catch { /* empty FTS table */ }
  }

  if (tier === 'all' || tier === 'longterm') {
    try {
      const longterm = db.prepare(`
        SELECT la.*, 'longterm' as tier, rank
        FROM longterm_fts fts
        JOIN longterm_archive la ON la.id = fts.rowid
        WHERE longterm_fts MATCH ?
        ORDER BY rank LIMIT ?
      `).all(ftsEscape(query), limit);
      results.push(...longterm);
    } catch { /* empty FTS table */ }
  }

  // Deduplicate
  const seen = new Set();
  results = results.filter(r => {
    const key = r.knowledge_id ? `k-${r.knowledge_id}` : `${r.tier}-${r.id}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });

  // LLM semantic reranking
  if (rerank && results.length > 3) {
    results = await rerankResults(query, results);
  }

  return results.slice(0, limit);
}

function ftsEscape(query) {
  return query
    .replace(/[^\w\säöüÄÖÜß-]/g, ' ')
    .split(/\s+/)
    .filter(w => w.length > 1)
    .map(w => `"${w}"`)
    .join(' OR ');
}

function findSimilarEntry(db, entry) {
  const exact = db.prepare(
    'SELECT * FROM knowledge_entries WHERE title = ? AND status != ?'
  ).get(entry.title, 'obsolete');
  if (exact) return exact;

  const searchTerms = [entry.title, ...(entry.tags || [])].join(' ');
  try {
    const fuzzy = db.prepare(`
      SELECT ke.*, rank FROM knowledge_fts fts
      JOIN knowledge_entries ke ON ke.id = fts.rowid
      WHERE knowledge_fts MATCH ? AND ke.category = ?
      ORDER BY rank LIMIT 1
    `).get(ftsEscape(searchTerms), entry.category);
    if (fuzzy && fuzzy.rank > -5) return fuzzy;
  } catch {}
  return null;
}

module.exports = { search, findSimilarEntry, ftsEscape };
