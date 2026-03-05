/**
 * Indexer Module
 *
 * Manages full-text search index using MiniSearch (pure JS, no native deps).
 * Core library for the Curated Search skill.
 *
 * Features:
 * - BM25 ranked full-text search
 * - Domain-filtered queries
 * - JSON persistence
 * - URL validation and normalization
 * - Document excerpt generation
 */

const MiniSearch = require('minisearch');
const path = require('path');
const fs = require('fs');

class Indexer {
  /**
   * Create a new Indexer instance
   * @param {Object} config - Configuration object
   * @param {string} config.path - Path to index files (without extension)
   */
  constructor(config) {
    if (!config || !config.path) {
      throw new Error('Indexer requires config.path');
    }
    
    this.config = config;
    this.indexPath = path.resolve(config.path + '.json');
    this.docsPath = path.resolve(config.path + '-docs.json');
    this.index = null;
    this.documents = new Map(); // url -> full document
    this.pendingSaves = 0;
    
    // Ensure data directory exists
    const dbDir = path.dirname(this.indexPath);
    if (!fs.existsSync(dbDir)) {
      fs.mkdirSync(dbDir, { recursive: true });
    }
  }

  /**
   * Initialize or load existing index from disk
   * @returns {boolean} True if loaded existing index, false if created new
   */
  open() {
    // Try to load existing index
    if (fs.existsSync(this.indexPath) && fs.existsSync(this.docsPath)) {
      try {
        const indexData = fs.readFileSync(this.indexPath, 'utf8');
        const indexObj = JSON.parse(indexData);
        
        // Load with same options used to create
        this.index = MiniSearch.loadJSON(indexData, {
          fields: ['title', 'content', 'domain'],
          storeFields: ['url', 'title', 'domain', 'excerpt', 'crawled_at', 'depth'],
          idField: 'url'
        });
        
        const docsData = fs.readFileSync(this.docsPath, 'utf8');
        const docsArray = JSON.parse(docsData);
        
        this.documents.clear();
        for (const doc of docsArray) {
          if (this._validateDocument(doc)) {
            this.documents.set(doc.url, doc);
          }
        }
        
        console.error(`[Indexer] Loaded ${this.documents.size} documents from ${this.indexPath}`);
        return true;
      } catch (e) {
        console.error(`[Indexer] Failed to load index: ${e.message}`);
        console.error('[Indexer] Starting with fresh index');
        this._createNewIndex();
        return false;
      }
    } else {
      this._createNewIndex();
      return false;
    }
  }

  /**
   * Create a fresh empty index
   * @private
   */
  _createNewIndex() {
    this.index = new MiniSearch({
      fields: ['title', 'content', 'domain'],
      storeFields: ['url', 'title', 'domain', 'excerpt', 'crawled_at', 'depth'],
      idField: 'url'
    });
    this.documents = new Map();
  }

  /**
   * Validate a document object
   * @private
   * @param {Object} doc - Document to validate
   * @returns {boolean} True if valid
   */
  _validateDocument(doc) {
    if (!doc || typeof doc !== 'object') return false;
    if (!doc.url || typeof doc.url !== 'string') return false;
    if (!doc.title || typeof doc.title !== 'string') return false;
    return true;
  }

  /**
   * Normalize and validate a URL
   * @private
   * @param {string} url - URL to normalize
   * @returns {string|null} Normalized URL or null if invalid
   */
  _normalizeUrl(url) {
    try {
      // Parse and reconstruct to normalize
      const parsed = new URL(url);
      
      // Remove fragment (hash)
      parsed.hash = '';
      
      // Normalize trailing slash
      let pathname = parsed.pathname;
      if (pathname.length > 1 && pathname.endsWith('/')) {
        parsed.pathname = pathname.slice(0, -1);
      }
      
      // Remove default ports
      if (parsed.port === '80' && parsed.protocol === 'http:') parsed.port = '';
      if (parsed.port === '443' && parsed.protocol === 'https:') parsed.port = '';
      
      return parsed.toString();
    } catch (e) {
      return null;
    }
  }

  /**
   * Generate excerpt from content
   * @private
   * @param {string} content - Full content
   * @param {number} maxLength - Maximum excerpt length (default 200)
   * @returns {string} Truncated excerpt
   */
  _createExcerpt(content, maxLength = 200) {
    if (!content || typeof content !== 'string') return '';
    if (content.length <= maxLength) return content;
    return content.substring(0, maxLength).trim() + '...';
  }

