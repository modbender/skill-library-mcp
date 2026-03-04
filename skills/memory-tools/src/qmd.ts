/**
 * QMD CLI Wrapper
 *
 * Handles interaction with the QMD search engine via CLI.
 * QMD provides BM25 + vector search + LLM reranking, all local.
 */

import { spawn } from 'node:child_process';

export interface QMDSearchResult {
  docid: string;
  filepath: string;
  file?: string; // QMD sometimes uses 'file' instead of 'filepath'
  line?: number;
  score: number;
  title?: string;
  context?: string;
  snippet?: string;
}

export interface QMDStatus {
  collections: Array<{
    name: string;
    path: string;
    documents: number;
  }>;
  totalDocuments: number;
  indexed: boolean;
}

export class QMDClient {
  private collectionName: string;
  private memoriesPath: string;
  private initialized: boolean = false;
  private qmdAvailable: boolean | null = null;
  private updateDebounceTimer: NodeJS.Timeout | null = null;
  private pendingUpdate: boolean = false;
  private disabled: boolean = false;
  private disableReason: string | null = null;

  constructor(memoriesPath: string, collectionName: string = 'memories', options?: { disabled?: boolean }) {
    this.memoriesPath = memoriesPath;
    this.collectionName = this.validateCollectionName(collectionName);
    // Allow disabling QMD for tests via env var or option
    this.disabled = options?.disabled || process.env.MEMORY_TOOLS_DISABLE_QMD === 'true';
  }

  /**
   * Check and cache QMD availability
   */
  private async checkQMDAvailable(): Promise<boolean> {
    if (this.disabled) return false;
    if (this.qmdAvailable !== null) return this.qmdAvailable;
    this.qmdAvailable = await this.isInstalled();
    return this.qmdAvailable;
  }

  /**
   * Check if QMD is installed
   */
  async isInstalled(): Promise<boolean> {
    try {
      await this.runQmd(['--version'], { timeout: 5000 });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Initialize QMD collection if needed
   */
  async ensureCollection(): Promise<void> {
    if (this.disabled) return;
    if (this.initialized) return;

    const installed = await this.isInstalled();
    if (!installed) {
      throw new Error(
        'QMD is not installed. Install it with: npm install -g @tobilu/qmd'
      );
    }

    // Check if collection exists by parsing text output
    try {
      const { stdout } = await this.runQmd(['collection', 'list'], { timeout: 10000 });

      // Parse text output - look for collection name in the output
      const exists = stdout.includes(`${this.collectionName} (qmd://`) ||
                     stdout.includes(`${this.collectionName}(`);

      if (!exists) {
        // Create collection
        await this.runQmd(['collection', 'add', this.memoriesPath, '--name', this.collectionName], {
          timeout: 30000,
        });
        console.log(`[memory-tools] Created QMD collection: ${this.collectionName}`);

        // Initial embedding
        await this.forceUpdate();
      }

      this.initialized = true;
    } catch (err: any) {
      // Collection list might fail if no collections exist yet
      if (err.message?.includes('No collections') || err.message?.includes('Collections (0)')) {
        await this.runQmd(['collection', 'add', this.memoriesPath, '--name', this.collectionName], {
          timeout: 30000,
        });
        await this.forceUpdate();
        this.initialized = true;
      } else {
        this.maybeDisableForFatalQmdError(err);
        throw err;
      }
    }
  }

  /**
   * Hybrid search (BM25 + vector + reranking)
   * This is the highest quality search mode
   */
  async query(query: string, limit: number = 10): Promise<QMDSearchResult[]> {
    const available = await this.checkQMDAvailable();
    if (!available) return [];

    try {
      await this.ensureCollection();
      const { stdout } = await this.runQmd(
        ['query', query, '-n', String(limit), '--json', '-c', this.collectionName],
        { timeout: 30000 } // 30s timeout for reranking
      );

      return this.parseResults(stdout);
    } catch (err: any) {
      // Fallback to vector search if query fails
      console.warn('[memory-tools] QMD query failed, falling back to vsearch:', err.message);
      return this.vectorSearch(query, limit);
    }
  }

  /**
   * Vector-only semantic search
   * Faster than query but no BM25 or reranking
   */
  async vectorSearch(query: string, limit: number = 10): Promise<QMDSearchResult[]> {
    const available = await this.checkQMDAvailable();
    if (!available) return [];

    try {
      await this.ensureCollection();
      const { stdout } = await this.runQmd(
        ['vsearch', query, '-n', String(limit), '--json', '-c', this.collectionName],
        { timeout: 10000 }
      );

      return this.parseResults(stdout);
    } catch (err: any) {
      console.error('[memory-tools] QMD vsearch failed:', err.message);
      return [];
    }
  }

  /**
   * BM25 keyword search
   * Fastest, good for exact matches
   */
  async search(query: string, limit: number = 10): Promise<QMDSearchResult[]> {
    const available = await this.checkQMDAvailable();
    if (!available) return [];

    try {
      await this.ensureCollection();
      const { stdout } = await this.runQmd(
        ['search', query, '-n', String(limit), '--json', '-c', this.collectionName],
        { timeout: 5000 }
      );

      return this.parseResults(stdout);
    } catch (err: any) {
      console.error('[memory-tools] QMD search failed:', err.message);
      return [];
    }
  }

  /**
   * Find similar documents (for duplicate detection)
   */
  async findSimilar(content: string, threshold: number = 0.9): Promise<QMDSearchResult[]> {
    const results = await this.vectorSearch(content, 3);

    // Filter by threshold
    return results.filter(r => r.score >= threshold);
  }

  /**
   * Update the QMD index (debounced)
   * Called after file changes
   */
  scheduleUpdate(): void {
    // Check availability synchronously using cached value
    if (this.qmdAvailable === false) return;

    this.pendingUpdate = true;

    if (this.updateDebounceTimer) {
      clearTimeout(this.updateDebounceTimer);
    }

    // Debounce updates by 2 seconds
    this.updateDebounceTimer = setTimeout(async () => {
      if (this.pendingUpdate) {
        // Check QMD availability before updating
        const available = await this.checkQMDAvailable();
        if (available) {
          await this.update();
        }
        this.pendingUpdate = false;
      }
    }, 2000);
  }

  /**
   * Immediately update the QMD index
   */
  async update(): Promise<void> {
    try {
      await this.runQmd(['update'], { timeout: 60000 });
    } catch (err: any) {
      console.error('[memory-tools] QMD update failed:', err.message);
    }
  }

  /**
   * Force re-embed all documents
   */
  async forceUpdate(): Promise<void> {
    try {
      console.log('[memory-tools] Running QMD embed (this may take a moment on first run)...');
      await this.runQmd(['embed'], { timeout: 300000 }); // 5 min timeout for initial embed
      console.log('[memory-tools] QMD embedding complete');
    } catch (err: any) {
      console.error('[memory-tools] QMD embed failed:', err.message);
    }
  }

  /**
   * Get QMD status
   */
  async status(): Promise<QMDStatus | null> {
    try {
      const { stdout } = await this.runQmd(['status', '--json'], { timeout: 10000 });
      return JSON.parse(stdout);
    } catch {
      return null;
    }
  }

  /**
   * Extract memory ID from QMD filepath result
   */
  extractMemoryId(result: QMDSearchResult): string | null {
    // filepath formats:
    // - qmd://memories/facts/abc123-def4-5678-90ab-cdef12345678.md
    // - memories/facts/abc123-def4-5678-90ab-cdef12345678.md
    // - qmd://memories/preferences/test-pref-1.md (non-UUID names)

    const filepath = result.filepath || result.file || '';

    // Try to extract UUID
    const uuidMatch = filepath.match(/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})\.md$/i);
    if (uuidMatch) {
      return uuidMatch[1];
    }

    // Fall back to extracting filename without extension
    const filenameMatch = filepath.match(/\/([^/]+)\.md$/);
    if (filenameMatch) {
      return filenameMatch[1];
    }

    return null;
  }

