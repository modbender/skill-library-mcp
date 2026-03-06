#!/usr/bin/env node
/**
 * Focus Agent - Context Curation System
 * 
 * Multi-pass retrieval for high-quality context:
 *   1. Retrieve: Broad fetch from vector DB (20+ chunks)
 *   2. Rank: Score relevance to query using embeddings
 *   3. Synthesize: Rewrite selected chunks into coherent narrative
 * 
 * Usage:
 *   node focus_agent.js --search "query" [--max-results 5]
 */

import path from 'path';
import { fileURLToPath } from 'url';
import { initDatabase } from './db.js';
import { getEmbedding, cosineSimilarity } from './embed.js';
import { vectorSearch } from './search.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DB_PATH = process.env.MEMORY_DB_PATH || path.join(__dirname, 'vector-memory.db');

/**
 * Configuration for focus curation
 */
const FOCUS_CONFIG = {
    retrievalCount: 20,      // How many chunks to retrieve initially
    selectionCount: 5,       // How many to keep after ranking
    synthesisMaxTokens: 1500, // Max length of synthesized context
    relevanceThreshold: 0.3,  // Minimum similarity score to keep
};

/**
 * Calculate weighted relevance score for a chunk
 * Combines vector similarity with structural signals
 * 
 * @param {Object} chunk - The chunk with vector score
 * @param {Float32Array} queryEmbedding - Query embedding
 * @param {string} query - Original query text
 * @returns {number} - Weighted relevance score (0-1)
 */
function calculateRelevance(chunk, queryEmbedding, query) {
    // Base: Vector similarity (already calculated)
    let score = chunk.vectorScore || chunk.score || chunk.hybridScore || 0;
    
    // Boost: Query terms appear in content
    const queryTerms = query.toLowerCase().split(/\s+/);
    const contentLower = chunk.content.toLowerCase();
    const termMatches = queryTerms.filter(term => contentLower.includes(term)).length;
    const termBoost = (termMatches / queryTerms.length) * 0.15;
    
    // Boost: Content from structured files (MEMORY.md, decisions, etc.)
    const pathLower = chunk.path.toLowerCase();
    let sourceBoost = 0;
    if (pathLower.includes('memory.md')) sourceBoost = 0.1;
    else if (pathLower.includes('decision')) sourceBoost = 0.08;
    else if (pathLower.includes('project')) sourceBoost = 0.05;
    
    // Boost: Recency (if date in filename)
    const dateMatch = pathLower.match(/(\d{4})-(\d{2})-(\d{2})/);
    if (dateMatch) {
        const fileDate = new Date(`${dateMatch[1]}-${dateMatch[2]}-${dateMatch[3]}`);
        const daysAgo = (Date.now() - fileDate.getTime()) / (1000 * 60 * 60 * 24);
        if (daysAgo < 7) sourceBoost += 0.05;  // Within a week
        else if (daysAgo < 30) sourceBoost += 0.02;  // Within a month
    }
    
    return Math.min(1, score + termBoost + sourceBoost);
}

/**
 * Rank chunks by relevance and select top N
 * 
 * @param {Array} chunks - Retrieved chunks
 * @param {Float32Array} queryEmbedding - Query embedding
 * @param {string} query - Original query
 * @returns {Array} - Ranked and selected chunks
 */
function rankAndSelect(chunks, queryEmbedding, query) {
    // Calculate weighted scores
    const scored = chunks.map(chunk => ({
        ...chunk,
        weightedScore: calculateRelevance(chunk, queryEmbedding, query)
    }));
    
    // Sort by weighted score descending
    scored.sort((a, b) => b.weightedScore - a.weightedScore);
    
    // Filter by threshold and take top N
    const selected = scored
        .filter(c => c.weightedScore >= FOCUS_CONFIG.relevanceThreshold)
        .slice(0, FOCUS_CONFIG.selectionCount);
    
    return selected;
}

/**
 * Synthesize selected chunks into coherent narrative
 * 
 * This is a lightweight synthesis that structures the context
 * for the main agent. Can be enhanced with LLM-based synthesis.
 * 
 * @param {Array} selectedChunks - Top-ranked chunks
 * @param {string} query - Original query
 * @returns {Object} - Synthesized context
 */
function synthesizeContext(selectedChunks, query) {
    if (selectedChunks.length === 0) {
        return {
            facts: [],
            synthesis: "No relevant memories found for this query.",
            confidence: 0,
            sources: []
        };
    }
    
    // Group by source file for narrative flow
    const bySource = {};
    for (const chunk of selectedChunks) {
        if (!bySource[chunk.path]) {
            bySource[chunk.path] = [];
        }
        bySource[chunk.path].push(chunk);
    }
    
    // Build synthesis
    const facts = selectedChunks.map(c => ({
        content: c.content.slice(0, 300).replace(/\n/g, ' ').trim(),
        source: c.path,
        lines: `${c.startLine}-${c.endLine}`,
        confidence: Math.round(c.weightedScore * 100) / 100
    }));
    
    // Generate narrative synthesis
    let synthesis = `Relevant context for: "${query}"\n\n`;
    
    for (const [path, chunks] of Object.entries(bySource)) {
        synthesis += `From ${path}:\n`;
        for (const chunk of chunks) {
            const content = chunk.content.slice(0, 250).replace(/\n/g, ' ').trim();
            synthesis += `  • ${content}${chunk.content.length > 250 ? '...' : ''}\n`;
        }
        synthesis += '\n';
    }
    
    // Calculate overall confidence
    const avgConfidence = selectedChunks.reduce((sum, c) => sum + c.weightedScore, 0) / selectedChunks.length;
    
    return {
        facts,
        synthesis: synthesis.trim(),
        confidence: Math.round(avgConfidence * 100) / 100,
        sources: Object.keys(bySource),
        chunkCount: selectedChunks.length
    };
}

