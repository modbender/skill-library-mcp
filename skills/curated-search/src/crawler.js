/**
 * Curated Crawler - Enhanced with Orchestration (Phase 3.4)
 *
 * Domain-restricted web crawler with politeness, robots.txt, state persistence,
 * checkpoint/resume, signal handling, health monitoring, and graceful shutdown.
 *
 * Architecture:
 *   State machine: IDLE → RUNNING → STOPPING → STOPPED
 *   Persistence: saves queue, seen set, stats every N docs + time interval
 *   Health: windowed error rate, recent success tracking
 */

// Use global fetch (Node 18+) directly; tests may mock it.
const fs = require('fs');
const path = require('path');
const RobotsParser = require('robots-parser');
const ContentExtractor = require('./content-extractor');
const urlNormalizer = require('./url-normalizer');
const RateLimiter = require('./rate-limiter');

class CuratedCrawler {
  constructor(config, indexer) {
    this.config = config;
    this.indexer = indexer;
    this.log = this.createLogger();
    this.extractor = new ContentExtractor(config);
    this.rateLimiter = new RateLimiter(config, this); // 'this' provides getRobotsParser

    // State file path
    this.statePath = path.resolve(__dirname, '..', 'data', 'crawl-state.json');
    this.stateDir = path.dirname(this.statePath);
    if (!fs.existsSync(this.stateDir)) {
      fs.mkdirSync(this.stateDir, { recursive: true });
    }

    // Load or initialize state
    this.state = this.loadState();

    // Queue and seen derived from state
    this.queue = this.state.queue ? [...this.state.queue] : [];
    this.seen = new Set(this.state.seen ? Object.keys(this.state.seen) : []);

    // Stats (merge persisted stats with runtime)
    this.stats = { ...this.state.stats, recentErrors: [], recentRequests: 0, recentErrorCount: 0 };

    this.robotsCache = new Map();
    this.running = false;
    this.startTime = null;
    this.lastCheckpoint = Date.now();

    // Shutdown handling
    this.shutdownRequested = false;
    this.shutdownReason = null;
    this.setupSignalHandlers();

    // Checkpoint configuration
    this.checkpointInterval = 5 * 60 * 1000; // 5 minutes
    this.autoSaveAfter = this.config.index?.auto_save_after || 100;
  }

  createLogger() {
    const levels = { debug: 0, info: 1, warn: 2, error: 3 };
    const level = levels[this.config.logging?.level || 'info'] || 1;

    return (msg, lvl = 'info', meta = {}) => {
      if (levels[lvl] >= level) {
        const timestamp = new Date().toISOString();
        const metaStr = Object.keys(meta).length ? ` ${JSON.stringify(meta)}` : '';
        console.log(`[${timestamp}] [${lvl.toUpperCase()}] ${msg}${metaStr}`);
      }
    };
  }

  // ============================================================================
  // STATE PERSISTENCE
  // ============================================================================

  loadState() {
    if (!fs.existsSync(this.statePath)) {
      this.log('No saved state found, starting fresh', 'info');
      return this.createFreshState();
    }

    try {
      const raw = fs.readFileSync(this.statePath, 'utf8');
      const state = JSON.parse(raw);
      this.log(`Resuming from state: ${state.stats?.documentsIndexed || 0} docs indexed, ${state.queue?.length || 0} queued`, 'info');
      return state;
    } catch (e) {
      this.log(`Corrupted state file, starting fresh: ${e.message}`, 'warn');
      fs.renameSync(this.statePath, this.statePath + '.corrupt');
      return this.createFreshState();
    }
  }

  createFreshState() {
    return {
      version: 1,
      createdAt: Date.now(),
      updatedAt: Date.now(),
      queue: [],
      seen: {},
      failed: {},
      robotsCache: {},
      stats: {
        started: Date.now(),
        documentsIndexed: 0,
        requestsMade: 0,
        urlsExtracted: 0,
        errors: 0,
        robotsBlocked: 0,
        rejectedDocuments: 0,
        maxDepthReached: 0,
        domainBreakdown: {}
      },
      lastCheckpoint: Date.now()
    };
  }

