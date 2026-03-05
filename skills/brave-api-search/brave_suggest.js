#!/usr/bin/env node
// Brave Autosuggest - uses Brave Search API suggest endpoint
// Requires: BRAVE_SEARCH_API_KEY env var

const BASE_URL = 'https://api.search.brave.com/res/v1';

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

async function braveSuggest(path, params) {
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

function formatSuggestions(data, rich) {
  const results = data.results || [];
  if (results.length === 0) {
    return 'No suggestions found.';
  }

  const lines = [`Got ${results.length} suggestion(s) for: ${data.query?.original || ''}\n`;

  if (rich) {
    // Rich suggestions with enhanced metadata
    for (let i = 0; i < results.length; i++) {
      const r = results[i];
      lines.push(`${i + 1}. **${r.query}**`);
      if (r.is_entity) {
        lines.push(`   [Entity: ${r.title || r.query}]`);
      }
      if (r.title) {
        lines.push(`   Title: ${r.title}`);
      }
      if (r.description) {
        lines.push(`   ${r.description}`);
      }
      if (r.img) {
        lines.push(`   Image: ${r.img}`);
      }
      lines.push('');
    }
  } else {
    // Simple suggestions
    for (let i = 0; i < results.length; i++) {
      lines.push(`${i + 1}. ${results[i].query}`);
    }
  }

  return lines.join('\n');
}

async function main() {
  const args = parseArgs(process.argv);

  const query = args.query || args.q;
  if (!query) {
    console.error('Usage: brave_suggest.js --query "search terms" [--count 5] [--country us] [--rich true]');
    console.error('Short form: --q "search terms"');
    process.exit(1);
  }

  const count = Math.min(10, Math.max(1, parseInt(args.count) || 5));
  const country = (args.country || 'US').toUpperCase();
  const rich = args.rich === 'true';

  const params = {
    q: query,
    count,
    country,
  };

  if (rich) {
    params.rich = 'true';
  }

  const data = await braveSuggest('/suggest/search', params);
  console.log(formatSuggestions(data, rich));
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
