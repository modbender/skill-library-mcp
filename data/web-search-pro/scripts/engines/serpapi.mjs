// SerpAPI - Multi-engine SERP API (Google, Bing, DuckDuckGo, Baidu, Yandex)
// API docs: https://serpapi.com/search-api

const API_URL = "https://serpapi.com/search.json";

export function isAvailable() {
  return !!(process.env.SERPAPI_API_KEY ?? "").trim();
}

export function name() {
  return "serpapi";
}

const ENGINE_MAP = {
  google: "google",
  bing: "bing",
  duckduckgo: "duckduckgo",
  baidu: "baidu",
  yandex: "yandex",
};

export async function search(query, opts = {}) {
  const apiKey = (process.env.SERPAPI_API_KEY ?? "").trim();
  if (!apiKey) throw new Error("Missing SERPAPI_API_KEY");

  const engine = ENGINE_MAP[opts.searchEngine ?? "google"] ?? "google";

  // Build query with site: filter
  let q = query;
  if (opts.includeDomains?.length === 1) {
    q = `site:${opts.includeDomains[0]} ${query}`;
  } else if (opts.includeDomains?.length > 1) {
    const sites = opts.includeDomains.map((d) => `site:${d}`).join(" OR ");
    q = `(${sites}) ${query}`;
  }
  if (opts.excludeDomains?.length) {
    q += " " + opts.excludeDomains.map((d) => `-site:${d}`).join(" ");
  }

  const params = new URLSearchParams({
    api_key: apiKey,
    engine,
    q,
    num: String(Math.max(1, Math.min(opts.count ?? 5, 100))),
  });

  // Date range (Google tbs)
  if (engine === "google") {
    if (opts.timeRange) {
      const tbsMap = { day: "qdr:d", week: "qdr:w", month: "qdr:m", year: "qdr:y" };
      if (tbsMap[opts.timeRange]) params.set("tbs", tbsMap[opts.timeRange]);
    }
    if (opts.fromDate && opts.toDate) {
      const [y1, m1, d1] = opts.fromDate.split("-");
      const [y2, m2, d2] = opts.toDate.split("-");
      params.set("tbs", `cdr:1,cd_min:${parseInt(m1)}/${parseInt(d1)}/${y1},cd_max:${parseInt(m2)}/${parseInt(d2)}/${y2}`);
    }
    if (opts.news) params.set("tbm", "nws");
  }

  if (opts.country) params.set("gl", opts.country.toLowerCase());
  if (opts.lang) params.set("hl", opts.lang);

  const resp = await fetch(`${API_URL}?${params.toString()}`);

  if (!resp.ok) {
    const text = await resp.text().catch(() => "");
    throw new Error(`SerpAPI search failed (${resp.status}): ${text}`);
  }

  const data = await resp.json();
  const items = data.organic_results ?? data.news_results ?? [];

  return {
    engine: `serpapi:${engine}`,
    answer: data.answer_box?.answer ?? data.answer_box?.snippet ?? data.knowledge_graph?.description ?? null,
    results: items.map((r) => ({
      title: r.title ?? "",
      url: r.link ?? "",
      content: r.snippet ?? r.description ?? "",
      score: null,
      date: r.date ?? null,
    })),
  };
}

export async function extract(_urls) {
  throw new Error("SerpAPI does not support content extraction. Use Tavily or Exa instead.");
}
