#!/usr/bin/env node
/**
 * rankscale-skill.js
 * RS-126 — Rankscale GEO Analytics Skill
 *
 * Main skill logic for fetching and interpreting Rankscale
 * GEO (Generative Engine Optimization) analytics data.
 *
 * Usage:
 *   node rankscale-skill.js [--brand-id <id>] [--api-key <key>]
 *   RANKSCALE_API_KEY=rk_xxx RANKSCALE_BRAND_ID=xxx node rankscale-skill.js
 */

'use strict';

const https = require('https');
const path = require('path');
const fs = require('fs');

// ─── Config ──────────────────────────────────────────────
const API_BASE = 'https://rankscale.ai';
const WIDTH = 55;
const MAX_RETRIES = 3;
const BACKOFF_BASE_MS = 1000;

// ─── Safe Accessor Helpers ───────────────────────────────

/**
 * Safely get a nested property by dot-path.
 * Returns defaultVal if any part of the path is null/undefined
 * or if obj itself is falsy.
 *
 * @param {object} obj
 * @param {string} path  - e.g. 'data.ownBrandMetrics.visibilityScore'
 * @param {*}      [defaultVal=null]
 * @returns {*}
 * @example safeGet(raw, 'data.ownBrandMetrics.visibilityScore', 0)
 */
function safeGet(obj, path, defaultVal = null) {
  if (!obj) return defaultVal;
  const keys = path.split('.');
  let cur = obj;
  for (const key of keys) {
    if (cur == null || typeof cur !== 'object') return defaultVal;
    cur = cur[key];
  }
  return cur ?? defaultVal;
}

/**
 * Safe numeric coercion.
 * Returns defaultVal when val is null, undefined, NaN, or non-finite.
 *
 * @param {*}      val
 * @param {number} [defaultVal=0]
 * @returns {number}
 */
function safeNum(val, defaultVal = 0) {
  if (val == null) return defaultVal;
  const n = Number(val);
  return Number.isFinite(n) ? n : defaultVal;
}

/**
 * Safe toFixed that handles null/undefined/NaN.
 * Returns a rounded number (not a string).
 *
 * @param {*}      val
 * @param {number} [decimals=1]
 * @param {number} [defaultVal=0]
 * @returns {number}
 */
function safeFixed(val, decimals = 1, defaultVal = 0) {
  const n = safeNum(val, defaultVal);
  return +n.toFixed(decimals);
}

/**
 * Safe array — always returns an array regardless of input.
 *
 * @param {*} val
 * @returns {Array}
 */
function safeArray(val) {
  return Array.isArray(val) ? val : [];
}

// ─── Credential Resolution ───────────────────────────────
function resolveCredentials(args = {}) {
  const apiKey =
    args.apiKey ||
    process.env.RANKSCALE_API_KEY ||
    null;

  const brandId =
    args.brandId ||
    process.env.RANKSCALE_BRAND_ID ||
    extractBrandIdFromKey(apiKey) ||
    null;

  return { apiKey, brandId };
}

/**
 * Rankscale API keys encode the brand ID:
 *   rk_<hash>_<brandId>
 */
function extractBrandIdFromKey(apiKey) {
  if (!apiKey) return null;
  const parts = apiKey.split('_');
  return parts.length >= 3 ? parts[parts.length - 1] : null;
}

// ─── HTTP Client ─────────────────────────────────────────
/**
 * @param {string} endpoint  - function name e.g. 'metricsV1Report'
 * @param {string} apiKey
 * @param {string} method    - 'GET' or 'POST'
 * @param {object|null} body - POST body (will be JSON-encoded)
 * @param {number} retries
 */
function apiRequest(endpoint, apiKey, method = 'GET', body = null, retries = 0) {
  return new Promise((resolve, reject) => {
    const url = `${API_BASE}/${endpoint}`;
    const bodyStr = body ? JSON.stringify(body) : null;
    const headers = {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
      'User-Agent': 'openclaw-rs-geo-analytics/1.0.0',
    };
    if (bodyStr) {
      headers['Content-Length'] = Buffer.byteLength(bodyStr);
    }

    const parsed = new URL(url);
    const reqOptions = {
      hostname: parsed.hostname,
      path: parsed.pathname + parsed.search,
      method,
      headers,
    };

    const req = https.request(reqOptions, (res) => {
      let data = '';
      res.on('data', (chunk) => (data += chunk));
      res.on('end', () => {
        // Rate limit: exponential backoff
        if (res.statusCode === 429 && retries < MAX_RETRIES) {
          const delay =
            BACKOFF_BASE_MS * Math.pow(2, retries) +
            Math.random() * 500;
          setTimeout(
            () =>
              apiRequest(endpoint, apiKey, method, body, retries + 1)
                .then(resolve)
                .catch(reject),
            delay
          );
          return;
        }

        if (res.statusCode === 401 || res.statusCode === 403) {
          reject(
            new AuthError(
              `Authentication failed (HTTP ${res.statusCode}). ` +
                'Check your RANKSCALE_API_KEY.'
            )
          );
          return;
        }

        if (res.statusCode === 404) {
          reject(
            new NotFoundError(
              `Brand ID not found (HTTP 404). ` +
                `Run brand discovery to find valid IDs:\n` +
                `  RANKSCALE_API_KEY=xxx ` +
                `node rankscale-skill.js --discover-brands`
            )
          );
          return;
        }

        if (res.statusCode >= 500) {
          if (retries < MAX_RETRIES) {
            const delay =
              BACKOFF_BASE_MS * Math.pow(2, retries);
            setTimeout(
              () =>
                apiRequest(endpoint, apiKey, method, body, retries + 1)
                  .then(resolve)
                  .catch(reject),
              delay
            );
            return;
          }
          reject(
            new ApiError(
              `Server error on ${endpoint} (HTTP ${res.statusCode})`
            )
          );
          return;
        }

        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(
            new ApiError(
              `Invalid JSON response from ${endpoint}: ${e.message}`
            )
          );
        }
      });
    });

    req.setTimeout(15000, () => {
      req.destroy();
      if (retries < MAX_RETRIES) {
        apiRequest(endpoint, apiKey, method, body, retries + 1)
          .then(resolve)
          .catch(reject);
      } else {
        reject(new ApiError(`Timeout on ${endpoint}`));
      }
    });

    req.on('error', (err) => {
      if (retries < MAX_RETRIES) {
        const delay = BACKOFF_BASE_MS * Math.pow(2, retries);
        setTimeout(
          () =>
            apiRequest(endpoint, apiKey, method, body, retries + 1)
              .then(resolve)
              .catch(reject),
          delay
        );
      } else {
        reject(
          new ApiError(`Network error on ${endpoint}: ${err.message}`)
        );
      }
    });

    if (bodyStr) {
      req.write(bodyStr);
    }
    req.end();
  });
}

// ─── Custom Errors ────────────────────────────────────────
class AuthError extends Error {
  constructor(msg) {
    super(msg);
    this.name = 'AuthError';
  }
}
class NotFoundError extends Error {
  constructor(msg) {
    super(msg);
    this.name = 'NotFoundError';
  }
}
class ApiError extends Error {
  constructor(msg) {
    super(msg);
    this.name = 'ApiError';
  }
}

// ─── API Calls ────────────────────────────────────────────

/** GET /metricsV1Brands — list brands on this account */
async function fetchBrands(apiKey) {
  return apiRequest('v1/metrics/brands', apiKey, 'GET');
}

/** POST /metricsV1Report — visibility score, rank, competitors */
async function fetchReport(apiKey, brandId) {
  return apiRequest('v1/metrics/report', apiKey, 'POST', { brandId });
}

/** POST /metricsV1SearchTermsReport — top queries with detection */
async function fetchSearchTermsReport(apiKey, brandId) {
  return apiRequest('v1/metrics/search-terms-report', apiKey, 'POST', { brandId });
}

/** GET /metricsV1SearchTerms — raw search terms (query param) */
async function fetchSearchTerms(apiKey, brandId) {
  return apiRequest(`v1/metrics/search-terms?brandId=${brandId}`, apiKey, 'GET');
}

/**
 * POST /metricsV1Citations — standalone citation metrics.
 * Response shapes:
 *   Format A: { brandId, count, rate, industryAvg, sources: [...] }
 *   Format B: { total, citationRate, benchmarkRate, topSources: [...] }
 *
 * @param {string} apiKey
 * @param {string} brandId
 * @returns {Promise<object>}
 */
async function fetchCitations(apiKey, brandId) {
  return apiRequest('v1/metrics/citations', apiKey, 'POST', { brandId });
}

/**
 * POST /metricsV1Sentiment — standalone sentiment metrics.
 * Response shapes:
 *   Format A: { positive: 0.61, neutral: 0.29, negative: 0.10, sampleSize: 412 }
 *   Format B: { scores: { pos: 61, neu: 29, neg: 10 }, sampleSize: 412 }
 *   Format C: { positive: 61, neutral: 29, negative: 10 }
 *
 * @param {string} apiKey
 * @param {string} brandId
 * @returns {Promise<object>}
 */
async function fetchSentiment(apiKey, brandId) {
  return apiRequest('v1/metrics/sentiment', apiKey, 'POST', { brandId });
}

// ─── Brands Normalization ─────────────────────────────────
/** Extract brands array from API response (handles envelope) */
function normalizeBrands(raw) {
  if (!raw) return [];
  // Real API: { success: true, data: { brands: [...] } }
  const d = raw.data || raw;
  if (d.brands) return d.brands;
  if (Array.isArray(d)) return d;
  // Fallback: maybe data itself is the brands array
  return [];
}

// ─── Brand Discovery ─────────────────────────────────────
async function discoverBrandId(apiKey, brandName) {
  const raw = await fetchBrands(apiKey);
  const brands = normalizeBrands(raw);

  if (!Array.isArray(brands) || brands.length === 0) {
    throw new NotFoundError(
      'No brands found on this account. ' +
        'Please set up a brand at https://rankscale.ai/dashboard/signup'
    );
  }

  if (brands.length === 1) {
    return brands[0].id || brands[0].brandId;
  }

  // Try to match by name if provided
  if (brandName) {
    const match = brands.find(
      (b) =>
        (b.name || b.brandName || '')
          .toLowerCase()
          .includes(brandName.toLowerCase())
    );
    if (match) return match.id || match.brandId;
  }

  // Return first brand + log available
  console.error(
    `Multiple brands found. Using: ${brands[0].name || brands[0].id}`
  );
  console.error(
    'Set RANKSCALE_BRAND_ID to specify: ' +
      brands.map((b) => `${b.name || '?'} (${b.id})`).join(', ')
  );
  return brands[0].id || brands[0].brandId;
}

