#!/usr/bin/env node

/**
 * Epstein Files Search — OpenClaw Skill
 *
 * Search 44,886+ DOJ-released Jeffrey Epstein documents via the
 * DugganUSA public API. Free, no payment or API keys required.
 *
 * Usage:
 *   node scripts/epstein.mjs search --query "search terms" [--limit N]
 *   node scripts/epstein.mjs stats
 *
 * Examples:
 *   node scripts/epstein.mjs search --query "Ghislaine Maxwell" --limit 10
 *   node scripts/epstein.mjs search --query "flight logs" --limit 50
 *   node scripts/epstein.mjs stats
 */

const API_BASE = 'https://analytics.dugganusa.com/api/v1';
const TIMEOUT = 15_000;

// ---------------------------------------------------------------------------
// Argument parsing
// ---------------------------------------------------------------------------

function parseArgs(argv) {
  const args = { _: [] };
  let i = 2; // skip node and script path
  while (i < argv.length) {
    const arg = argv[i];
    if (arg.startsWith('--')) {
      const key = arg.slice(2);
      const next = argv[i + 1];
      if (next && !next.startsWith('--')) {
        args[key] = next;
        i += 2;
      } else {
        args[key] = true;
        i += 1;
      }
    } else {
      args._.push(arg);
      i += 1;
    }
  }
  return args;
}

// ---------------------------------------------------------------------------
// Search command
// ---------------------------------------------------------------------------

async function search(query, limit) {
  const apiUrl = `${API_BASE}/search?q=${encodeURIComponent(query)}&indexes=epstein_files`;
  process.stderr.write(`Searching Epstein files for: "${query}" (limit: ${limit})\n`);

  const res = await fetch(apiUrl, { signal: AbortSignal.timeout(TIMEOUT) });
  if (!res.ok) throw new Error(`API returned ${res.status}: ${res.statusText}`);

  const body = await res.json();
  const hits = (body?.data?.hits || []).slice(0, limit);
  const result = {
    query: body?.data?.query || query,
    totalHits: body?.data?.totalHits ?? 0,
    hits,
  };

  console.log(JSON.stringify(result, null, 2));

  // Print human-readable summary to stderr
  process.stderr.write(`\nFound ${result.totalHits} documents (showing ${hits.length})\n`);
  if (hits.length > 0) {
    process.stderr.write('\n--- Quick Links ---\n');
    hits.forEach((doc, i) => {
      const id = doc.efta_id || doc.id;
      const url = doc.doj_url;
      if (url) {
        process.stderr.write(`${i + 1}. ${id}: ${url}\n`);
      }
    });
  }
}

// ---------------------------------------------------------------------------
// Stats command
// ---------------------------------------------------------------------------

async function stats() {
  process.stderr.write('Fetching index statistics...\n');

  const res = await fetch(`${API_BASE}/search/stats`, {
    signal: AbortSignal.timeout(TIMEOUT),
  });
  if (!res.ok) throw new Error(`API returned ${res.status}: ${res.statusText}`);

  const body = await res.json();
  const epsteinIndex = body?.data?.indexes?.find((i) => i.name === 'epstein_files');

  const result = {
    totalDocuments: epsteinIndex?.numberOfDocuments ?? 0,
    databaseSize: body?.data?.databaseSize ?? 'unknown',
    lastUpdate: body?.data?.lastUpdate ?? 'unknown',
    isIndexing: epsteinIndex?.isIndexing ?? false,
  };

  console.log(JSON.stringify(result, null, 2));
  process.stderr.write(
    `\nIndex: ${result.totalDocuments.toLocaleString()} documents, ` +
      `${result.databaseSize}, indexing: ${result.isIndexing}\n`
  );
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const args = parseArgs(process.argv);
  const command = args._[0];

  if (!command || command === 'help' || command === '--help' || command === '-h') {
    process.stderr.write(`
Epstein Files Search — OpenClaw Skill

Search 44,886+ DOJ-released Jeffrey Epstein documents (Jan 2026).
Free — no API keys, no payment, no accounts required.

Usage: node scripts/epstein.mjs <command> [options]

Commands:
  search    Search documents by keyword, name, topic, or location
  stats     Show index statistics (document count, size, status)

Options:
  --query <terms>   Search query (required for search command)
  --limit <N>       Number of results, 1-500 (default: 10)

Examples:
  node scripts/epstein.mjs search --query "Ghislaine Maxwell" --limit 10
  node scripts/epstein.mjs search --query "flight logs" --limit 50
  node scripts/epstein.mjs search --query "Little St James"
  node scripts/epstein.mjs stats
`);
    process.exit(0);
  }

  if (command === 'stats') {
    try {
      await stats();
    } catch (err) {
      process.stderr.write(`\nError: ${err.message}\n`);
      process.stderr.write('The DugganUSA API may be temporarily unavailable.\n');
      process.exit(1);
    }
    process.exit(0);
  }

  if (command === 'search') {
    const query = args.query || args.q || args._.slice(1).join(' ');
    if (!query) {
      process.stderr.write('Error: --query <search terms> is required\n');
      process.stderr.write(
        'Example: node scripts/epstein.mjs search --query "flight logs"\n'
      );
      process.exit(1);
    }
    const limit = Math.min(Math.max(parseInt(args.limit || '10', 10), 1), 500);

    try {
      await search(query, limit);
    } catch (err) {
      process.stderr.write(`\nError: ${err.message}\n`);
      process.stderr.write('The DugganUSA API may be temporarily unavailable.\n');
      process.exit(1);
    }
    process.exit(0);
  }

  process.stderr.write(`Unknown command: ${command}\n`);
  process.stderr.write('Run: node scripts/epstein.mjs help\n');
  process.exit(1);
}

main();
