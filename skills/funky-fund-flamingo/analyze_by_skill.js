/**
 * evolution-report.js
 *
 * Purpose:
 * - Parse full evolution history without hand-wavy filtering
 * - Extract concrete mutations, fixes, and real work
 * - Group outcomes by skill or system area
 * - Generate a high-signal Markdown report
 *
 * Design goals:
 * - Robust to format drift
 * - Noise-resistant (skip no-op churn)
 * - Deterministic output
 * - Safe to run repeatedly
 */

'use strict';

const fs = require('fs');
const path = require('path');

// -----------------------------------------------------------------------------
// Paths
// -----------------------------------------------------------------------------
const LOG_FILE = path.resolve(__dirname, '../../evolution_history_full.md');
const OUT_FILE = path.resolve(__dirname, '../../evolution_detailed_report.md');

// -----------------------------------------------------------------------------
// Heuristics & Signals
// -----------------------------------------------------------------------------

// Keywords that indicate a *real* evolution (not a no-op scan)
const INTERESTING_KEYWORDS = [
    'fixed',
    'hardened',
    'optimized',
    'patched',
    'created',
    'added',
    'removed',
    'refactored',
    'instrumented',
    'secured',
    'permission',
    'monetiz',
    'billing',
    'pricing',
    'revenue'
];

// Skill path matcher: skills/foo-bar/anything
const SKILL_PATH_REGEX = /skills\/([a-zA-Z0-9\-_]+)/;

// Common status matcher
const STATUS_REGEX = /Status:\s*\[?([A-Z\s_]+)\]?/i;

// Capture explicit “Action:” blocks if present
const ACTION_REGEX = /Action:\s*([\s\S]*?)(?=\n\n|\n[A-Z][a-zA-Z ]+:|$)/i;

// Date matcher (best-effort)
const DATE_REGEX = /\((\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2}.*?)\)/;

// -----------------------------------------------------------------------------
// Utilities
// -----------------------------------------------------------------------------

function exists(file) {
    try {
        return fs.existsSync(file);
    } catch {
        return false;
    }
}

function read(file) {
    try {
        return fs.readFileSync(file, 'utf8');
    } catch {
        return '';
    }
}

function write(file, content) {
    fs.writeFileSync(file, content, 'utf8');
}

function normalize(text) {
    return String(text || '')
        .replace(/\r\n/g, '\n')
        .replace(/\n{3,}/g, '\n\n')
        .trim();
}

function looksInteresting(entry) {
    const lower = entry.toLowerCase();
    return INTERESTING_KEYWORDS.some(k => lower.includes(k));
}

function inferSkill(entry) {
    const match = entry.match(SKILL_PATH_REGEX);
    if (match) return match[1];

    const lower = entry.toLowerCase();
    if (lower.includes('feishu')) return 'feishu-card';
    if (lower.includes('git-sync')) return 'git-sync';
    if (lower.includes('logger')) return 'interaction-logger';
    if (lower.includes('evolve')) return 'funky-fund-flamingo';
    if (lower.includes('memory')) return 'memory-system';

    return 'General / System';
}

function inferIcon(description) {
    const d = description.toLowerCase();
    if (d.includes('optimiz')) return '⚡';
    if (d.includes('secur') || d.includes('harden') || d.includes('permission')) return '🛡️';
    if (d.includes('fix') || d.includes('patch') || d.includes('repair')) return '🚑';
    if (d.includes('creat') || d.includes('add') || d.includes('introduc')) return '✨';
    if (d.includes('monetiz') || d.includes('billing') || d.includes('revenue')) return '💰';
    if (d.includes('remov') || d.includes('cleanup')) return '🧹';
    return '🔧';
}

function extractDescription(entry) {
    const actionMatch = entry.match(ACTION_REGEX);
    if (actionMatch) {
        return normalize(actionMatch[1].replace(/^Action:\s*/i, ''));
    }

    // Fallback: drop headers and status lines, keep substance
    const lines = entry.split('\n').filter(line => {
        const t = line.trim();
        if (!t) return false;
        if (t.startsWith('#')) return false;
        if (/^Status:/i.test(t)) return false;
        return true;
    });

    return normalize(lines.slice(1).join('\n'));
}

function extractStatus(entry) {
    const match = entry.match(STATUS_REGEX);
    return match ? match[1].trim().toUpperCase() : 'UNKNOWN';
}

function extractDate(entry) {
    const match = entry.match(DATE_REGEX);
    return match ? match[1] : 'Unknown';
}

// -----------------------------------------------------------------------------
// Core Analysis
// -----------------------------------------------------------------------------

function analyzeEvolution() {
    if (!exists(LOG_FILE)) {
        console.error('❌ Source evolution history file is missing.');
        return;
    }

    const raw = read(LOG_FILE);
    const entries = normalize(raw)
        .split('\n---\n')
        .map(e => e.trim())
        .filter(Boolean);

    /** @type {Record<string, Array<{date:string,status:string,desc:string}>>} */
    const skillUpdates = {};

    entries.forEach(entry => {
        if (!looksInteresting(entry)) return;

        const skill = inferSkill(entry);
        const status = extractStatus(entry);
        const date = extractDate(entry);
        const desc = extractDescription(entry);

        if (!desc) return;

        if (!skillUpdates[skill]) skillUpdates[skill] = [];

        // Deduplicate by prefix similarity
        const isDuplicate = skillUpdates[skill].some(u =>
            u.desc.slice(0, 40) === desc.slice(0, 40)
        );

        if (!isDuplicate) {
            skillUpdates[skill].push({ date, status, desc });
        }
    });

    // ---------------------------------------------------------------------------
    // Markdown Generation
    // ---------------------------------------------------------------------------

    let md = `# 🧬 Detailed Evolution Report (By Skill)

> Canonical breakdown of meaningful system evolution events.
> Generated from historical evolution logs.

---

`;

    const skills = Object.keys(skillUpdates).sort();

    skills.forEach(skill => {
        md += `## 📦 ${skill}\n\n`;

        skillUpdates[skill].forEach(update => {
            const icon = inferIcon(update.desc);
            md += `### ${icon} ${update.date} — ${update.status}\n\n`;
            md += `${update.desc}\n\n`;
        });

        md += `---\n\n`;
    });

    write(OUT_FILE, md);

    console.log(`✅ Evolution report generated.`);
    console.log(`• Skills covered: ${skills.length}`);
    console.log(`• Output: ${OUT_FILE}`);
}

// -----------------------------------------------------------------------------
// Entry Point
// -----------------------------------------------------------------------------

analyzeEvolution();
