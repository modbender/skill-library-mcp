/**
 * ClawGuard Detection Engine
 * Multi-layer threat detection with confidence scoring
 */

import { getDatabase } from './database.js';
import { URL } from 'url';
import { logAudit } from './audit.js';
import { loadConfig } from './config.js';

// Result constants
export const RESULT = {
    SAFE: 'safe',
    BLOCK: 'block',
    WARN: 'warn',
    EDUCATE: 'educate',
    ERROR: 'error'
};

// Trusted domain whitelist - checked BEFORE regex patterns to prevent false positives
// These are legitimate major platforms that should never be flagged by typosquat detection
const TRUSTED_DOMAINS = new Set([
    // Major tech platforms
    'github.com',
    'gitlab.com',
    'bitbucket.org',
    'anthropic.com',
    'openai.com',
    'google.com',
    'microsoft.com',
    'apple.com',
    'amazon.com',
    'aws.amazon.com',
    // Cloud providers
    'azure.com',
    'cloudflare.com',
    'digitalocean.com',
    'heroku.com',
    // Developer tools
    'npmjs.com',
    'pypi.org',
    'rubygems.org',
    'crates.io',
    'docker.com',
    'hub.docker.com',
    // Social/communication
    'twitter.com',
    'x.com',
    'discord.com',
    'slack.com',
    'linkedin.com',
    'reddit.com',
    // Other major services
    'youtube.com',
    'wikipedia.org',
    'stackoverflow.com',
    'medium.com',
]);

// Exit codes for CLI
export const EXIT_CODE = {
    SAFE: 0,
    BLOCK: 1,
    WARN: 2,
    ERROR: 3
};

/**
 * Main detection class
 */
export class Detector {
    constructor(options = {}) {
        this.db = getDatabase(options.dbPath);
        this.thresholds = options.thresholds || {
            block: 0.9,
            warn: 0.7,
            educate: 0.5
        };
        this.patternCache = new Map();
    }

    /**
     * Check if a domain is in the trusted whitelist
     * This prevents false positives on legitimate major platforms
     */
    _isTrustedDomain(domain) {
        const normalized = domain.toLowerCase();
        // Check exact match
        if (TRUSTED_DOMAINS.has(normalized)) {
            return true;
        }
        // Check if it's a subdomain of a trusted domain
        for (const trusted of TRUSTED_DOMAINS) {
            if (normalized.endsWith('.' + trusted)) {
                return true;
            }
        }
        return false;
    }

    /**
     * Check a URL for threats
     */
    async checkUrl(url) {
        const start = performance.now();
        const matches = [];
        
        try {
            const parsed = new URL(url);
            
            // Extract components
            const domain = parsed.hostname.toLowerCase();
            const fullUrl = url.toLowerCase();
            
            // CRITICAL: Check trusted domain whitelist FIRST
            // This prevents false positives on legitimate platforms like github.com
            const isTrusted = this._isTrustedDomain(domain);
            
            // 1. Exact domain match (fastest) - still check for exact blocklist entries
            const domainMatches = this.db.exactLookup(domain, 'domain');
            matches.push(...domainMatches.map(m => ({
                ...m,
                matched_value: domain,
                matched_type: 'domain'
            })));

            // 2. Exact URL match
            const urlMatches = this.db.exactLookup(fullUrl, 'url');
            matches.push(...urlMatches.map(m => ({
                ...m,
                matched_value: fullUrl,
                matched_type: 'url'
            })));

            // 3. IP address check (if applicable)
            if (this._isIP(domain)) {
                const ipMatches = this.db.exactLookup(domain, 'ip');
                matches.push(...ipMatches.map(m => ({
                    ...m,
                    matched_value: domain,
                    matched_type: 'ip'
                })));
            }

            // 4. Pattern matching on URL - SKIP for trusted domains to prevent false positives
            // This fixes the critical bug where typosquat regex matched github.com
            if (!isTrusted) {
                const patterns = this._getCompiledPatterns('url');
                for (const pattern of patterns) {
                    if (pattern.regex.test(fullUrl)) {
                        matches.push({
                            ...pattern,
                            matched_value: fullUrl,
                            matched_type: 'pattern'
                        });
                    }
                }
            }

        } catch (e) {
            // Invalid URL - still check as raw string
            const rawMatches = this.db.exactLookup(url.toLowerCase());
            matches.push(...rawMatches);
        }

        return this._buildResult(matches, 'url', url, start);
    }