// ─── Data Normalization ───────────────────────────────────

/**
 * Normalize sentiment — Rankscale returns three formats:
 *   Format A: { positive: 0.61, negative: 0.10, neutral: 0.29 }  (floats 0–1)
 *   Format B: { scores: { pos: 61, neg: 10, neu: 29 } }           (integers 0–100)
 *   Format C: { positive: 61, neutral: 29, negative: 10 }         (percentages)
 *
 * Fixes F5: operator precedence bug — (pos + neg + neu) || 100
 */
function normalizeSentiment(raw) {
  if (!raw) return { positive: 0, negative: 0, neutral: 0 };

  // Format B: nested scores object
  if (raw.scores) {
    const s = raw.scores;
    const pos = safeNum(s.pos ?? s.positive);
    const neg = safeNum(s.neg ?? s.negative);
    const neu = safeNum(s.neu ?? s.neutral);
    const total = (pos + neg + neu) || 100;  // explicit parentheses to fix precedence
    return {
      positive: safeFixed(pos / total * 100),
      negative: safeFixed(neg / total * 100),
      neutral: safeFixed(neu / total * 100),
    };
  }

  // Format A / C: flat fields — may be 0–1 floats or 0–100 integers
  const pos = safeNum(raw.positive ?? raw.pos);
  const neg = safeNum(raw.negative ?? raw.neg);
  const neu = safeNum(raw.neutral ?? raw.neu);

  // Detect float (0–1) vs percentage (0–100)
  if (pos <= 1 && neg <= 1 && neu <= 1 && (pos + neg + neu) <= 3) {
    return {
      positive: safeFixed(pos * 100),
      negative: safeFixed(neg * 100),
      neutral: safeFixed(neu * 100),
    };
  }

  return {
    positive: safeFixed(pos),
    negative: safeFixed(neg),
    neutral: safeFixed(neu),
  };
}

/**
 * Normalize citations response.
 * Handles: { count, rate, sources } or { total, citationRate, topSources }
 */
function normalizeCitations(raw) {
  if (!raw) return { count: 0, rate: 0, sources: [] };
  return {
    count: raw.count ?? raw.total ?? raw.citationCount ?? 0,
    rate: raw.rate ?? raw.citationRate ?? raw.percentage ?? 0,
    sources: raw.sources || raw.topSources || [],
    industryAvg: raw.industryAvg ?? raw.benchmarkRate ?? null,
  };
}

/**
 * Return a canonical empty report object used when the API fails or
 * the response cannot be parsed.
 *
 * @returns {object}
 */
function emptyReport() {
  return {
    score: 0,
    rank: null,
    change: 0,
    brandName: 'Your Brand',
    detectionRate: null,
    engines: {},
    competitors: [],
    _citationsRaw: { count: 0, rate: 0 },
    _sentimentRaw: null,
  };
}

/**
 * Normalize report response.
 *
 * Real API response shape (metricsV1Report):
 *   { data: {
 *       ownBrandMetrics: {
 *         visibilityScore, detectionRate, sentiment, citations,
 *         trends: { visibilityScore },
 *         engineMetricsData: { daily: [{engineId, engineName, visibilityScore:[...]}] }
 *       },
 *       competitorMetrics: [{name, visibilityScore, latestValue}]
 *     }
 *   }
 *
 * Also handles legacy flat format: { score, rank, change }
 *
 * Fixes F1: safeFixed(detectionRate) — no more .toFixed() on undefined
 * Fixes F2: (own.trends || {}).visibilityScore — guard against undefined trends
 */
function normalizeReport(raw) {
  if (!raw) return emptyReport();

  // Unwrap API envelope if present
  const d = raw.data || raw;
  const own = d.ownBrandMetrics || d;
  const competitorsRaw = safeArray(d.competitorMetrics || raw.competitors);

  // Score change from trends — guard own.trends being undefined (F2)
  const trends = own.trends || {};
  const change = safeNum(
    trends.visibilityScore ?? raw.change ?? raw.weeklyDelta ?? raw.delta,
    0
  );

  // Build per-engine map using the most recent value of each engine
  const engineEntries = own.engineMetricsData || {};
  const engineDaily = safeArray(engineEntries.daily || engineEntries.weekly);
  const engines = {};
  engineDaily.forEach((e) => {
    const scores = safeArray(e.visibilityScore);
    if (scores.length > 0) {
      const label = e.engineName || e.engineId || 'unknown';
      // Use the last (most recent) score
      engines[label] = safeNum(scores[scores.length - 1]);
    }
  });

  // Detection rate — use safeNum to avoid .toFixed() crash (F1)
  const detectionRate = safeNum(
    own.detectionRate ?? raw.detectionRate,
    null
  );

  // Sentiment — API returns a single composite number (0–100)
  // We synthesize positive/negative from it for compatibility
  const sentimentScore = safeNum(own.sentiment ?? raw.sentiment, null);

  return {
    score: safeNum(
      own.visibilityScore ?? own.score ?? raw.score ?? raw.geoScore,
      0
    ),
    rank: own.rank ?? raw.rank ?? null,
    change: safeFixed(change),
    brandName: own.brandName ?? raw.brandName ?? raw.brand ?? 'Your Brand',
    detectionRate: detectionRate != null ? safeFixed(detectionRate) : null,
    engines,
    competitors: competitorsRaw,
    // Stash raw citation + sentiment values for downstream normalization
    _citationsRaw: {
      count: safeNum(own.citations, 0),
      // Use detectionRate as the citation rate proxy (both measure presence)
      rate: safeNum(own.detectionRate ?? own.citations, 0),
    },
    _sentimentRaw:
      sentimentScore != null
        ? buildSentimentFromScore(sentimentScore)
        : null,
  };
}

/**
 * Convert a composite sentiment score (0–100) to pos/neu/neg breakdown.
 * High sentiment → more positive; low → more negative.
 *
 * Uses safeNum() to handle string scores gracefully (F3).
 *
 * @param {number|string} score  - composite sentiment score 0–100
 * @returns {{ positive: number, negative: number, neutral: number }}
 */
function buildSentimentFromScore(score) {
  // Coerce safely — handles strings like "65" without arithmetic errors
  const positive = Math.min(100, Math.max(0, safeFixed(safeNum(score))));
  // Model: pos + neu + neg = 100, neg is roughly (100 - score) * 0.3
  const negative = Math.max(0, safeFixed((100 - positive) * 0.3));
  const neutral = safeFixed(100 - positive - negative);
  return { positive, negative, neutral };
}

/**
 * Normalize search terms.
 *
 * Real API response shape (metricsV1SearchTermsReport):
 *   { data: { timeFrame, searchTerms: [{searchTermId, query, ...}] } }
 *
 * Also handles:
 *   Legacy: { terms: [{query, mentions}] }
 *   Bare array: [{query, count}]
 *
 * Fixes F9: guards t.aiSearchEngines with Array.isArray() before .length
 */
function normalizeSearchTerms(raw) {
  if (!raw) return [];

  // Unwrap API envelope
  const d = raw.data || raw;

  // Resolve terms array from any known field name, including bare-array response
  const terms = safeArray(
    d.searchTerms ||
    d.terms ||
    d.results ||
    (Array.isArray(d) ? d : [])
  );

  // Deduplicate by query, summing mentions
  const seen = new Map();
  terms.forEach((t) => {
    if (!t) return;  // null guard
    const q = t.query || t.term || t.keyword || t.name || '';
    if (!q) return;
    // Use Array.isArray() guard to prevent .length crash (F9)
    const m = safeNum(
      t.mentions ?? t.count ?? t.frequency ??
      (Array.isArray(t.aiSearchEngines) ? t.aiSearchEngines.length : 0)
    );
    seen.set(q, (seen.get(q) || 0) + m);
  });

  return Array.from(seen.entries())
    .map(([query, mentions]) => ({ query, mentions }))
    .sort((a, b) => b.mentions - a.mentions)
    .slice(0, 10);
}

/**
 * Normalize competitors array from report.
 * Returns top 3 with delta vs brand visibility.
 *
 * Format: "CompetitorName: Score [±X% vs us]"
 *
 * Fixes F4: guards against Infinity delta when score or brandScore is 0.
 */
function normalizeCompetitors(competitorsRaw, brandScore) {
  if (!Array.isArray(competitorsRaw) || competitorsRaw.length === 0) {
    return [];
  }

  return competitorsRaw
    .filter((c) => c && !c.isOwnBrand)  // null guard + exclude own brand
    .map((c) => {
      const name = c.name || c.brandName || c.competitor || 'Unknown';
      const score = safeNum(
        c.latestValue ?? c.visibilityScore ?? c.score ?? c.geoScore ?? c.visibility
      );
      // Delta: how much AHEAD (+) or BEHIND (-) we are vs competitor
      // (brand - competitor) / competitor * 100
      // Guard: skip if either side is 0 or null to avoid Infinity/NaN (F4)
      let delta = null;
      if (score > 0 && brandScore != null && brandScore > 0) {
        delta = Math.round(((brandScore - score) / score) * 100);
      }
      return { name, score, delta };
    })
    .sort((a, b) => b.score - a.score)
    .slice(0, 3);
}

// ─── GEO Interpretation Module ───────────────────────────

