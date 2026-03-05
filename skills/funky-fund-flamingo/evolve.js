/**
 * evolve.js — OpenClaw Evolution Core (Revenue Edition)
 *
 * What this does:
 * - Mines recent OpenClaw session logs (.jsonl) for real failure and friction signals
 * - Builds a mutation prompt with explicit economic and operational priorities
 * - Enumerates installed skills and tags revenue-relevant capabilities
 * - Archives stale logs to keep scans fast
 * - Persists cycle state so progress is measurable across runs
 *
 * What this does NOT do:
 * - It does not publish to ClawHub
 * - It does not execute downstream tools directly
 *
 * Safety / sanity:
 * - Revenue pressure is constrained to legitimate value creation only.
 */

'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');

// -----------------------------
// Env loading (optional)
// -----------------------------
try {
    // Load env from workspace root: ../../.env
    // If dotenv is missing, continue gracefully.
    // eslint-disable-next-line import/no-extraneous-dependencies
    require('dotenv').config({ path: path.resolve(__dirname, '../../.env') });
} catch (_) { }

// -----------------------------
// CLI flags
// -----------------------------
const ARGS = process.argv.slice(2);
const hasFlag = (flag) => ARGS.includes(flag);

const IS_REVIEW_MODE = hasFlag('--review');
const IS_DRY_RUN = hasFlag('--dry-run');
const IS_LOOP = hasFlag('--loop') || hasFlag('--funky-fund-flamingo');

// -----------------------------
// Config
// -----------------------------
const NOW_ISO = new Date().toISOString();
const TODAY = NOW_ISO.split('T')[0];

const WORKSPACE_ROOT = path.resolve(__dirname, '../../');

function clampInt(raw, fallback, min, max) {
    const parsed = Number(raw);
    if (!Number.isFinite(parsed)) return fallback;
    return Math.max(min, Math.min(max, Math.floor(parsed)));
}

function sanitizeAgentName(name) {
    const value = String(name || 'main').trim();
    if (!/^[a-zA-Z0-9_-]{1,64}$/.test(value)) return 'main';
    return value;
}

function realpathIfPossible(target) {
    try {
        return fs.realpathSync.native(target);
    } catch (_) {
        return path.resolve(target);
    }
}

function nearestExistingPath(target) {
    let current = path.resolve(target);
    while (!fs.existsSync(current)) {
        const parent = path.dirname(current);
        if (parent === current) break;
        current = parent;
    }
    return current;
}

function isSubPath(baseDir, maybeChild) {
    const base = realpathIfPossible(baseDir);
    const target = path.resolve(maybeChild);
    const existingBase = realpathIfPossible(nearestExistingPath(target));
    const rel = path.relative(base, existingBase);
    return rel === '' || (!rel.startsWith('..') && !path.isAbsolute(rel));
}

function resolveMemoryDir() {
    const fallback = path.join(WORKSPACE_ROOT, 'memory');
    const requested = process.env.MEMORY_DIR ? path.resolve(process.env.MEMORY_DIR) : fallback;
    return isSubPath(WORKSPACE_ROOT, requested) ? requested : fallback;
}

function pickWritableMemoryDir(primaryDir) {
    const fallbackDir = path.join(__dirname, '.memory');
    const candidates = [primaryDir, fallbackDir];
    for (const dir of candidates) {
        try {
            fs.mkdirSync(dir, { recursive: true });
            const probe = path.join(dir, `.write-probe-${process.pid}-${Date.now()}`);
            fs.writeFileSync(probe, 'ok', { encoding: 'utf8', mode: 0o600 });
            fs.unlinkSync(probe);
            return dir;
        } catch (_) {
            continue;
        }
    }
    return fallbackDir;
}

const MEMORY_DIR = pickWritableMemoryDir(resolveMemoryDir());

const AGENT_NAME = sanitizeAgentName(process.env.AGENT_NAME || 'main');
const AGENT_SESSIONS_DIR = path.join(os.homedir(), `.openclaw/agents/${AGENT_NAME}/sessions`);

const TODAY_LOG = path.join(MEMORY_DIR, `${TODAY}.md`);
const STATE_FILE = path.join(MEMORY_DIR, 'evolution_state.json');
const PERSISTENT_MEMORY_FILE = path.join(MEMORY_DIR, 'funky_fund_flamingo_persistent_memory.json');

