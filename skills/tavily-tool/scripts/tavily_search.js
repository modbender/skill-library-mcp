#!/usr/bin/env node
/**
 * Tavily Search CLI
 *
 * - Reads TAVILY_API_KEY from env only.
 * - Prints full JSON response to stdout.
 * - Prints a simple list of URLs to stderr by default (can be disabled).
 */

const TAVILY_ENDPOINT = 'https://api.tavily.com/search';

function usage(msg) {
  if (msg) console.error(`Error: ${msg}\n`);
  console.error(`Usage:
  tavily_search.js --query "..." [--max_results 5] [--include_domains a.com,b.com] [--exclude_domains x.com,y.com]

Options:
  --query, -q              Search query (required)
  --max_results, -n        Max results (default: 5; clamped to 0..20)
  --include_domains        Comma-separated domains to include
  --exclude_domains        Comma-separated domains to exclude
  --urls-stderr            Print URL list to stderr (default: true)
  --no-urls-stderr         Disable URL list to stderr
  --urls-only              Print URLs (one per line) to stdout instead of JSON
  --help, -h               Show help

Env:
  TAVILY_API_KEY            (required) Tavily API key

Exit codes:
  0 success
  2 usage / missing required inputs
  3 network / HTTP error
  4 invalid JSON response
`);
}

function parseArgs(argv) {
  const out = {
    query: null,
    max_results: 5,
    include_domains: null,
    exclude_domains: null,
    urls_stderr: true,
    urls_only: false,
    help: false,
  };

  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--help' || a === '-h') out.help = true;
    else if (a === '--query' || a === '-q') out.query = argv[++i];
    else if (a === '--max_results' || a === '-n') out.max_results = Number(argv[++i]);
    else if (a === '--include_domains') out.include_domains = argv[++i];
    else if (a === '--exclude_domains') out.exclude_domains = argv[++i];
    else if (a === '--urls-stderr') out.urls_stderr = true;
    else if (a === '--no-urls-stderr') out.urls_stderr = false;
    else if (a === '--urls-only') out.urls_only = true;
    else return { error: `Unknown arg: ${a}` };
  }

  if (Number.isNaN(out.max_results) || !Number.isFinite(out.max_results)) {
    return { error: `--max_results must be a number` };
  }
  // Tavily allows 0..20; clamp to stay in range.
  out.max_results = Math.max(0, Math.min(20, Math.trunc(out.max_results)));

  const csvToArray = (s) => {
    if (!s) return null;
    const arr = s.split(',').map(x => x.trim()).filter(Boolean);
    return arr.length ? arr : null;
  };

  out.include_domains = csvToArray(out.include_domains);
  out.exclude_domains = csvToArray(out.exclude_domains);

  return out;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.error) {
    usage(args.error);
    process.exit(2);
  }
  if (args.help) {
    usage();
    process.exit(0);
  }

  const apiKey = process.env.TAVILY_API_KEY;
  if (!apiKey) {
    usage('TAVILY_API_KEY env var is required');
    process.exit(2);
  }

  if (!args.query) {
    usage('--query is required');
    process.exit(2);
  }

  const payload = {
    query: args.query,
    max_results: args.max_results,
  };
  if (args.include_domains) payload.include_domains = args.include_domains;
  if (args.exclude_domains) payload.exclude_domains = args.exclude_domains;

  let res;
  try {
    res = await fetch(TAVILY_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify(payload),
    });
  } catch (e) {
    console.error(`Network error calling Tavily: ${e?.message || String(e)}`);
    process.exit(3);
  }

  if (!res.ok) {
    let bodyText = '';
    try { bodyText = await res.text(); } catch {}
    console.error(`Tavily HTTP error: ${res.status} ${res.statusText}`);
    if (bodyText) console.error(bodyText);
    process.exit(3);
  }

  let data;
  try {
    data = await res.json();
  } catch (e) {
    console.error(`Invalid JSON response from Tavily: ${e?.message || String(e)}`);
    process.exit(4);
  }

  const urls = Array.isArray(data?.results)
    ? data.results.map(r => r?.url).filter(Boolean)
    : [];

  if (args.urls_only) {
    for (const u of urls) process.stdout.write(`${u}\n`);
    process.exit(0);
  }

  process.stdout.write(JSON.stringify(data, null, 2));
  process.stdout.write('\n');

  if (args.urls_stderr && urls.length) {
    console.error('\nURLs:');
    for (const u of urls) console.error(u);
  }
}

main().catch((e) => {
  console.error(`Unexpected error: ${e?.stack || e?.message || String(e)}`);
  process.exit(1);
});