  /**
   * Add or update a single document
   * @param {Object} doc - Document to add
   * @param {string} doc.url - Document URL (required)
   * @param {string} doc.title - Document title (required)
   * @param {string} doc.content - Full text content
   * @param {string} doc.domain - Domain name
   * @param {number} doc.depth - Crawl depth
   * @returns {Object} The indexed document
   */
  addDocument(doc) {
    if (!doc || typeof doc !== 'object') {
      throw new Error('addDocument requires a document object');
    }
    
    // Validate and normalize URL
    const normalizedUrl = this._normalizeUrl(doc.url);
    if (!normalizedUrl) {
      throw new Error(`Invalid URL: ${doc.url}`);
    }
    
    if (!doc.title || typeof doc.title !== 'string' || doc.title.trim().length === 0) {
      throw new Error('Document must have a non-empty title');
    }
    
    // Build the document
    const content = doc.content || '';
    const document = {
      id: normalizedUrl,   // Provide explicit id for MiniSearch compatibility
      url: normalizedUrl,
      title: doc.title.trim(),
      content: content,
      excerpt: doc.excerpt || this._createExcerpt(content),
      domain: doc.domain || new URL(normalizedUrl).hostname,
      crawled_at: typeof doc.crawled_at === 'number' ? doc.crawled_at : Date.now(),
      depth: typeof doc.depth === 'number' ? doc.depth : 0
    };

    // If document with same URL exists, remove first (MiniSearch does not auto-replace)
    if (this.documents.has(normalizedUrl)) {
      this.index.remove({ url: normalizedUrl });
    }

    // Add to MiniSearch
    try {
      this.index.add(document);
      this.documents.set(normalizedUrl, document);
    } catch (e) {
      throw new Error(`Failed to index document: ${e.message}`);
    }
    
    return document;
  }

  /**
   * Add multiple documents in batch (more efficient)
   * @param {Array<Object>} docs - Array of documents
   * @returns {number} Number of documents successfully added
   */
  addDocuments(docs) {
    if (!Array.isArray(docs)) {
      throw new Error('addDocuments requires an array');
    }
    
    let added = 0;
    const errors = [];
    
    for (const doc of docs) {
      try {
        this.addDocument(doc);
        added++;
      } catch (e) {
        errors.push(`${doc.url || 'unknown'}: ${e.message}`);
      }
    }
    
    if (errors.length > 0) {
      console.warn(`[Indexer] ${errors.length} documents failed:`, errors.slice(0, 3).join(', '));
    }
    
    return added;
  }

  /**
   * Remove a document by URL
   * @param {string} url - URL of document to remove
   * @returns {boolean} True if document was removed, false if not found
   */
  removeByUrl(url) {
    const normalizedUrl = this._normalizeUrl(url);
    if (!normalizedUrl) return false;
    
    if (!this.documents.has(normalizedUrl)) {
      return false;
    }
    
    try {
      this.index.remove({ url: normalizedUrl });
      this.documents.delete(normalizedUrl);
      return true;
    } catch (e) {
      console.error(`[Indexer] Failed to remove ${normalizedUrl}: ${e.message}`);
      return false;
    }
  }

  /**
   * Check if a document exists
   * @param {string} url - URL to check
   * @returns {boolean} True if document exists in index
   */
  hasDocument(url) {
    const normalizedUrl = this._normalizeUrl(url);
    return normalizedUrl ? this.documents.has(normalizedUrl) : false;
  }

  /**
   * Get a single document by URL
   * @param {string} url - Document URL
   * @returns {Object|null} Document or null if not found
   */
  getDocument(url) {
    const normalizedUrl = this._normalizeUrl(url);
    return normalizedUrl ? this.documents.get(normalizedUrl) || null : null;
  }