  saveState() {
    try {
      // Truncate queue and seen to prevent unbounded growth
      const truncatedQueue = this.queue.slice(0, 10000);
      const seenEntries = Array.from(this.seen).map(url => ({ url, seenAt: Date.now() }));
      const truncatedSeen = seenEntries.slice(0, 50000);

      const state = {
        ...this.state,
        queue: truncatedQueue.map(item => ({ url: item.url, depth: item.depth })),
        seen: Object.fromEntries(truncatedSeen.map(entry => [entry.url, entry.seenAt])),
        failed: this.state.failed, // keep as-is (could truncate)
        robotsCache: this.robotsCache, // Could truncate to recent 100
        stats: this.stats,
        updatedAt: Date.now(),
        lastCheckpoint: Date.now()
      };

      const tempPath = this.statePath + '.tmp';
      fs.writeFileSync(tempPath, JSON.stringify(state, null, 2));
      fs.renameSync(tempPath, this.statePath);

      this.lastCheckpoint = Date.now();
      this.log(`Checkpoint saved: queue=${this.queue.length}, seen=${this.seen.size}, indexed=${this.stats.documentsIndexed}`, 'debug');
    } catch (e) {
      this.log(`Failed to save checkpoint: ${e.message}`, 'error');
    }
  }

  // ============================================================================
  // SIGNAL HANDLING
  // ============================================================================

  setupSignalHandlers() {
    process.on('SIGINT', this.handleSignal.bind(this, 'SIGINT'));
    process.on('SIGTERM', this.handleSignal.bind(this, 'SIGTERM'));
  }

  handleSignal(signal) {
    if (this.shutdownRequested) {
      this.log('Force exit (second signal)', 'warn');
      process.exit(1);
    }

    this.shutdownRequested = true;
    this.shutdownReason = signal;
    this.log(`Received ${signal}, initiating graceful shutdown...`, 'info');
    this.stop();
  }

  // ============================================================================
  // HEALTH MONITORING
  // ============================================================================

  updateHealthMetrics(success = false) {
    const now = Date.now();
    this.stats.recentRequests++;

    if (success) {
      this.stats.lastSuccessTime = now;
      this.stats.recentErrorCount = 0;
      this.stats.recentErrors = [];
    } else {
      this.stats.recentErrorCount++;
      this.stats.recentErrors.push({ time: now });
    }

    // Keep only last 100 requests
    if (this.stats.recentRequests > 100) {
      this.stats.recentRequests = 100;
      this.stats.recentErrorCount = Math.min(this.stats.recentErrorCount, 100);
    }
  }

  isHealthy() {
    const recentFailRate = this.stats.recentRequests > 0
      ? this.stats.recentErrorCount / this.stats.recentRequests
      : 0;

    const fiveMinAgo = Date.now() - 5 * 60 * 1000;
    const hasRecentSuccess = this.stats.lastSuccessTime && this.stats.lastSuccessTime > fiveMinAgo;

    // Stop conditions
    if (recentFailRate > 0.7 && !hasRecentSuccess) {
      return { healthy: false, reason: `High failure rate (${(recentFailRate*100).toFixed(1)}%) with no recent success` };
    }

    if (this.stats.recentErrors.length > 20 && this.stats.recentErrorCount > 10) {
      const errorTypes = new Set(this.stats.recentErrors.map(e => e.type)).size;
      if (errorTypes === 1) {
        return { healthy: false, reason: 'Repeated identical errors' };
      }
    }

    return { healthy: true };
  }

  /**
   * Check if a URL's domain is allowed by the whitelist
   * @param {string} urlStr - URL to check
   * @returns {boolean}
   */
  isAllowedDomain(urlStr) {
    try {
      const { hostname } = new URL(urlStr);
      // Strip leading www.
      const cleanHost = hostname.replace(/^www\./i, '');
      // Check against whitelist: exact match or subdomain match
      return this.config.domains.some(allowed => {
        return cleanHost === allowed || cleanHost.endsWith('.' + allowed);
      });
    } catch {
      return false;
    }
  }

  // ============================================================================
  // CHECKPOINT & AUTO-SAVE
  // ============================================================================

  maybeCheckpoint(force = false) {
    const now = Date.now();
    const timeSinceLast = now - this.lastCheckpoint;

    if (force || (this.stats.documentsIndexed % this.autoSaveAfter === 0) || timeSinceLast > this.checkpointInterval) {
      this.saveState();
      this.indexer.save(); // Persist index to disk
    }
  }