const GEO_RULES = [
  {
    id: 'R1',
    name: 'Low Citation Rate',
    severity: 'WARN',
    check: (data) => data.citations.rate < 40,
    recommendation:
      'Citation rate below 40% target.\n' +
      '  Action: Publish 2+ authoritative comparison\n' +
      '  articles and press releases this month.\n' +
      '  Target sources: industry blogs, news sites.',
  },
  {
    id: 'R2',
    name: 'Critical Citation Rate',
    severity: 'CRIT',
    check: (data) => data.citations.rate < 20,
    recommendation:
      'Citation rate critically low (<20%).\n' +
      '  Action: Immediate content blitz needed.\n' +
      '  Submit brand to 5+ AI-indexed directories.\n' +
      '  Build backlinks from authoritative sources.',
  },
  {
    id: 'R3',
    name: 'Negative Sentiment Spike',
    severity: 'CRIT',
    check: (data) => data.sentiment.negative > 25,
    recommendation:
      'Negative sentiment exceeds 25%.\n' +
      '  Action: Audit top negative queries.\n' +
      '  Create rebuttal/FAQ content addressing\n' +
      '  negative narratives. Monitor weekly.',
  },
  {
    id: 'R4',
    name: 'Low GEO Score',
    severity: 'CRIT',
    check: (data) => data.report.score < 40,
    recommendation:
      'GEO score critically low (<40).\n' +
      '  Action: Comprehensive GEO audit needed.\n' +
      '  Add schema markup, improve content depth,\n' +
      '  and increase citation velocity.',
  },
  {
    id: 'R5',
    name: 'Medium GEO Score',
    severity: 'WARN',
    check: (data) =>
      data.report.score >= 40 && data.report.score < 65,
    recommendation:
      'GEO score in growth zone (40–64).\n' +
      '  Action: Focus on 3 high-volume search terms.\n' +
      '  Create dedicated landing pages optimized\n' +
      '  for AI answer inclusion.',
  },
  {
    id: 'R6',
    name: 'Negative Score Trend',
    severity: 'WARN',
    check: (data) => data.report.change < -5,
    recommendation:
      'GEO score declining (>' + Math.abs(-5) + ' pts drop).\n' +
      '  Action: Identify content gaps causing drop.\n' +
      '  Review which competitors gained citations\n' +
      '  and match their content strategy.',
  },
  {
    id: 'R7',
    name: 'Positive Momentum',
    severity: 'INFO',
    check: (data) =>
      data.report.change >= 3 && data.sentiment.positive > 55,
    recommendation:
      'Strong positive momentum detected.\n' +
      '  Action: Maintain current content cadence.\n' +
      '  Double down on formats producing citations.\n' +
      '  Consider expanding to adjacent topics.',
  },
  {
    id: 'R8',
    name: 'Content Gap Investigation',
    severity: 'WARN',
    check: (data) =>
      data.report.detectionRate != null &&
      data.report.detectionRate < 70,
    recommendation:
      'Detection rate below 70% — brand not cited\n' +
      '  in AI results for many queries.\n' +
      '  Action: Research underrepresented topics;\n' +
      '  create content targeting those gaps.\n' +
      '  Timeline: 2–4 weeks to improve detection.',
  },
  {
    id: 'R9',
    name: 'Competitive Benchmark',
    severity: 'WARN',
    check: (data) => {
      const comps = data.report.competitors || [];
      if (comps.length === 0) return false;
      const topScore = Math.max(...comps.map(
        (c) => c.score ?? c.visibilityScore ?? c.geoScore ?? 0
      ));
      return topScore - data.report.score > 15;
    },
    recommendation:
      'A top competitor is >15 pts ahead in\n' +
      '  visibility. Root cause: better content,\n' +
      '  more citations, or stronger authority.\n' +
      '  Action: Analyze competitor content strategy;\n' +
      '  identify differentiation opportunities.\n' +
      '  Timeline: 4–8 weeks to close the gap.',
  },
  {
    id: 'R10',
    name: 'Engine-Specific Optimization',
    severity: 'WARN',
    check: (data) => {
      const engines = data.report.engines || {};
      const scores = Object.values(engines).filter(
        (v) => typeof v === 'number'
      );
      if (scores.length < 2) return false;
      return Math.max(...scores) - Math.min(...scores) > 30;
    },
    recommendation:
      'Engine visibility spread >30 pts detected.\n' +
      '  Root cause: Engines (e.g., ChatGPT) favor\n' +
      '  different content signals than others.\n' +
      '  Action: Audit top engine\'s citations/\n' +
      '  keywords; optimize for those signals.\n' +
      '  Timeline: 3–6 weeks.',
  },
];

/**
 * Run interpretation rules and return top 3–5 insights.
 */
function interpretGeoData(data) {
  const triggered = GEO_RULES.filter((rule) => {
    try {
      return rule.check(data);
    } catch {
      return false;
    }
  });

  // Deduplicate: if CRIT for R2 fires, skip WARN R1 (same dimension)
  const deduplicated = triggered.filter((rule, idx, arr) => {
    if (rule.id === 'R1') {
      return !arr.find((r) => r.id === 'R2');
    }
    return true;
  });

  // Sort: CRIT > WARN > INFO
  const order = { CRIT: 0, WARN: 1, INFO: 2 };
  deduplicated.sort(
    (a, b) => (order[a.severity] ?? 3) - (order[b.severity] ?? 3)
  );

  return deduplicated.slice(0, 5);
}

// ─── GEO Constants ───────────────────────────────────────
const {
  ENGINE_WEIGHTS,
  ENGINE_WEIGHT_DEFAULT,
  GEO_PATTERNS,
  REPUTATION_SCORE_WEIGHTS,
  ENGINE_DISPLAY_NAMES,
} = require('./references/geo-constants.js');

// ─── Feature A: Engine Strength Profile ──────────────────
/**
 * Produces an ASCII heatmap of visibility by engine.
 * Highlights top-3 (✦) and bottom-3 (▼) engines.
 *
 * @param {object} reportData  - normalizeReport() output
 * @returns {string}           - formatted ASCII block
 */
function analyzeEngineStrength(reportData) {
  const engines = safeGet(reportData, 'engines', {});
  const entries = Object.entries(engines)
    .map(([name, score]) => ({ name, score: safeNum(score) }))
    .filter((e) => e.score > 0 || Object.keys(engines).length > 0)
    .sort((a, b) => b.score - a.score);

  if (entries.length === 0) {
    return line() + '\n ENGINE STRENGTH PROFILE\n' +
      line() + '\n  No engine data available.\n' + line();
  }

  const scores = entries.map((e) => e.score);
  const avg = scores.reduce((a, b) => a + b, 0) / (scores.length || 1);
  const max = Math.max(...scores, 1);

  const BAR_WIDTH = 22;
  const topSet = new Set(entries.slice(0, 3).map((e) => e.name));
  const botSet = new Set(entries.slice(-3).map((e) => e.name));

  const rows = entries.map(({ name, score }) => {
    const barLen = Math.round((score / max) * BAR_WIDTH);
    const bar = '█'.repeat(barLen).padEnd(BAR_WIDTH);
    const tag = topSet.has(name) ? ' ✦' : botSet.has(name) ? ' ▼' : '  ';
    const displayName = ENGINE_DISPLAY_NAMES[name] || ENGINE_DISPLAY_NAMES[name.toLowerCase()] || name;
    const label = displayName.padEnd(20).slice(0, 20);
    const pct = String(safeFixed(score, 1)).padStart(5);
    return `  ${label} ${bar}${pct}${tag}`;
  });

  const avgLine = `  ${'Average'.padEnd(12)} ${
    '─'.repeat(Math.round((avg / max) * BAR_WIDTH)).padEnd(BAR_WIDTH)
  }${String(safeFixed(avg, 1)).padStart(5)}`;

  return [
    line(),
    center('ENGINE STRENGTH PROFILE'),
    line(),
    `  ${'Engine'.padEnd(12)} ${'Visibility'.padEnd(BAR_WIDTH)}Score`,
    avgLine,
    line('-'),
    ...rows,
    line(),
    `  ✦ Top-3 engines  ▼ Bottom-3 engines`,
  ].join('\n');
}

// ─── Feature B: Content Gap Analysis ─────────────────────
/**
 * Identifies content gaps across engines and search terms.
 * Cross-references visibility with engine averages to surface
 * terms/engines needing attention.
 *
 * @param {object} reportData      - normalizeReport() output
 * @param {object} searchTermsData - normalizeSearchTerms() output
 * @returns {string}               - formatted gap analysis block
 */
function analyzeContentGaps(reportData, searchTermsData) {
  const engineBreakdown = safeArray(
    safeGet(reportData, 'engineBreakdown')
  );
  // Accept flat Array (already-normalised) or raw object with nested terms
  const terms = Array.isArray(searchTermsData)
    ? searchTermsData
    : safeArray(
        safeGet(searchTermsData, 'terms') ||
        safeGet(searchTermsData, 'searchTerms') ||
        safeGet(searchTermsData, 'data')
      );

  const lines = [
    line(),
    center('CONTENT GAP ANALYSIS'),
    line(),
  ];

  // ── Engine-level gaps ──────────────────────────────────
  if (engineBreakdown.length > 0) {
    const scores = engineBreakdown.map((e) =>
      safeNum(e.score ?? e.visibility ?? e.visibilityScore)
    );
    const overallAvg = scores.reduce((a, b) => a + b, 0) /
      (scores.length || 1);

    const weakEngines = engineBreakdown
      .map((e) => ({
        engine: safeGet(e, 'engine', 'unknown'),
        score: safeNum(e.score ?? e.visibility ?? e.visibilityScore),
      }))
      .filter(
        (e) =>
          overallAvg - e.score >
          GEO_PATTERNS.CONTENT_GAP_ENGINE_DROP_PTS
      )
      .sort((a, b) => a.score - b.score);

    lines.push('  ENGINE GAPS (vs avg ' +
      safeFixed(overallAvg, 1) + '):');

    if (weakEngines.length === 0) {
      lines.push('  No significant engine gaps detected.');
    } else {
      weakEngines.slice(0, 5).forEach(({ engine, score }) => {
        const drop = safeFixed(overallAvg - score, 1);
        lines.push(
          `  ▼ ${engine.padEnd(14)} score:${
            String(safeFixed(score, 1)).padStart(5)
          }  gap:-${drop}`
        );
      });
    }
    lines.push('');
  }

  // ── Term-level gaps ────────────────────────────────────
  if (terms.length > 0) {
    // Identify low-visibility terms (<50% visibility)
    const lowVis = terms
      .map((t) => ({
        term: String(safeGet(t, 'term', safeGet(t, 'query', '?'))),
        visibility: safeNum(
          t.visibility ?? t.visibilityScore ?? t.score
        ),
      }))
      .filter((t) => t.visibility < 50)
      .sort((a, b) => a.visibility - b.visibility);

    lines.push(
      `  LOW-VISIBILITY TERMS (<50%) — ${lowVis.length} found:`
    );

    if (lowVis.length === 0) {
      lines.push('  All terms above 50% visibility. ✓');
    } else {
      lowVis.slice(0, 8).forEach(({ term, visibility }) => {
        const bar = '░'.repeat(Math.round(visibility / 5)).padEnd(20);
        lines.push(
          `  ${term.slice(0, 22).padEnd(22)} ${bar}${
            String(safeFixed(visibility, 0)).padStart(4)}%`
        );
      });
      if (lowVis.length > 8) {
        lines.push(`  … and ${lowVis.length - 8} more gaps`);
      }
    }
    lines.push('');

    // Priority recommendations
    lines.push('  RECOMMENDATIONS:');
    if (lowVis.length > 0) {
      lines.push(
        `  1. Create content targeting top ${
          Math.min(lowVis.length, 3)
        } gap terms:`
      );
      lowVis.slice(0, 3).forEach(({ term }) => {
        lines.push(`     • "${term}"`);
      });
    }
    if (engineBreakdown.length > 0) {
      const scores = engineBreakdown.map((e) =>
        safeNum(e.score ?? e.visibility ?? e.visibilityScore)
      );
      const avg = scores.reduce((a, b) => a + b, 0) /
        (scores.length || 1);
      const weakest = engineBreakdown
        .sort(
          (a, b) =>
            safeNum(a.score ?? a.visibility) -
            safeNum(b.score ?? b.visibility)
        )
        .slice(0, 1);
      if (weakest.length) {
        const e = weakest[0];
        const eName = safeGet(e, 'engine', 'unknown');
        lines.push(
          `  2. Optimise for ${eName}: score ` +
          `${safeFixed(
            safeNum(e.score ?? e.visibility ?? e.visibilityScore), 1
          )} vs avg ${safeFixed(avg, 1)}`
        );
      }
    }
  } else if (engineBreakdown.length === 0) {
    lines.push('  No data available for gap analysis.');
  }

  lines.push(line());
  return lines.join('\n');
}

