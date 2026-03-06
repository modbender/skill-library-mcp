// Tavily Search Engine - AI-optimized search with full parameter support
// API docs: https://docs.tavily.com/documentation/api-reference/endpoint/search

const API_URL = "https://api.tavily.com/search";
const EXTRACT_URL = "https://api.tavily.com/extract";

export function isAvailable() {
  return !!(process.env.TAVILY_API_KEY ?? "").trim();
}

export function name() {
  return "tavily";
}

export async function search(query, opts = {}) {
  const apiKey = (process.env.TAVILY_API_KEY ?? "").trim();
  if (!apiKey) throw new Error("Missing TAVILY_API_KEY");

  const body = {
    api_key: apiKey,
    query,
    search_depth: opts.deep ? "advanced" : "basic",
    topic: opts.news ? "news" : "general",
    max_results: Math.max(1, Math.min(opts.count ?? 5, 20)),
    include_answer: true,
    include_raw_content: false,
  };

  if (opts.includeDomains?.length) body.include_domains = opts.includeDomains;
  if (opts.excludeDomains?.length) body.exclude_domains = opts.excludeDomains;
  if (opts.timeRange) body.time_range = opts.timeRange; // day|week|month|year
  if (opts.fromDate) body.from_date = opts.fromDate; // YYYY-MM-DD
  if (opts.toDate) body.to_date = opts.toDate; // YYYY-MM-DD
  if (opts.news && opts.days) body.days = opts.days;

  const resp = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!resp.ok) {
    const text = await resp.text().catch(() => "");
    throw new Error(`Tavily search failed (${resp.status}): ${text}`);
  }

  const data = await resp.json();
  return {
    engine: "tavily",
    answer: data.answer ?? null,
    results: (data.results ?? []).map((r) => ({
      title: r.title ?? "",
      url: r.url ?? "",
      content: r.content ?? "",
      score: r.score ?? null,
    })),
  };
}

export async function extract(urls) {
  const apiKey = (process.env.TAVILY_API_KEY ?? "").trim();
  if (!apiKey) throw new Error("Missing TAVILY_API_KEY");

  const resp = await fetch(EXTRACT_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ api_key: apiKey, urls }),
  });

  if (!resp.ok) {
    const text = await resp.text().catch(() => "");
    throw new Error(`Tavily extract failed (${resp.status}): ${text}`);
  }

  const data = await resp.json();
  return {
    engine: "tavily",
    results: (data.results ?? []).map((r) => ({
      url: r.url ?? "",
      content: r.raw_content ?? "",
    })),
    failed: data.failed_results ?? [],
  };
}
