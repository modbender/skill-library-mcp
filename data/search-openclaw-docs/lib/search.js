/**
 * FTS5 Keyword Search
 * Returns file paths ranked by relevance
 */

const fs = require('fs');

/**
 * Build FTS5 query from natural language
 */
function buildFtsQuery(query) {
  const terms = query
    .toLowerCase()
    .replace(/[^\w\s]/g, ' ')
    .split(/\s+/)
    .filter(t => t.length > 1)
    .filter(t => !['the', 'a', 'an', 'is', 'are', 'how', 'do', 'i', 'to', 'in', 'on', 'for', 'what', 'why'].includes(t));
  
  if (terms.length === 0) return null;
  
  return terms.map(t => `"${t}"*`).join(' OR ');
}

/**
 * Search docs using FTS5
 */
async function search(indexPath, query, options = {}) {
  const { topK = 3, candidateMultiplier = 5 } = options;
  
  if (!fs.existsSync(indexPath)) {
    throw new Error('Index not found. Run: node docs-index.js rebuild');
  }
  
  const Database = require('better-sqlite3');
  const db = new Database(indexPath, { readonly: true });
  
  const ftsQuery = buildFtsQuery(query);
  let candidates = [];
  
  if (ftsQuery) {
    try {
      candidates = db.prepare(`
        SELECT 
          f.id,
          f.path,
          f.rel_path as rel_path,
          f.title,
          f.headers,
          f.keywords,
          f.summary,
          bm25(files_fts, 2.0, 3.0, 2.0, 1.5, 1.0) as bm25_score
        FROM files_fts
        INNER JOIN files f ON files_fts.rowid = f.id
        WHERE files_fts MATCH ?
        ORDER BY bm25_score ASC
        LIMIT ?
      `).all(ftsQuery, topK * candidateMultiplier);
    } catch (e) {
      candidates = [];
    }
  }
  
  // If FTS returns few results, add more from all files
  if (candidates.length < topK * 2) {
    const allFiles = db.prepare(`
      SELECT id, path, rel_path, title, headers, keywords, summary
      FROM files
      WHERE id NOT IN (${candidates.map(c => c.id).join(',') || '0'})
      LIMIT ?
    `).all(topK * candidateMultiplier - candidates.length);
    
    candidates = [...candidates, ...allFiles.map(f => ({ ...f, bm25_score: 0 }))];
  }
  
  const results = candidates.map(candidate => {
    // Normalize BM25: more negative = better match
    const score = candidate.bm25_score 
      ? Math.min(1, Math.max(0, -candidate.bm25_score / 10))
      : 0;
    
    const queryTerms = query.toLowerCase().split(/\s+/);
    const matchedKeywords = (candidate.keywords || '').split(' ')
      .filter(k => queryTerms.some(qt => k.includes(qt) || qt.includes(k)))
      .slice(0, 5);
    
    return {
      path: candidate.path,
      relPath: candidate.rel_path,
      title: candidate.title,
      summary: candidate.summary,
      matchedKeywords,
      score
    };
  });
  
  results.sort((a, b) => b.score - a.score);
  db.close();
  
  return results.slice(0, topK);
}

/**
 * Format search results for display
 */
function formatResults(results, query) {
  const lines = [];
  
  lines.push(`🔍 Query: ${query}\n`);
  
  if (results.length === 0) {
    lines.push('❌ No matching docs found');
    return lines.join('\n');
  }
  
  const best = results[0];
  lines.push(`🎯 Best match:`);
  lines.push(`   ${best.relPath}`);
  if (best.title) lines.push(`   "${best.title}"`);
  if (best.matchedKeywords.length > 0) {
    lines.push(`   Keywords: ${best.matchedKeywords.join(', ')}`);
  }
  lines.push(`   Score: ${best.score.toFixed(2)}`);
  lines.push('');
  
  if (results.length > 1) {
    lines.push(`📄 Also relevant:`);
    for (const result of results.slice(1)) {
      lines.push(`   ${result.relPath} (${result.score.toFixed(2)})`);
      if (result.matchedKeywords.length > 0) {
        lines.push(`      Keywords: ${result.matchedKeywords.join(', ')}`);
      }
    }
    lines.push('');
  }
  
  lines.push(`💡 Read with:`);
  lines.push(`   cat ${best.path}`);
  
  return lines.join('\n');
}

module.exports = {
  search,
  formatResults,
  buildFtsQuery
};