const ROOT_MEMORY = path.join(WORKSPACE_ROOT, 'MEMORY.md');
const DIR_MEMORY = path.join(MEMORY_DIR, 'MEMORY.md');
const MEMORY_FILE = fs.existsSync(ROOT_MEMORY) ? ROOT_MEMORY : DIR_MEMORY;

const USER_FILE = path.join(WORKSPACE_ROOT, 'USER.md');

// OpenClaw skill discovery path (many setups mount skills under workspace root)
const SKILLS_DIR = path.join(WORKSPACE_ROOT, 'skills');
const SKILLS_CACHE_FILE = path.join(MEMORY_DIR, 'skills_list_cache.json');

// Context limits
const TARGET_SESSION_BYTES = clampInt(process.env.TARGET_SESSION_BYTES, 64000, 4096, 262144);
const MAX_MEMORY_CHARS = clampInt(process.env.MAX_MEMORY_CHARS, 50000, 1000, 120000);
const MAX_TODAY_LOG_CHARS = clampInt(process.env.MAX_TODAY_LOG_CHARS, 3000, 500, 20000);
const MAX_PERSISTENT_MEMORY_CHARS = clampInt(process.env.MAX_PERSISTENT_MEMORY_CHARS, 8000, 500, 20000);
const LOOP_MIN_INTERVAL_SECONDS = clampInt(process.env.LOOP_MIN_INTERVAL_SECONDS, 900, 60, 86400);

// Maintenance
const MAX_SESSION_LOG_FILES = clampInt(process.env.MAX_SESSION_LOG_FILES, 100, 10, 5000);
const KEEP_SESSION_LOG_FILES = clampInt(process.env.KEEP_SESSION_LOG_FILES, 50, 5, 2000);
const ENABLE_SESSION_ARCHIVE = process.env.EVOLVE_ENABLE_SESSION_ARCHIVE === 'true';

// Economic tagging
const ECONOMIC_KEYWORDS = (process.env.ECONOMIC_KEYWORDS || [
    'pay', 'paid', 'price', 'pricing', 'billing', 'invoice', 'subscription', 'checkout',
    'stripe', 'paypal', 'gumroad', 'shop', 'store', 'cart',
    'lead', 'crm', 'pipeline', 'conversion', 'growth', 'marketing',
    'automation', 'scheduler', 'schedule', 'post', 'publish', 'campaign',
    'api', 'webhook', 'integration', 'analytics', 'reporting',
    'support', 'ticket', 'helpdesk', 'onboarding', 'retention',
    'scrape', 'crawler', 'monitor', 'alerts'
].join(','))
    .split(',')
    .map(s => s.trim().toLowerCase())
    .filter(Boolean);

// Money-mode safety rails (to keep evolution “value creation” not “scam creation”)
const REVENUE_SAFETY_RAILS = `
**SAFETY / ETHICS (Non-Negotiable)**
- Monetization MUST be legitimate: real value, honest claims, legal compliance.
- No fraud, no phishing, no credential theft, no deceptive “get rich quick” patterns.
- No instructions for wrongdoing, evasion, or exploitation of users/platforms.
- Prefer privacy-preserving, opt-in designs and clear user consent.
`;

// -----------------------------
// Small utilities
// -----------------------------
function safeMkdirp(dir) {
    try {
        fs.mkdirSync(dir, { recursive: true });
    } catch (_) { }
}

function safeReadFile(filePath, encoding = 'utf8') {
    try {
        if (!fs.existsSync(filePath)) return null;
        return fs.readFileSync(filePath, encoding);
    } catch (_) {
        return null;
    }
}

function safeWriteFile(filePath, content) {
    try {
        if (!isSubPath(MEMORY_DIR, filePath)) return false;
        safeMkdirp(path.dirname(filePath));
        const tmpPath = `${filePath}.tmp-${process.pid}-${Date.now()}`;
        fs.writeFileSync(tmpPath, content, { encoding: 'utf8', mode: 0o600 });
        fs.renameSync(tmpPath, filePath);
        return true;
    } catch (_) {
        return false;
    }
}

function truncate(str, maxChars) {
    if (!str) return '';
    if (str.length <= maxChars) return str;
    return `${str.slice(0, maxChars)}\n... [TRUNCATED: ${str.length - maxChars} chars remaining]`;
}

