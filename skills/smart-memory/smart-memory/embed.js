/**
 * Local embeddings using Transformers.js
 * Model: all-MiniLM-L6-v2 (384 dims, ~80MB)
 */

import { pipeline, env } from '@xenova/transformers';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const MODEL_NAME = 'Xenova/all-MiniLM-L6-v2';
const EMBEDDING_DIM = 384;

// Cache directory in workspace
const CACHE_DIR = path.join(process.cwd(), '.cache', 'transformers');
env.cacheDir = CACHE_DIR;

// Lazy-loaded pipeline
let embedder = null;
let modelLoading = false;
let loadPromise = null;

/**
 * Get or create the embedding pipeline
 * @returns {Promise<Object>}
 */
export async function getEmbedder() {
    if (embedder) return embedder;
    if (loadPromise) return loadPromise;
    
    loadPromise = loadModel();
    return loadPromise;
}

async function loadModel() {
    console.error(`Loading embedding model: ${MODEL_NAME}`);
    console.error(`Cache directory: ${CACHE_DIR}`);
    
    try {
        embedder = await pipeline('feature-extraction', MODEL_NAME, {
            quantized: true, // Smaller, faster model
        });
        
        console.error('✓ Model loaded successfully');
        return embedder;
    } catch (err) {
        console.error('✗ Failed to load model:', err.message);
        throw err;
    }
}

/**
 * Get embedding for text
 * @param {string} text - Text to embed
 * @returns {Promise<Float32Array>} - 384-dimensional embedding
 */
export async function getEmbedding(text) {
    const pipe = await getEmbedder();
    
    // Truncate very long text (model has ~512 token limit)
    const truncatedText = text.slice(0, 2000);
    
    const result = await pipe(truncatedText, {
        pooling: 'mean',
        normalize: true,
    });
    
    return result.data; // Float32Array
}

/**
 * Get embeddings for multiple texts (batch processing)
 * @param {string[]} texts - Array of texts
 * @returns {Promise<Float32Array[]>}
 */
export async function getEmbeddings(texts) {
    const embeddings = [];
    
    for (let i = 0; i < texts.length; i++) {
        const emb = await getEmbedding(texts[i]);
        embeddings.push(emb);
        
        // Progress indicator
        if ((i + 1) % 5 === 0 || i === texts.length - 1) {
            process.stderr.write(`. (${i + 1}/${texts.length})\r`);
        }
    }
    
    console.error(); // New line after progress
    return embeddings;
}

/**
 * Get embedding dimension
 * @returns {number}
 */
export function getEmbeddingDimension() {
    return EMBEDDING_DIM;
}

/**
 * Convert embedding to Buffer for SQLite storage
 * @param {Float32Array} embedding
 * @returns {Buffer}
 */
export function embeddingToBuffer(embedding) {
    return Buffer.from(embedding.buffer);
}

/**
 * Convert Buffer back to Float32Array
 * @param {Buffer} buffer
 * @returns {Float32Array}
 */
export function bufferToEmbedding(buffer) {
    return new Float32Array(buffer.buffer, buffer.byteOffset, EMBEDDING_DIM);
}

/**
 * Compute cosine similarity between two embeddings
 * @param {Float32Array} a
 * @param {Float32Array} b
 * @returns {number} - Similarity score 0-1
 */
export function cosineSimilarity(a, b) {
    let dotProduct = 0;
    let normA = 0;
    let normB = 0;
    
    for (let i = 0; i < a.length; i++) {
        dotProduct += a[i] * b[i];
        normA += a[i] * a[i];
        normB += b[i] * b[i];
    }
    
    const denominator = Math.sqrt(normA) * Math.sqrt(normB);
    return denominator === 0 ? 0 : dotProduct / denominator;
}