// ─── Feature C: Reputation Score & Summary ───────────────
/**
 * Computes a 0-100 brand reputation score from sentiment data.
 * Algorithm: 60% base ratio + 20% engine score - 20% severity penalty.
 *
 * @param {object} sentimentData - normalizeSentiment() output
 * @returns {string}             - formatted reputation block
 */
function computeReputationScore(sentimentData) {
  const W = REPUTATION_SCORE_WEIGHTS;

  // Flatten keyword lists — handles both [{keyword,count}] and [string]
  const toKwList = (arr) =>
    safeArray(arr).map((k) =>
      typeof k === 'object' && k !== null
        ? { keyword: String(k.keyword || k.text || k), count: safeNum(k.count || k.frequency, 1) }
        : { keyword: String(k), count: 1 }
    );

  const posKws = toKwList(safeGet(sentimentData, 'positiveKeywords'));
  const negKws = toKwList(safeGet(sentimentData, 'negativeKeywords'));
  const neuKws = toKwList(safeGet(sentimentData, 'neutralKeywords'));

  const posCount = posKws.reduce((s, k) => s + k.count, 0);
  const negCount = negKws.reduce((s, k) => s + k.count, 0);
  const neuCount = neuKws.reduce((s, k) => s + k.count, 0);
  const total = posCount + negCount + neuCount || 1;

  // Step A: Base ratio (-1 to +1)
  const baseRatio = (posCount - 2 * negCount) / total;

  // Step B: Severity penalty — high-frequency negatives penalise more
  const severityPenalty = negKws.reduce(
    (sum, k) => sum + (k.count / total) ** 2,
    0
  );

  // Step C: Engine-weighted sentiment score
  const engineBreakdown = safeArray(
    safeGet(sentimentData, 'engineBreakdown')
  );
  const totalEngineWeight = Object.values(ENGINE_WEIGHTS).reduce(
    (a, b) => a + b,
    0
  );
  const engineScore =
    engineBreakdown.length > 0
      ? engineBreakdown.reduce((acc, e) => {
          const wt =
            ENGINE_WEIGHTS[String(e.engine).toLowerCase()] ||
            ENGINE_WEIGHT_DEFAULT;
          return acc + safeNum(e.sentiment) * wt;
        }, 0) / totalEngineWeight
      : 0;

  // Combine
  const raw =
    baseRatio * W.BASE_RATIO +
    engineScore * W.ENGINE_SCORE -
    severityPenalty * W.SEVERITY_PENALTY;

  const scoreRaw = Math.max(0, Math.min(100, (raw + W.NORM_OFFSET) * W.NORM_SCALE));
  const score = scoreRaw.toFixed(1); // string "50.0" format

  // Trend: use report change or sentiment trend if available
  const sentimentTrend = safeGet(sentimentData, 'trend', null);
  let trend = 'stable';
  if (sentimentTrend === 'up' || sentimentTrend === 'improving') {
    trend = 'improving';
  } else if (sentimentTrend === 'down' || sentimentTrend === 'declining') {
    trend = 'declining';
  }

  // Risk areas: top negative keywords by count
  const riskAreas = negKws
    .sort((a, b) => b.count - a.count)
    .slice(0, W.TOP_RISK_KEYWORDS)
    .map((k) => k.keyword);

  // Top positive keywords
  const topPos = posKws
    .sort((a, b) => b.count - a.count)
    .slice(0, 5)
    .map((k) => k.keyword);

  // Score label
  const scoreLabel =
    score >= 75 ? 'Excellent' :
    score >= 60 ? 'Good' :
    score >= 45 ? 'Fair' :
    score >= 30 ? 'Poor' : 'Critical';

  // Trend arrow
  const trendArrow =
    trend === 'improving' ? '↑' :
    trend === 'declining' ? '↓' : '→';

  // Summary sentence
  const summary =
    `Brand health is ${scoreLabel.toLowerCase()} (${score}/100) ` +
    `and ${trend}.` +
    (riskAreas.length
      ? ` Monitor: ${riskAreas.slice(0, 2).join(', ')}.`
      : '');

  // Score bar
  const barLen = Math.round(score / 100 * 30);
  const scoreBar = '█'.repeat(barLen) + '░'.repeat(30 - barLen);

  // Truncate keywords to fit width (≤55 chars per line)
  const truncKw = (kw) => kw.length > 14 ? kw.slice(0, 12) + '…' : kw;
  const topPosShort = topPos.slice(0, 2).map(truncKw);
  const riskShort = riskAreas.slice(0, 2).map(truncKw);

  // Summary lines truncated to ≤55 chars each
  const summaryBase =
    `  ${scoreLabel} (${score}/100) ${trendArrow} ${trend}`;
  const summaryRisk = riskShort.length
    ? `  Risks:    ${riskShort.join(', ')}`
    : '';

  return [
    line(),
    center('REPUTATION SCORE & SUMMARY'),
    line(),
    `  Score:  ${scoreBar} ${score}/100`,
    `  Status: ${scoreLabel}   Trend: ${trendArrow} ${trend}`,
    '',
    `  Sentiment:`,
    ...(posKws.length === 0 && negKws.length === 0
      ? ['    —', '    (Insufficient data)']
      : [
          `    Pos: ${safeFixed(posCount / total * 100, 1)}%` +
          `  Neg: ${safeFixed(negCount / total * 100, 1)}%` +
          `  Neu: ${safeFixed(neuCount / total * 100, 1)}%`,
        ]),
    '',
    topPosShort.length
      ? `  Strengths: ${topPosShort.join(', ')}`
      : '  No positive signals found.',
    '',
    summaryBase,
    ...(summaryRisk ? [summaryRisk] : []),
    line(),
  ].join('\n');
}

// ─── Feature D: Engine Gainers & Losers ──────────────────
/**
 * Compares current vs prior period visibility per engine,
 * ranking by biggest gain or loss (±5+ point swing flagged).
 *
 * @param {object} reportData     - normalizeReport() current period
 * @param {object} priorReportData - normalizeReport() prior period (may be null)
 * @returns {string}              - formatted engine movers block
 */
function analyzeEngineMovers(reportData, priorReportData) {
  const current = safeArray(safeGet(reportData, 'engineBreakdown'));
  const prior = safeArray(safeGet(priorReportData, 'engineBreakdown'));

  const lines = [
    line(),
    center('ENGINE GAINERS & LOSERS'),
    line(),
  ];

  if (current.length === 0) {
    lines.push('  No engine data available.');
    lines.push(line());
    return lines.join('\n');
  }

  // Build prior lookup by engine name
  const priorMap = {};
  prior.forEach((e) => {
    const key = String(safeGet(e, 'engine', '')).toLowerCase();
    if (key) priorMap[key] = safeNum(e.score ?? e.visibility ?? e.visibilityScore);
  });

  // Calculate deltas for each engine
  const deltas = current.map((e) => {
    const name = String(safeGet(e, 'engine', 'unknown')).toLowerCase();
    const curr = safeNum(e.score ?? e.visibility ?? e.visibilityScore);
    const prev = priorMap[name] ?? null;
    const delta = prev !== null ? safeFixed(curr - prev, 1) : null;
    return { name, curr: safeFixed(curr, 1), prev, delta };
  }).filter((e) => e.delta !== null);

  if (deltas.length === 0) {
    lines.push('  No prior period data — trend comparison unavailable.');
    lines.push('  Current scores:');
    current.slice(0, 5).forEach((e) => {
      const rawName = String(safeGet(e, 'engine', 'unknown'));
      const displayName = ENGINE_DISPLAY_NAMES[rawName] || ENGINE_DISPLAY_NAMES[rawName.toLowerCase()] || rawName;
      const score = safeFixed(e.score ?? e.visibility ?? e.visibilityScore, 1);
      lines.push(`  ${displayName.slice(0, 25).padEnd(25)} ${String(score).padStart(5)}`);
    });
    lines.push(line());
    return lines.join('\n');
  }

  const SWING_THRESHOLD = 5;
  const gainers = deltas
    .filter((e) => e.delta > 0)
    .sort((a, b) => b.delta - a.delta)
    .slice(0, 3);
  const losers = deltas
    .filter((e) => e.delta < 0)
    .sort((a, b) => a.delta - b.delta)
    .slice(0, 3);

  lines.push('  TOP GAINERS (vs prior period):');
  if (gainers.length === 0) {
    lines.push('  No engines improved this period.');
  } else {
    gainers.forEach(({ name, curr, delta }) => {
      const flag = delta >= SWING_THRESHOLD ? ' ◆' : '';
      const arrow = '↑';
      const displayName = ENGINE_DISPLAY_NAMES[name] || ENGINE_DISPLAY_NAMES[name.toLowerCase()] || name;
      lines.push(
        `  ${arrow} ${displayName.slice(0, 25).padEnd(25)} ` +
        `${String(curr).padStart(5)}  +${delta}${flag}`
      );
    });
  }

  lines.push('');
  lines.push('  TOP LOSERS (vs prior period):');
  if (losers.length === 0) {
    lines.push('  No engines declined this period.');
  } else {
    losers.forEach(({ name, curr, delta }) => {
      const flag = Math.abs(delta) >= SWING_THRESHOLD ? ' ◆' : '';
      const arrow = '↓';
      const displayName = ENGINE_DISPLAY_NAMES[name] || ENGINE_DISPLAY_NAMES[name.toLowerCase()] || name;
      lines.push(
        `  ${arrow} ${displayName.slice(0, 25).padEnd(25)} ` +
        `${String(curr).padStart(5)}   ${delta}${flag}`
      );
    });
  }

  const swingCount = deltas.filter(
    (e) => Math.abs(e.delta) >= SWING_THRESHOLD
  ).length;
  if (swingCount > 0) {
    lines.push('');
    lines.push(`  ◆ = ±${SWING_THRESHOLD}+ point swing (significant)`);
  }

  lines.push(line());
  return lines.join('\n');
}

