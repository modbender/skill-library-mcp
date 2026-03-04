#!/usr/bin/env npx tsx

/**
 * Zyla API Hub — API Call CLI
 *
 * Usage:
 *   npx tsx zyla-api.ts call --api 781 --endpoint 1234 --params '{"zip":"10001"}'
 *   npx tsx zyla-api.ts call --api 781 --endpoint 1234 --method POST --params '{"key":"value"}'
 *   npx tsx zyla-api.ts info --api 781
 *   npx tsx zyla-api.ts health
 *
 * Requires: ZYLA_API_KEY environment variable
 */

import { ZYLA_HUB_URL as HUB_URL, ZYLA_API_KEY as API_KEY } from "./config.js";

// ─── Helpers ──────────────────────────────────────────────────────────────────

function die(message: string, code = 1): never {
  console.error(JSON.stringify({ error: message }));
  process.exit(code);
}

function parseArgs(args: string[]): Record<string, string> {
  const result: Record<string, string> = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith("--") && i + 1 < args.length) {
      result[args[i].slice(2)] = args[i + 1];
      i++;
    }
  }
  return result;
}

async function fetchJson(url: string, options: RequestInit = {}): Promise<any> {
  const headers: Record<string, string> = {
    "Accept": "application/json",
    ...(options.headers as Record<string, string> || {}),
  };

  if (API_KEY) {
    headers["Authorization"] = `Bearer ${API_KEY}`;
  }

  const res = await fetch(url, { ...options, headers });

  // Extract and display rate limit info
  const rateLimitInfo: Record<string, string> = {};
  for (const [key, value] of res.headers.entries()) {
    if (key.toLowerCase().startsWith("x-zyla")) {
      rateLimitInfo[key] = value;
    }
  }

  const body = await res.text();
  let json: any;
  try {
    json = JSON.parse(body);
  } catch {
    json = { raw_response: body };
  }

  if (!res.ok) {
    console.error(JSON.stringify({
      error: `HTTP ${res.status} ${res.statusText}`,
      response: json,
      rate_limits: Object.keys(rateLimitInfo).length > 0 ? rateLimitInfo : undefined,
    }, null, 2));
    process.exit(1);
  }

  return { data: json, rate_limits: rateLimitInfo };
}

// ─── Commands ─────────────────────────────────────────────────────────────────

async function callApi(flags: Record<string, string>) {
  if (!API_KEY) die("ZYLA_API_KEY environment variable is required");

  const apiId = flags["api"];
  const endpointId = flags["endpoint"];
  if (!apiId || !endpointId) die("Usage: call --api <id> --endpoint <id> [--method GET] [--params '{...}']");

  const method = (flags["method"] || "GET").toUpperCase();
  const params = flags["params"] ? JSON.parse(flags["params"]) : {};

  // Build URL — slug parts are optional (the IDs do the routing)
  const apiSlug = flags["api-slug"] || "api";
  const endpointSlug = flags["endpoint-slug"] || "endpoint";
  let url = `${HUB_URL}/api/${apiId}/${apiSlug}/${endpointId}/${endpointSlug}`;

  const fetchOptions: RequestInit = { method };

  if (method === "GET") {
    const qs = new URLSearchParams(params).toString();
    if (qs) url += `?${qs}`;
  } else {
    fetchOptions.body = JSON.stringify(params);
    fetchOptions.headers = { "Content-Type": "application/json" };
  }

  const { data, rate_limits } = await fetchJson(url, fetchOptions);

  console.log(JSON.stringify({
    success: true,
    data,
    rate_limits: Object.keys(rate_limits).length > 0 ? rate_limits : undefined,
  }, null, 2));
}

async function getInfo(flags: Record<string, string>) {
  if (!API_KEY) die("ZYLA_API_KEY environment variable is required");

  const apiId = flags["api"];
  if (!apiId) die("Usage: info --api <id>");

  // Fetch from catalog and filter
  const { data } = await fetchJson(`${HUB_URL}/api/openclaw/catalog?limit=500`);
  const api = data.apis?.find((a: any) => String(a.id) === String(apiId));

  if (!api) die(`API with ID ${apiId} not found in catalog`);

  console.log(JSON.stringify(api, null, 2));
}

async function healthCheck() {
  if (!API_KEY) die("ZYLA_API_KEY environment variable is required");

  const { data } = await fetchJson(`${HUB_URL}/api/openclaw/health`);
  console.log(JSON.stringify(data, null, 2));
}

// ─── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  const [command, ...rest] = process.argv.slice(2);
  const flags = parseArgs(rest);

  switch (command) {
    case "call":
      await callApi(flags);
      break;
    case "info":
      await getInfo(flags);
      break;
    case "health":
      await healthCheck();
      break;
    default:
      console.log(JSON.stringify({
        usage: {
          call: "zyla-api.ts call --api <id> --endpoint <id> [--method GET] [--params '{...}']",
          info: "zyla-api.ts info --api <id>",
          health: "zyla-api.ts health",
        },
        env: {
          ZYLA_API_KEY: API_KEY ? "set" : "NOT SET",
          ZYLA_HUB_URL: HUB_URL,
        },
      }, null, 2));
      break;
  }
}

main().catch((err) => die(err.message));
