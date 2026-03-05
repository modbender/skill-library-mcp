/**
 * git-evolution-history.js
 *
 * Purpose:
 * - Extract evolution commits from git history
 * - Preserve strict chronology (oldest → newest)
 * - Normalize timestamps to CST (UTC+8)
 * - Generate a clean, high-signal Markdown report
 *
 * Assumptions:
 * - Evolution commits are tagged with the keyword "🧬 Evolution"
 * - Git is available and the script is run inside a git repository
 * - Commit bodies may be multiline
 *
 * Output:
 * - memory/evolution_history.md
 */

'use strict';

const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// -----------------------------------------------------------------------------
// Configuration
// -----------------------------------------------------------------------------

// Separator for parsing git log output (intentionally obscure)
const SEP = '|||';

// Root of the git repository
const REPO_ROOT = path.resolve(__dirname, '../../');

// Output location
const OUT_FILE = path.resolve(__dirname, '../../memory/evolution_history.md');

// Git log filter
const EVOLUTION_GREP = '🧬 Evolution';

// Timezone offset for CST (UTC+8)
const CST_OFFSET_MS = 8 * 60 * 60 * 1000;

// -----------------------------------------------------------------------------
// Utilities
// -----------------------------------------------------------------------------

function write(file, content) {
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, content, 'utf8');
}

function normalize(text) {
    return String(text || '')
        .replace(/\r\n/g, '\n')
        .replace(/\n{3,}/g, '\n\n')
        .trim();
}

function toCST(date) {
    const shifted = new Date(date.getTime() + CST_OFFSET_MS);
    return shifted.toISOString().replace('T', ' ').substring(0, 19);
}

// -----------------------------------------------------------------------------
// Core Logic
// -----------------------------------------------------------------------------

function generateEvolutionHistory() {
    let output;

    try {
        /**
         * Git command explanation:
         * --reverse : chronological order (oldest → newest)
         * --grep    : filter commits containing evolution marker
         * --format  : machine-parseable output using a custom separator
         */
        console.log('🔍 Executing git log for evolution history...');
        output = execFileSync('git', [
            'log',
            '--reverse',
            `--grep=${EVOLUTION_GREP}`,
            `--format=%H${SEP}%ai${SEP}%an${SEP}%s${SEP}%b`
        ], {
            encoding: 'utf8',
            cwd: REPO_ROOT,
            maxBuffer: 1024 * 1024 * 20 // 20MB safety buffer
        });
    } catch (err) {
        console.error('❌ Failed to execute git log.');
        console.error(err.message);
        process.exit(1);
    }

    if (!output || !output.trim()) {
        console.warn('⚠️  No evolution commits found.');
        write(
            OUT_FILE,
            '# 🧬 Evolution History\n\n> No evolution commits found.\n'
        );
        return;
    }

    const lines = output
        .split('\n')
        .map(l => l.trim())
        .filter(Boolean);

    let markdown = `# 🧬 Evolution History (Time Sequence)

> **Filter**: "${EVOLUTION_GREP}"  
> **Order**: Oldest → Newest  
> **Timezone**: CST (UTC+8)

---

`;

    let count = 0;

    lines.forEach(line => {
        const parts = line.split(SEP);

        if (parts.length < 4) return;

        const [
            fullHash,
            isoDate,
            author,
            subject,
            body = ''
        ] = parts;

        let parsedDate;
        try {
            parsedDate = new Date(isoDate);
            if (Number.isNaN(parsedDate.getTime())) throw new Error('Invalid date');
        } catch {
            parsedDate = new Date(0);
        }

        const timeStr =
            parsedDate.getTime() === 0
                ? 'Unknown Time'
                : toCST(parsedDate);

        markdown += `## ${timeStr}\n`;
        markdown += `- **Commit**: \`${fullHash.slice(0, 7)}\`\n`;
        markdown += `- **Author**: ${author}\n`;
        markdown += `- **Subject**: ${subject}\n`;

        if (body.trim()) {
            const formattedBody = normalize(body)
                .split('\n')
                .map(l => `> ${l}`)
                .join('\n');

            markdown += `- **Details**:\n${formattedBody}\n`;
        }

        markdown += '\n';
        count++;
    });

    write(OUT_FILE, markdown);

    console.log('✅ Evolution history generated successfully.');
    console.log(`• Commits captured: ${count}`);
    console.log(`• Output file: ${OUT_FILE}`);
}

// -----------------------------------------------------------------------------
// Entry Point
// -----------------------------------------------------------------------------

generateEvolutionHistory();