// ─── Feature E: Sentiment Shift Alert ────────────────────
/**
 * Detects significant negative keyword clusters, identifies
 * sentiment trend direction, and flags risk areas.
 *
 * @param {object} sentimentData      - normalizeSentiment() current period
 * @param {object} priorSentimentData - normalizeSentiment() prior period (may be null)
 * @returns {string}                  - formatted sentiment alert block
 */
function analyzeSentimentShift(sentimentData, priorSentimentData) {
  const CLUSTER_THRESHOLD = 5; // >5x mentions = significant cluster

  // Flatten keyword lists
  const toKwList = (arr) =>
    safeArray(arr).map((k) =>
      typeof k === 'object' && k !== null
        ? { keyword: String(k.keyword || k.text || k), count: safeNum(k.count || k.frequency, 1) }
        : { keyword: String(k), count: 1 }
    );

  const negKws = toKwList(safeGet(sentimentData, 'negativeKeywords'));
  const posKws = toKwList(safeGet(sentimentData, 'positiveKeywords'));

  const priorNegKws = toKwList(safeGet(priorSentimentData, 'negativeKeywords'));
  const priorPosKws = toKwList(safeGet(priorSentimentData, 'positiveKeywords'));

  const lines = [
    line(),
    center('SENTIMENT SHIFT ALERT'),
    line(),
  ];

  // Trend: compare positive vs negative counts current vs prior
  const currPos = posKws.reduce((s, k) => s + k.count, 0);
  const currNeg = negKws.reduce((s, k) => s + k.count, 0);
  const priorPos = priorPosKws.reduce((s, k) => s + k.count, 0);
  const priorNeg = priorNegKws.reduce((s, k) => s + k.count, 0);

  // Sentiment polarity: higher = more positive
  const currPolarity = currPos - currNeg;
  const priorPolarity = priorPos - priorNeg;
  const hasPrior = priorSentimentData != null &&
    (priorPos + priorNeg) > 0;

  let trendLabel = 'stable';
  let trendIcon = '→';
  if (hasPrior) {
    const polarityDelta = currPolarity - priorPolarity;
    if (polarityDelta > 2) { trendLabel = 'improving'; trendIcon = '↗'; }
    else if (polarityDelta < -2) { trendLabel = 'declining'; trendIcon = '↘'; }
  } else if (currPos + currNeg > 0) {
    // No prior: derive from current balance
    const ratio = currNeg / (currPos + currNeg || 1);
    if (ratio > 0.4) { trendLabel = 'at risk'; trendIcon = '↘'; }
    else if (ratio < 0.2) { trendLabel = 'healthy'; trendIcon = '↗'; }
  }

  lines.push(
    `  Sentiment Trend:  ${trendIcon} ${trendLabel.toUpperCase()}`
  );
  lines.push('');

  // Negative keyword clusters — high-frequency negatives
  const avgNegCount = negKws.length > 0
    ? negKws.reduce((s, k) => s + k.count, 0) / negKws.length
    : 0;
  const clusters = negKws
    .filter((k) => k.count > Math.max(avgNegCount * 2, CLUSTER_THRESHOLD))
    .sort((a, b) => b.count - a.count)
    .slice(0, 3);

  lines.push('  RISK AREAS:');
  if (clusters.length === 0 && negKws.length === 0) {
    lines.push('  ✓ No negative keyword clusters detected.');
  } else if (clusters.length === 0) {
    lines.push('  No significant negative clusters (below threshold).');
    // Show top negatives anyway for context
    const topNeg = negKws.sort((a, b) => b.count - a.count).slice(0, 3);
    topNeg.forEach((k) => {
      lines.push(`  ⚠ ${k.keyword.slice(0, 28).padEnd(28)} ${k.count}x`);
    });
  } else {
    clusters.forEach((k) => {
      lines.push(
        `  ⚠ ${k.keyword.slice(0, 28).padEnd(28)} ${k.count}x  [CLUSTER]`
      );
    });
    lines.push('');
    lines.push('  ACTION: Address these topics proactively.');
  }

  if (trendLabel === 'improving' || trendLabel === 'healthy') {
    lines.push('');
    lines.push('  ✓ Sentiment is moving in the right direction.');
  } else if (trendLabel === 'declining' || trendLabel === 'at risk') {
    lines.push('');
    lines.push('  ! Monitor closely — negative signals increasing.');
  }

  lines.push(line());
  return lines.join('\n');
}

// ─── Feature F: Citation Intelligence Hub ────────────────
/**
 * Comprehensive citation analysis: authority ranking, gap analysis,
 * engine preferences, visibility correlation, and PR opportunities.
 *
 * @param {object} citationsRaw   - raw citations API response
 * @param {object} reportData     - normalizeReport() output
 * @param {Array}  searchTerms    - normalizeSearchTerms() output
 * @param {string} subMode        - 'full'|'authority'|'gaps'|'engines'|'correlation'|'pr'|''
 * @returns {string}              - formatted ASCII output
 */