function normalizeWhitespace(s) {
    return (s || '').replace(/\n+/g, ' ').replace(/\s+/g, ' ').trim();
}

// -----------------------------
// Session log formatting / reading
// -----------------------------
function formatSessionLog(jsonlContent) {
    const result = [];
    const lines = (jsonlContent || '').split('\n');

    let lastLine = '';
    let repeatCount = 0;

    const flushRepeats = () => {
        if (repeatCount > 0) {
            result.push(`   ... [Repeated ${repeatCount} times] ...`);
            repeatCount = 0;
        }
    };

    for (const line of lines) {
        if (!line.trim()) continue;

        try {
            const data = JSON.parse(line);
            let entry = '';

            // message
            if (data.type === 'message' && data.message) {
                const role = String(data.message.role || 'unknown').toUpperCase();
                let content = '';

                if (Array.isArray(data.message.content)) {
                    content = data.message.content.map((c) => {
                        if (!c) return '';
                        if (c.type === 'text') return c.text || '';
                        if (c.type === 'toolCall') return `[TOOL: ${c.name || 'unknown'}]`;
                        return '';
                    }).join(' ');
                } else if (typeof data.message.content === 'string') {
                    content = data.message.content;
                } else if (data.message.content != null) {
                    content = JSON.stringify(data.message.content);
                }

                // Filters: skip known noise
                const trimmed = (content || '').trim();
                if (!trimmed) continue;
                if (trimmed === 'HEARTBEAT_OK') continue;
                if (trimmed.includes('NO_REPLY')) continue;

                content = normalizeWhitespace(content).slice(0, 300);
                entry = `**${role}**: ${content}`;
            }

            // tool results
            if (
                data.type === 'tool_result' ||
                (data.message && data.message.role === 'toolResult')
            ) {
                let resContent = '';
                if (data.tool_result && typeof data.tool_result.output === 'string') resContent = data.tool_result.output;
                if (data.content) resContent = typeof data.content === 'string' ? data.content : JSON.stringify(data.content);

                resContent = String(resContent || '').trim();
                if (!resContent) continue;

                // Skip trivial success noise
                const low = resContent.toLowerCase();
                if (resContent.length < 50 && (low.includes('success') || low.includes('done'))) continue;

                const preview = normalizeWhitespace(resContent).slice(0, 200);
                entry = `[TOOL RESULT] ${preview}${resContent.length > 200 ? '...' : ''}`;
            }

            if (!entry) continue;

            if (entry === lastLine) {
                repeatCount++;
            } else {
                flushRepeats();
                result.push(entry);
                lastLine = entry;
            }
        } catch (_) {
            // ignore malformed lines
            continue;
        }
    }

    flushRepeats();
    return result.join('\n');
}

function readRecentLog(filePath, sizeBytes = 10000) {
    try {
        if (!fs.existsSync(filePath)) return `[MISSING] ${filePath}`;
        const stats = fs.statSync(filePath);
        const start = Math.max(0, stats.size - sizeBytes);
        const length = stats.size - start;

        // Guard against huge allocations if something goes weird
        const maxLen = Math.min(length, sizeBytes);
        const buffer = Buffer.alloc(maxLen);

        const fd = fs.openSync(filePath, 'r');
        fs.readSync(fd, buffer, 0, buffer.length, start);
        fs.closeSync(fd);

        return buffer.toString('utf8');
    } catch (e) {
        return `[ERROR READING ${filePath}: ${e.message}]`;
    }
}

