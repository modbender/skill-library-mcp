const BRAVE_API_BASE = 'https://api.search.brave.com/res/v1';

const baseHeaders = {
  'Accept': 'application/json',
  'Accept-Encoding': 'gzip',
};

function getSearchApiKey() {
  const key = process.env.BRAVE_SEARCH_API_KEY;
  if (!key) {
    throw new Error(
      'BRAVE_SEARCH_API_KEY environment variable is not set. ' +
      'Export it with: export BRAVE_SEARCH_API_KEY=your_key_here'
    );
  }
  return key;
}

function getAnswersApiKey() {
  const key = process.env.BRAVE_ANSWERS_API_KEY;
  if (!key) {
    throw new Error(
      'BRAVE_ANSWERS_API_KEY environment variable is not set. ' +
      'Export it with: export BRAVE_ANSWERS_API_KEY=your_key_here'
    );
  }
  return key;
}

// ── Command: brave-search ──────────────────────────────────────────────────

async function braveSearch({ query, count = 10, freshness }) {
  const apiKey = getSearchApiKey();

  const params = new URLSearchParams({ q: query, count: String(count) });
  if (freshness) params.set('freshness', freshness);

  const res = await fetch(`${BRAVE_API_BASE}/web/search?${params}`, {
    headers: { ...baseHeaders, 'X-Subscription-Token': apiKey },
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Brave Search API error ${res.status}: ${err}`);
  }

  const data = await res.json();
  const results = data?.web?.results ?? [];

  if (results.length === 0) {
    return { summary: 'No web results found for that query.', results: [] };
  }

  const formatted = results.map((r, i) => ({
    rank: i + 1,
    title: r.title,
    url: r.url,
    snippet: r.description ?? '',
    age: r.age ?? null,
  }));

  return {
    query,
    total_results: data?.web?.total_results ?? null,
    results: formatted,
  };
}

// ── Command: brave-answer ──────────────────────────────────────────────────

async function braveAnswer({ query }) {
  const searchApiKey = getSearchApiKey();
  const answersApiKey = getAnswersApiKey();

  const searchHeaders = { ...baseHeaders, 'X-Subscription-Token': searchApiKey };
  const answersHeaders = { ...baseHeaders, 'X-Subscription-Token': answersApiKey };

  // Step 1: Web search with summary flag to get the summarizer key
  const searchParams = new URLSearchParams({ q: query, summary: '1' });
  const searchRes = await fetch(`${BRAVE_API_BASE}/web/search?${searchParams}`, {
    headers: searchHeaders,
  });

  if (!searchRes.ok) {
    const err = await searchRes.text();
    throw new Error(`Brave Search API error ${searchRes.status}: ${err}`);
  }

  const searchData = await searchRes.json();
  const summarizerKey = searchData?.summarizer?.key;

  if (!summarizerKey) {
    // Fall back to top web result snippets if no summary is available
    const fallbackResults = (searchData?.web?.results ?? []).slice(0, 3).map(r => ({
      title: r.title,
      url: r.url,
      snippet: r.description ?? '',
    }));
    return {
      query,
      answer: null,
      note: 'No AI summary available for this query. Returning top web results instead.',
      fallback_results: fallbackResults,
    };
  }

  // Step 2: Fetch the actual summary using the Answers API key
  const summaryParams = new URLSearchParams({ key: summarizerKey, entity_info: '1' });
  const summaryRes = await fetch(`${BRAVE_API_BASE}/summarizer/search?${summaryParams}`, {
    headers: answersHeaders,
  });

  if (!summaryRes.ok) {
    const err = await summaryRes.text();
    throw new Error(`Brave Summarizer API error ${summaryRes.status}: ${err}`);
  }

  const summaryData = await summaryRes.json();
  const answer = summaryData?.summary?.[0]?.data ?? null;
  const followUps = summaryData?.followups ?? [];
  const enrichments = summaryData?.enrichments ?? null;

  return {
    query,
    answer,
    follow_up_questions: followUps,
    enrichments: enrichments ?? undefined,
  };
}

// ── Entry point ────────────────────────────────────────────────────────────

const [,, command, ...args] = process.argv;

// Supports both --key=value and --key value (two separate argv elements).
// Using separate elements (execFile-style) is preferred — it ensures user-
// supplied values are never parsed by the shell.
const params = {};
for (let i = 0; i < args.length; i++) {
  const arg = args[i];
  if (!arg.startsWith('--')) continue;
  const key = arg.slice(2);
  if (key.includes('=')) {
    // --key=value form
    const eq = key.indexOf('=');
    params[key.slice(0, eq)] = key.slice(eq + 1);
  } else if (i + 1 < args.length && !args[i + 1].startsWith('--')) {
    // --key value form (value is the next element)
    params[key] = args[++i];
  } else {
    // boolean flag (--key with no value)
    params[key] = true;
  }
}

const handlers = {
  'brave-search': braveSearch,
  'brave-answer': braveAnswer,
};

const handler = handlers[command];
if (!handler) {
  console.error(JSON.stringify({
    error: `Unknown command: ${command}. Available: ${Object.keys(handlers).join(', ')}`
  }));
  process.exit(1);
}

handler(params)
  .then(result => console.log(JSON.stringify(result, null, 2)))
  .catch(err => {
    console.error(JSON.stringify({ error: err.message }));
    process.exit(1);
  });