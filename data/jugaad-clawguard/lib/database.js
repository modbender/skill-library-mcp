/**
 * ClawGuard Database Manager
 * Handles SQLite operations for threat storage and lookup
 */

import Database from 'better-sqlite3';
import { readFileSync, existsSync, mkdirSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { homedir } from 'os';

const __dirname = dirname(fileURLToPath(import.meta.url));

export class ClawGuardDatabase {
    constructor(dbPath = null) {
        this.dbPath = dbPath || join(homedir(), '.clawguard', 'osbs.db');
        this.db = null;
        this.initialized = false;
    }

    /**
     * Initialize database connection and schema
     */
    init() {
        if (this.initialized) return;

        // Ensure directory exists
        const dbDir = dirname(this.dbPath);
        if (!existsSync(dbDir)) {
            mkdirSync(dbDir, { recursive: true });
        }

        // Open database
        this.db = new Database(this.dbPath);
        this.db.pragma('journal_mode = WAL');
        this.db.pragma('synchronous = NORMAL');
        this.db.pragma('cache_size = 10000');
        this.db.pragma('foreign_keys = ON');

        // Apply schema
        const schemaPath = join(__dirname, 'schema.sql');
        const schema = readFileSync(schemaPath, 'utf8');
        this.db.exec(schema);

        // Prepare frequently used statements
        this._prepareStatements();

        this.initialized = true;
    }

    _prepareStatements() {
        // Insert statements
        this._insertThreat = this.db.prepare(`
            INSERT OR REPLACE INTO threats 
            (id, version, created, updated, status, tier, category, subcategory, tags,
             name, description, teaching_prompt, severity, confidence, false_positive_rate,
             response, source, refs, related, mitre_attack, cve, campaign)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `);

        this._insertIndicator = this.db.prepare(`
            INSERT INTO indicators 
            (threat_id, type, value, value_lower, match_type, weight, context, negation, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        `);

        this._insertExactIndex = this.db.prepare(`
            INSERT OR REPLACE INTO exact_index (value_lower, indicator_id, threat_id, type)
            VALUES (?, ?, ?, ?)
        `);

        this._insertPatternIndex = this.db.prepare(`
            INSERT INTO pattern_index (indicator_id, threat_id, pattern, context)
            VALUES (?, ?, ?, ?)
        `);

        // Lookup statements
        this._exactLookup = this.db.prepare(`
            SELECT e.*, t.*, i.weight, i.context, i.match_type
            FROM exact_index e
            JOIN threats t ON e.threat_id = t.id
            JOIN indicators i ON e.indicator_id = i.id
            WHERE e.value_lower = ? AND t.status = 'active'
        `);

        this._exactLookupByType = this.db.prepare(`
            SELECT e.*, t.*, i.weight, i.context, i.match_type
            FROM exact_index e
            JOIN threats t ON e.threat_id = t.id
            JOIN indicators i ON e.indicator_id = i.id
            WHERE e.value_lower = ? AND e.type = ? AND t.status = 'active'
        `);

        this._getPatterns = this.db.prepare(`
            SELECT p.*, t.*, i.weight, i.match_type
            FROM pattern_index p
            JOIN threats t ON p.threat_id = t.id
            JOIN indicators i ON p.indicator_id = i.id
            WHERE (p.context = ? OR p.context IS NULL) AND t.status = 'active'
        `);

        this._getThreat = this.db.prepare(`
            SELECT * FROM threats WHERE id = ?
        `);

        this._getIndicators = this.db.prepare(`
            SELECT * FROM indicators WHERE threat_id = ?
        `);

        this._searchFTS = this.db.prepare(`
            SELECT t.* FROM threats_fts fts
            JOIN threats t ON fts.id = t.id
            WHERE threats_fts MATCH ? AND t.status = 'active'
            ORDER BY rank
            LIMIT ?
        `);

        this._getThreatsByTier = this.db.prepare(`
            SELECT * FROM threats WHERE tier = ? AND status = 'active'
        `);

        this._getThreatsByTag = this.db.prepare(`
            SELECT * FROM threats WHERE tags LIKE ? AND status = 'active'
        `);

        this._getStats = this.db.prepare(`
            SELECT 
                COUNT(*) as total_threats,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_threats,
                SUM(CASE WHEN tier = 1 THEN 1 ELSE 0 END) as tier1,
                SUM(CASE WHEN tier = 2 THEN 1 ELSE 0 END) as tier2,
                SUM(CASE WHEN tier = 3 THEN 1 ELSE 0 END) as tier3,
                SUM(CASE WHEN tier = 4 THEN 1 ELSE 0 END) as tier4,
                SUM(CASE WHEN tier = 5 THEN 1 ELSE 0 END) as tier5,
                SUM(CASE WHEN tier = 6 THEN 1 ELSE 0 END) as tier6,
                SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END) as critical,
                SUM(CASE WHEN severity = 'high' THEN 1 ELSE 0 END) as high,
                SUM(CASE WHEN severity = 'medium' THEN 1 ELSE 0 END) as medium,
                SUM(CASE WHEN severity = 'low' THEN 1 ELSE 0 END) as low
            FROM threats
        `);

        this._getIndicatorCount = this.db.prepare(`
            SELECT COUNT(*) as count FROM indicators
        `);

        this._getSyncMeta = this.db.prepare(`
            SELECT value FROM sync_meta WHERE key = ?
        `);

        this._setSyncMeta = this.db.prepare(`
            INSERT OR REPLACE INTO sync_meta (key, value, updated) VALUES (?, ?, datetime('now'))
        `);

        this._insertReport = this.db.prepare(`
            INSERT INTO reports (created, type, value, reason, submitted)
            VALUES (datetime('now'), ?, ?, ?, 0)
        `);

        this._getPendingReports = this.db.prepare(`
            SELECT * FROM reports WHERE submitted = 0
        `);

        this._clearIndicators = this.db.prepare(`
            DELETE FROM indicators WHERE threat_id = ?
        `);

        this._clearExactIndex = this.db.prepare(`
            DELETE FROM exact_index WHERE threat_id = ?
        `);

        this._clearPatternIndex = this.db.prepare(`
            DELETE FROM pattern_index WHERE threat_id = ?
        `);
    }

    /**
     * Add or update a threat entry
     */
    upsertThreat(threat) {
        const now = new Date().toISOString();
        
        // Clear existing indicators for updates
        this._clearIndicators.run(threat.id);
        this._clearExactIndex.run(threat.id);
        this._clearPatternIndex.run(threat.id);

        // Insert threat
        this._insertThreat.run(
            threat.id,
            threat.version || 1,
            threat.created || now,
            now,
            threat.status || 'active',
            threat.tier,
            threat.category,
            threat.subcategory || null,
            JSON.stringify(threat.tags || []),
            threat.name,
            threat.description,
            threat.teaching_prompt || null,
            threat.severity,
            threat.confidence || 0.5,
            threat.false_positive_rate || 0.1,
            JSON.stringify(threat.response),
            JSON.stringify(threat.source || {}),
            JSON.stringify(threat.references || []),  // stored as 'refs' in DB
            JSON.stringify(threat.related || []),
            JSON.stringify(threat.mitre_attack || []),
            JSON.stringify(threat.cve || []),
            threat.campaign || null
        );

        // Insert indicators
        for (const indicator of (threat.indicators || [])) {
            const result = this._insertIndicator.run(
                threat.id,
                indicator.type,
                indicator.value,
                indicator.value.toLowerCase(),
                indicator.match_type || 'exact',
                indicator.weight || 1.0,
                indicator.context || null,
                indicator.negation ? 1 : 0,
                JSON.stringify(indicator.metadata || {})
            );

            const indicatorId = result.lastInsertRowid;

            // Index for fast lookup
            if (['exact', 'prefix', 'suffix', 'contains', 'hash'].includes(indicator.match_type || 'exact')) {
                this._insertExactIndex.run(
                    indicator.value.toLowerCase(),
                    indicatorId,
                    threat.id,
                    indicator.type
                );
            }

            if (indicator.match_type === 'regex') {
                this._insertPatternIndex.run(
                    indicatorId,
                    threat.id,
                    indicator.value,
                    indicator.context || null
                );
            }
        }
    }

    /**
     * Exact value lookup (O(1) for domains, IPs, etc.)
     */
    exactLookup(value, type = null) {
        const normalized = value.toLowerCase();
        if (type) {
            return this._exactLookupByType.all(normalized, type);
        }
        return this._exactLookup.all(normalized);
    }

    /**
     * Get all regex patterns for a context
     */
    getPatterns(context) {
        return this._getPatterns.all(context);
    }

    /**
     * Get a threat by ID
     */
    getThreat(id) {
        const threat = this._getThreat.get(id);
        if (!threat) return null;

        // Parse JSON fields
        threat.tags = JSON.parse(threat.tags || '[]');
        threat.response = JSON.parse(threat.response || '{}');
        threat.source = JSON.parse(threat.source || '{}');
        threat.references = JSON.parse(threat.refs || '[]');
        threat.related = JSON.parse(threat.related || '[]');
        threat.mitre_attack = JSON.parse(threat.mitre_attack || '[]');
        threat.cve = JSON.parse(threat.cve || '[]');

        // Get indicators
        threat.indicators = this._getIndicators.all(id).map(ind => ({
            ...ind,
            metadata: JSON.parse(ind.metadata || '{}')
        }));

        return threat;
    }

    /**
     * Full-text search
     */
    search(query, limit = 20) {
        // Escape FTS special characters
        const escaped = query.replace(/["\-*]/g, ' ');
        const threats = this._searchFTS.all(escaped, limit);
        
        return threats.map(t => ({
            ...t,
            tags: JSON.parse(t.tags || '[]'),
            response: JSON.parse(t.response || '{}')
        }));
    }

    /**
     * Get threats by tier
     */
    getThreatsByTier(tier) {
        return this._getThreatsByTier.all(tier).map(t => ({
            ...t,
            tags: JSON.parse(t.tags || '[]'),
            response: JSON.parse(t.response || '{}')
        }));
    }

    /**
     * Get threats by tag
     */
    getThreatsByTag(tag) {
        return this._getThreatsByTag.all(`%"${tag}"%`).map(t => ({
            ...t,
            tags: JSON.parse(t.tags || '[]'),
            response: JSON.parse(t.response || '{}')
        }));
    }

    /**
     * Get database statistics
     */
    getStats() {
        const stats = this._getStats.get();
        const indicators = this._getIndicatorCount.get();
        const lastSync = this._getSyncMeta.get('last_sync');
        const version = this._getSyncMeta.get('db_version');

        return {
            ...stats,
            total_indicators: indicators.count,
            last_sync: lastSync?.value || 'never',
            db_version: version?.value || '1.0.0'
        };
    }

    /**
     * Set sync metadata
     */
    setSyncMeta(key, value) {
        this._setSyncMeta.run(key, value);
    }

    /**
     * Get sync metadata
     */
    getSyncMeta(key) {
        const result = this._getSyncMeta.get(key);
        return result?.value || null;
    }

    /**
     * Add a threat report
     */
    addReport(type, value, reason) {
        this._insertReport.run(type, value, reason);
    }

    /**
     * Get pending reports
     */
    getPendingReports() {
        return this._getPendingReports.all();
    }

    /**
     * Bulk import from JSONL
     */
    importJSONL(jsonlPath) {
        const content = readFileSync(jsonlPath, 'utf8');
        const lines = content.split('\n').filter(l => l.trim() && !l.startsWith('#'));
        
        const importMany = this.db.transaction((threats) => {
            for (const threat of threats) {
                this.upsertThreat(threat);
            }
        });

        const threats = lines.map(line => JSON.parse(line));
        importMany(threats);
        
        return threats.length;
    }

    /**
     * Close database connection
     */
    close() {
        if (this.db) {
            this.db.close();
            this.initialized = false;
        }
    }
}

// Singleton instance
let instance = null;

export function getDatabase(dbPath = null) {
    if (!instance) {
        instance = new ClawGuardDatabase(dbPath);
        instance.init();
    }
    return instance;
}

export function closeDatabase() {
    if (instance) {
        instance.close();
        instance = null;
    }
}
