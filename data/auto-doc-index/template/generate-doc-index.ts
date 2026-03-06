#!/usr/bin/env npx tsx
/**
 * Auto-generates the index table in ADR and Pitfall README.md files.
 *
 * Scans *.md files in the target directory, parses frontmatter from each,
 * and replaces the content between <!-- INDEX:START --> / <!-- INDEX:END -->
 * markers in README.md. Content outside the markers is preserved.
 *
 * Usage:
 *   npx tsx scripts/generate-doc-index.ts adr
 *   npx tsx scripts/generate-doc-index.ts pitfall
 *   npx tsx scripts/generate-doc-index.ts all       # both
 *
 * Zero external dependencies — uses only Node.js built-ins.
 */

import { readdirSync, readFileSync, writeFileSync, existsSync } from 'fs';
import { join, basename } from 'path';

const DOC_ROOT = join(__dirname, '..', 'doc');

// ---------------------------------------------------------------------------
// Parsers
// ---------------------------------------------------------------------------

interface AdrEntry {
  num: string;
  title: string;
  status: string;
  date: string;
  file: string;
}

interface PitEntry {
  id: string;
  title: string;
  area: string;
  severity: string;
  status: string;
  file: string;
}

function parseAdr(filePath: string): AdrEntry | null {
  const content = readFileSync(filePath, 'utf-8');
  const name = basename(filePath);

  // Extract number from filename: 001-slug.md → "001"
  const numMatch = name.match(/^(\d+)-/);
  if (!numMatch) return null;

  // Title from H1: # ADR-NNN: Title
  const titleMatch = content.match(/^#\s+ADR-\d+:\s*(.+)$/m);
  const title = titleMatch?.[1]?.trim() ?? name;

  // Status: try "Status: value" line first, then "## Status\n\nvalue"
  let status = 'unknown';
  const statusLineMatch = content.match(/^Status:\s*(.+)$/im);
  if (statusLineMatch) {
    status = statusLineMatch[1].trim();
  } else {
    const statusSectionMatch = content.match(/^##\s+Status\s*\n+(\w+)/m);
    if (statusSectionMatch) {
      status = statusSectionMatch[1].trim();
    }
  }

  // Date: try "Date: value" line
  let date = '—';
  const dateMatch = content.match(/^Date:\s*(\d{4}-\d{2}-\d{2})/m);
  if (dateMatch) {
    date = dateMatch[1];
  }

  return { num: numMatch[1], title, status, date, file: name };
}

function parsePitfall(filePath: string): PitEntry | null {
  const content = readFileSync(filePath, 'utf-8');
  const name = basename(filePath);

  const idMatch = name.match(/^(PIT-\d+)/);
  if (!idMatch) return null;

  const titleMatch = content.match(/^#\s+PIT-\d+:\s*(.+)$/m);
  const title = titleMatch?.[1]?.trim() ?? name;

  const field = (key: string): string => {
    const m = content.match(new RegExp(`^\\*\\*${key}:\\*\\*\\s*(.+)$`, 'mi'));
    return m?.[1]?.trim() ?? '—';
  };

  return {
    id: idMatch[1],
    title,
    area: field('Area'),
    severity: field('Severity'),
    status: field('Status'),
    file: name,
  };
}

// ---------------------------------------------------------------------------
// Table generators
// ---------------------------------------------------------------------------

function generateAdrTable(entries: AdrEntry[]): string {
  const sorted = entries.sort((a, b) => a.num.localeCompare(b.num));
  const rows = sorted.map(
    (e) => `| ${e.num} | [${e.title}](${e.file}) | ${e.status} | ${e.date} |`,
  );
  return [
    '| ADR | Title | Status | Date |',
    '|-----|-------|--------|------|',
    ...rows,
  ].join('\n');
}

function generatePitfallTable(entries: PitEntry[]): string {
  const sorted = entries.sort((a, b) => a.id.localeCompare(b.id));
  const rows = sorted.map(
    (e) =>
      `| [${e.id}](${e.file}) | ${e.title} | ${e.area} | ${e.severity} | ${e.status} |`,
  );
  return [
    '| ID | Title | Area | Severity | Status |',
    '|----|-------|------|----------|--------|',
    ...rows,
  ].join('\n');
}

// ---------------------------------------------------------------------------
// README injection (marker-based)
// ---------------------------------------------------------------------------

const START_MARKER = '<!-- INDEX:START -->';
const END_MARKER = '<!-- INDEX:END -->';

function injectIndex(readmePath: string, table: string): void {
  if (!existsSync(readmePath)) {
    console.error(`README not found: ${readmePath}`);
    process.exit(1);
  }

  const content = readFileSync(readmePath, 'utf-8');
  const startIdx = content.indexOf(START_MARKER);
  const endIdx = content.indexOf(END_MARKER);

  let updated: string;
  if (startIdx !== -1 && endIdx !== -1) {
    const before = content.slice(0, startIdx + START_MARKER.length);
    const after = content.slice(endIdx);
    updated = `${before}\n${table}\n${after}`;
  } else {
    console.error(
      `Markers not found in ${readmePath}. Add ${START_MARKER} and ${END_MARKER} around the index section.`,
    );
    process.exit(1);
  }

  writeFileSync(readmePath, updated, 'utf-8');
  console.log(`✅ Updated ${readmePath}`);
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

function processAdr(): void {
  const dir = join(DOC_ROOT, 'adr');
  const files = readdirSync(dir)
    .filter((f) => /^\d{3}-.*\.md$/.test(f))
    .map((f) => join(dir, f));

  const entries = files.map(parseAdr).filter(Boolean) as AdrEntry[];
  const table = generateAdrTable(entries);
  injectIndex(join(dir, 'README.md'), table);
  console.log(`   ${entries.length} ADR entries indexed`);
}

function processPitfall(): void {
  const dir = join(DOC_ROOT, 'pitfall');
  const files = readdirSync(dir)
    .filter((f) => /^PIT-\d+.*\.md$/.test(f))
    .map((f) => join(dir, f));

  const entries = files.map(parsePitfall).filter(Boolean) as PitEntry[];
  const table = generatePitfallTable(entries);
  injectIndex(join(dir, 'README.md'), table);
  console.log(`   ${entries.length} Pitfall entries indexed`);
}

const mode = process.argv[2] ?? 'all';
if (mode === 'adr' || mode === 'all') processAdr();
if (mode === 'pitfall' || mode === 'all') processPitfall();
if (!['adr', 'pitfall', 'all'].includes(mode)) {
  console.error('Usage: generate-doc-index.ts [adr|pitfall|all]');
  process.exit(1);
}
