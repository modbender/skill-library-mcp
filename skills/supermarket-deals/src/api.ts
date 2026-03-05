import { mkdir, readFile, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";

const MARKTGURU_HOME = "https://www.marktguru.de";
const SEARCH_ENDPOINT = "https://api.marktguru.de/api/v1/offers/search";
const CACHE_TTL_MS = 6 * 60 * 60 * 1000;
const CACHE_DIR = path.join(os.homedir(), ".supermarket-deals");
const KEYS_PATH = path.join(CACHE_DIR, "keys.json");

export interface Advertiser {
  name?: string;
}

export interface Unit {
  shortName?: string;
}

export interface ValidityDate {
  from?: string;
  to?: string;
}

export interface OfferResult {
  id?: string | number;
  product?: {
    name?: string;
  };
  advertisers?: Advertiser[];
  price?: number;
  referencePrice?: number;
  description?: string;
  volume?: number;
  quantity?: number;
  unit?: Unit;
  validityDates?: ValidityDate[];
}

export interface OfferSearchResponse {
  totalResults: number;
  results: OfferResult[];
}

interface ApiKeys {
  apiKey: string;
  clientKey: string;
  fetchedAt: number;
}

async function ensureCacheDir(): Promise<void> {
  await mkdir(CACHE_DIR, { recursive: true });
}

async function readCachedKeys(): Promise<ApiKeys | null> {
  try {
    const raw = await readFile(KEYS_PATH, "utf8");
    const parsed = JSON.parse(raw) as ApiKeys;
    if (!parsed.apiKey || !parsed.clientKey || !parsed.fetchedAt) {
      return null;
    }
    if (Date.now() - parsed.fetchedAt > CACHE_TTL_MS) {
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}

async function saveKeys(keys: ApiKeys): Promise<void> {
  await ensureCacheDir();
  await writeFile(KEYS_PATH, `${JSON.stringify(keys, null, 2)}\n`, "utf8");
}

function extractKeysFromHtml(html: string): Pick<ApiKeys, "apiKey" | "clientKey"> {
  const scriptRegex = /<script[^>]*type=["']application\/json["'][^>]*>([\s\S]*?)<\/script>/gi;
  let match: RegExpExecArray | null;

  while ((match = scriptRegex.exec(html)) !== null) {
    const content = match[1]?.trim();
    if (!content) {
      continue;
    }

    try {
      const parsed = JSON.parse(content) as { config?: { apiKey?: string; clientKey?: string } };
      const apiKey = parsed.config?.apiKey;
      const clientKey = parsed.config?.clientKey;
      if (apiKey && clientKey) {
        return { apiKey, clientKey };
      }
    } catch {
      // Ignore malformed JSON blocks and continue scanning.
    }
  }

  throw new Error("Could not extract API keys from marktguru homepage JSON config.");
}

async function fetchFreshKeys(): Promise<ApiKeys> {
  const response = await fetch(MARKTGURU_HOME, {
    headers: {
      Accept: "text/html"
    }
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch Marktguru homepage: HTTP ${response.status}`);
  }

  const html = await response.text();
  const keys = extractKeysFromHtml(html);
  const full: ApiKeys = {
    ...keys,
    fetchedAt: Date.now()
  };
  await saveKeys(full);
  return full;
}

async function getKeys(forceRefresh = false): Promise<ApiKeys> {
  if (!forceRefresh) {
    const cached = await readCachedKeys();
    if (cached) {
      return cached;
    }
  }

  try {
    return await fetchFreshKeys();
  } catch (firstError) {
    // Graceful fallback: retry once before failing.
    try {
      return await fetchFreshKeys();
    } catch {
      throw firstError;
    }
  }
}

const MAX_QUERY_LENGTH = 100;
const MAX_LIMIT = 100;
const ZIP_REGEX = /^\d{4,6}$/;

function validateInputs(query: string, zipCode: string, limit: number): void {
  if (!query || query.trim().length === 0) {
    throw new Error("Query must not be empty.");
  }
  if (query.length > MAX_QUERY_LENGTH) {
    throw new Error(`Query too long (max ${MAX_QUERY_LENGTH} characters).`);
  }
  if (!ZIP_REGEX.test(zipCode)) {
    throw new Error(`Invalid ZIP code: "${zipCode}". Expected 4–6 digits.`);
  }
  if (!Number.isInteger(limit) || limit < 1 || limit > MAX_LIMIT) {
    throw new Error(`Limit must be an integer between 1 and ${MAX_LIMIT}.`);
  }
}

function sanitizeOfferId(id: string | number | undefined): string | null {
  if (id == null) return null;
  const str = String(id).trim();
  // Only allow numeric IDs to prevent URL injection
  return /^\d+$/.test(str) ? str : null;
}

function buildSearchUrl(query: string, zipCode: string, limit: number): URL {
  const url = new URL(SEARCH_ENDPOINT);
  url.searchParams.set("as", "web");
  url.searchParams.set("limit", String(limit));
  url.searchParams.set("q", query);
  url.searchParams.set("zipCode", zipCode);
  return url;
}

export async function searchOffers(query: string, zipCode: string, limit: number): Promise<OfferSearchResponse> {
  validateInputs(query, zipCode, limit);
  const run = async (forceRefreshKeys: boolean): Promise<OfferSearchResponse> => {
    const keys = await getKeys(forceRefreshKeys);
    const url = buildSearchUrl(query, zipCode, limit);
    const response = await fetch(url, {
      headers: {
        "x-apikey": keys.apiKey,
        "x-clientkey": keys.clientKey,
        Accept: "application/json"
      }
    });

    if (!response.ok) {
      const body = await response.text().catch(() => "");
      throw new Error(`Marktguru search failed: HTTP ${response.status} ${body.slice(0, 200)}`.trim());
    }

    const raw = await response.json() as Record<string, unknown>;
    if (typeof raw !== "object" || raw === null) {
      throw new Error("Unexpected Marktguru response: not an object.");
    }
    if (!Array.isArray(raw["results"])) {
      throw new Error("Unexpected Marktguru response: results is not an array.");
    }
    return {
      totalResults: typeof raw["totalResults"] === "number" ? raw["totalResults"] : 0,
      results: raw["results"] as OfferResult[],
    };
  };

  try {
    return await run(false);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    if (message.includes("HTTP 401") || message.includes("HTTP 403")) {
      return run(true);
    }
    throw error;
  }
}

export { sanitizeOfferId };

export function getKeysPath(): string {
  return KEYS_PATH;
}