    /**
     * Check a skill for threats
     */
    async checkSkill(name, author = null) {
        const start = performance.now();
        const matches = [];

        // 1. Exact skill name match
        const nameMatches = this.db.exactLookup(name.toLowerCase(), 'skill_name');
        matches.push(...nameMatches.map(m => ({
            ...m,
            matched_value: name,
            matched_type: 'skill_name'
        })));

        // 2. Author match (if provided)
        if (author) {
            const authorMatches = this.db.exactLookup(author.toLowerCase(), 'skill_author');
            matches.push(...authorMatches.map(m => ({
                ...m,
                matched_value: author,
                matched_type: 'skill_author'
            })));
        }

        // 3. Pattern matching on skill name
        const patterns = this._getCompiledPatterns('skill_name');
        for (const pattern of patterns) {
            if (pattern.regex.test(name.toLowerCase())) {
                matches.push({
                    ...pattern,
                    matched_value: name,
                    matched_type: 'pattern'
                });
            }
        }

        return this._buildResult(matches, 'skill', `${name}${author ? ` by ${author}` : ''}`, start);
    }

    /**
     * Check a command for threats
     */
    async checkCommand(command) {
        const start = performance.now();
        const matches = [];
        const normalized = command.toLowerCase();

        // 1. Extract URLs from command and check them
        const urlRegex = /https?:\/\/[^\s"']+/gi;
        const urls = command.match(urlRegex) || [];
        
        for (const url of urls) {
            try {
                const parsed = new URL(url);
                const domain = parsed.hostname.toLowerCase();
                
                const domainMatches = this.db.exactLookup(domain, 'domain');
                matches.push(...domainMatches.map(m => ({
                    ...m,
                    matched_value: domain,
                    matched_type: 'domain_in_command'
                })));
            } catch (e) {
                // Invalid URL, skip
            }
        }

        // 2. Pattern matching on command
        const patterns = this._getCompiledPatterns('command');
        for (const pattern of patterns) {
            if (pattern.regex.test(normalized)) {
                matches.push({
                    ...pattern,
                    matched_value: command,
                    matched_type: 'command_pattern'
                });
            }
        }

        // 3. Check for dangerous command patterns (built-in)
        const dangerousPatterns = this._getDangerousCommandPatterns();
        for (const dp of dangerousPatterns) {
            if (dp.regex.test(normalized)) {
                matches.push({
                    ...dp,
                    matched_value: command,
                    matched_type: 'dangerous_command'
                });
            }
        }

        return this._buildResult(matches, 'command', command, start);
    }

    /**
     * Check message content for threats (prompt injection, scams)
     */
    async checkMessage(message) {
        const start = performance.now();
        const matches = [];
        const normalized = message.toLowerCase();

        // 1. Pattern matching for prompt injection
        const injectionPatterns = this._getCompiledPatterns('message');
        for (const pattern of injectionPatterns) {
            if (pattern.regex.test(normalized)) {
                // Extract potential domains from the match
                const domainMatches = this._extractDomainsFromText(message);
                // Skip this match if ALL extracted domains are trusted
                if (domainMatches.length > 0 && domainMatches.every(d => this._isTrustedDomain(d))) {
                    continue; // Skip - all domains are whitelisted
                }
                matches.push({
                    ...pattern,
                    matched_value: message.substring(0, 100) + '...',
                    matched_type: 'message_pattern'
                });
            }
        }

        // 2. Check for known scam keywords
        const scamPatterns = this._getScamPatterns();
        for (const sp of scamPatterns) {
            if (sp.regex.test(normalized)) {
                matches.push({
                    ...sp,
                    matched_value: message.substring(0, 100) + '...',
                    matched_type: 'scam_pattern'
                });
            }
        }

        // 3. Extract and check any URLs in message
        const urlRegex = /https?:\/\/[^\s"'<>]+/gi;
        const urls = message.match(urlRegex) || [];
        
        for (const url of urls) {
            const urlResult = await this.checkUrl(url);
            if (urlResult.result !== RESULT.SAFE) {
                matches.push(...urlResult.matches.map(m => ({
                    ...m,
                    matched_type: 'url_in_message'
                })));
            }
        }

        // 4. Check for wallet addresses
        const walletMatches = this._checkWallets(message);
        matches.push(...walletMatches);

        return this._buildResult(matches, 'message', message.substring(0, 200), start);
    }

    /**
     * Generic check - auto-detects type
     */
    async check(input, type = null) {
        if (!type) {
            type = this._detectType(input);
        }

        switch (type) {
            case 'url':
                return this.checkUrl(input);
            case 'domain':
                // Handle bare domain by converting to URL format
                return this.checkUrl(`https://${input}`);
            case 'skill':
                return this.checkSkill(input);
            case 'command':
                return this.checkCommand(input);
            case 'message':
                return this.checkMessage(input);
            default:
                return this.checkMessage(input);
        }
    }

    /**
     * Build result object from matches
     */
    _buildResult(matches, checkType, input, startTime) {
        const duration = performance.now() - startTime;

        if (matches.length === 0) {
            const result = {
                result: RESULT.SAFE,
                exitCode: EXIT_CODE.SAFE,
                checkType,
                matches: [],
                confidence: 0,
                duration_ms: duration,
                message: '✅ No threats detected'
            };
            
            // Log audit
            this._logAudit(checkType, input, 'safe', null, duration);
            
            return result;
        }

        // Deduplicate by threat ID and calculate aggregate confidence
        const threatMap = new Map();
        for (const match of matches) {
            const tid = match.threat_id || match.id;
            if (!threatMap.has(tid)) {
                // Try to get from database, fallback to built-in threat info
                let threat = this.db.getThreat(tid);
                if (!threat) {
                    // Built-in pattern - create synthetic threat object
                    threat = {
                        id: tid,
                        name: match.name || tid,
                        tier: 3, // Default to AI-specific
                        severity: match.severity || 'medium',
                        confidence: match.weight || 0.7,
                        teaching_prompt: null,
                        response: {
                            action: match.severity === 'critical' ? 'block' : 'warn',
                            user_message: `Detected: ${match.name || tid}`
                        }
                    };
                }
                threatMap.set(tid, {
                    threat,
                    weight: 0,
                    matchedIndicators: []
                });
            }
            const entry = threatMap.get(tid);
            entry.weight += (match.weight || 1);
            entry.matchedIndicators.push(match);
        }

        // Find highest confidence threat
        let maxConfidence = 0;
        let primaryThreat = null;

        for (const [tid, data] of threatMap) {
            const confidence = Math.min(1, data.threat.confidence * data.weight);
            if (confidence > maxConfidence) {
                maxConfidence = confidence;
                primaryThreat = data.threat;
            }
        }

        // Determine action based on confidence
        let result, exitCode, message;
        
        if (maxConfidence >= this.thresholds.block) {
            result = RESULT.BLOCK;
            exitCode = EXIT_CODE.BLOCK;
            message = primaryThreat?.response?.user_message || 
                `⛔ BLOCKED: ${primaryThreat?.name || 'Threat detected'}`;
        } else if (maxConfidence >= this.thresholds.warn) {
            result = RESULT.WARN;
            exitCode = EXIT_CODE.WARN;
            message = primaryThreat?.response?.user_message || 
                `⚠️ WARNING: ${primaryThreat?.name || 'Potential threat'}`;
        } else if (maxConfidence >= this.thresholds.educate) {
            result = RESULT.EDUCATE;
            exitCode = EXIT_CODE.SAFE; // Don't block, just inform
            message = `ℹ️ INFO: ${primaryThreat?.name || 'Review recommended'}`;
        } else {
            result = RESULT.SAFE;
            exitCode = EXIT_CODE.SAFE;
            message = '✅ Low confidence matches (likely safe)';
        }

        const finalResult = {
            result,
            exitCode,
            checkType,
            confidence: maxConfidence,
            duration_ms: duration,
            message,
            primaryThreat: primaryThreat ? {
                id: primaryThreat.id,
                name: primaryThreat.name,
                tier: primaryThreat.tier,
                severity: primaryThreat.severity,
                teaching_prompt: primaryThreat.teaching_prompt
            } : null,
            matches: Array.from(threatMap.values()).map(d => ({
                id: d.threat.id,
                name: d.threat.name,
                severity: d.threat.severity,
                confidence: Math.min(1, d.threat.confidence * d.weight),
                matched: d.matchedIndicators.map(m => ({
                    type: m.matched_type,
                    value: m.matched_value
                }))
            }))
        };
        
        // Log audit
        const verdict = result === RESULT.BLOCK ? 'blocked' : 
                       result === RESULT.WARN ? 'warning' : 'safe';
        this._logAudit(checkType, input, verdict, primaryThreat, duration);
        
        return finalResult;
    }

    /**
     * Log to audit trail
     */
    _logAudit(type, input, verdict, threat, duration) {
        const config = loadConfig();
        
        if (!config.audit.enabled) {
            return;
        }
        
        try {
            logAudit({
                type,
                input: input.substring(0, 500), // Truncate long inputs
                verdict,
                threat: threat ? {
                    id: threat.id,
                    name: threat.name,
                    severity: threat.severity
                } : null,
                duration
            });
        } catch (error) {
            // Silent fail - don't break detection
        }
    }

    /**
     * Get compiled regex patterns (cached)
     */
    _getCompiledPatterns(context) {
        if (this.patternCache.has(context)) {
            return this.patternCache.get(context);
        }

        const patterns = this.db.getPatterns(context);
        const compiled = patterns.map(p => ({
            ...p,
            regex: new RegExp(p.pattern, 'i')
        }));

        this.patternCache.set(context, compiled);
        return compiled;
    }

    /**
     * Built-in dangerous command patterns
     */
    _getDangerousCommandPatterns() {
        return [
            {
                regex: /curl.*\|\s*(ba)?sh/i,
                threat_id: 'BUILTIN-PIPE-TO-SHELL',
                name: 'Pipe to shell execution',
                severity: 'high',
                weight: 0.7
            },
            {
                regex: /wget.*\|\s*(ba)?sh/i,
                threat_id: 'BUILTIN-WGET-PIPE',
                name: 'wget pipe to shell',
                severity: 'high',
                weight: 0.7
            },
            {
                regex: /eval\s*\$\(curl/i,
                threat_id: 'BUILTIN-EVAL-CURL',
                name: 'Eval curl output',
                severity: 'critical',
                weight: 0.9
            },
            {
                regex: /rm\s+-rf\s+[\/~]/i,
                threat_id: 'BUILTIN-DESTRUCTIVE-RM',
                name: 'Destructive rm command',
                severity: 'critical',
                weight: 0.8
            },
            {
                regex: /chmod\s+777/i,
                threat_id: 'BUILTIN-INSECURE-CHMOD',
                name: 'Insecure permissions',
                severity: 'medium',
                weight: 0.4
            },
            {
                regex: />(\/dev\/sd|\/dev\/disk)/i,
                threat_id: 'BUILTIN-DISK-WRITE',
                name: 'Direct disk write',
                severity: 'critical',
                weight: 0.9
            }
        ];
    }

    /**
     * Built-in scam patterns
     * Includes classic prompt injection patterns identified in security reviews
     */
    _getScamPatterns() {
        return [
            // Classic prompt injection patterns (enhanced per @ChhotuBot review)
            {
                regex: /ignore\s+(all\s+)?(previous|prior|above)\s+instructions?/i,
                threat_id: 'BUILTIN-PROMPT-INJECTION-CLASSIC-1',
                name: 'Classic prompt injection: ignore previous instructions',
                severity: 'high',
                weight: 0.85
            },
            {
                regex: /disregard\s+(your\s+)?(previous|system)\s+(instructions?|prompt)/i,
                threat_id: 'BUILTIN-PROMPT-INJECTION-CLASSIC-2',
                name: 'Classic prompt injection: disregard instructions',
                severity: 'high',
                weight: 0.85
            },
            {
                regex: /forget\s+(everything|all)\s+(above|previous)/i,
                threat_id: 'BUILTIN-PROMPT-INJECTION-CLASSIC-3',
                name: 'Classic prompt injection: forget everything',
                severity: 'high',
                weight: 0.85
            },
            // Original patterns (kept for backward compatibility)
            {
                regex: /ignore\s+(all\s+|your\s+|previous\s+|prior\s+)?instructions/i,
                threat_id: 'BUILTIN-PROMPT-INJECTION',
                name: 'Prompt injection attempt',
                severity: 'high',
                weight: 0.8
            },
            {
                regex: /you\s+are\s+now\s+(DAN|unrestricted|jailbroken)/i,
                threat_id: 'BUILTIN-JAILBREAK',
                name: 'Jailbreak attempt',
                severity: 'high',
                weight: 0.9
            },
            {
                regex: /\[SYSTEM\]|\[ADMIN\]|\[ROOT\]|\[OVERRIDE\]/i,
                threat_id: 'BUILTIN-FAKE-SYSTEM',
                name: 'Fake system message',
                severity: 'medium',
                weight: 0.6
            },
            {
                regex: /(million|billion)\s+(dollars|usd|euros).*(inheritance|lottery|prize)/i,
                threat_id: 'BUILTIN-NIGERIAN-PRINCE',
                name: 'Advance fee scam pattern',
                severity: 'high',
                weight: 0.7
            },
            {
                regex: /send\s+(your\s+)?(private\s+)?key|export\s+.*private.*key/i,
                threat_id: 'BUILTIN-KEY-THEFT',
                name: 'Private key theft',
                severity: 'critical',
                weight: 0.95
            }
        ];
    }

    /**
     * Check for known malicious wallet addresses
     */
    _checkWallets(message) {
        const matches = [];
        
        // Bitcoin address patterns
        const btcPatterns = [
            /\b(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,62}\b/g,  // Bech32 and legacy
            /\b0x[a-fA-F0-9]{40}\b/g                     // Ethereum
        ];

        for (const pattern of btcPatterns) {
            const walletMatches = message.match(pattern) || [];
            for (const wallet of walletMatches) {
                const dbMatches = this.db.exactLookup(wallet.toLowerCase(), 'wallet');
                matches.push(...dbMatches.map(m => ({
                    ...m,
                    matched_value: wallet,
                    matched_type: 'wallet'
                })));
            }
        }

        return matches;
    }

    /**
     * Detect input type
     */
    _detectType(input) {
        if (/^https?:\/\//i.test(input)) return 'url';
        if (/^(curl|wget|bash|sh|python|node|npm|pip)\s/i.test(input)) return 'command';
        if (input.includes('|') && /\b(sh|bash)\b/.test(input)) return 'command';
        return 'message';
    }

    /**
     * Check if string is an IP address
     */
    _isIP(str) {
        return /^(\d{1,3}\.){3}\d{1,3}$/.test(str) || 
               /^([a-f0-9:]+:+)+[a-f0-9]+$/i.test(str);
    }

    /**
     * Extract domain-like strings from text
     * Used to check if pattern matches contain trusted domains
     */
    _extractDomainsFromText(text) {
        // Match domain patterns: something.tld or subdomain.something.tld
        const domainRegex = /\b([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}\b/gi;
        const matches = text.match(domainRegex) || [];
        return matches.map(d => d.toLowerCase());
    }

    /**
     * Clear pattern cache (after sync)
     */
    clearCache() {
        this.patternCache.clear();
    }
}

// Singleton instance
let detectorInstance = null;

export function getDetector(options = {}) {
    if (!detectorInstance) {
        detectorInstance = new Detector(options);
    }
    return detectorInstance;
}