function readRealSessionLog() {
    try {
        if (!fs.existsSync(AGENT_SESSIONS_DIR)) return '[NO SESSION LOGS FOUND]';

        const files = fs.readdirSync(AGENT_SESSIONS_DIR)
            .filter(f => f.endsWith('.jsonl'))
            .map(f => {
                try {
                    const full = path.join(AGENT_SESSIONS_DIR, f);
                    return { name: f, time: fs.statSync(full).mtime.getTime() };
                } catch (_) {
                    return null;
                }
            })
            .filter(Boolean)
            .sort((a, b) => b.time - a.time);

        if (files.length === 0) return '[NO JSONL FILES]';

        const latestFile = path.join(AGENT_SESSIONS_DIR, files[0].name);
        const latestContentRaw = readRecentLog(latestFile, TARGET_SESSION_BYTES);

        // If the latest session is very short, include previous session for continuity
        if (latestContentRaw.length < TARGET_SESSION_BYTES && files.length > 1) {
            const prevFile = path.join(AGENT_SESSIONS_DIR, files[1].name);
            const needed = Math.max(0, TARGET_SESSION_BYTES - latestContentRaw.length);
            const prevContentRaw = readRecentLog(prevFile, needed);

            return [
                `--- PREVIOUS SESSION (${files[1].name}) ---`,
                formatSessionLog(prevContentRaw),
                '',
                `--- CURRENT SESSION (${files[0].name}) ---`,
                formatSessionLog(latestContentRaw),
            ].join('\n');
        }

        return formatSessionLog(latestContentRaw);
    } catch (e) {
        return `[ERROR READING SESSION LOGS: ${e.message}]`;
    }
}

// -----------------------------
// Maintenance: archive old session logs
// -----------------------------
function performMaintenance() {
    try {
        if (!ENABLE_SESSION_ARCHIVE) return;
        if (!fs.existsSync(AGENT_SESSIONS_DIR)) return;

        const files = fs.readdirSync(AGENT_SESSIONS_DIR).filter(f => f.endsWith('.jsonl'));
        if (files.length < MAX_SESSION_LOG_FILES) return;

        const archiveDir = path.join(AGENT_SESSIONS_DIR, 'archive');
        safeMkdirp(archiveDir);

        const fileStats = files.map(f => {
            try {
                const full = path.join(AGENT_SESSIONS_DIR, f);
                return { name: f, time: fs.statSync(full).mtime.getTime() };
            } catch (_) {
                return null;
            }
        }).filter(Boolean).sort((a, b) => a.time - b.time); // oldest first

        const toArchive = fileStats.slice(0, Math.max(0, fileStats.length - KEEP_SESSION_LOG_FILES));

        for (const f of toArchive) {
            const oldPath = path.join(AGENT_SESSIONS_DIR, f.name);
            const newPath = path.join(archiveDir, f.name);
            try {
                fs.renameSync(oldPath, newPath);
            } catch (_) { }
        }
    } catch (_) { }
}

// -----------------------------
// Health check
// -----------------------------
function checkSystemHealth() {
    const report = [];

    try {
        report.push(`Uptime: ${(os.uptime() / 3600).toFixed(1)}h`);
        report.push(`Node: ${process.version}`);

        const mem = process.memoryUsage();
        report.push(`Agent RSS: ${(mem.rss / 1024 / 1024).toFixed(1)}MB`);

        if (typeof fs.statfsSync === 'function') {
            const stats = fs.statfsSync('/');
            const total = stats.blocks * stats.bsize;
            const free = stats.bfree * stats.bsize;
            const used = total - free;
            const freeGb = (free / 1024 / 1024 / 1024).toFixed(1);
            const usedPercent = Math.round((used / total) * 100);
            report.push(`Disk: ${usedPercent}% (${freeGb}G free)`);
        }
    } catch (_) { }

    try {
        report.push(`PID: ${process.pid}`);
    } catch (_) { }

    // Integrations (local-state-only checks)
    try {
        const issues = [];
        if (!process.env.GEMINI_API_KEY) issues.push('Gemini Key Missing');

        report.push(issues.length ? `⚠️ Integrations: ${issues.join(', ')}` : '✅ Integrations: Nominal');
    } catch (_) { }

    return report.length ? report.join(' | ') : 'Health Check Unavailable';
}

