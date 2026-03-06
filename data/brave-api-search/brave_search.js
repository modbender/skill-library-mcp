#!/usr/bin/env node
// Brave Web Search - uses Brave Search API web/search endpoint
// Requires: BRAVE_SEARCH_API_KEY env var

const BASE_URL = 'https://api.search.brave.com/res/v1';
const VALID_FRESHNESS = new Set(['pd', 'pw', 'pm', 'py']);

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      const key = argv[i].slice(2);
      const val = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : 'true';
      args[key] = val;
    }
  }
  return args;
}

async function braveGet(path, params) {
  const apiKey = process.env.BRAVE_SEARCH_API_KEY;
  if (!apiKey) {
    console.error('Error: BRAVE_SEARCH_API_KEY environment variable not set.');
    console.error('Get your key at: https://api-dashboard.search.brave.com');
    process.exit(1);
  }

  const url = new URL(`${BASE_URL}${path}`);
  for (const [k, v] of Object.entries(params)) {
    if (v !== '' && v !== undefined && v !== null) url.searchParams.set(k, v);
  }

  const res = await fetch(url.toString(), {
    headers: {
      'Accept': 'application/json',
      'Accept-Encoding': 'gzip',
      'X-Subscription-Token': apiKey,
    },
  });

  if (!res.ok) {
    const body = await res.text();
    console.error(`Brave API error ${res.status}: ${body}`);
    process.exit(1);
  }

  return res.json();
}

function formatResults(data, extraSnippets) {
  const results = data.web?.results || [];
  if (results.length === 0) {
    return 'No results found.';
  }

  const lines = [`Found ${results.length} result(s) for: ${data.query?.original || ''}\n`];

  for (let i = 0; i < results.length; i++) {
    const r = results[i];
    lines.push(`${i + 1}. **${r.title}**`);
    lines.push(`   URL: ${r.url}`);
    if (r.description) lines.push(`   ${r.description}`);
    if (extraSnippets && r.extra_snippets?.length) {
      lines.push('   Additional context:');
      for (const s of r.extra_snippets) {
        lines.push(`   - ${s}`);
      }
    }
    lines.push('');
  }

  return lines.join('\n');
}

function formatSummary(data) {
  if (!data || data.status === 'failed') return null;
  const lines = [];
  if (data.title) lines.push(`## ${data.title}\n`);
  if (data.summary?.length) {
    const text = data.summary.map(s => s.data || '').join('');
    lines.push(text);
  }
  if (data.enrichments?.raw) lines.push(`\n${data.enrichments.raw}`);
  if (data.followups?.length) {
    lines.push('\n**Related questions:**');
    for (const q of data.followups) lines.push(`- ${q}`);
  }
  return lines.join('\n');
}

async function main() {
  const args = parseArgs(process.argv);

  const query = args.query;
  if (!query) {
    console.error('Usage: brave_search.js --query "search terms" [--count 10] [--country us] [--freshness pd] [--extra-snippets true] [--summary true]');
    process.exit(1);
  }

  const count = Math.min(20, Math.max(1, parseInt(args.count) || 10));
  const country = args.country || 'us';
  const freshness = VALID_FRESHNESS.has(args.freshness) ? args.freshness : undefined;
  const extraSnippets = args['extra-snippets'] === 'true';
  const wantSummary = args.summary === 'true';

  const params = {
    q: query,
    count,
    country,
    freshness,
    extra_snippets: extraSnippets ? '1' : undefined,
    summary: wantSummary ? '1' : undefined,
  };

  const data = await braveGet('/web/search', params);
  console.log(formatResults(data, extraSnippets));

  if (wantSummary && data.summarizer?.key) {
    const summaryData = await braveGet('/summarizer/search', {
      key: data.summarizer.key,
      inline_references: 'true',
    });
    const summary = formatSummary(summaryData);
    if (summary) {
      console.log('\n---\n**AI Summary:**\n');
      console.log(summary);
    }
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
