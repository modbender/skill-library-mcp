/**
 * funky-fund-flamingo-history-extractor.js
 *
 * Purpose:
 * - Parse Funky Fund Flamingo prompt logs at scale
 * - Extract cycle reports embedded in feishu-card send commands
 * - Reconstruct a hard chronological evolution history
 *
 * Important Semantics:
 * - The source log contains the *PROMPTS GENERATED* by the engine,
 *   not the LLM's free-form response.
 * - Therefore, the feishu-card command embedded in the prompt is the
 *   authoritative record of the intended evolution report.
 *
 * This script intentionally treats the prompt as truth.
 */

'use strict';

const fs = require('fs');
const path = require('path');

// -----------------------------------------------------------------------------
// Paths
// -----------------------------------------------------------------------------
const LOG_FILE = path.resolve(__dirname, '../../memory/funky_fund_flamingo_evolution.log');
const OUT_FILE = path.resolve(__dirname, '../../evolution_history.md');

// -----------------------------------------------------------------------------
// Regex Patterns
// -----------------------------------------------------------------------------

// 🧬 Cycle Start: Sun Feb  1 19:17:44 UTC 2026
const CYCLE_START_REGEX = /🧬 Cycle Start:\s*(.*)$/;

// node skills/feishu-card/send.js --title "..." --color ... --text "..."
const FEISHU_CMD_REGEX =
    /node\s+skills\/feishu-card\/send\.js\s+--title\s+"([^"]+)"[\s\S]*?--text\s+"([\s\S]*?)"/;

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

function parseDate(dateStr) {
    try {
        const d = new Date(dateStr);
        return Number.isNaN(d.getTime()) ? null : d;
    } catch {
        return null;
    }
}

function toCST(date) {
    return date.toLocaleString('en-US', {
        timeZone: 'Asia/Shanghai',
        hour12: false,
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// -----------------------------------------------------------------------------
// Core Parsing Logic
// -----------------------------------------------------------------------------

function parseLog() {
    if (!exists(LOG_FILE)) {
        console.log('⚠️  Funky Fund Flamingo evolution log not found.');
        return;
    }

    const content = read(LOG_FILE);
    const lines = content.split('\n');

    /** @type {Array<{ts: Date, title: string, text: string, id: string}>} */
    const reports = [];

    let currentTimestamp = null;

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];

        // -------------------------------------------------------------------------
        // 1. Detect cycle start timestamps
        // -------------------------------------------------------------------------
        const tsMatch = line.match(CYCLE_START_REGEX);
        if (tsMatch) {
            const parsed = parseDate(tsMatch[1].trim());
            currentTimestamp = parsed;
            continue;
        }

        // -------------------------------------------------------------------------
        // 2. Detect feishu-card report command inside prompt
        // -------------------------------------------------------------------------
        const cmdMatch = line.match(FEISHU_CMD_REGEX);
        if (!cmdMatch) continue;

        const title = cmdMatch[1];
        let text = cmdMatch[2];

        // Unescape prompt-encoded text
        text = text
            .replace(/\\n/g, '\n')
            .replace(/\\"/g, '"')
            .trim();

        if (!currentTimestamp) {
            // If timestamp is missing, still record but mark it
            currentTimestamp = new Date(0);
        }

        reports.push({
            ts: currentTimestamp,
            title,
            text,
            id: title // Cycle title acts as a stable ID
        });
    }

    // ---------------------------------------------------------------------------
    // Deduplication & Ordering
    // ---------------------------------------------------------------------------

    /**
     * Deduplication strategy:
     * - Prompts are appended chronologically
     * - Same cycle title should only appear once
     * - Keep the LAST occurrence (most complete)
     */
    const unique = {};
    for (const r of reports) {
        unique[r.id] = r;
    }

    const ordered = Object.values(unique).sort((a, b) => a.ts - b.ts);

    // ---------------------------------------------------------------------------
    // Markdown Generation
    // ---------------------------------------------------------------------------

    let md = `# 🧬 Evolution History (Funky Fund Flamingo Extracted)

> This document is auto-generated from the Funky Fund Flamingo prompt log.
> It reflects the *intended evolution reports* produced by the system.

---

`;

    ordered.forEach(r => {
        const dateLabel =
            r.ts.getTime() === 0 ? 'Unknown Time' : toCST(r.ts);

        md += `## ${r.title}\n`;
        md += `**Timestamp (CST)**: ${dateLabel}\n\n`;
        md += `${normalize(r.text)}\n\n`;
        md += `---\n\n`;
    });

    write(OUT_FILE, md);

    console.log('✅ Funky Fund Flamingo evolution history extracted.');
    console.log(`• Cycles captured: ${ordered.length}`);
    console.log(`• Output file: ${OUT_FILE}`);
}

// -----------------------------------------------------------------------------
// Entry Point
// -----------------------------------------------------------------------------

parseLog();