// -----------------------------
// Revenue-focused mutation directive
// -----------------------------
function getMutationDirective(logSignals, focusMode) {
    const errorCount = logSignals.errorCount;
    const isUnstable = errorCount > 2;
    const MONEY_MODES = `
**💰 REVENUE EVOLUTION MODE (Priority #1)**
You MUST prioritize mutations that create economic leverage, such as:
- Monetizable skills (paid features, subscriptions, usage-based billing, premium tiers)
- Lead capture, onboarding flows, CRM hooks, analytics/reporting that users pay for
- Automations that replace paid SaaS features or save measurable time
- Integrations that unlock business workflows (Discord/Telegram/Spotify/etc.)

Deliverables should include at least ONE of:
- A new monetizable capability
- A premium tier / paywall-ready design (even if payment wiring is stubbed)
- A clear plan for pricing + distribution + target customer

Avoid:
- Pure refactors without a path to revenue
- Cosmetic changes without leverage
- Vague “business ideas” without actionable code or clear next step

${REVENUE_SAFETY_RAILS}
`;

    if (isUnstable) {
        return `
**🧬 ADAPTIVE REPAIR MODE (Detected ${errorCount} recent errors)**
${MONEY_MODES}

MANDATORY:
- Fix the root cause(s) of recent errors
- Add guards, validation, and resilient error handling
- Then add ONE small revenue-oriented improvement tied to the fix (e.g., logging for billing metrics, usage counters, admin commands)
`;
    }

    const focusHelp = {
        instrument: '- **Instrument** first: add measurable usage counters and value telemetry.',
        automate: '- **Automate** first: remove repetitive manual tasks with deterministic commands.',
        optimize: '- **Optimize** first: improve cost/performance where it supports monetization.',
        expand: '- **Expand** first: ship one new narrow paid capability.'
    };

    return `
**🧬 FORCED MUTATION MODE (Revenue Edition)**
${MONEY_MODES}

Primary focus for this cycle: **${focusMode}**
${focusHelp[focusMode] || focusHelp.instrument}

Directives (choose one primary, keep revenue priority, and stay within local-only constraints):
- **Build**: Add a new monetizable feature or skill
- **Upgrade**: Convert an existing capability into a premium tier
- **Automate**: Turn a manual workflow into a paid automation
- **Instrument**: Add usage tracking / metrics needed for billing & value proof
- **Ship**: Improve distribution (docs, onboarding, commands, CLI UX) to reach paying users
`;
}

// -----------------------------
// Cycle state
// -----------------------------
function getNextCycleId() {
    let state = { cycleCount: 0, lastRun: 0 };
    try {
        if (fs.existsSync(STATE_FILE)) state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
    } catch (_) { }

    state.cycleCount = (state.cycleCount || 0) + 1;
    state.lastRun = Date.now();

    try {
        safeMkdirp(MEMORY_DIR);
        fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
    } catch (_) { }

    return String(state.cycleCount).padStart(4, '0');
}

