/**
 * Hybrid search combining FTS5 (keyword) and vector similarity
 */

import {
    searchVectorKNN,
    searchFTS,
    getAllChunksWithEmbeddings,
    isSqliteVecAvailable,
} from './db.js';
import { cosineSimilarity } from './embed.js';

// Default weights for hybrid scoring
const VECTOR_WEIGHT = 0.7;
const TEXT_WEIGHT = 0.3;
const CANDIDATE_MULTIPLIER = 4;

/**
 * Perform hybrid search (BM25 + vector)
 * @param {Database} db
 * @param {string} query - Search query text
 * @param {Float32Array} queryEmbedding - Query embedding vector
 * @param {Object} options
 * @returns {Array} - Ranked results
 */
export function hybridSearch(db, query, queryEmbedding, options = {}) {
    const {
        maxResults = 5,
        vectorWeight = VECTOR_WEIGHT,
        textWeight = TEXT_WEIGHT,
    } = options;
    
    const candidateLimit = maxResults * CANDIDATE_MULTIPLIER;
    
    // Gather candidates from both sources
    const vectorCandidates = getVectorCandidates(db, queryEmbedding, candidateLimit);
    const textCandidates = getTextCandidates(db, query, candidateLimit);
    
    // Merge and score candidates
    const merged = mergeCandidates(vectorCandidates, textCandidates, vectorWeight, textWeight);
    
    // Return top results
    return merged.slice(0, maxResults);
}

/**
 * Get vector similarity candidates
 */
function getVectorCandidates(db, queryEmbedding, limit) {
    if (isSqliteVecAvailable()) {
        // Use native sqlite-vec KNN search
        const results = searchVectorKNN(db, queryEmbedding, limit);
        
        return results.map(r => ({
            id: r.id,
            path: r.path,
            startLine: r.start_line,
            endLine: r.end_line,
            content: r.content,
            vectorScore: 1 - (r.vec_distance / 2), // Convert distance to similarity (approximate)
            textScore: null,
        }));
    } else {
        // Fall back to JS cosine similarity
        const allChunks = getAllChunksWithEmbeddings(db);
        
        const scored = allChunks.map(chunk => {
            const embedding = new Float32Array(chunk.embedding.buffer, chunk.embedding.byteOffset, 384);
            return {
                id: chunk.id,
                path: chunk.path,
                startLine: chunk.start_line,
                endLine: chunk.end_line,
                content: chunk.content,
                vectorScore: cosineSimilarity(queryEmbedding, embedding),
                textScore: null,
            };
        });
        
        return scored
            .filter(c => c.vectorScore > 0.3)
            .sort((a, b) => b.vectorScore - a.vectorScore)
            .slice(0, limit);
    }
}

/**
 * Get FTS5 text search candidates
 */
function getTextCandidates(db, query, limit) {
    const results = searchFTS(db, query, limit);
    
    return results.map(r => {
        // Convert BM25 rank to 0-1 score (lower rank is better)
        // BM25 ranks are negative, smaller absolute value = better
        const rank = Math.abs(r.fts_rank);
        const textScore = 1 / (1 + rank);
        
        return {
            id: r.id,
            path: r.path,
            startLine: r.start_line,
            endLine: r.end_line,
            content: r.content,
            vectorScore: null,
            textScore,
        };
    });
}

/**
 * Merge candidates from both sources and compute hybrid scores
 */
function mergeCandidates(vectorCandidates, textCandidates, vectorWeight, textWeight) {
    const candidateMap = new Map();
    
    // Normalize weights
    const totalWeight = vectorWeight + textWeight;
    const normVectorWeight = vectorWeight / totalWeight;
    const normTextWeight = textWeight / totalWeight;
    
    // Add vector candidates
    for (const c of vectorCandidates) {
        candidateMap.set(c.id, { ...c });
    }
    
    // Merge text candidates
    for (const c of textCandidates) {
        const existing = candidateMap.get(c.id);
        if (existing) {
            existing.textScore = c.textScore;
        } else {
            candidateMap.set(c.id, { ...c });
        }
    }
    
    // Compute hybrid scores
    const merged = Array.from(candidateMap.values()).map(c => {
        const vScore = c.vectorScore ?? 0;
        const tScore = c.textScore ?? 0;
        
        // If one score is missing, boost the other
        let hybridScore;
        if (c.vectorScore === null) {
            hybridScore = tScore;
        } else if (c.textScore === null) {
            hybridScore = vScore;
        } else {
            hybridScore = (normVectorWeight * vScore) + (normTextWeight * tScore);
        }
        
        return {
            ...c,
            hybridScore,
        };
    });
    
    // Sort by hybrid score
    return merged.sort((a, b) => b.hybridScore - a.hybridScore);
}

/**
 * Pure vector search (fallback when FTS5 unavailable)
 * @param {Database} db
 * @param {Float32Array} queryEmbedding
 * @param {number} maxResults
 * @returns {Array}
 */
export function vectorSearch(db, queryEmbedding, maxResults = 5) {
    const candidates = getVectorCandidates(db, queryEmbedding, maxResults);
    
    return candidates.map(c => ({
        ...c,
        hybridScore: c.vectorScore,
    }));
}

/**
 * Pure text search (fallback when embeddings unavailable)
 * @param {Database} db
 * @param {string} query
 * @param {number} maxResults
 * @returns {Array}
 */
export function textSearch(db, query, maxResults = 5) {
    const candidates = getTextCandidates(db, query, maxResults);
    
    return candidates.map(c => ({
        ...c,
        hybridScore: c.textScore,
    }));
}