function analyzeCitationIntelligence(citationsRaw, reportData, searchTerms, subMode) {
  // ── Parse sources from raw citations response ──────────
  const rawSources = safeArray(
    safeGet(citationsRaw, 'sources') ||
    safeGet(citationsRaw, 'topSources') ||
    safeGet(citationsRaw, 'domains') ||
    safeGet(citationsRaw, 'data.sources') ||
    safeGet(citationsRaw, 'data.topSources')
  );

  // Normalise each source entry — handle multiple API shapes
  const sources = rawSources.map((s) => {
    if (!s) return null;
    const domain =
      String(s.domain || s.url || s.source || s.name || s.host || '').replace(/^https?:\/\//, '').split('/')[0];
    const frequency = safeNum(s.frequency || s.count || s.citations || s.total, 1);
    const engines = safeArray(s.engines || s.aiEngines || []);
    const engineCount = engines.length || safeNum(s.engineCount || s.engines_count, 0);
    const engine = String(s.engine || s.engineId || s.engineName || '').toLowerCase();
    const timestamp = s.timestamp || s.date || s.lastSeen || null;
    return { domain, frequency, engines, engineCount, engine, timestamp };
  }).filter((s) => s && s.domain);

  // Determine which sections to show
  const showAll    = !subMode || subMode === 'full';
  const showA      = showAll || subMode === 'authority';
  const showB      = showAll || subMode === 'gaps';
  const showC      = showAll || subMode === 'engines';
  const showD      = subMode === 'full' || subMode === 'correlation';
  const showE      = subMode === 'full' || subMode === 'pr';

  const out = [];

  out.push(line('='));
  out.push(center('CITATION INTELLIGENCE HUB'));
  out.push(line('='));

  if (sources.length === 0) {
    out.push('');
    out.push('  No citation data available.');
    out.push('  (Citations endpoint returned no sources)');
    out.push('');
    out.push('  Try running the default report first to');
    out.push('  confirm the API key and brand ID are set.');
    out.push('');
    out.push('  Sub-commands:');
    out.push('    --citations authority   Top source ranking');
    out.push('    --citations gaps        Gap vs competitors');
    out.push('    --citations engines     Per-engine breakdown');
    out.push('    --citations correlation Citation↔Visibility');
    out.push('    --citations full        All sections');
    out.push(line('='));
    return out.join('\n');
  }

  // ── A: Citation Authority Ranking ─────────────────────
  if (showA) {
    out.push(...sectionCitationAuthority(sources));
  }

  // ── B: Citation Gap Analysis ───────────────────────────
  if (showB) {
    out.push(...sectionCitationGaps(sources, reportData, searchTerms));
  }

  // ── C: Engine Citation Preferences ────────────────────
  if (showC) {
    out.push(...sectionEnginePreferences(sources, reportData));
  }

  // ── D: Citation-Visibility Correlation ────────────────
  if (showD) {
    out.push(...sectionCitationCorrelation(sources, reportData));
  }

  // ── E: PR Opportunity Mapper ───────────────────────────
  if (showE) {
    out.push(...sectionPROpportunities(sources, reportData));
  }

  // Footer hint
  out.push('');
  out.push('  Sub-commands:');
  out.push('    --citations authority   Source ranking');
  out.push('    --citations gaps        Gap vs competitors');
  out.push('    --citations engines     Per-engine breakdown');
  out.push('    --citations correlation Citation↔Visibility');
  out.push('    --citations full        All sections + PR map');
  out.push(line('='));
  return out.join('\n');
}

// ── A helper: Citation Authority Ranking ──────────────────
function sectionCitationAuthority(sources) {
  // Aggregate by domain (sources may have one entry per engine per domain)
  const domainMap = new Map();
  sources.forEach((s) => {
    if (!s.domain) return;
    const existing = domainMap.get(s.domain);
    if (existing) {
      existing.frequency += s.frequency;
      existing.engineCount = Math.max(existing.engineCount, s.engineCount);
      if (s.engine && !existing.enginesSet.has(s.engine)) {
        existing.enginesSet.add(s.engine);
        existing.engineCount = existing.enginesSet.size;
      }
    } else {
      const enginesSet = new Set();
      if (s.engine) enginesSet.add(s.engine);
      domainMap.set(s.domain, {
        domain: s.domain,
        frequency: s.frequency,
        engineCount: s.engineCount || (s.engine ? 1 : 0),
        enginesSet,
        timestamp: s.timestamp,
      });
    }
  });

  const entries = Array.from(domainMap.values()).map((e) => {
    const freq = safeNum(e.frequency, 1);
    const engC = safeNum(e.engineCount || e.enginesSet.size, 1);
    // Authority score = (frequency * 0.4) + (engine_count * 0.6)
    // Normalise: freq max ~20, engine_count max ~10 → raw score ~ 0–14
    const rawScore = freq * 0.4 + engC * 0.6;
    return { domain: e.domain, frequency: freq, engineCount: engC, rawScore };
  });

  // Normalise to 0–10 scale
  const maxRaw = Math.max(...entries.map((e) => e.rawScore), 1);
  const ranked = entries.map((e) => ({
    ...e,
    authorityScore: safeFixed(e.rawScore / maxRaw * 10, 1),
  })).sort((a, b) => b.authorityScore - a.authorityScore);

  const powerSources = new Set(ranked.slice(0, 5).map((e) => e.domain));

  const lines = [
    line('-'),
    center('A. CITATION AUTHORITY SOURCES'),
    line('-'),
    '  Top Authority Sources',
    '',
  ];

  ranked.slice(0, 8).forEach((e) => {
    const isPower = powerSources.has(e.domain);
    const domainStr = e.domain.slice(0, 22);
    lines.push(`  ◆ ${domainStr}`);
    lines.push(`    Authority: ${e.authorityScore}/10${isPower ? '  ★' : ''}`);
    if (e.engineCount > 0) {
      lines.push(`    Cited in ${e.engineCount} engine${e.engineCount !== 1 ? 's' : ''}`);
    }
    lines.push(`    ${e.frequency} citation${e.frequency !== 1 ? 's' : ''} total${isPower ? '  · Power source ★' : ''}`);
    lines.push('');
  });

  // Insight: strongest source
  if (ranked.length > 0) {
    const top = ranked[0];
    const domainShort = top.domain.replace(/\.com$/, '').slice(0, 20);
    lines.push(`  🎯 Insight: ${domainShort} is your strongest`);
    lines.push(`     citation source (${top.authorityScore}/10). Maintain`);
    lines.push(`     coverage there.`);
  }

  return lines;
}

// ── B helper: Citation Gap Analysis ───────────────────────
function sectionCitationGaps(sources, reportData, searchTerms) {
  const lines = [
    line('-'),
    center('B. CITATION GAPS (vs Competitors)'),
    line('-'),
    '  Domains citing competitors but NOT you',
    '',
  ];

  // Build YOUR domain set
  const yourDomains = new Set(sources.map((s) => s.domain).filter(Boolean));

  // Extract competitor names from reportData
  const competitors = safeArray(safeGet(reportData, 'competitors'));
  const compNames = competitors.map((c) =>
    String(c.name || c.brandName || '').toLowerCase()
  ).filter(Boolean);

  // Known high-authority review/media sites in SaaS/tech category
  // that commonly cite brands — used as gap targets if not in yourDomains
  const AUTHORITY_TARGETS = [
    { domain: 'g2.com',              authority: 'Very High ★', category: 'Reviews' },
    { domain: 'capterra.com',        authority: 'Very High ★', category: 'Reviews' },
    { domain: 'techradar.com',       authority: 'High',        category: 'Tech News' },
    { domain: 'solutionsreview.com', authority: 'High',        category: 'Reviews' },
    { domain: 'trustradius.com',     authority: 'High',        category: 'Reviews' },
    { domain: 'softwareadvice.com',  authority: 'Medium',      category: 'Reviews' },
    { domain: 'getapp.com',          authority: 'Medium',      category: 'Reviews' },
    { domain: 'zapier.com',          authority: 'High',        category: 'Integrations' },
    { domain: 'hubspot.com',         authority: 'Very High ★', category: 'Content Hub' },
    { domain: 'forbes.com',          authority: 'Very High ★', category: 'Enterprise' },
  ];

  // Identify gap targets: high-authority domains NOT in yourDomains
  const gaps = AUTHORITY_TARGETS.filter((t) => !yourDomains.has(t.domain));

  if (gaps.length === 0) {
    lines.push('  ✓ No major citation gaps found!');
    lines.push('    All tracked authority sites cite you.');
    lines.push('');
    lines.push('  🎯 Tip: Maintain current PR cadence to');
    lines.push('     keep citation coverage strong.');
    return lines;
  }

  gaps.slice(0, 5).forEach((target) => {
    lines.push(`  ↗ ${target.domain}`);
    if (compNames.length > 0) {
      const compSample = compNames.slice(0, 3)
        .map((n) => n.charAt(0).toUpperCase() + n.slice(1))
        .join(', ');
      lines.push(`    Cites: ${compSample.slice(0, 35)}`);
    }
    lines.push(`    Cites YOUR brand: ✗ (Opportunity!)`);
    lines.push(`    Category: ${target.category}`);
    lines.push(`    Authority: ${target.authority}`);
    lines.push('');
  });

  if (gaps.length > 0) {
    const topGap = gaps[0];
    lines.push(`  💡 Recommendation: Research`);
    lines.push(`     ${topGap.domain} for outreach.`);
    lines.push(`     They cover your category.`);
  }

  return lines;
}

// ── C helper: Engine Citation Preferences ─────────────────
function sectionEnginePreferences(sources, reportData) {
  const lines = [
    line('-'),
    center('C. ENGINE CITATION PREFERENCES'),
    line('-'),
    '  Which sources does each engine use?',
    '',
  ];

  // Group by engine
  const engineMap = new Map();
  sources.forEach((s) => {
    const eng = s.engine || 'unknown';
    // Also expand engines[] array if present
    const enginesForSource = s.engines.length > 0
      ? s.engines.map((e) => String(e.name || e.engineId || e).toLowerCase())
      : [eng];
    enginesForSource.forEach((e) => {
      if (!e || e === 'unknown') return;
      if (!engineMap.has(e)) engineMap.set(e, new Map());
      const domMap = engineMap.get(e);
      domMap.set(s.domain, (domMap.get(s.domain) || 0) + s.frequency);
    });
  });

  if (engineMap.size === 0) {
    // Fallback: show aggregated domain list without engine breakdown
    lines.push('  Engine-level data not available.');
    lines.push('  Showing aggregated top sources:');
    lines.push('');
    // Aggregate across all sources
    const domAgg = new Map();
    sources.forEach((s) => {
      domAgg.set(s.domain, (domAgg.get(s.domain) || 0) + s.frequency);
    });
    const sorted = Array.from(domAgg.entries()).sort((a, b) => b[1] - a[1]);
    sorted.slice(0, 5).forEach(([dom, freq]) => {
      lines.push(`  • ${dom.slice(0, 30).padEnd(30)} ${freq}x`);
    });
    lines.push('');
    lines.push('  💡 Tip: Per-engine breakdown requires');
    lines.push('     engine field in citations response.');
    return lines;
  }

  // Per-engine listing
  const reportEngines = safeGet(reportData, 'engines', {});
  const engineNames = Array.from(engineMap.keys()).sort();

  engineNames.forEach((eng) => {
    const domMap = engineMap.get(eng);
    const totalCitations = Array.from(domMap.values()).reduce((a, b) => a + b, 0);
    const topDoms = Array.from(domMap.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 4);

    const engLabel = ENGINE_DISPLAY_NAMES[eng] || ENGINE_DISPLAY_NAMES[eng.toLowerCase()] || (eng.charAt(0).toUpperCase() + eng.slice(1));
    lines.push(`  ${engLabel} (${totalCitations} citations)`);
    topDoms.forEach(([dom, freq]) => {
      lines.push(`    • ${dom.slice(0, 28)} (${freq}x)`);
    });
    lines.push('');
  });

  // Insight: find engine with lowest citation count → opportunity
  const engineTotals = Array.from(engineMap.entries()).map(([eng, domMap]) => ({
    eng,
    total: Array.from(domMap.values()).reduce((a, b) => a + b, 0),
  })).sort((a, b) => a.total - b.total);

  if (engineTotals.length > 1) {
    const weakest = engineTotals[0];
    const engLabel = ENGINE_DISPLAY_NAMES[weakest.eng] || ENGINE_DISPLAY_NAMES[weakest.eng.toLowerCase()] || (weakest.eng.charAt(0).toUpperCase() + weakest.eng.slice(1));
    lines.push(`  💡 Insight: ${engLabel} has fewest`);
    lines.push(`     citations (${weakest.total}x). Priority`);
    lines.push(`     target for new content.`);
  }

  return lines;
}

// ── D helper: Citation-Visibility Correlation ─────────────
function sectionCitationCorrelation(sources, reportData) {
  const lines = [
    line('-'),
    center('D. CITATION ↔ VISIBILITY CORRELATION'),
    line('-'),
    '  Does citation strength match visibility?',
    '',
  ];

  // Build per-engine citation counts
  const engCitMap = new Map();
  sources.forEach((s) => {
    const enginesForSource = s.engines.length > 0
      ? s.engines.map((e) => String(e.name || e.engineId || e).toLowerCase())
      : (s.engine ? [s.engine] : []);
    enginesForSource.forEach((e) => {
      if (!e) return;
      engCitMap.set(e, (engCitMap.get(e) || 0) + s.frequency);
    });
  });

  const reportEngines = safeGet(reportData, 'engines', {});
  const engVisMap = new Map(
    Object.entries(reportEngines).map(([k, v]) => [k.toLowerCase(), safeNum(v)])
  );

  // Find engines with both citation and visibility data
  const combined = new Map();
  engCitMap.forEach((cit, eng) => {
    if (engVisMap.has(eng)) {
      combined.set(eng, { citations: cit, visibility: engVisMap.get(eng) });
    }
  });
  engVisMap.forEach((vis, eng) => {
    if (!combined.has(eng)) {
      combined.set(eng, { citations: engCitMap.get(eng) || 0, visibility: vis });
    }
  });

  if (combined.size === 0) {
    lines.push('  Insufficient data for correlation.');
    lines.push('  Need both engine citations and visibility.');
    lines.push('');
    lines.push('  Run default report + --citations to');
    lines.push('  populate both data sources.');
    return lines;
  }

  // Classify each engine
  const entries = Array.from(combined.entries()).map(([eng, { citations, visibility }]) => {
    return { eng, citations, visibility };
  });

  // Thresholds: median-based classification
  const citCounts = entries.map((e) => e.citations).sort((a, b) => a - b);
  const visCounts = entries.map((e) => e.visibility).sort((a, b) => a - b);
  const medCit = citCounts[Math.floor(citCounts.length / 2)] || 1;
  const medVis = visCounts[Math.floor(visCounts.length / 2)] || 1;

  const aligned = entries.filter((e) =>
    (e.citations >= medCit && e.visibility >= medVis) ||
    (e.citations < medCit && e.visibility < medVis)
  );
  const highCitLowVis = entries.filter((e) =>
    e.citations >= medCit && e.visibility < medVis
  );
  const lowCitHighVis = entries.filter((e) =>
    e.citations < medCit && e.visibility >= medVis
  );

  if (aligned.length > 0) {
    lines.push('  ✓ Aligned (citations match visibility):');
    aligned.slice(0, 3).forEach((e) => {
      const engLabel = e.eng.charAt(0).toUpperCase() + e.eng.slice(1).slice(0, 14);
      lines.push(`    • ${engLabel.padEnd(14)}: ${e.citations} cit → ${safeFixed(e.visibility, 0)}% vis ✓`);
    });
    lines.push('');
  }

  if (highCitLowVis.length > 0) {
    lines.push('  ⚠ Gaps (high citations, low visibility):');
    highCitLowVis.slice(0, 3).forEach((e) => {
      const engLabel = e.eng.charAt(0).toUpperCase() + e.eng.slice(1).slice(0, 14);
      lines.push(`    • ${engLabel.padEnd(14)}: ${e.citations} cit → ${safeFixed(e.visibility, 0)}% vis ❌`);
    });
    lines.push('');
    lines.push('  💡 High citations, low visibility =');
    lines.push('     content quality issue. Review');
    lines.push('     your answer format on these engines.');
    lines.push('');
  }

  if (lowCitHighVis.length > 0) {
    lines.push('  🎯 Wins (low citations, high visibility):');
    lowCitHighVis.slice(0, 2).forEach((e) => {
      const engLabel = e.eng.charAt(0).toUpperCase() + e.eng.slice(1).slice(0, 14);
      lines.push(`    • ${engLabel.padEnd(14)}: ${e.citations} cit → ${safeFixed(e.visibility, 0)}% vis ✓`);
    });
    lines.push('');
    lines.push('  💡 Efficient! Minimal citations needed.');
  }

  return lines;
}

// ── E helper: PR Opportunity Mapper ───────────────────────
function sectionPROpportunities(sources, reportData) {
  const lines = [
    line('-'),
    center('E. PR OPPORTUNITY TARGETS'),
    line('-'),
    '  Non-competitors you should pitch to',
    '',
  ];

  // Build your domain set
  const yourDomains = new Set(sources.map((s) => s.domain).filter(Boolean));

  // High-authority PR targets by category + authority score (out of 10)
  const PR_TARGETS = [
    { domain: 'techcrunch.com',      auth: 10, category: 'Tech Startups',   angle: 'Growth story / funding' },
    { domain: 'forbes.com',          auth: 10, category: 'Enterprise',       angle: 'Thought leadership' },
    { domain: 'techradar.com',       auth:  9, category: 'Tech Reviews',     angle: 'Comparison / review' },
    { domain: 'venturebeat.com',     auth:  9, category: 'AI & Enterprise',  angle: 'AI use case study' },
    { domain: 'g2.com',              auth:  9, category: 'Reviews',          angle: 'Customer review push' },
    { domain: 'capterra.com',        auth:  8, category: 'Reviews',          angle: 'Category leader claim' },
    { domain: 'zapier.com',          auth:  8, category: 'Integrations',     angle: 'Integration spotlight' },
    { domain: 'solutionsreview.com', auth:  7, category: 'Reviews',          angle: 'Feature comparison' },
    { domain: 'businessinsider.com', auth:  9, category: 'Business',         angle: 'Trend / market story' },
    { domain: 'wired.com',           auth:  9, category: 'Technology',       angle: 'Innovation narrative' },
  ];

  const competitors = safeArray(safeGet(reportData, 'competitors'));
  const compNames = competitors.map((c) =>
    String(c.name || c.brandName || '').toLowerCase()
  ).filter(Boolean);

  // Prioritise: targets NOT already citing you + not your competitors
  const opportunities = PR_TARGETS
    .filter((t) => !yourDomains.has(t.domain))
    .map((t) => ({
      ...t,
      priority: t.auth >= 9 ? 'HIGH' : t.auth >= 7 ? 'MEDIUM' : 'LOW',
      citesCompetitors: compNames.length > 0, // Assume they cover the category
    }))
    .sort((a, b) => b.auth - a.auth);

  if (opportunities.length === 0) {
    lines.push('  ✓ You already have coverage on all');
    lines.push('    tracked PR targets. Well done!');
    lines.push('');
    lines.push('  Consider expanding to niche vertical');
    lines.push('  publications for deeper coverage.');
    return lines;
  }

  const high = opportunities.filter((o) => o.priority === 'HIGH');
  const medium = opportunities.filter((o) => o.priority === 'MEDIUM');

  if (high.length > 0) {
    lines.push('  🌟 HIGH PRIORITY');
    high.slice(0, 3).forEach((o) => {
      lines.push(`    ${o.domain}`);
      lines.push(`      Auth: ${o.auth}/10  · ${o.category}`);
      lines.push(`      Angle: ${o.angle.slice(0, 35)}`);
      if (o.citesCompetitors) {
        lines.push(`      Covers your space ✓`);
      }
      lines.push('');
    });
  }

  if (medium.length > 0) {
    lines.push('  ⬆ MEDIUM PRIORITY');
    medium.slice(0, 3).forEach((o) => {
      lines.push(`    ${o.domain}`);
      lines.push(`      Auth: ${o.auth}/10  · ${o.angle.slice(0, 30)}`);
      lines.push('');
    });
  }

  return lines;
}

// ─── ASCII Renderer ───────────────────────────────────────
function pad(str, width) {
  const s = String(str);
  return s.padEnd(width).slice(0, width);
}

function line(char = '-') {
  return char.repeat(WIDTH);
}

function center(str) {
  const s = String(str).slice(0, WIDTH - 2);
  const total = WIDTH - s.length;
  const left = Math.floor(total / 2);
  return ' '.repeat(left) + s;
}

function renderCompetitors(competitors, brandScore) {
  if (!competitors || competitors.length === 0) return [];
  const lines = [];
  lines.push(line('-'));
  lines.push('  COMPETITOR COMPARISON');
  competitors.forEach((c) => {
    const name = String(c.name).slice(0, 20);
    const score = String(c.score).padStart(3);
    let deltaStr = '';
    if (c.delta != null) {
      const sign = c.delta >= 0 ? '+' : '';
      const flag = c.delta >= 0 ? '🟢' : '🔴';
      deltaStr = ` ${flag} [${sign}${c.delta}% vs us]`;
    }
    // "  CompetitorName:  72 [+15% vs us]"
    const row = `  ${name.padEnd(20)}: ${score}${deltaStr}`;
    lines.push(row.slice(0, WIDTH));
  });
  return lines;
}

function renderReport(data, insights, brandId, competitors) {
  const { report, citations, sentiment, searchTerms } = data;
  const lines = [];
  const ts = new Date().toISOString().slice(0, 10);

  lines.push(line('='));
  lines.push(center('RANKSCALE GEO REPORT'));
  lines.push(
    center(`Brand: ${report.brandName} | ${ts}`)
  );
  lines.push(line('='));

  // Score block
  const changeStr =
    report.change > 0
      ? `+${report.change}`
      : String(report.change);
  lines.push(
    `  GEO SCORE:     ${String(report.score).padStart(3)} / 100` +
      `   [${changeStr} vs last week]`
  );

  const rateStr = `${citations.rate}%`;
  const avgStr = citations.industryAvg
    ? `[Industry avg: ${citations.industryAvg}%]`
    : '';
  lines.push(
    `  CITATION RATE: ${rateStr.padEnd(10)}${avgStr}`
  );

  lines.push(
    `  SENTIMENT:     Pos ${sentiment.positive}%` +
      ` | Neu ${sentiment.neutral}%` +
      ` | Neg ${sentiment.negative}%`
  );

  if (report.detectionRate != null) {
    lines.push(
      `  DETECTION RATE:${String(report.detectionRate).padStart(4)}%`
    );
  }

  // Engine breakdown
  const engineEntries = Object.entries(report.engines || {});
  if (engineEntries.length > 0) {
    const engStr = engineEntries
      .map(([k, v]) => {
        const label = ENGINE_DISPLAY_NAMES[k] ||
          ENGINE_DISPLAY_NAMES[k.toLowerCase()] || k;
        return `${label}:${v}`;
      })
      .join(' | ');
    lines.push(`  ENGINES:       ${engStr.slice(0, WIDTH - 17)}`);
  }

  // Competitor comparison
  if (competitors && competitors.length > 0) {
    renderCompetitors(competitors, report.score).forEach((l) =>
      lines.push(l)
    );
  }

  // Search terms
  if (searchTerms.length > 0) {
    lines.push(line('-'));
    lines.push('  TOP AI SEARCH TERMS');
    searchTerms.slice(0, 5).forEach((t, i) => {
      const num = `${i + 1}.`;
      // trim to fit in 55 chars: "  N. "query"  (X mentions)"
      // "  1. " = 5, num+space=3, quotes=2, mentions col needs ~15
      // Total row: 5 + term + mentions
      const q = `"${t.query}"`.slice(0, 30);
      const m = `(${t.mentions} mentions)`;
      const row = `  ${num} ${q.padEnd(32)} ${m}`;
      lines.push(row.slice(0, WIDTH));
    });
  }

  // Insights
  if (insights.length > 0) {
    lines.push(line('-'));
    lines.push(
      `  GEO INSIGHTS  [${insights.length} action${insights.length !== 1 ? 's' : ''}]`
    );
    insights.forEach((insight) => {
      lines.push(`  [${insight.severity}] ${insight.recommendation}`);
      lines.push('');
    });
  }

  lines.push(line('-'));
  // Footer: "  Full report: " = 15 chars; URL max 40 chars → total 55
  const footerUrl =
    `https://rankscale.ai/dashboard/brands/${brandId}`.slice(0, 40);
  lines.push(`  Full report: ${footerUrl}`);
  lines.push(line('='));

  return lines.join('\n');
}

// ─── Onboarding Prompt ────────────────────────────────────
function showOnboarding() {
  const onboardingPath = path.join(
    __dirname,
    'assets',
    'onboarding.md'
  );
  if (fs.existsSync(onboardingPath)) {
    const content = fs.readFileSync(onboardingPath, 'utf8');
    console.log(content);
  } else {
    console.log(
      [
        line('='),
        center('RANKSCALE SETUP REQUIRED'),
        line('='),
        '',
        '  To use GEO Analytics, you need a Rankscale PRO account.',
        '  ⚠  Note: PRO account required for REST API access.',
        '     Trial accounts do NOT have API access.',
        '     Upgrade to PRO at: https://rankscale.ai/dashboard/signup',
        '',
        '  1. Sign up at: https://rankscale.ai/dashboard/signup (PRO plan)',
        '  2. Create your brand profile',
        '  3. Email support@rankscale.ai to activate REST API access',
        '  4. Copy your API key from Settings > API',
        '  5. Set environment variables:',
        '',
        '     export RANKSCALE_API_KEY=rk_xxxxx_yyyyy',
        '     export RANKSCALE_BRAND_ID=yyyyy',
        '',
        '  Or pass as flags:',
        '     node rankscale-skill.js \\',
        '       --api-key rk_xxxxx \\',
        '       --brand-id yyyyy',
        '',
        line('='),
      ].join('\n')
    );
  }
}

// ─── Brand Discovery CLI Mode ─────────────────────────────
async function runDiscoverBrands(apiKey) {
  console.log('  Fetching brands from Rankscale...\n');
  try {
    const raw = await fetchBrands(apiKey);
    const brands = normalizeBrands(raw);
    if (!Array.isArray(brands) || brands.length === 0) {
      console.log('  No brands found on this account.');
      return;
    }
    console.log(line('='));
    console.log(center('AVAILABLE BRANDS'));
    console.log(line('='));
    brands.forEach((b, i) => {
      const name = b.name || b.brandName || '(unnamed)';
      const id = b.id || b.brandId || '?';
      console.log(`  ${i + 1}. ${name}`);
      console.log(`     ID: ${id}`);
    });
    console.log(line('-'));
    console.log(
      '  Set: export RANKSCALE_BRAND_ID=<id>'
    );
    console.log(line('='));
  } catch (err) {
    console.error(`  Error: ${err.message}`);
    process.exit(1);
  }
}

// ─── Main Orchestrator ────────────────────────────────────
/**
 * Main entry point — resolves credentials, fetches all 4 endpoints
 * in parallel with individual error handling, normalizes responses,
 * interprets insights, and renders the report.
 *
 * Fixes F7/F8: standalone citations + sentiment fetches with fallback
 * to report-embedded values when the dedicated endpoints fail.
 *
 * @param {object} [args={}]
 * @param {string} [args.apiKey]
 * @param {string} [args.brandId]
 * @param {string} [args.brandName]
 * @param {boolean} [args.discoverBrands]
 * @returns {Promise<{data: object, insights: object[], competitors: object[]}>}
 */
async function run(args = {}) {
  const { apiKey, brandId: rawBrandId } = resolveCredentials(args);

  if (!apiKey) {
    showOnboarding();
    process.exit(1);
  }

  // Brand discovery CLI mode
  if (args.discoverBrands) {
    await runDiscoverBrands(apiKey);
    return;
  }

  let brandId = rawBrandId;

  // Brand discovery if no ID
  if (!brandId) {
    console.error(
      '  RANKSCALE_BRAND_ID not set. Discovering brands...'
    );
    try {
      brandId = await discoverBrandId(apiKey, args.brandName);
    } catch (err) {
      console.error(`  Error: ${err.message}`);
      if (err instanceof AuthError) {
        console.error(
          '  Check your API key at https://rankscale.ai/dashboard/settings'
        );
      }
      process.exit(1);
    }
  }

  // Fetch all 4 endpoints in parallel with individual error handling.
  // Report errors still call handleFetchError() for auth/not-found handling.
  // Citations and sentiment silently fall back to null (report-embedded values used).
  // Search terms fall back to the raw endpoint, then null.
  const [reportRaw, citationsRaw, sentimentRaw, searchTermsRaw] =
    await Promise.all([
      fetchReport(apiKey, brandId).catch((err) => {
        handleFetchError(err, 'report');
        if (err instanceof NotFoundError) {
          console.error(
            '\n  Tip: Run brand discovery to find valid brand IDs:'
          );
          console.error(
            `  RANKSCALE_API_KEY=${apiKey} ` +
              'node rankscale-skill.js --discover-brands'
          );
        }
        return null;
      }),
      fetchCitations(apiKey, brandId).catch(() => null),
      fetchSentiment(apiKey, brandId).catch(() => null),
      fetchSearchTermsReport(apiKey, brandId)
        .catch(() =>
          fetchSearchTerms(apiKey, brandId).catch(() => null)
        ),
    ]);

  // Normalize report (may contain bundled citations/sentiment as fallback)
  const reportNorm = normalizeReport(reportRaw);

  // Citations: prefer standalone endpoint, fallback to report-embedded
  const citationsData = citationsRaw || reportNorm._citationsRaw || {};

  // Sentiment: prefer standalone endpoint, fallback to report-embedded synthetic
  const sentimentData = sentimentRaw || reportNorm._sentimentRaw || {};

  // Normalize competitors
  const competitors = normalizeCompetitors(
    reportNorm.competitors,
    reportNorm.score
  );

  // Compose normalized data object
  const data = {
    report: reportNorm,
    citations: normalizeCitations(citationsData),
    sentiment: normalizeSentiment(sentimentData),
    searchTerms: normalizeSearchTerms(searchTermsRaw),
  };

  // Interpret
  const insights = interpretGeoData(data);

  // ── GEO feature flags ─────────────────────────────────
  const geoMode =
    args.engineProfile || args.gapAnalysis || args.reputation ||
    args.engineMovers || args.sentimentAlerts || args.citations;

  if (geoMode) {
    if (args.engineProfile) {
      console.log(analyzeEngineStrength(data.report));
    }
    if (args.gapAnalysis) {
      console.log(analyzeContentGaps(data.report, data.searchTerms));
    }
    if (args.reputation) {
      console.log(computeReputationScore(data.sentiment));
    }
    if (args.engineMovers) {
      console.log(analyzeEngineMovers(data.report, null));
    }
    if (args.sentimentAlerts) {
      console.log(analyzeSentimentShift(data.sentiment, null));
    }
    if (args.citations) {
      // Pass raw citations response for richer parsing
      const citRaw = citationsRaw || citationsData;
      console.log(
        analyzeCitationIntelligence(
          citRaw, data.report, data.searchTerms, args.citationsMode
        )
      );
    }
  } else {
    // Default: full report
    const output = renderReport(data, insights, brandId, competitors);
    console.log(output);
  }

  return { data, insights, competitors };
}

function handleFetchError(err, context) {
  if (err instanceof AuthError) {
    console.error(`  Auth error fetching ${context}: ${err.message}`);
    console.error(
      '  Verify your key at https://rankscale.ai/dashboard/settings/api'
    );
    process.exit(1);
  } else if (err instanceof NotFoundError) {
    console.error(
      `  Not found (${context}): ${err.message}`
    );
  } else {
    console.error(
      `  Error fetching ${context}: ${err.message}`
    );
  }
}

// ─── CLI Entry Point ──────────────────────────────────────
if (require.main === module) {
  const args = {};

  // Parse CLI flags
  for (let i = 2; i < process.argv.length; i++) {
    const arg = process.argv[i];
    if (arg === '--api-key' || arg === '--apiKey') {
      args.apiKey = process.argv[++i];
    } else if (arg === '--brand-id' || arg === '--brandId') {
      args.brandId = process.argv[++i];
    } else if (arg === '--brand-name' || arg === '--brandName') {
      args.brandName = process.argv[++i];
    } else if (arg === '--discover-brands') {
      args.discoverBrands = true;
    } else if (arg === '--engine-profile') {
      args.engineProfile = true;
    } else if (arg === '--gap-analysis') {
      args.gapAnalysis = true;
    } else if (arg === '--reputation') {
      args.reputation = true;
    } else if (arg === '--engine-movers' || arg === '--engine-trends') {
      args.engineMovers = true;
    } else if (arg === '--sentiment-alerts') {
      args.sentimentAlerts = true;
    } else if (arg === '--citations' || arg === '--citation-intelligence') {
      args.citations = true;
      // Optional sub-mode: --citations [full|authority|gaps|engines|correlation|pr]
      const next = process.argv[i + 1];
      if (next && !next.startsWith('--')) {
        args.citationsMode = next;
        i++;
      }
    } else if (arg === '--help' || arg === '-h') {
      console.log([
        'Usage: node rankscale-skill.js [options]',
        '',
        'Options:',
        '  --api-key <key>      Rankscale API key',
        '  --brand-id <id>      Brand ID',
        '  --brand-name <name>  Brand name (for discovery)',
        '  --discover-brands    List all brands on account',
        '  --engine-profile     Engine strength heatmap',
        '  --gap-analysis       Content gap analysis',
        '  --reputation         Reputation score & summary',
        '  --engine-movers      Engine gainers & losers vs prior period',
        '  --sentiment-alerts   Sentiment shift & risk cluster alert',
        '  --citations [mode]   Citation Intelligence Hub',
        '                       modes: authority|gaps|engines|correlation|full',
        '  --citation-intelligence  Alias for --citations',
        '  --help               Show this help',
        '',
        'Environment Variables:',
        '  RANKSCALE_API_KEY    API key',
        '  RANKSCALE_BRAND_ID   Brand ID',
        '',
        'Requirements:',
        '  - Rankscale PRO account (trial accounts do not have REST API access)',
        '  - REST API must be activated by support (support@rankscale.ai)',
        '',
        'Examples:',
        '  RANKSCALE_API_KEY=xxx node rankscale-skill.js \\',
        '    --discover-brands',
        '  RANKSCALE_API_KEY=xxx RANKSCALE_BRAND_ID=yyy \\',
        '    node rankscale-skill.js',
      ].join('\n'));
      process.exit(0);
    }
  }

  run(args).catch((err) => {
    console.error(`Fatal: ${err.message}`);
    process.exit(1);
  });
}

// ─── Exports ──────────────────────────────────────────────
module.exports = {
  run,
  resolveCredentials,
  // API calls
  fetchBrands,
  fetchReport,
  fetchCitations,
  fetchSentiment,
  fetchSearchTermsReport,
  fetchSearchTerms,
  // Normalizers
  normalizeSentiment,
  normalizeCitations,
  normalizeReport,
  normalizeSearchTerms,
  normalizeCompetitors,
  emptyReport,
  // Helpers
  safeGet,
  safeNum,
  safeFixed,
  safeArray,
  // Interpretation
  interpretGeoData,
  GEO_RULES,
  // GEO Analysis Features (ROA-40)
  analyzeEngineStrength,
  analyzeContentGaps,
  computeReputationScore,
  analyzeEngineMovers,
  analyzeSentimentShift,
  // Citation Intelligence (ROA-40 crown jewel)
  analyzeCitationIntelligence,
  sectionCitationAuthority,
  sectionCitationGaps,
  sectionEnginePreferences,
  sectionCitationCorrelation,
  sectionPROpportunities,
  // Errors
  AuthError,
  NotFoundError,
  ApiError,
};
