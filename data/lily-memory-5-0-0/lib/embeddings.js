import { randomUUID } from "node:crypto";
import { sqliteQuery, sqliteExec, escapeSqlValue } from "./sqlite.js";

// ============================================================================
// Cosine similarity
// ============================================================================

/**
 * Cosine similarity between two vectors. Returns 0 on invalid input.
 * @param {number[]} a
 * @param {number[]} b
 * @returns {number}
 */
export function cosineSimilarity(a, b) {
  if (!a || !b || a.length === 0 || b.length === 0 || a.length !== b.length) return 0;
  let dot = 0, normA = 0, normB = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  const denom = Math.sqrt(normA) * Math.sqrt(normB);
  return denom === 0 ? 0 : dot / denom;
}

// ============================================================================
// Ollama embedding
// ============================================================================

/**
 * Get an embedding vector from Ollama. Returns float[] or null.
 * @param {string} ollamaUrl - Base URL e.g. "http://localhost:11434"
 * @param {string} model - Embedding model name
 * @param {string} text - Text to embed
 * @returns {Promise<number[]|null>}
 */
export async function generateEmbedding(ollamaUrl, model, text) {
  try {
    const res = await fetch(`${ollamaUrl}/api/embeddings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model, prompt: text }),
      signal: AbortSignal.timeout(10000),
    });
    if (!res.ok) return null;
    const data = await res.json();
    return data.embedding || null;
  } catch {
    return null;
  }
}

/**
 * Check if Ollama embedding is available for the given model.
 * @param {string} ollamaUrl - Base URL e.g. "http://localhost:11434"
 * @param {string} model - Embedding model name
 * @returns {Promise<{ available: boolean, dimensions?: number, reason?: string }>}
 */
export async function checkOllamaHealth(ollamaUrl, model) {
  try {
    const res = await fetch(`${ollamaUrl}/api/embeddings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model, prompt: "health check" }),
      signal: AbortSignal.timeout(10000),
    });
    if (!res.ok) return { available: false, reason: `HTTP ${res.status}` };
    const data = await res.json();
    if (data.embedding && data.embedding.length > 0) {
      return { available: true, dimensions: data.embedding.length };
    }
    return { available: false, reason: "empty embedding response" };
  } catch (err) {
    return { available: false, reason: String(err?.message || err) };
  }
}

// ============================================================================
// DB helpers
// ============================================================================

/**
 * Ensure the vectors table exists. Thin wrapper for backward compatibility;
 * ensureTables() in sqlite.js already creates this table.
 * @param {string} dbPath
 * @returns {boolean}
 */
export function ensureVectorsTable(dbPath) {
  return sqliteExec(dbPath, `
    CREATE TABLE IF NOT EXISTS vectors (
      id TEXT PRIMARY KEY,
      decision_id TEXT NOT NULL,
      text_content TEXT NOT NULL,
      embedding TEXT NOT NULL,
      model TEXT NOT NULL,
      created_at INTEGER NOT NULL
    )
  `);
}

/**
 * Generate and store an embedding for a decision.
 * @param {string} dbPath
 * @param {string} ollamaUrl
 * @param {string} model
 * @param {string} decisionId
 * @param {string} text
 * @returns {Promise<boolean>}
 */
export async function storeEmbedding(dbPath, ollamaUrl, model, decisionId, text) {
  const embedding = await generateEmbedding(ollamaUrl, model, text);
  if (!embedding) return false;

  const id = randomUUID();
  const safeText = escapeSqlValue(text);
  const safeDecisionId = escapeSqlValue(decisionId);
  const safeModel = escapeSqlValue(model);
  // Embeddings are compact numeric JSON — no truncation, only quote-escape.
  const embJson = JSON.stringify(embedding).replace(/'/g, "''");

  return sqliteExec(dbPath, `
    INSERT OR REPLACE INTO vectors (id, decision_id, text_content, embedding, model, created_at)
    VALUES ('${id}', '${safeDecisionId}', '${safeText}', '${embJson}', '${safeModel}', ${Date.now()})
  `);
}

/**
 * Search vectors by semantic similarity. Returns scored results sorted by similarity.
 * @param {string} dbPath
 * @param {string} ollamaUrl
 * @param {string} model
 * @param {string} query
 * @param {number} limit
 * @param {number} threshold - Minimum similarity score (0-1)
 * @returns {Promise<Array>}
 */
export async function vectorSearch(dbPath, ollamaUrl, model, query, limit, threshold) {
  const queryEmb = await generateEmbedding(ollamaUrl, model, query);
  if (!queryEmb) return [];

  const rows = sqliteQuery(dbPath, `
    SELECT v.decision_id, v.embedding,
           d.entity, d.fact_key, d.fact_value, d.description, d.category
    FROM vectors v
    JOIN decisions d ON v.decision_id = d.id
    WHERE d.expires_at IS NULL OR d.expires_at > ${Date.now()}
  `);

  const scored = [];
  for (const row of rows) {
    let emb;
    try { emb = JSON.parse(row.embedding); } catch { continue; }
    const sim = cosineSimilarity(queryEmb, emb);
    if (sim >= threshold) {
      scored.push({ ...row, similarity: sim, embedding: undefined });
    }
  }

  scored.sort((a, b) => b.similarity - a.similarity);
  return scored.slice(0, limit);
}

/**
 * Backfill embeddings for decisions that don't have vectors yet.
 * @param {string} dbPath
 * @param {string} ollamaUrl
 * @param {string} model
 * @param {{ info?: Function }} logger
 * @returns {Promise<number>} Count of embeddings created
 */
export async function backfillEmbeddings(dbPath, ollamaUrl, model, logger) {
  const unembedded = sqliteQuery(dbPath, `
    SELECT d.id, d.entity, d.fact_key, d.fact_value, d.description
    FROM decisions d
    LEFT JOIN vectors v ON d.id = v.decision_id
    WHERE v.id IS NULL
      AND (d.expires_at IS NULL OR d.expires_at > ${Date.now()})
    ORDER BY d.importance DESC
    LIMIT 200
  `);

  if (unembedded.length === 0) {
    logger.info?.("lily-memory: all decisions have embeddings");
    return 0;
  }

  logger.info?.(`lily-memory: backfilling embeddings for ${unembedded.length} decisions...`);
  let count = 0;

  for (const row of unembedded) {
    const text = row.entity && row.fact_key
      ? `${row.entity}.${row.fact_key} = ${row.fact_value}`
      : row.description || "";

    if (text.length < 5) continue;

    const ok = await storeEmbedding(dbPath, ollamaUrl, model, row.id, text);
    if (ok) count++;

    // Small delay to avoid hammering Ollama
    await new Promise(r => setTimeout(r, 50));
  }

  logger.info?.(`lily-memory: backfilled ${count}/${unembedded.length} embeddings`);
  return count;
}