/**
 * Perform focused search with curation
 * 
 * @param {string} query - Search query
 * @param {Object} options - Search options
 * @returns {Object} - Curated results with synthesis
 */
export async function focusSearch(query, options = {}) {
    const config = { ...FOCUS_CONFIG, ...options };
    
    console.error(`[Focus Mode] Searching: "${query}"`);
    
    // Step 1: Retrieve broad set
    const db = initDatabase(DB_PATH);
    const queryEmbedding = await getEmbedding(query);
    
    console.error(`[Focus Mode] Retrieving ${config.retrievalCount} chunks...`);
    const rawResults = vectorSearch(db, queryEmbedding, config.retrievalCount);
    
    if (rawResults.length === 0) {
        db.close();
        return synthesizeContext([], query);
    }
    
    console.error(`[Focus Mode] Retrieved ${rawResults.length} chunks, ranking...`);
    
    // Step 2: Rank and select
    const selected = rankAndSelect(rawResults, queryEmbedding, query);
    console.error(`[Focus Mode] Selected ${selected.length} chunks above threshold`);
    
    // Step 3: Synthesize
    const result = synthesizeContext(selected, query);
    
    db.close();
    
    console.error(`[Focus Mode] Confidence: ${result.confidence}, Sources: ${result.sources.join(', ')}`);
    
    return result;
}

/**
 * Quick check if focus mode should be suggested
 * Based on query complexity signals
 * 
 * @param {string} query - Search query
 * @returns {boolean} - Whether focus mode is recommended
 */
export function shouldSuggestFocus(query) {
    const complexitySignals = [
        /\b(decide|decision|choose|plan|strategy)\b/i,
        /\b(compare|contrast|difference between|versus|vs)\b/i,
        /\b(why|how should|what if|pros and cons)\b/i,
        /\b(summarize|overview|explain)\b/i,
        /\b(project|initiative|goal|objective)\b/i,
    ];
    
    const queryLower = query.toLowerCase();
    const signalCount = complexitySignals.filter(pattern => pattern.test(queryLower)).length;
    
    // Also check query length (longer = more complex)
    const wordCount = query.split(/\s+/).length;
    
    return signalCount >= 2 || wordCount > 10;
}

/**
 * CLI handler
 */
async function main() {
    const args = process.argv.slice(2);
    const command = args[0];
    
    switch (command) {
        case '--search': {
            const query = args[1];
            if (!query) {
                console.error('Usage: --search "query" [--max-results N]');
                process.exit(1);
            }
            
            const maxResultsIdx = args.indexOf('--max-results');
            const maxResults = maxResultsIdx >= 0 
                ? parseInt(args[maxResultsIdx + 1]) || 5
                : 5;
            
            const result = await focusSearch(query, { selectionCount: maxResults });
            console.log(JSON.stringify(result, null, 2));
            break;
        }
        
        case '--suggest': {
            const query = args[1];
            if (!query) {
                console.error('Usage: --suggest "query"');
                process.exit(1);
            }
            
            const suggest = shouldSuggestFocus(query);
            console.log(JSON.stringify({ 
                query, 
                suggestFocus: suggest,
                reason: suggest 
                    ? 'Query complexity signals detected' 
                    : 'Standard query, fast mode sufficient'
            }, null, 2));
            break;
        }
            
        default:
            console.log(`
Focus Agent - Context Curation System

Performs multi-pass retrieval for high-quality context:
  1. Retrieve: Broad fetch (${FOCUS_CONFIG.retrievalCount} chunks)
  2. Rank: Weighted relevance scoring
  3. Synthesize: Coherent narrative output

Usage:
  node focus_agent.js --search "query" [--max-results 5]
    Perform focused search with curation

  node focus_agent.js --suggest "query"
    Check if focus mode is recommended for query

Configuration (environment variables):
  MEMORY_DB_PATH  - Path to SQLite database

Focus mode is ideal for:
  - Complex decisions
  - Multi-fact queries
  - Planning and strategy
  - Comparing options
  - Summarizing project context
`);
    }
}

// Only run main if this file is executed directly (not imported)
if (import.meta.url === `file://${process.argv[1]}`) {
    main().catch(err => {
        console.error('Error:', err.message);
        process.exit(1);
    });
}
