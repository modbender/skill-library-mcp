/**
 * BM25 Retrieval Implementation
 * 
 * Sparse retrieval using Okapi BM25 ranking function.
 * Complements dense (semantic) search with exact term matching.
 */

import type { Memory } from '../storage/index.js';

export interface BM25Options {
  /** BM25 k1 parameter (term frequency saturation) */
  k1?: number;
  /** BM25 b parameter (document length normalization) */
  b?: number;
  /** Average document length for corpus */
  avgDocLen?: number;
}

/**
 * Default BM25 parameters
 */
const DEFAULT_K1 = 1.5;
const DEFAULT_B = 0.75;

/**
 * BM25 Scorer class
 */
export class BM25Scorer {
  private k1: number;
  private b: number;
  private avgDocLen: number;
  private idf: Map<string, number> = new Map();
  private docLengths: Map<string, number> = new Map();
  private docTermFreqs: Map<string, Map<string, number>> = new Map();
  
  constructor(options: BM25Options = {}) {
    this.k1 = options.k1 ?? DEFAULT_K1;
    this.b = options.b ?? DEFAULT_B;
    this.avgDocLen = options.avgDocLen ?? 100; // Default estimate
  }
  
  /**
   * Index a corpus of documents
   */
  index(documents: Memory[]): void {
    const docCount = documents.length;
    const termDocFreq = new Map<string, number>(); // df - document frequency
    
    // First pass: collect document frequencies
    for (const doc of documents) {
      const terms = this.tokenize(doc.content);
      const uniqueTerms = new Set(terms);
      this.docLengths.set(doc.id, terms.length);
      
      // Update average
      if (terms.length > 0) {
        this.avgDocLen = (this.avgDocLen + terms.length) / 2;
      }
      
      // Count document frequency for each unique term
      for (const term of uniqueTerms) {
        termDocFreq.set(term, (termDocFreq.get(term) || 0) + 1);
      }
    }
    
    // Second pass: build term frequency maps
    for (const doc of documents) {
      const terms = this.tokenize(doc.content);
      const termFreqs = new Map<string, number>();
      
      for (const term of terms) {
        termFreqs.set(term, (termFreqs.get(term) || 0) + 1);
      }
      
      this.docTermFreqs.set(doc.id, termFreqs);
    }
    
    // Calculate IDF for each term
    for (const [term, df] of termDocFreq) {
      // IDF using standard BM25 formula
      const idf = Math.log((docCount - df + 0.5) / (df + 0.5) + 1);
      this.idf.set(term, idf);
    }
  }
  
  /**
   * Tokenize text into terms
   */
  private tokenize(text: string): string[] {
    return text
      .toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(term => term.length > 1); // Skip single chars
  }
  
  /**
   * Calculate BM25 score for a single document
   */
  private scoreDocument(query: string, docId: string): number {
    const queryTerms = this.tokenize(query);
    const termFreqs = this.docTermFreqs.get(docId);
    const docLen = this.docLengths.get(docId) || this.avgDocLen;
    
    if (!termFreqs) return 0;
    
    let score = 0;
    
    for (const term of queryTerms) {
      const tf = termFreqs.get(term) || 0;
      const idf = this.idf.get(term) || 0;
      
      // BM25 scoring formula
      const numerator = tf * (this.k1 + 1);
      const denominator = tf + this.k1 * (1 - this.b + this.b * (docLen / this.avgDocLen));
      
      score += idf * (numerator / denominator);
    }
    
    return score;
  }
  
  /**
   * Search documents using BM25
   */
  search(query: string, documents: Memory[], k: number = 10): Memory[] {
    // Re-index if needed (for simplicity, re-index each search)
    // In production, you'd want to cache this
    this.index(documents);
    
    // Score all documents
    const scores = documents.map(doc => ({
      doc,
      score: this.scoreDocument(query, doc.id)
    }));
    
    // Sort by score descending
    scores.sort((a, b) => b.score - a.score);
    
    // Return top k
    return scores.slice(0, k).map(s => ({
      ...s.doc,
      _bm25Score: s.score
    } as Memory & { _bm25Score: number }));
  }
}

/**
 * Simple BM25 search function (convenience wrapper)
 */
export function bm25Search(
  query: string,
  documents: Memory[],
  options: {
    k?: number;
    k1?: number;
    b?: number;
  } = {}
): Memory[] {
  const scorer = new BM25Scorer({
    k1: options.k1,
    b: options.b
  });
  
  return scorer.search(query, documents, options.k || 10);
}