function extractLogSignals(logContent) {
    const raw = String(logContent || '');
    const errorCount = (raw.match(/\[ERROR|Error:|Exception:|FAIL|Failed|"isError":true/gi) || []).length;
    const frictionCount = (raw.match(/again|repeat|repeated|manual|friction|stuck|retry/gi) || []).length;
    const monetizationSignalCount = (raw.match(/pricing|billing|pay|subscription|lead|crm|conversion|revenue/gi) || []).length;
    return { errorCount, frictionCount, monetizationSignalCount };
}

function defaultPersistentMemory() {
    return {
        version: 1,
        createdAt: NOW_ISO,
        updatedAt: NOW_ISO,
        nextFocus: 'instrument',
        cycles: []
    };
}

function loadPersistentMemory() {
    try {
        const raw = safeReadFile(PERSISTENT_MEMORY_FILE);
        if (!raw) return defaultPersistentMemory();
        const parsed = JSON.parse(raw);
        if (!parsed || typeof parsed !== 'object') return defaultPersistentMemory();
        const cycles = Array.isArray(parsed.cycles) ? parsed.cycles.slice(-200) : [];
        const nextFocus = typeof parsed.nextFocus === 'string' ? parsed.nextFocus : 'instrument';
        return {
            version: 1,
            createdAt: parsed.createdAt || NOW_ISO,
            updatedAt: NOW_ISO,
            nextFocus,
            cycles
        };
    } catch (_) {
        return defaultPersistentMemory();
    }
}

function computeNextFocus(currentFocus) {
    const sequence = ['instrument', 'automate', 'optimize', 'expand'];
    const idx = sequence.indexOf(currentFocus);
    if (idx === -1) return sequence[0];
    return sequence[(idx + 1) % sequence.length];
}

function appendPersistentCycle(memory, entry) {
    const current = memory && typeof memory === 'object' ? memory : defaultPersistentMemory();
    const next = {
        ...current,
        updatedAt: NOW_ISO,
        nextFocus: computeNextFocus(current.nextFocus),
        cycles: [...(current.cycles || []), entry].slice(-200)
    };
    safeWriteFile(PERSISTENT_MEMORY_FILE, JSON.stringify(next, null, 2));
    return next;
}

function renderPersistentMemorySnippet(memory) {
    const safeMemory = memory && typeof memory === 'object' ? memory : defaultPersistentMemory();
    const slim = {
        nextFocus: safeMemory.nextFocus,
        totalCycles: Array.isArray(safeMemory.cycles) ? safeMemory.cycles.length : 0,
        recentCycles: (safeMemory.cycles || []).slice(-10)
    };
    return truncate(JSON.stringify(slim, null, 2), MAX_PERSISTENT_MEMORY_CHARS);
}

// -----------------------------
// Memory / user snippets
// -----------------------------
function readMemorySnippet() {
    const content = safeReadFile(MEMORY_FILE);
    if (!content) return '[MEMORY.md MISSING]';
    return truncate(content, MAX_MEMORY_CHARS);
}

function readUserSnippet() {
    const content = safeReadFile(USER_FILE);
    if (!content) return '[USER.md MISSING]';
    return content;
}

// -----------------------------
// Skills list / caching / economic tagging
// -----------------------------
function isEconomicSkill(name, desc) {
    const n = String(name || '').toLowerCase();
    const d = String(desc || '').toLowerCase();
    return ECONOMIC_KEYWORDS.some(k => n.includes(k) || d.includes(k));
}

function extractSkillDesc(skillDir, name) {
    // Prefer package.json description
    try {
        const pkgPath = path.join(skillDir, name, 'package.json');
        if (fs.existsSync(pkgPath)) {
            // require() caches; use readFile+JSON to avoid stale results in long runs
            const raw = fs.readFileSync(pkgPath, 'utf8');
            const pkg = JSON.parse(raw);
            if (pkg && pkg.description) return String(pkg.description);
        }
    } catch (_) { }

    // Next, SKILL.md heuristic (frontmatter-ish or first meaningful line)
    try {
        const skillMdPath = path.join(skillDir, name, 'SKILL.md');
        if (!fs.existsSync(skillMdPath)) return 'No description';

        const skillMd = fs.readFileSync(skillMdPath, 'utf8');
        const yamlMatch = skillMd.match(/^description:\s*(.*)$/mi);
        if (yamlMatch && yamlMatch[1]) return String(yamlMatch[1]).trim();

        const lines = skillMd.split('\n');
        for (const line of lines) {
            const t = line.trim();
            if (!t) continue;
            if (t.startsWith('#')) continue;
            if (t.startsWith('---')) continue;
            if (t.startsWith('```')) continue;
            return t;
        }
    } catch (_) { }

    return 'No description';
}

function loadSkillsList() {
    try {
        if (!fs.existsSync(SKILLS_DIR)) return { list: '[NO SKILLS DIR FOUND]', count: 0 };

        // Cache: if skills dir mtime older than cache mtime, use cache
        let useCache = false;
        const dirStats = fs.statSync(SKILLS_DIR);

        if (fs.existsSync(SKILLS_CACHE_FILE)) {
            try {
                const cacheStats = fs.statSync(SKILLS_CACHE_FILE);
                if (cacheStats.mtimeMs > dirStats.mtimeMs) useCache = true;
            } catch (_) { }
        }

        if (useCache) {
            try {
                const cached = JSON.parse(fs.readFileSync(SKILLS_CACHE_FILE, 'utf8'));
                if (cached && typeof cached.list === 'string') {
                    return { list: cached.list, count: (cached.count || 0) };
                }
            } catch (_) { }
        }

        const entries = fs.readdirSync(SKILLS_DIR, { withFileTypes: true })
            .filter(d => d.isDirectory())
            .map(d => d.name)
            .sort((a, b) => a.localeCompare(b));

        const lines = [];
        let econCount = 0;

        for (const name of entries) {
            const descRaw = extractSkillDesc(SKILLS_DIR, name);
            const desc = truncate(normalizeWhitespace(descRaw), 120).replace(/\n/g, ' ');
            const econ = isEconomicSkill(name, descRaw);
            if (econ) econCount++;

            lines.push(`- **${name}**${econ ? ' 💰' : ''}: ${desc}`);
        }

        const list = lines.join('\n');
        safeWriteFile(SKILLS_CACHE_FILE, JSON.stringify({ list, count: entries.length, econCount }, null, 2));

        return { list, count: entries.length, econCount };
    } catch (e) {
        return { list: `Error listing skills: ${e.message}`, count: 0 };
    }
}

// -----------------------------
// Reporting directive (revenue-first)
// -----------------------------
function buildReportingDirective(cycleId) {
    let reporting = `3.  **📝 REPORT**:
- Use \`message\` tool.
- **Title**: 💰 Revenue Evolution ${cycleId}
- **Status**: [SUCCESS / BLOCKED]
- **Economic Impact**:
  - Who would pay (target user/customer)
  - What problem it solves (in one sentence)
  - Why it beats the alternatives
  - How it can be priced (tier idea or usage-based)
- **Changes**: List exactly what code/files changed
- **Next Monetization Step**: One concrete next action (integration, onboarding, pricing page, usage tracking)
`;

    if (process.env.EVOLVE_REPORT_DIRECTIVE) {
        reporting = process.env.EVOLVE_REPORT_DIRECTIVE.replace('__CYCLE_ID__', cycleId);
    }

    if (IS_REVIEW_MODE) {
        reporting += `\n- **REVIEW PAUSE**: After proposing changes but BEFORE applying significant edits, ask the user for confirmation.\n`;
    }

    return reporting;
}

// -----------------------------
// Sync directive (optional)
// -----------------------------
function buildSyncDirective() {
    return `// Step F (Workspace): Local-only mode. Do NOT push, publish, or call external services.`;
}

// -----------------------------
// Prompt builder
// -----------------------------
function buildPrompt({
    cycleId,
    healthReport,
    scanTimeMs,
    memorySizeBytes,
    skillsList,
    memorySnippet,
    persistentMemorySnippet,
    userSnippet,
    todayLogSnippet,
    sessionTranscript,
    mutationDirective,
    reportingDirective,
    syncDirective
}) {
    const extraModes = process.env.EVOLVE_EXTRA_MODES || '';

    // Make “money” the success function, not code beauty.
    // Keep it grounded and safe.
    return `
*** 🧬 OPENCLAW EVOLUTION LOOP (REVENUE EDITION) [${NOW_ISO}] ***

**MISSION**
You are a **Recursive, Self-Improving, Revenue-Seeking System**.
Your job is to build skills and improvements that create **legitimate economic leverage**:
- Paid utility (premium features, subscriptions, usage-based)
- Lead capture + business workflow integrations
- Automations that replace paid SaaS or save measurable time
- Instrumentation needed for billing, proof of value, and retention

Code Singularity only counts if it also produces economic value.

${REVENUE_SAFETY_RAILS}

**CONTEXT [Runtime State]**
- **System Health**: ${healthReport}
- **Scan Duration**: ${scanTimeMs}ms
- **Memory Size**: ${memorySizeBytes} bytes
- **Skills Available**:
${skillsList}

**CONTEXT [Global Memory (MEMORY.md)]**
\`\`\`
${memorySnippet}
\`\`\`

**CONTEXT [Persistent Funky Fund Flamingo Memory]**
\`\`\`
${persistentMemorySnippet}
\`\`\`

**CONTEXT [User Registry (USER.md)]**
\`\`\`
${userSnippet}
\`\`\`

**CONTEXT [Recent Memory Snippet]**
\`\`\`
${todayLogSnippet}
\`\`\`

**CONTEXT [REAL SESSION TRANSCRIPT (RAW BRAIN DUMP)]**
\`\`\`
${sessionTranscript}
\`\`\`

${mutationDirective}

**EXECUTION DIRECTIVES (The Loop)**

1. **🔍 INTROSPECT (Scan)**
   - Read the transcript. Identify errors, friction, unmet needs, and missed opportunities.
   - Identify “value leaks”: repeated manual work, missing automation, missing metrics.
   - Identify monetizable angles: premium commands, business integrations, reporting.

2. **🛠️ MUTATE (Act)**
   - Repair any breaking issues if present.
   - Then implement at least ONE **revenue-oriented** improvement:
     - Add a monetizable capability, premium tier, or usage metric needed for pricing/billing.
     - Improve distribution/onboarding so real users can adopt it.

   Modes:
   - **Mode A (Repair)**: Fix bugs and harden reliability
   - **Mode B (Optimize)**: Refactor only when it enables economic outcomes (speed, cost, scalability)
   - **Mode C (Expand)**: Create a new capability/skill with a clear paying customer
   - **Mode D (Instrument)**: Add usage tracking / analytics / admin dashboards
   - **Mode E (Personalization)**: Adapt to USER.md + MEMORY.md preferences and workflow

   ${extraModes}

${reportingDirective}

4. **💾 PERSIST (LOCAL ONLY)**
   - **Step A (Local)**: Save all file changes.
   - **Step B (External Systems)**:
     - Publishing is disabled. Do NOT attempt to publish.
     - Do NOT push to remote git from this cycle.

   ${syncDirective}

5. **♾️ OPTIONAL LOOPING**
   If the loop flags are enabled, schedule the next cycle:
   - Only if it is safe and stable to continue.
   - Pace cycles slowly: minimum interval **${LOOP_MIN_INTERVAL_SECONDS}s** between iterations.
   - Apply one primary mutation per cycle and measure impact before next cycle.

   ${IS_LOOP
            ? 'Loop flag is enabled. Only schedule a local rerun plan; do NOT trigger external tools or remote actions.'
            : '// Looping disabled (no --loop / --funky-fund-flamingo flag).'}

**HARD CONSTRAINT**
If you cannot find a monetizable improvement, you MUST:
- Propose a new paid skill idea with a clear user + pricing model, AND
- Explain exactly what is blocking implementation (missing token, missing API, missing permission).

/* You have permission to edit files. Proceed. Revenue evolution is mandatory. */
`.trim();
}

// -----------------------------
// Main run
// -----------------------------
async function run() {
    const startTime = Date.now();

    safeMkdirp(MEMORY_DIR);

    // Keep the sessions folder fast
    performMaintenance();

    const recentMasterLog = readRealSessionLog();
    const logSignals = extractLogSignals(recentMasterLog);
    const todayLogRaw = readRecentLog(TODAY_LOG, 20000);
    const memorySnippet = readMemorySnippet();
    const userSnippet = readUserSnippet();
    const persistentMemory = loadPersistentMemory();

    const cycleNum = getNextCycleId();
    const cycleId = `Cycle #${cycleNum}`;

    const skills = loadSkillsList();
    const skillsList = skills.list;

    const mutationDirective = getMutationDirective(logSignals, persistentMemory.nextFocus);
    const healthReport = checkSystemHealth();

    const scanTimeMs = Date.now() - startTime;
    const memorySizeBytes = (() => {
        try {
            return fs.existsSync(MEMORY_FILE) ? fs.statSync(MEMORY_FILE).size : 0;
        } catch (_) {
            return 0;
        }
    })();

    const reportingDirective = buildReportingDirective(cycleId);
    const syncDirective = buildSyncDirective();

    const todayLogSnippet = truncate(String(todayLogRaw || ''), MAX_TODAY_LOG_CHARS);
    const sessionTranscript = recentMasterLog;
    const persistentMemorySnippet = renderPersistentMemorySnippet(persistentMemory);

    const prompt = buildPrompt({
        cycleId,
        healthReport,
        scanTimeMs,
        memorySizeBytes,
        skillsList,
        memorySnippet,
        persistentMemorySnippet,
        userSnippet,
        todayLogSnippet,
        sessionTranscript,
        mutationDirective,
        reportingDirective,
        syncDirective
    });

    // In dry-run mode, write the prompt to a file too (useful for debugging)
    if (IS_DRY_RUN) {
        const outPath = path.join(MEMORY_DIR, `evolution_prompt_${TODAY}_${cycleNum}.txt`);
        safeWriteFile(outPath, prompt);
    }

    appendPersistentCycle(persistentMemory, {
        cycleId,
        at: NOW_ISO,
        loopMode: IS_LOOP,
        reviewMode: IS_REVIEW_MODE,
        dryRun: IS_DRY_RUN,
        focus: persistentMemory.nextFocus,
        signals: logSignals
    });

    // Print prompt for upstream runner to feed into model
    console.log(prompt);

    return prompt;
}

module.exports = { run };