  private validateCollectionName(name: string): string {
    if (!/^[A-Za-z0-9_-]{1,64}$/.test(name)) {
      throw new Error(
        `Invalid qmd collection name "${name}". Use letters, numbers, "_" or "-" (max 64 chars).`
      );
    }
    return name;
  }

  private maybeDisableForFatalQmdError(err: unknown): void {
    const message = err instanceof Error ? err.message : String(err);
    const fatalPatterns = [
      /NODE_MODULE_VERSION/i,
      /better-sqlite3/i,
      /was compiled against a different Node\.js version/i,
    ];

    if (!fatalPatterns.some(p => p.test(message))) return;
    if (this.disabled) return;

    this.disabled = true;
    this.qmdAvailable = false;
    this.disableReason = message;
    console.warn('[memory-tools] QMD disabled due to runtime incompatibility:', message);
  }

  private async runQmd(
    args: string[],
    options: { timeout?: number } = {}
  ): Promise<{ stdout: string; stderr: string }> {
    const timeoutMs = options.timeout ?? 10000;

    return new Promise((resolve, reject) => {
      const child = spawn('qmd', args, { stdio: ['ignore', 'pipe', 'pipe'] });
      let stdout = '';
      let stderr = '';
      let timedOut = false;

      const timer = setTimeout(() => {
        timedOut = true;
        child.kill('SIGTERM');
      }, timeoutMs);

      child.stdout.on('data', chunk => {
        stdout += chunk.toString();
      });

      child.stderr.on('data', chunk => {
        stderr += chunk.toString();
      });

      child.on('error', err => {
        clearTimeout(timer);
        this.maybeDisableForFatalQmdError(err);
        reject(err);
      });

      child.on('close', code => {
        clearTimeout(timer);
        if (timedOut) {
          reject(new Error(`qmd ${args.join(' ')} timed out after ${timeoutMs}ms`));
          return;
        }

        if (code !== 0) {
          const err = new Error(
            `qmd ${args.join(' ')} failed with code ${code}: ${(stderr || stdout).trim()}`
          );
          this.maybeDisableForFatalQmdError(err);
          reject(err);
          return;
        }

        resolve({ stdout, stderr });
      });
    });
  }

  private parseResults(stdout: string): QMDSearchResult[] {
    try {
      // QMD sometimes outputs progress text before JSON, extract just the JSON array
      // Look for [ ... ] pattern that could be the JSON array
      const jsonMatch = stdout.match(/\[\s*\{[\s\S]*\}\s*\]/);
      if (!jsonMatch) return [];

      const parsed = JSON.parse(jsonMatch[0]);
      // QMD returns array of results
      if (Array.isArray(parsed)) {
        return parsed.map(r => ({
          docid: r.docid || '',
          filepath: r.filepath || r.file || '', // QMD uses 'file' field
          line: r.line,
          score: r.score || 0,
          title: r.title,
          context: r.context,
          snippet: r.snippet,
        }));
      }
      return [];
    } catch {
      return [];
    }
  }
}