  // ============================================================================
  // COMPLETION DETECTION
  // ============================================================================

  isCompletion() {
    if (this.queue.length === 0) {
      return { complete: true, reason: 'Queue exhausted', success: true };
    }

    if (this.stats.documentsIndexed >= this.config.crawl.max_documents) {
      return { complete: true, reason: `Reached max_documents (${this.config.crawl.max_documents})`, success: true };
    }

    return { complete: false };
  }

  // ============================================================================
  // ROBOTS PARSER (CACHED) - with 24h TTL
  // ============================================================================

  async getRobotsParser(domain) {
    const now = Date.now();
    const cached = this.robotsCache.get(domain);
    if (cached) {
      const age = now - cached.fetchedAt;
      const ttl = 24 * 60 * 60 * 1000; // 24 hours
      if (age < ttl) {
        return cached.parser;
      } else {
        this.robotsCache.delete(domain); // expired
      }
    }

    const robotsUrl = `https://${domain}/robots.txt`;
    try {
      const resp = await fetch(robotsUrl, { timeout: 10000 });
      let parser;
      if (resp.ok) {
        const body = await resp.text();
        parser = RobotsParser(robotsUrl, body);
      } else {
        parser = RobotsParser(robotsUrl, '');
      }
      this.robotsCache.set(domain, { parser, fetchedAt: Date.now() });
      return parser;
    } catch (e) {
      this.log(`Failed to fetch robots.txt for ${domain}: ${e.message}`, 'warn');
      const parser = RobotsParser(robotsUrl, '');
      this.robotsCache.set(domain, { parser, fetchedAt: Date.now() });
      return parser;
    }
  }

  /**
   * Get crawl delay for a host from robots.txt (seconds)
   * Returns null if not specified
   * @param {string} hostname
   * @returns {Promise<number|null>}
   */
  async getCrawlDelay(hostname) {
    const parser = await this.getRobotsParser(hostname);
    return parser.getCrawlDelay(this.config.crawl.user_agent);
  }

  // ============================================================================
  // QUEUE MANAGEMENT
  // ============================================================================

  enqueue(rawUrl, depth = 0) {
    // Normalize URL first
    const normalized = urlNormalizer.normalizeUrl(rawUrl);
    if (!normalized) {
      return false;
    }

    // Check if already seen
    if (this.seen.has(normalized)) {
      return false;
    }

    // SSRF prevention: block private IP ranges
    try {
      const parsed = new URL(normalized);
      if (urlNormalizer.isBlockedHost(parsed.hostname)) {
        this.log(`Blocked private IP/host: ${parsed.hostname} (SSRF prevention)`, 'warn');
        return false;
      }
    } catch (e) {
      return false;
    }

    // Domain whitelist check
    if (!urlNormalizer.isWhitelisted(normalized, this.config.domains)) {
      this.stats.skipped_domain = (this.stats.skipped_domain || 0) + 1;
      return false;
    }

    // Depth check
    if (depth > this.config.crawl.depth) {
      return false;
    }

    this.seen.add(normalized);
    this.queue.push({ url: normalized, depth });
    this.stats.queued = (this.stats.queued || 0) + 1;
    return true;
  }

  // ============================================================================
  // FETCH WITH RETRY (Politeness - Phase 3.3)
  // ============================================================================