  /**
   * Search the index
   * @param {string} query - Search query
   * @param {Object} options - Search options
   * @param {number} options.limit - Maximum results (default 10)
   * @param {number} options.offset - Skip first N results (default 0)
   * @param {string} options.domainFilter - Filter to specific domain
   * @param {number} options.minScore - Minimum score threshold (default 0)
   * @returns {Object} {total: number, results: Array}
   */
  search(query, options = {}) {
    if (!query || typeof query !== 'string') {
      return { total: 0, results: [] };
    }
    
    const {
      limit = 10,
      offset = 0,
      domainFilter = null,
      minScore = 0
    } = options;
    
    // Get raw results from MiniSearch
    let results = this.index.search(query, {
      prefix: true, // Enable prefix matching for partial words
      fuzzy: 0.2   // Light fuzziness for typos
    });
    
    // Apply score filter
    if (minScore > 0) {
      results = results.filter(r => r.score >= minScore);
    }
    
    // Apply domain filter
    if (domainFilter) {
      results = results.filter(r => r.domain === domainFilter);
    }
    
    // Get total before pagination
    const total = results.length;
    
    // Apply pagination
    const paged = results.slice(offset, offset + limit);
    
    // Transform to clean output format
    const transformed = paged.map(r => ({
      title: r.title,
      url: r.url,
      domain: r.domain,
      snippet: r.excerpt || '',
      score: Math.round(r.score * 1000) / 1000, // Round to 3 decimals
      crawled_at: r.crawled_at
    }));
    
    return { total, results: transformed };
  }

  /**
   * Get detailed statistics about the index
   * @returns {Object} Statistics
   */
  getStats() {
    const docs = Array.from(this.documents.values());
    const count = docs.length;
    
    if (count === 0) {
      return {
        documents: 0,
        domains: 0,
        newest_crawl: null,
        oldest_crawl: null,
        domain_breakdown: {}
      };
    }
    
    const domains = new Set(docs.map(d => d.domain));
    const timestamps = docs.map(d => d.crawled_at);
    
    // Domain breakdown
    const domainBreakdown = {};
    for (const doc of docs) {
      domainBreakdown[doc.domain] = (domainBreakdown[doc.domain] || 0) + 1;
    }
    
    return {
      documents: count,
      domains: domains.size,
      newest_crawl: Math.max(...timestamps),
      oldest_crawl: Math.min(...timestamps),
      domain_breakdown: domainBreakdown
    };
  }

  /**
   * Get all domains in the index
   * @returns {Array<string>} Sorted list of unique domains
   */
  getDomains() {
    const domains = new Set();
    for (const doc of this.documents.values()) {
      domains.add(doc.domain);
    }
    return Array.from(domains).sort();
  }

  /**
   * Save index to disk (synchronous)
   * @returns {boolean} True on success
   */
  save() {
    try {
      // Create temp files first for atomicity
      const tempIndex = this.indexPath + '.tmp';
      const tempDocs = this.docsPath + '.tmp';
      
      // Serialize index
      const indexJson = this.index.toJSON();
      fs.writeFileSync(tempIndex, JSON.stringify(indexJson, null, 0));
      
      // Serialize documents
      const docsArray = Array.from(this.documents.values());
      fs.writeFileSync(tempDocs, JSON.stringify(docsArray, null, 0));
      
      // Atomic rename
      fs.renameSync(tempIndex, this.indexPath);
      fs.renameSync(tempDocs, this.docsPath);
      
      return true;
    } catch (e) {
      console.error('[Indexer] Save failed:', e.message);
      return false;
    }
  }

  /**
   * Save index asynchronously (non-blocking)
   * @returns {Promise<boolean>}
   */
  async saveAsync() {
    return new Promise((resolve) => {
      try {
        const result = this.save();
        resolve(result);
      } catch (e) {
        console.error('[Indexer] Async save failed:', e.message);
        resolve(false);
      }
    });
  }

  /**
   * Clear all documents from the index
   * @param {boolean} deleteFiles - Also delete saved files (default false)
   */
  clear(deleteFiles = false) {
    this._createNewIndex();
    
    if (deleteFiles) {
      try {
        if (fs.existsSync(this.indexPath)) {
          fs.unlinkSync(this.indexPath);
        }
        if (fs.existsSync(this.docsPath)) {
          fs.unlinkSync(this.docsPath);
        }
      } catch (e) {
        console.error('[Indexer] Failed to delete files:', e.message);
      }
    }
  }

  /**
   * Close the indexer (save pending changes)
   */
  close() {
    this.save();
    console.error(`[Indexer] Closed (${this.documents.size} documents)`);
  }
}

module.exports = Indexer;
