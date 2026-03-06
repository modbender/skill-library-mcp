#!/usr/bin/env npx tsx

/**
 * Zyla API Hub — Catalog Discovery CLI
 *
 * Usage:
 *   npx tsx zyla-catalog.ts search "weather"
 *   npx tsx zyla-catalog.ts list --category "Finance"
 *   npx tsx zyla-catalog.ts endpoints --api 781
 *
 * Public endpoint — no API key required for catalog browsing.
 */

import { ZYLA_HUB_URL as HUB_URL } from "./config.js";

// ─── Helpers ──────────────────────────────────────────────────────────────────

function die(message: string, code = 1): never {
  console.error(JSON.stringify({ error: message }));
  process.exit(code);
}

function parseArgs(args: string[]): Record<string, string> {
  const result: Record<string, string> = {};
  const positional: string[] = [];

  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith("--") && i + 1 < args.length) {
      result[args[i].slice(2)] = args[i + 1];
      i++;
    } else if (!args[i].startsWith("--")) {
      positional.push(args[i]);
    }
  }

  if (positional.length > 0) {
    result["_query"] = positional.join(" ");
  }

  return result;
}

interface CatalogApi {
  id: number;
  name: string;
  description: string;
  category: string | null;
  popularity: number;
  endpoints: Array<{
    id: number;
    name: string;
    method: string;
    description: string;
    parameters: Array<{
      key: string;
      type: string;
      required: boolean;
      description: string;
      example: string;
    }>;
  }>;
}

async function fetchCatalog(limit = 500): Promise<CatalogApi[]> {
  const url = `${HUB_URL}/api/openclaw/catalog?limit=${limit}&sort=popularity`;
  const res = await fetch(url, {
    headers: { "Accept": "application/json" },
  });

  if (!res.ok) {
    die(`Failed to fetch catalog: HTTP ${res.status} ${res.statusText}`);
  }

  const data = await res.json();
  return data.apis || [];
}

// ─── Commands ─────────────────────────────────────────────────────────────────

async function searchApis(query: string) {
  if (!query) die("Usage: search <query>\nExample: search \"weather\"");

  const apis = await fetchCatalog();
  const q = query.toLowerCase();

  const matches = apis.filter((api) => {
    const searchable = [
      api.name,
      api.description,
      api.category,
      ...api.endpoints.map((e) => e.name),
      ...api.endpoints.map((e) => e.description),
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();

    return searchable.includes(q);
  });

  if (matches.length === 0) {
    console.log(JSON.stringify({
      query,
      results: [],
      message: `No APIs found matching "${query}". Try a broader search term.`,
    }, null, 2));
    return;
  }

  // Return compact results (name, id, description, category, endpoint count)
  const results = matches.map((api) => ({
    id: api.id,
    name: api.name,
    description: api.description,
    category: api.category,
    endpoints_count: api.endpoints.length,
    popularity: api.popularity,
  }));

  console.log(JSON.stringify({
    query,
    total: results.length,
    results,
  }, null, 2));
}

async function listApis(flags: Record<string, string>) {
  const apis = await fetchCatalog();
  const category = flags["category"];

  let filtered = apis;
  if (category) {
    const cat = category.toLowerCase();
    filtered = apis.filter(
      (api) => api.category?.toLowerCase().includes(cat)
    );
  }

  // Group by category
  const grouped: Record<string, Array<{ id: number; name: string; description: string }>> = {};
  for (const api of filtered) {
    const cat = api.category || "Uncategorized";
    if (!grouped[cat]) grouped[cat] = [];
    grouped[cat].push({
      id: api.id,
      name: api.name,
      description: api.description,
    });
  }

  console.log(JSON.stringify({
    total: filtered.length,
    categories: grouped,
  }, null, 2));
}

async function getEndpoints(flags: Record<string, string>) {
  const apiId = flags["api"];
  if (!apiId) die("Usage: endpoints --api <id>");

  const apis = await fetchCatalog();
  const api = apis.find((a) => String(a.id) === String(apiId));

  if (!api) die(`API with ID ${apiId} not found in catalog`);

  console.log(JSON.stringify({
    api_id: api.id,
    api_name: api.name,
    description: api.description,
    category: api.category,
    endpoints: api.endpoints.map((ep) => ({
      id: ep.id,
      name: ep.name,
      method: ep.method,
      description: ep.description,
      parameters: ep.parameters,
      example_call: `npx tsx zyla-api.ts call --api ${api.id} --endpoint ${ep.id} --params '${JSON.stringify(
        Object.fromEntries(
          ep.parameters.filter((p) => p.required).map((p) => [p.key, p.example || `<${p.type}>`])
        )
      )}'`,
    })),
  }, null, 2));
}

// ─── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  const [command, ...rest] = process.argv.slice(2);
  const flags = parseArgs(rest);

  switch (command) {
    case "search":
      await searchApis(flags["_query"] || flags["query"] || "");
      break;
    case "list":
      await listApis(flags);
      break;
    case "endpoints":
      await getEndpoints(flags);
      break;
    default:
      console.log(JSON.stringify({
        usage: {
          search: 'zyla-catalog.ts search "weather"',
          list: 'zyla-catalog.ts list [--category "Finance"]',
          endpoints: "zyla-catalog.ts endpoints --api <id>",
        },
        hub_url: HUB_URL,
      }, null, 2));
      break;
  }
}

main().catch((err) => die(err.message));