  async fetchWithRetry(url, options = {}, maxRetries = 3) {
    let attempt = 0;
    const isRetryable = (error, response) => {
      if (response && response.status >= 500) return true;
      if (error && ['ETIMEDOUT', 'ECONNRESET', 'ECONNREFUSED', 'ENETUNREACH', 'EHOSTUNREACH', 'EAI_AGAIN'].includes(error.code)) {
        return true;
      }
      return false;
    };

    while (attempt <= maxRetries) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), (this.config.crawl.timeout || 30) * 1000);

        const resp = await fetch(url, {
          ...options,
          signal: controller.signal,
          headers: {
            'User-Agent': this.config.crawl.user_agent,
            ...options.headers
          }
        });
        clearTimeout(timeoutId);

        if (resp.status === 429) {
          const retryAfterHeader = resp.headers.get('Retry-After');
          let delay = 0;
          if (retryAfterHeader) {
            const seconds = parseInt(retryAfterHeader, 10);
            if (!isNaN(seconds)) {
              delay = seconds * 1000;
            } else {
              const date = new Date(retryAfterHeader);
              if (!isNaN(date.getTime())) {
                delay = date.getTime() - Date.now();
              }
            }
          }
          if (delay <= 0) delay = Math.pow(2, attempt) * 1000;

          if (attempt === maxRetries) {
            throw new Error(`Max retries (429) for ${url}`);
          }

          this.log(`429 Too Many Requests for ${url}, retry ${attempt + 1}/${maxRetries} after ${delay}ms`, 'warn');
          await new Promise(resolve => setTimeout(resolve, delay));
          attempt++;
          continue;
        }

        // Treat any other non-OK status as error
        if (!resp.ok) {
          const error = new Error(`HTTP error ${resp.status}`);
          error.status = resp.status;
          throw error;
        }

        return resp;
      } catch (error) {
        if (attempt === maxRetries || !isRetryable(error, null)) {
          throw error;
        }
        const delay = Math.pow(2, attempt) * 1000;
        this.log(`Fetch error ${url}: ${error.message}, retry ${attempt + 1}/${maxRetries} after ${delay}ms`, 'warn');
        await new Promise(resolve => setTimeout(resolve, delay));
        attempt++;
      }
    }
  }

  // ============================================================================
  // FETCH & PARSE
  // ============================================================================

  async fetchUrl(url, depth) {
    try {
      const resp = await this.fetchWithRetry(url);

      if (!resp.ok) {
        this.log(`HTTP ${resp.status} ${url}`, 'warn');
        return null;
      }

      const contentType = resp.headers.get('content-type') || '';
      if (!contentType.includes('text/html')) {
        this.log(`Skipping non-HTML: ${contentType} ${url}`, 'debug');
        return null;
      }

      const html = await resp.text();
      this.stats.requestsMade = (this.stats.requestsMade || 0) + 1;

      return this.parseHtml(url, html, depth);
    } catch (e) {
      this.stats.errors = (this.stats.errors || 0) + 1;
      this.log(`Fetch failed ${url}: ${e.message}`, 'warn');
      return null;
    }
  }

  /**
   * Parse HTML, extract title, content, excerpt, and links
   * Uses ContentExtractor for high-quality extraction
   */
  async parseHtml(url, html, depth) {
    try {
      // Use ContentExtractor for title and content
      const extracted = await this.extractor.extract(html, url);
      const hostname = new URL(url).hostname;

      // Extract links separately (still needed for crawl)
      const links = [];
      const { JSDOM } = require('jsdom');
      const dom = new JSDOM(html, { url });
      const doc = dom.window.document;
      const anchors = doc.querySelectorAll('a[href]');
      for (const a of anchors) {
        try {
          const href = a.getAttribute('href');
          if (!href || href.startsWith('#') || href.startsWith('javascript:') || href.startsWith('mailto:')) continue;
          const absolute = new URL(href, url).href;
          links.push(absolute);
        } catch (e) {
          // ignore malformed
        }
      }

      return {
        url,
        title: extracted.title,
        content: extracted.content,
        excerpt: extracted.excerpt,
        quality: extracted.quality,
        issues: extracted.issues,
        type: extracted.type,
        domain: hostname,
        depth,
        links
      };
    } catch (e) {
      this.log(`Parse failed ${url}: ${e.message}`, 'error');
      return null;
    }
  }

  // ============================================================================
  // INDEXING
  // ============================================================================

  async indexDocument(doc) {
    try {
      this.indexer.addDocument(doc);
      this.stats.documentsIndexed = (this.stats.documentsIndexed || 0) + 1;
      this.stats.urlsExtracted = (this.stats.urlsExtracted || 0) + (doc.links?.length || 0);
      this.stats.domainBreakdown = this.stats.domainBreakdown || {};
      this.stats.domainBreakdown[doc.domain] = (this.stats.domainBreakdown[doc.domain] || 0) + 1;

      const maxDepth = this.stats.maxDepthReached || 0;
      if (doc.depth > maxDepth) {
        this.stats.maxDepthReached = doc.depth;
      }

      this.log(`Indexed: ${doc.title || doc.url} (${doc.domain})`, 'info');

      // Auto-save checkpoint
      this.maybeCheckpoint();
    } catch (e) {
      this.stats.errors = (this.stats.errors || 0) + 1;
      this.log(`Index failed ${doc.url}: ${e.message}`, 'error');
    }
  }

  // ============================================================================
  // MAIN CRAWL LOOP
  // ============================================================================

  async crawl() {
    this.running = true;
    this.startTime = Date.now();
    this.log(`Crawler started: ${this.queue.length} URLs queued, ${this.seen.size} seen`, 'info');

    while (this.running && this.queue.length > 0) {
      const { url, depth } = this.queue.shift();

      // Check completion conditions
      if (this.stats.documentsIndexed >= this.config.crawl.max_documents) {
        this.log(`Reached max_documents (${this.config.crawl.max_documents})`, 'info');
        break;
      }

      // Determine hostname for rate limiting
      let hostname = null;
      try {
        const parsedUrl = new URL(url);
        hostname = parsedUrl.hostname;
      } catch (e) {
        this.log(`Invalid URL, skipping: ${url}`, 'warn');
        this.updateHealthMetrics(false);
        continue;
      }

      // Politeness: per-host rate limiting
      await this.rateLimiter.waitForSlot(hostname);

      // Robots.txt check
      try {
        const robots = await this.getRobotsParser(hostname);
        if (this.config.crawl.respect_robots && !robots.isAllowed(url, this.config.crawl.user_agent)) {
          this.stats.robotsBlocked = (this.stats.robotsBlocked || 0) + 1;
          this.log(`Robots denied: ${url}`, 'debug');
          this.updateHealthMetrics(false);
          continue;
        }
      } catch (e) {
        this.log(`Robots check failed for ${hostname}: ${e.message}`, 'warn');
        // Continue anyway (permissive)
      }

      // Fetch and process
      const result = await this.fetchUrl(url, depth);
      if (result) {
        await this.indexDocument(result);

        // Enqueue links if within depth
        if (depth < this.config.crawl.depth) {
          for (const link of result.links) {
            this.enqueue(link, depth + 1);
          }
        }
        this.updateHealthMetrics(true);
      } else {
        this.updateHealthMetrics(false);
      }

      // Periodic checkpoint (time-based)
      this.maybeCheckpoint();

      // Health check
      const health = this.isHealthy();
      if (!health.healthy) {
        this.log(`Stopping due to health: ${health.reason}`, 'error');
        break;
      }
    }

    await this.finalize();
  }

  async finalize() {
    this.running = false;
    const completion = this.isCompletion();
    const duration = Date.now() - this.startTime;

    // Save index and state before exit
    this.indexer.save();
    this.saveState(); // Final checkpoint

    this.log(`Crawler ${completion.success ? 'completed' : 'stopped'}: ${completion.reason}`, 'info');
    this.log(`Duration: ${(duration/1000).toFixed(1)}s, Indexed: ${this.stats.documentsIndexed}, Fetched: ${this.stats.requestsMade}, Errors: ${this.stats.errors}`, 'info');

    // Simple stats printed
    console.log(`
=== Crawl Statistics ===
Documents indexed: ${this.stats.documentsIndexed}
Requests made: ${this.stats.requestsMade}
URLs extracted: ${this.stats.urlsExtracted}
Errors: ${this.stats.errors}
Robots blocked: ${this.stats.robotsBlocked || 0}
Skipped (domain): ${this.stats.skipped_domain || 0}
Max depth reached: ${this.stats.maxDepthReached || 0}
Domain breakdown:
${Object.entries(this.stats.domainBreakdown || {}).map(([d, c]) => `  ${d}: ${c}`).join('\n')}
========================
    `);

    // Exit cleanly
    process.exit(0);
  }

  // ============================================================================
  // PUBLIC API
  // ============================================================================

  stop() {
    if (this.running) {
      this.log('Stopping crawl...', 'info');
      this.saveState(); // Save before exit
    }
  }

  async start() {
    // If starting fresh, initialize seeds
    if (this.queue.length === 0) {
      this.log('Initializing crawl seeds', 'info');
      for (const seed of this.config.seeds) {
        this.enqueue(seed, 0);
      }
    }

    await this.crawl();
  }
}

module.exports = CuratedCrawler;
