// Exa Search Engine - AI-native semantic search
// API docs: https://exa.ai/docs/reference/search

const SEARCH_URL = "https://api.exa.ai/search";
const CONTENTS_URL = "https://api.exa.ai/contents";

export function isAvailable() {
  return !!(process.env.EXA_API_KEY ?? "").trim();
}

export function name() {
  return "exa";
}

export async function search(query, opts = {}) {
  const apiKey = (process.env.EXA_API_KEY ?? "").trim();
  if (!apiKey) throw new Error("Missing EXA_API_KEY");

  const body = {
    query,
    numResults: Math.max(1, Math.min(opts.count ?? 5, 100)),
    useAutoprompt: true,
    type: opts.deep ? "deep" : "auto",
  };

  if (opts.includeDomains?.length) body.includeDomains = opts.includeDomains;
  if (opts.excludeDomains?.length) body.excludeDomains = opts.excludeDomains;
  if (opts.fromDate) body.startPublishedDate = opts.fromDate + "T00:00:00.000Z";
  if (opts.toDate) body.endPublishedDate = opts.toDate + "T23:59:59.999Z";

  // Map timeRange to date
  if (opts.timeRange && !opts.fromDate) {
    const now = new Date();
    const offsets = { day: 1, week: 7, month: 30, year: 365 };
    const days = offsets[opts.timeRange] ?? 30;
    const from = new Date(now.getTime() - days * 86400000);
    body.startPublishedDate = from.toISOString();
  }

  // Request highlights for snippet content
  body.contents = { highlights: true };

  const resp = await fetch(SEARCH_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": apiKey,
    },
    body: JSON.stringify(body),
  });

  if (!resp.ok) {
    const text = await resp.text().catch(() => "");
    throw new Error(`Exa search failed (${resp.status}): ${text}`);
  }

  const data = await resp.json();
  return {
    engine: "exa",
    answer: null, // Exa doesn't provide AI answers
    results: (data.results ?? []).map((r) => ({
      title: r.title ?? "",
      url: r.url ?? "",
      content: (r.highlights ?? []).join(" ") || r.text?.slice(0, 500) || "",
      score: r.score ?? null,
      publishedDate: r.publishedDate ?? null,
    })),
  };
}

export async function extract(urls) {
  const apiKey = (process.env.EXA_API_KEY ?? "").trim();
  if (!apiKey) throw new Error("Missing EXA_API_KEY");

  const resp = await fetch(CONTENTS_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": apiKey,
    },
    body: JSON.stringify({
      ids: urls, // Exa uses IDs or URLs
      text: true,
      livecrawl: "fallback",
    }),
  });

  if (!resp.ok) {
    const text = await resp.text().catch(() => "");
    throw new Error(`Exa extract failed (${resp.status}): ${text}`);
  }

  const data = await resp.json();
  return {
    engine: "exa",
    results: (data.results ?? []).map((r) => ({
      url: r.url ?? "",
      content: r.text ?? "",
    })),
    failed: [],
  };
}
