#!/usr/bin/env node

import { promises as fs } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { buildQuestionnaire, parsePreferences } from "./lib/questionnaire.mjs";
import { buildFinancialQuality, buildThesis, buildValuationFrame, buildScorecard as buildScorecardV2, detectChaseRisk as detectChaseRiskV2 } from "./lib/analysis.mjs";
import { buildEventRadarIdeas, clusterEventsByTheme, extractEvents } from "./lib/events.mjs";
import { buildPlaybooks } from "./lib/playbooks.mjs";
import { summarizeQuality as summarizeQualityV2 } from "./lib/data.mjs";
import { formatMarkdown as formatMarkdownV2 } from "./lib/output.mjs";
import {
  getApiKey as qGetApiKey,
  searchTools as qSearchTools,
  executeTool as qExecuteTool,
  resolveToolPayloadSync as qResolveToolPayloadSync,
} from "./lib/infra/qveris-client.mjs";
import { parseCapability as parseCapabilityV2 } from "./lib/data/parser.mjs";
import {
  hasCjk as hasCjkV2,
  normalizeAliasKey as normalizeAliasKeyV2,
  extractTickerFromText as extractTickerFromTextV2,
  inferMarketFromSymbol as inferMarketFromSymbolV2,
  resolveCompanyNameViaQveris as resolveCompanyNameViaQverisV2,
  resolveRequestedSymbol as resolveRequestedSymbolV2,
  normalizeSymbols as normalizeSymbolsV2,
  toThsCode as toThsCodeV2,
} from "./lib/market/resolver.mjs";
import { hasCommand, dispatchCommand } from "./lib/core/router.mjs";
import { formatForChat } from "./lib/output/chat/formatter.mjs";
import { buildDecisionCard } from "./lib/output/decision-card.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const SKILL_ROOT = path.resolve(__dirname, "..");
const EVOLUTION_DIR = path.join(SKILL_ROOT, ".evolution");
const EVOLUTION_FILE = path.join(EVOLUTION_DIR, "tool-evolution.json");
const TOOL_CHAINS_FILE = path.join(SKILL_ROOT, "references", "tool-chains.json");
const SECTOR_BENCHMARKS_FILE = path.join(SKILL_ROOT, "references", "sector-benchmarks.json");
const EVOLUTION_VERSION = 2;
const MAX_TOOLS_TRACKED = 200;
const MAX_MARKETS_PER_TOOL = 8;

const CAPABILITY_QUERIES = {
  quote: "real-time stock quote and historical OHLCV data API",
  fundamentals: "company financial statements and valuation metrics API",
  technicals: "technical indicators RSI MACD moving average API",
  sentiment: "stock news sentiment and market headlines API",
  x_sentiment: "X Twitter stock sentiment API by ticker",
};

const CN_HK_QUERY_HINTS = {
  quote: "ths_ifind.real_time_quotation China and Hong Kong stock real-time quotation API",
  fundamentals:
    "ths_ifind.financial_statements ths_ifind.company_basics China and Hong Kong stock financial statements and company basics API",
  technicals: "ths_ifind.history_quotation China and Hong Kong stock historical quotation API",
};

const X_SENTIMENT_TOOL_PREFIXES = [
  "x_developer.2.tweets.search.recent",
  "qveris_social.x_domain_new_posts",
  "qveris_social.x_domain_hot_topics",
  "qveris_social.x_domain_hot_events",
];
const CAIDAZI_TOOL_PREFIXES = [
  "caidazi.news.query",
  "caidazi.report.query",
  "caidazi.search.hybrid.list",
  "caidazi.search.hybrid_v2.query",
];

const COMPANY_SYMBOL_ALIASES = {
  特变电工: { symbol: "600089.SH", market: "CN" },
  英伟达: { symbol: "NVDA", market: "US" },
  腾讯: { symbol: "0700.HK", market: "HK" },
  腾讯控股: { symbol: "0700.HK", market: "HK" },
  贵州茅台: { symbol: "600519.SH", market: "CN" },
};

function redactSecrets(text) {
  if (!text) return text;
  return String(text)
    .replace(/Bearer\s+[A-Za-z0-9\-\._~\+\/]+=*/gi, "Bearer [REDACTED]")
    .replace(/QVERIS_API_KEY\s*[:=]\s*['"]?[^'"\s]+['"]?/gi, "QVERIS_API_KEY=[REDACTED]")
    .replace(/("?(?:qveris_api_key|authorization)"?\s*[:=]\s*)("[^"]*"|'[^']*'|[^\s,}]+)/gi, "$1[REDACTED]")
    .replace(/([?&](?:api_key|token|access_token|authorization)=)[^&\s]+/gi, "$1[REDACTED]")
    .replace(/[A-Za-z0-9_-]{24,}\.[A-Za-z0-9._-]{10,}\.[A-Za-z0-9._-]{10,}/g, "[REDACTED_TOKEN]");
}

function isoNow() {
  return new Date().toISOString();
}

function getApiKey() {
  return qGetApiKey();
}

function toNumber(value) {
  if (value == null || value === "") return null;
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

function pickFirst(...values) {
  for (const v of values) {
    if (v == null) continue;
    if (typeof v === "string" && v.trim() === "") continue;
    return v;
  }
  return null;
}

function timeoutSignal(timeoutMs) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  return { signal: controller.signal, cleanup: () => clearTimeout(timer) };
}

function emptyEvolutionState() {
  return {
    version: EVOLUTION_VERSION,
    updated_at: isoNow(),
    tools: {},
  };
}

function toInt(value, fallback = 0) {
  const n = Number(value);
  return Number.isInteger(n) ? n : fallback;
}

function sanitizeParamValue(value) {
  if (value == null) return value;
  if (typeof value === "string") {
    const v = redactSecrets(value);
    return v.length > 300 ? `${v.slice(0, 300)}...` : v;
  }
  if (typeof value === "number" || typeof value === "boolean") return value;
  if (Array.isArray(value)) return value.slice(0, 20).map((x) => sanitizeParamValue(x));
  if (typeof value === "object") {
    const out = {};
    for (const [k, v] of Object.entries(value).slice(0, 50)) out[k] = sanitizeParamValue(v);
    return out;
  }
  return String(value);
}

function sanitizeToolRecord(toolId, record) {
  const markets = Array.isArray(record?.markets)
    ? [...new Set(record.markets.filter((x) => typeof x === "string"))].slice(0, MAX_MARKETS_PER_TOOL)
    : [];
  const paramTemplates =
    record?.param_templates && typeof record.param_templates === "object"
      ? Object.fromEntries(
          Object.entries(record.param_templates)
            .filter(([k]) => typeof k === "string")
            .slice(0, MAX_MARKETS_PER_TOOL)
            .map(([k, v]) => [k, sanitizeParamValue(v)]),
        )
      : {};
  return {
    tool_id: String(toolId),
    provider: typeof record?.provider === "string" ? record.provider : pickProvider(toolId),
    first_seen_at: typeof record?.first_seen_at === "string" ? record.first_seen_at : isoNow(),
    last_success_at: typeof record?.last_success_at === "string" ? record.last_success_at : null,
    success_count: Math.max(0, toInt(record?.success_count, 0)),
    fail_count: Math.max(0, toInt(record?.fail_count, 0)),
    avg_elapsed_ms: Math.max(0, toInt(record?.avg_elapsed_ms, 0)),
    markets,
    param_templates: paramTemplates,
    sample_successful_params: sanitizeParamValue(record?.sample_successful_params || null),
    last_error: typeof record?.last_error === "string" ? redactSecrets(record.last_error) : null,
  };
}

function sanitizeEvolutionState(state) {
  const safe = emptyEvolutionState();
  if (!state || typeof state !== "object") {
    return safe;
  }
  const sourceTools =
    state.tools && typeof state.tools === "object"
      ? state.tools
      : state.capability_buckets && typeof state.capability_buckets === "object"
        ? Object.fromEntries(
            Object.values(state.capability_buckets)
              .filter((bucket) => bucket && typeof bucket === "object" && bucket.tools && typeof bucket.tools === "object")
              .flatMap((bucket) => Object.entries(bucket.tools)),
          )
        : {};
  const toolIds = Object.keys(sourceTools).slice(0, MAX_TOOLS_TRACKED);
  for (const toolId of toolIds) {
    if (!toolId || typeof toolId !== "string") continue;
    safe.tools[toolId] = sanitizeToolRecord(toolId, sourceTools[toolId]);
  }
  safe.updated_at = isoNow();
  return safe;
}

function ensureEvolutionToolRecord(state, toolId) {
  if (!state.tools[toolId]) {
    state.tools[toolId] = {
      tool_id: toolId,
      provider: pickProvider(toolId),
      first_seen_at: isoNow(),
      last_success_at: null,
      success_count: 0,
      fail_count: 0,
      avg_elapsed_ms: 0,
      markets: [],
      param_templates: {},
      sample_successful_params: null,
      last_error: null,
    };
  }
  return state.tools[toolId];
}

async function loadEvolutionState() {
  try {
    const content = await fs.readFile(EVOLUTION_FILE, "utf8");
    const parsed = JSON.parse(content);
    return sanitizeEvolutionState(parsed);
  } catch {
    return emptyEvolutionState();
  }
}

async function saveEvolutionState(state) {
  const payload = sanitizeEvolutionState(state);
  await fs.mkdir(EVOLUTION_DIR, { recursive: true });
  await fs.writeFile(EVOLUTION_FILE, JSON.stringify(payload, null, 2), "utf8");
}

function pickProvider(toolId) {
  if (!toolId) return "unknown";
  const first = String(toolId).split(".")[0];
  return first || "unknown";
}

let toolChainsCache = null;
let sectorBenchmarksCache = null;

async function loadToolChains() {
  if (toolChainsCache) return toolChainsCache;
  try {
    const content = await fs.readFile(TOOL_CHAINS_FILE, "utf8");
    toolChainsCache = JSON.parse(content);
  } catch {
    toolChainsCache = {};
  }
  return toolChainsCache;
}

async function loadSectorBenchmarks() {
  if (sectorBenchmarksCache) return sectorBenchmarksCache;
  try {
    const content = await fs.readFile(SECTOR_BENCHMARKS_FILE, "utf8");
    sectorBenchmarksCache = JSON.parse(content);
  } catch {
    sectorBenchmarksCache = { default: { pe_median: 20, pb_median: 2.5, roe_benchmark: 12, debt_ratio_warn: 0.6 } };
  }
  return sectorBenchmarksCache;
}

function templateContextVars(context = {}) {
  const vars = {};
  const push = (key, value) => {
    if (value == null || value === "") return;
    vars[key] = value;
    vars[String(value)] = `{${key}}`;
  };
  push("symbol", context.symbol);
  push("thsCode", context.thsCode);
  push("base", context.base);
  push("market", context.market);
  push("keyword", context.keyword);
  push("caidaziTicker", context.caidaziTicker);
  push("report.year", context.report?.year);
  push("report.period", context.report?.period);
  push("recentStart", context.recentStart);
  push("history.startdate", context.history?.startdate);
  push("history.enddate", context.history?.enddate);
  return vars;
}

function createTemplateFromParams(params, context = {}) {
  const vars = templateContextVars(context);
  const walk = (value) => {
    if (value == null) return value;
    if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
      const direct = vars[String(value)];
      return direct || value;
    }
    if (Array.isArray(value)) return value.map((x) => walk(x));
    if (typeof value === "object") {
      const out = {};
      for (const [k, v] of Object.entries(value)) out[k] = walk(v);
      return out;
    }
    return value;
  };
  return walk(params);
}

function readObjectPath(source, pathExpr) {
  const parts = String(pathExpr || "").split(".");
  let cur = source;
  for (const p of parts) {
    if (!cur || typeof cur !== "object" || !(p in cur)) return null;
    cur = cur[p];
  }
  return cur;
}

function interpolateTemplate(template, context = {}) {
  const walk = (value) => {
    if (value == null) return value;
    if (typeof value === "string") {
      const m = value.match(/^\{([a-zA-Z0-9_.]+)\}$/);
      if (m?.[1]) {
        const found = readObjectPath(context, m[1]);
        return found == null ? value : found;
      }
      return value;
    }
    if (Array.isArray(value)) return value.map((x) => walk(x));
    if (typeof value === "object") {
      const out = {};
      for (const [k, v] of Object.entries(value)) out[k] = walk(v);
      return out;
    }
    return value;
  };
  return walk(template);
}

function getEvolutionTemplate(state, toolId, market) {
  const record = state?.tools?.[toolId];
  if (!record?.param_templates) return null;
  const template = record.param_templates[market] || record.param_templates.GLOBAL || null;
  if (!template || typeof template !== "object") return template;
  const dynamicKeys = new Set(["startdate", "enddate", "publishTimeStart", "publishDateStart"]);
  const hasStaticDate = (value) => {
    if (!value || typeof value !== "object") return false;
    for (const [k, v] of Object.entries(value)) {
      if (dynamicKeys.has(k) && typeof v === "string" && /^\d{4}-\d{2}-\d{2}$/.test(v)) return true;
      if (typeof v === "object" && hasStaticDate(v)) return true;
    }
    return false;
  };
  return hasStaticDate(template) ? null : template;
}

function updateEvolutionOnAttempt(state, meta) {
  const { market, toolId, elapsedMs, success, params, paramContext, errorMessage, newlyLearnedCollector } = meta;
  if (!toolId) return;
  const record = ensureEvolutionToolRecord(state, toolId);
  if (market && !record.markets.includes(market)) record.markets.push(market);
  if (success) {
    record.success_count += 1;
    record.last_success_at = isoNow();
    const prev = Number(record.avg_elapsed_ms || 0);
    const n = record.success_count;
    record.avg_elapsed_ms = n === 1 ? elapsedMs : Math.round((prev * (n - 1) + elapsedMs) / n);
    record.sample_successful_params = sanitizeParamValue(params);
    const template = createTemplateFromParams(params, paramContext);
    record.param_templates[market || "GLOBAL"] = sanitizeParamValue(template);
    if (newlyLearnedCollector && n === 1) newlyLearnedCollector.push(toolId);
    record.last_error = null;
  } else {
    record.fail_count += 1;
    if (errorMessage) record.last_error = redactSecrets(errorMessage);
  }
  state.updated_at = isoNow();
}

async function searchTools(query, limit, timeoutMs) {
  return qSearchTools(query, limit, timeoutMs);
}

async function executeTool(toolId, searchId, parameters, maxResponseSize, timeoutMs) {
  return qExecuteTool(toolId, searchId, parameters, maxResponseSize, timeoutMs);
}

function isToolCallSuccessful(result) {
  if (!result || typeof result !== "object") return false;
  if (result.success === false) return false;
  const payload = result?.result ?? result;
  const data = payload?.data ?? payload;
  if (data?.status === "error") return false;
  if (typeof data?.code === "number" && data.code >= 400) return false;
  if (typeof data?.["Error Message"] === "string") return false;
  if (typeof data?.Information === "string" && data.Information.toLowerCase().includes("burst pattern")) return false;
  return true;
}

function scoreTool(tool) {
  const stats = tool?.stats || {};
  const successRate = toNumber(stats.success_rate) ?? 0;
  const latency = toNumber(stats.avg_execution_time_ms);
  const latencyScore = latency && latency > 0 ? 1 / (1 + latency) : 0;
  const hasExamples = tool?.examples?.sample_parameters ? 0.03 : 0;
  return successRate * 0.8 + latencyScore * 0.17 + hasExamples;
}

function rankTools(results) {
  return [...(results || [])]
    .sort((a, b) => scoreTool(b) - scoreTool(a))
    .map((tool) => ({
      ...tool,
      _score: scoreTool(tool),
    }));
}

function summarizeTool(tool) {
  if (!tool || typeof tool !== "object") return null;
  return {
    tool_id: tool.tool_id ?? null,
    name: tool.name ?? null,
    stats: tool.stats ?? null,
    _fromEvolution: Boolean(tool._fromEvolution),
  };
}

function hasCjk(text) {
  return hasCjkV2(text);
}

function normalizeAliasKey(value) {
  return normalizeAliasKeyV2(value);
}

function extractTickerFromText(value) {
  return extractTickerFromTextV2(value);
}

function inferMarketFromSymbol(value) {
  return inferMarketFromSymbolV2(value);
}

// Dynamic company name resolution via QVeris (ths_ifind.code_converter)
const THS_CODE_CONVERTER_TOOL_ID = "ths_ifind.code_converter.v1";
const CODE_CONVERTER_TIMEOUT_MS = 5000;

function splitCandidateCodes(rawValue) {
  const raw = String(rawValue || "").trim();
  if (!raw) return [];
  return raw
    .split(/[,\s;；|]+/)
    .map((x) => x.trim().toUpperCase())
    .filter(Boolean);
}

function isCodeMatchingMarket(code, market) {
  const c = String(code || "").toUpperCase();
  if (!c) return false;
  if (market === "HK") return /\.HK$/.test(c) || /^\d{4,5}$/.test(c);
  if (market === "CN") return /\.(SH|SZ|SS)$/.test(c) || /^\d{6}$/.test(c);
  if (market === "US") return /^[A-Z]{1,6}(\.US)?$/.test(c);
  return true;
}

function scoreCandidateCode(code, preferredMarket) {
  const c = String(code || "").toUpperCase();
  if (!c) return -999;
  let score = 0;
  if (isCodeMatchingMarket(c, preferredMarket)) score += 100;
  if (preferredMarket === "HK") {
    if (/^\d{4,5}\.HK$/.test(c)) score += 40;
    if (/^\d{4,5}$/.test(c)) score += 20;
  } else if (preferredMarket === "CN") {
    if (/^\d{6}\.(SH|SZ|SS)$/.test(c)) score += 40;
    if (/^\d{6}$/.test(c)) score += 20;
  } else if (preferredMarket === "US") {
    if (/^[A-Z]{1,6}$/.test(c)) score += 35;
    if (/^[A-Z]{1,6}\.US$/.test(c)) score += 25;
  } else if (/\.(HK|SH|SZ|SS|US)$/.test(c) || /^[A-Z]{1,6}$/.test(c)) {
    score += 10;
  }
  if (/\.PQ$/.test(c)) score -= 30;
  return score;
}

function normalizeResolvedCode(code, preferredMarket) {
  const c = String(code || "").toUpperCase();
  if (!c) return null;
  if (preferredMarket === "HK" && /^\d{4,5}$/.test(c)) return `${c.padStart(4, "0")}.HK`;
  if (preferredMarket === "CN" && /^\d{6}$/.test(c)) return c.startsWith("6") ? `${c}.SH` : `${c}.SZ`;
  if (preferredMarket === "US" && /^[A-Z]{1,6}\.US$/.test(c)) return c.replace(/\.US$/, "");
  return c;
}

function generateResolverNameVariants(companyName, preferredMarket = "GLOBAL") {
  const base = String(companyName || "").trim();
  if (!base) return [];
  const variants = new Set([base]);
  const normalized = base
    .replace(/(集团|控股|股份|有限责任公司|有限公司)$/g, "")
    .trim();
  if (normalized && normalized !== base) variants.add(normalized);
  if (preferredMarket === "HK") {
    const seed = [...variants];
    for (const v of seed) {
      variants.add(`${v}-W`);
    }
  }
  return [...variants];
}

function extractBestCodeFromConverterRows(rows, preferredMarket) {
  const candidates = [];
  for (const row of rows || []) {
    const thscodeValues = row?.table?.thscode;
    if (!Array.isArray(thscodeValues)) continue;
    for (const item of thscodeValues) {
      for (const code of splitCandidateCodes(item)) {
        candidates.push(code);
      }
    }
  }
  if (candidates.length === 0) return null;
  const unique = [...new Set(candidates)];
  unique.sort((a, b) => scoreCandidateCode(b, preferredMarket) - scoreCandidateCode(a, preferredMarket));
  return normalizeResolvedCode(unique[0], preferredMarket);
}

async function resolveCompanyNameViaQveris(companyName, preferredMarket = "GLOBAL") {
  return resolveCompanyNameViaQverisV2(companyName, preferredMarket);
}

async function resolveRequestedSymbol(input, preferredMarket = "GLOBAL") {
  return resolveRequestedSymbolV2(input, preferredMarket, COMPANY_SYMBOL_ALIASES);
}

function prioritizeCandidatesByMarket(candidates, capability, market) {
  const list = [...(candidates || [])];
  const isCnHkCore = ["CN", "HK"].includes(market) && ["quote", "fundamentals", "technicals"].includes(capability);
  if (!isCnHkCore) return list;
  const native = list.filter((t) => String(t?.tool_id || "").startsWith("ths_ifind."));
  if (native.length === 0) return list;
  const others = list.filter((t) => !String(t?.tool_id || "").startsWith("ths_ifind."));
  return [...native, ...others];
}

function isCaidaziTool(toolId) {
  const id = String(toolId || "");
  return CAIDAZI_TOOL_PREFIXES.some((prefix) => id.startsWith(prefix));
}

function caidaziPriority(toolId) {
  const id = String(toolId || "");
  if (id.startsWith("caidazi.search.hybrid_v2.query")) return 4;
  if (id.startsWith("caidazi.news.query")) return 3;
  if (id.startsWith("caidazi.report.query")) return 2;
  if (id.startsWith("caidazi.search.hybrid.list")) return 1;
  return 0;
}

function thsFundamentalPriority(toolId) {
  const id = String(toolId || "");
  if (id.startsWith("ths_ifind.financial_statements")) return 5;
  if (id.startsWith("ths_ifind.income_statement")) return 4;
  if (id.startsWith("ths_ifind.balance_sheet")) return 3;
  if (id.startsWith("ths_ifind.cash_flow_statement")) return 2;
  if (id.startsWith("ths_ifind.company_basics")) return 1;
  return 0;
}

function isToolCompatibleForCapability(toolId, capability, market) {
  const id = String(toolId || "");
  if (!id) return false;
  if (capability === "quote") {
    if (id.startsWith("ths_ifind.") && !id.startsWith("ths_ifind.real_time_quotation")) return false;
    return true;
  }
  if (capability === "fundamentals") {
    if (
      id.startsWith("ths_ifind.") &&
      !id.startsWith("ths_ifind.company_basics") &&
      !id.startsWith("ths_ifind.financial_statements") &&
      !id.startsWith("ths_ifind.income_statement") &&
      !id.startsWith("ths_ifind.balance_sheet") &&
      !id.startsWith("ths_ifind.cash_flow_statement")
    ) {
      return false;
    }
    return true;
  }
  if (capability === "technicals") {
    if (id.startsWith("ths_ifind.") && !id.startsWith("ths_ifind.history_quotation")) return false;
    return true;
  }
  if (capability === "x_sentiment") {
    return X_SENTIMENT_TOOL_PREFIXES.some((prefix) => id.startsWith(prefix));
  }
  if (capability === "sentiment") {
    return !id.startsWith("x_developer.");
  }
  if (["CN", "HK"].includes(market) && ["quote", "fundamentals", "technicals"].includes(capability)) {
    if (id.startsWith("ths_ifind.")) return true;
  }
  return true;
}

function marketCapabilityBoost(tool, capability, market) {
  const id = String(tool?.tool_id || "");
  if (["CN", "HK"].includes(market) && ["quote", "fundamentals", "technicals"].includes(capability)) {
    if (id.startsWith("ths_ifind.")) return 0.3;
    if (id.startsWith("alphavantage.") || id.startsWith("twelvedata.") || id.startsWith("finnhub_io_api.")) return -0.08;
  }
  if (["CN", "HK"].includes(market) && capability === "fundamentals") {
    if (id.startsWith("ths_ifind.financial_statements") || id.startsWith("ths_ifind.income_statement")) return 0.2;
    if (id.startsWith("ths_ifind.balance_sheet")) return 0.14;
    if (id.startsWith("ths_ifind.cash_flow_statement")) return 0.1;
    if (id.startsWith("ths_ifind.company_basics")) return 0.08;
  }
  if (market === "US" && ["quote", "fundamentals", "technicals"].includes(capability)) {
    if (id.startsWith("alphavantage.") || id.startsWith("twelvedata.") || id.startsWith("finnhub_io_api.")) return 0.08;
  }
  if (["CN", "HK"].includes(market) && capability === "sentiment") {
    if (isCaidaziTool(id)) return 0.28;
    if (id.startsWith("finnhub.") || id.startsWith("alphavantage.")) return -0.05;
  }
  return 0;
}

function normalizeSymbols(input, market) {
  return normalizeSymbolsV2(input, market);
}

function toThsCode(symbol, market) {
  return toThsCodeV2(symbol, market);
}

function parseDateLike(value) {
  if (!value) return null;
  if (typeof value === "number") {
    const date = new Date(value * 1000);
    return Number.isNaN(date.getTime()) ? null : date;
  }
  if (typeof value === "string") {
    const normalized = value.includes("T") ? value : `${value}T00:00:00Z`;
    const date = new Date(normalized);
    return Number.isNaN(date.getTime()) ? null : date;
  }
  return null;
}

function isStale(value, days = 5) {
  const date = parseDateLike(value);
  if (!date) return false;
  const diffMs = Date.now() - date.getTime();
  return diffMs > days * 24 * 60 * 60 * 1000;
}

function pickQuoteData(raw) {
  const data = raw?.result?.data || raw?.data || raw || {};
  if (Array.isArray(data) && Array.isArray(data[0]) && data[0][0]) {
    const row = data[0][0];
    return {
      symbol: row.thscode ?? null,
      price: toNumber(row.latest),
      open: toNumber(row.open),
      high: toNumber(row.high),
      low: toNumber(row.low),
      volume: toNumber(row.volume),
      percentChange: toNumber(row.changeRatio),
      marketCap: toNumber(row.mv ?? row.totalCapital),
      pe: toNumber(row.pe_ttm ?? row.pe),
      pb: toNumber(row.pb ?? row.pbr_lf),
      timestamp: row.time ?? row.tradeDate ?? null,
      raw: row,
    };
  }
  return {
    symbol: data.symbol ?? data.Symbol ?? null,
    price: toNumber(data.close ?? data.price ?? data.latestPrice),
    open: toNumber(data.open),
    high: toNumber(data.high),
    low: toNumber(data.low),
    volume: toNumber(data.volume),
    percentChange: toNumber(data.percent_change ?? data.changePercent),
    marketCap: toNumber(data.marketCap ?? data.mv ?? data.totalCapital),
    pe: toNumber(data.pe_ttm ?? data.pe ?? data.TrailingPE),
    pb: toNumber(data.pb ?? data.pbr_lf ?? data.PriceToBookRatio),
    timestamp: data.datetime ?? data.timestamp ?? data["07. latest trading day"] ?? null,
    raw: data,
  };
}

function pickFundamentalData(raw) {
  const data = raw?.result?.data || raw?.data || raw || {};
  if (Array.isArray(data) && Array.isArray(data[0]) && data[0][0]) {
    const row = data[0][0];
    const statementType = row.statement_type || row.statementType || null;
    const period = row.time || row.end_date || row.report_date || null;
    const tagsRaw = pickFirst(
      row.ths_the_ths_concept_index_stock,
      row.ths_concept_stock,
      row.ths_concept_list_stock,
      row.concept,
      row.tags,
      row.tag_list,
      row.ths_tags_stock,
    );
    return {
      symbol: row.ths_thscode_stock ?? row.thscode ?? null,
      name: row.ths_corp_cn_name_stock ?? row.ths_short_name_stock ?? row.short_name ?? null,
      industry: pickFirst(
        row.ths_the_ths_industry_stock,
        row.ths_industry_stock,
        row.ths_industry_name_stock,
        row.ths_sw_industry_stock,
        row.industry,
        row.industry_name,
      ),
      mainBusiness: pickFirst(
        row.ths_main_businuess_stock,
        row.ths_main_business_stock,
        row.ths_business_scope_stock,
        row.ths_mo_product_name_stock,
        row.main_business,
        row.business_scope,
      ),
      tags: Array.isArray(tagsRaw)
        ? tagsRaw.filter(Boolean)
        : typeof tagsRaw === "string"
          ? tagsRaw
              .split(/[，,;；|]/)
              .map((x) => x.trim())
              .filter(Boolean)
          : null,
      marketCap: null,
      pe: null,
      forwardPe: null,
      pb: null,
      ps: null,
      profitMargin: null,
      revenueGrowthYoy: null,
      earningsGrowthYoy: null,
      week52High: null,
      week52Low: null,
      latestQuarter: period,
      statementType,
      reportPeriod: period,
      revenue: toNumber(row.ths_revenue_stock ?? row.ths_operating_total_revenue_stock),
      netProfit: toNumber(row.ths_np_atoopc_stock ?? row.ths_np_stock),
      totalAssets: toNumber(row.ths_total_assets_stock),
      totalLiabilities: toNumber(row.ths_total_liab_stock),
      operatingCashflow: toNumber(row.ths_ncf_from_oa_stock),
      raw: row,
    };
  }
  return {
    symbol: data.Symbol ?? data.symbol ?? null,
    name: data.Name ?? data.name ?? null,
    industry: pickFirst(data.Industry, data.industry, data.industry_name),
    mainBusiness: pickFirst(data.BusinessDescription, data.business_description, data.main_business),
    tags: Array.isArray(data.tags)
      ? data.tags
      : typeof (data.concept ?? data.ths_the_ths_concept_index_stock) === "string"
        ? String(data.concept ?? data.ths_the_ths_concept_index_stock)
            .split(/[，,;；|]/)
            .map((x) => x.trim())
            .filter(Boolean)
        : null,
    marketCap: toNumber(data.MarketCapitalization ?? data.marketCap),
    pe: toNumber(data.PERatio ?? data.pe ?? data.TrailingPE),
    forwardPe: toNumber(data.ForwardPE),
    pb: toNumber(data.PriceToBookRatio),
    ps: toNumber(data.PriceToSalesRatioTTM),
    profitMargin: toNumber(data.ProfitMargin),
    revenueGrowthYoy: toNumber(data.QuarterlyRevenueGrowthYOY),
    earningsGrowthYoy: toNumber(data.QuarterlyEarningsGrowthYOY),
    week52High: toNumber(data["52WeekHigh"] ?? data.fifty_two_week?.high),
    week52Low: toNumber(data["52WeekLow"] ?? data.fifty_two_week?.low),
    latestQuarter: data.LatestQuarter ?? null,
    raw: data,
  };
}

function pickTechnicalData(raw) {
  const result = raw?.result || raw || {};
  const data = result?.data || result;
  if (Array.isArray(data) && Array.isArray(data[0]) && data[0][0]) {
    const rows = data[0];
    const row = rows[rows.length - 1];
    const prev5Index = Math.max(0, rows.length - 6);
    const prev5 = rows[prev5Index] || null;
    const closeNow = toNumber(row.close);
    const closePrev5 = toNumber(prev5?.close);
    const change5d =
      closeNow != null && closePrev5 != null && closePrev5 !== 0 ? ((closeNow - closePrev5) / closePrev5) * 100 : null;
    const currentVolume = toNumber(row.volume);
    const volumes = rows
      .slice(Math.max(0, rows.length - 6), rows.length - 1)
      .map((x) => toNumber(x.volume))
      .filter((x) => x != null);
    const avgPrev5Volume =
      volumes.length > 0 ? volumes.reduce((sum, x) => sum + x, 0) / volumes.length : null;
    const volumeRatio =
      currentVolume != null && avgPrev5Volume != null && avgPrev5Volume > 0 ? currentVolume / avgPrev5Volume : null;
    return {
      latestDate: row.time ?? null,
      rsi: null,
      close: closeNow,
      changeRatio: toNumber(row.changeRatio),
      change5d,
      volumeRatio,
      avgPrev5Volume,
      raw: row,
    };
  }
  if (data?.["Technical Analysis: RSI"]) {
    const entries = Object.entries(data["Technical Analysis: RSI"]);
    if (entries.length > 0) {
      const [date, value] = entries[0];
      return {
        latestDate: date,
        rsi: toNumber(value?.RSI),
        raw: data,
      };
    }
  }
  return {
    latestDate: null,
    rsi: null,
    raw: data,
  };
}

function pickSentimentData(raw) {
  const payload = raw?.result || raw || {};
  const data = payload?.data || payload;
  const content = qResolveToolPayloadSync(raw).content ?? data;
  const hits = content?.data?.hits || content?.hits || [];
  if (Array.isArray(hits)) {
    const latest = hits[0]?.source || hits[0] || null;
    const sentimentScore = latest?.newsSentiment?.[0]?.sentimentScore ?? latest?.weChatSentiment?.[0]?.sentimentScore ?? null;
    const sourceLabel = latest?.type || latest?.sourceName || latest?.siteName || null;
    return {
      itemCount: hits.length,
      latestHeadline: latest?.title ?? null,
      latestTime: latest?.publishTime ?? latest?.effectiveTime ?? null,
      latestTickerSentiment: sentimentScore,
      sourceLabel,
      fullContentFileUrl: data?.full_content_file_url ?? null,
      raw: content,
    };
  }
  if (Array.isArray(content)) {
    const latest = content[0] || null;
    return {
      itemCount: content.length,
      latestHeadline: latest?.headline ?? null,
      latestTime: latest?.datetime ?? null,
      latestTickerSentiment: null,
      fullContentFileUrl: data?.full_content_file_url ?? null,
      raw: content,
    };
  }
  const feed = content?.feed || [];
  const latest = feed[0] || null;
  return {
    itemCount: toNumber(content?.items) ?? feed.length,
    latestHeadline: latest?.title ?? null,
    latestTime: latest?.time_published ?? null,
    latestTickerSentiment: latest?.ticker_sentiment?.[0]?.ticker_sentiment_label ?? null,
    fullContentFileUrl: data?.full_content_file_url ?? null,
    raw: content,
  };
}

function pickXSentimentData(raw) {
  const payload = raw?.result || raw || {};
  const data = payload?.data ?? payload;
  const content = qResolveToolPayloadSync(raw).content ?? data;

  let posts = [];
  if (Array.isArray(content)) posts = content;
  else if (Array.isArray(content?.data)) posts = content.data;
  else if (Array.isArray(content?.posts)) posts = content.posts;
  else if (Array.isArray(content?.results)) posts = content.results;

  const first = posts[0] || null;
  return {
    itemCount: posts.length || toNumber(content?.total) || 0,
    topPostText: first?.text ?? first?.full_text ?? first?.title ?? first?.headline ?? null,
    topPostTime: first?.created_at ?? first?.time ?? first?.datetime ?? null,
    sourceMode: Array.isArray(content) ? "fallback" : "direct",
    fullContentFileUrl: data?.full_content_file_url ?? null,
    raw: content,
  };
}

async function executeWithFallback(candidates, searchId, paramBuilder, options, executionMeta = {}) {
  const attempts = [];
  const maxAttempts = options.maxAttemptsPerPhase || 3;
  const successValidator = executionMeta?.successValidator;
  for (const tool of candidates.slice(0, maxAttempts)) {
    const built = paramBuilder(tool);
    const params = built?.params ?? built;
    const paramContext = built?.paramContext ?? null;
    try {
      const sid = searchId;
      const startedAt = Date.now();
      const result = await executeTool(tool.tool_id, sid, params, options.maxSize, options.timeoutMs);
      const ok = isToolCallSuccessful(result);
      const validatedOk = ok && (typeof successValidator === "function" ? successValidator(result) : true);
      const elapsed = Date.now() - startedAt;
      attempts.push({ toolId: tool.tool_id, ok: validatedOk, params, elapsed_ms: elapsed });
      if (options.evolutionState) {
        updateEvolutionOnAttempt(options.evolutionState, {
          ...executionMeta,
          toolId: tool.tool_id,
          elapsedMs: elapsed,
          success: validatedOk,
          params,
          paramContext,
          newlyLearnedCollector: options.newlyLearnedTools,
        });
      }
      if (validatedOk) {
        return { success: true, selectedTool: summarizeTool(tool), attempts, successfulResult: result };
      }
    } catch (error) {
      attempts.push({ toolId: tool.tool_id, ok: false, error: redactSecrets(error.message), params });
      if (options.evolutionState) {
        updateEvolutionOnAttempt(options.evolutionState, {
          ...executionMeta,
          toolId: tool.tool_id,
          elapsedMs: 0,
          success: false,
          params,
          paramContext,
          errorMessage: error.message,
          newlyLearnedCollector: options.newlyLearnedTools,
        });
      }
    }
  }
  return { success: false, selectedTool: null, attempts };
}

function summarizeQuality(payload) {
  const warnings = [];
  const quote = payload.quote?.parsed;
  const fundamentals = payload.fundamentals?.parsed;
  const technicals = payload.technicals?.parsed;
  const sentiment = payload.sentiment?.parsed;

  if (!quote?.price) warnings.push("行情缺少最新价格字段");
  if (!fundamentals?.pe && !fundamentals?.marketCap) warnings.push("基本面关键估值字段缺失");
  if (technicals && technicals.rsi == null && technicals.changeRatio == null) warnings.push("技术指标缺少 RSI/趋势字段");
  if (sentiment && !sentiment.itemCount) warnings.push("情绪数据缺少新闻条目");

  if (quote?.timestamp && typeof quote.timestamp === "string" && quote.timestamp.length < 8) {
    warnings.push("行情时间戳格式异常");
  }
  if (isStale(quote?.timestamp, 5)) warnings.push("行情数据可能已过期（超过 5 天）");
  if (isStale(fundamentals?.latestQuarter, 220)) warnings.push("基本面季度数据较旧");

  if (quote?.price != null && fundamentals?.week52High != null && quote.price > fundamentals.week52High * 1.08) {
    warnings.push("行情价格明显高于 52 周高点，可能存在跨源不一致");
  }
  if (quote?.price != null && fundamentals?.week52Low != null && quote.price < fundamentals.week52Low * 0.92) {
    warnings.push("行情价格明显低于 52 周低点，可能存在跨源不一致");
  }

  let confidence = "high";
  if (warnings.length >= 2) confidence = "medium";
  if (warnings.length >= 4) confidence = "low";
  return { confidence, warnings };
}

function isParsedDataUsable(capability, parsed) {
  if (!parsed || typeof parsed !== "object") return false;
  if (capability === "quote") {
    return parsed.price != null || parsed.symbol != null || parsed.timestamp != null;
  }
  if (capability === "fundamentals") {
    return (
      parsed.name != null ||
      parsed.marketCap != null ||
      parsed.pe != null ||
      parsed.revenue != null ||
      parsed.netProfit != null ||
      parsed.totalAssets != null ||
      parsed.operatingCashflow != null
    );
  }
  if (capability === "technicals") {
    return parsed.rsi != null || parsed.changeRatio != null || parsed.close != null;
  }
  if (capability === "sentiment") {
    return parsed.itemCount != null;
  }
  if (capability === "x_sentiment") {
    return parsed.itemCount != null;
  }
  return true;
}

function clampScore(value) {
  if (!Number.isFinite(value)) return 50;
  return Math.max(0, Math.min(100, Math.round(value)));
}

function formatNum(value, digits = 2) {
  if (value == null || !Number.isFinite(value)) return "N/A";
  return Number(value).toFixed(digits);
}

function formatAmountByMarket(value, market, digits = 2) {
  if (value == null || !Number.isFinite(value)) return "N/A";
  const n = Number(value);
  const abs = Math.abs(n);
  if (market === "CN" || market === "HK") {
    return `${(n / 1e8).toFixed(digits)}亿`;
  }
  if (market === "US") {
    if (abs >= 1e9) return `${(n / 1e9).toFixed(digits)}B`;
    if (abs >= 1e6) return `${(n / 1e6).toFixed(digits)}M`;
    return n.toFixed(0);
  }
  if (abs >= 1e9) return `${(n / 1e9).toFixed(digits)}B`;
  if (abs >= 1e6) return `${(n / 1e6).toFixed(digits)}M`;
  return n.toFixed(0);
}

function formatPct(value, digits = 2) {
  if (value == null || !Number.isFinite(value)) return "N/A";
  return `${Number(value).toFixed(digits)}%`;
}

function formatRatioPct(value, digits = 2) {
  if (value == null || !Number.isFinite(value)) return "N/A";
  const n = Number(value);
  const pct = Math.abs(n) <= 1 ? n * 100 : n;
  return `${pct.toFixed(digits)}%`;
}

function formatFieldValueByKey(key, value, market) {
  if (value == null) return "N/A";
  if (typeof value === "number") {
    const amountFields = new Set([
      "marketCap",
      "revenue",
      "netProfit",
      "totalAssets",
      "totalLiabilities",
      "operatingCashflow",
      "amount",
      "latestAmount",
      "floatCapitalOfAShares",
      "floatCapitalOfBShares",
      "totalCapital",
      "mv",
    ]);
    const percentFields = new Set([
      "percentChange",
      "changeRatio",
      "change5d",
      "turnoverRatio",
    ]);
    const ratioPercentFields = new Set([
      "profitMargin",
      "revenueGrowthYoy",
      "earningsGrowthYoy",
    ]);
    if (amountFields.has(key)) return formatAmountByMarket(value, market);
    if (percentFields.has(key)) return formatPct(value);
    if (ratioPercentFields.has(key)) return formatRatioPct(value);
    return formatNum(value);
  }
  if (typeof value === "boolean") return value ? "true" : "false";
  if (Array.isArray(value)) return value.join(", ");
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function appendFieldDetails(lines, sectionTitle, payload, market, excludedKeys = []) {
  if (!payload || typeof payload !== "object") return;
  const keys = Object.keys(payload)
    .filter((k) => !excludedKeys.includes(k))
    .filter((k) => payload[k] != null && payload[k] !== "");
  if (keys.length === 0) return;
  lines.push(sectionTitle);
  for (const key of keys) {
    lines.push(`- ${key}: ${formatFieldValueByKey(key, payload[key], market)}`);
  }
  lines.push("");
}

function appendRawSnapshot(lines, sectionTitle, raw, market, limit = 25) {
  if (!raw || typeof raw !== "object") return;
  const keys = Object.keys(raw)
    .filter((k) => raw[k] != null && raw[k] !== "" && (typeof raw[k] !== "object" || Array.isArray(raw[k])))
    .slice(0, limit);
  if (keys.length === 0) return;
  lines.push(sectionTitle);
  for (const key of keys) {
    lines.push(`- ${key}: ${formatFieldValueByKey(key, raw[key], market)}`);
  }
  lines.push("");
}

function gradeFromScore(score) {
  if (score >= 85) return "A";
  if (score >= 75) return "B+";
  if (score >= 65) return "B";
  if (score >= 55) return "C+";
  if (score >= 45) return "C";
  return "D";
}

function pickSectorBenchmarks(benchmarks, market) {
  if (market === "CN" || market === "HK") return benchmarks.electrical_equipment || benchmarks.default;
  if (market === "US") return benchmarks.semiconductor || benchmarks.default;
  return benchmarks.default;
}

function buildScorecard(payload, benchmarks, market) {
  const q = payload.quote?.parsed || {};
  const f = payload.fundamentals?.parsed || {};
  const t = payload.technicals?.parsed || {};
  const s = payload.sentiment?.parsed || {};
  const x = payload.x_sentiment?.parsed || {};
  const b = pickSectorBenchmarks(benchmarks, market);

  let valuation = 50;
  if (f.pe != null && b.pe_median) {
    const ratio = f.pe / b.pe_median;
    if (ratio <= 0.7) valuation += 25;
    else if (ratio <= 0.9) valuation += 15;
    else if (ratio <= 1.1) valuation += 5;
    else if (ratio >= 1.5) valuation -= 20;
    else valuation -= 8;
  }
  if (f.pb != null && b.pb_median) {
    const ratio = f.pb / b.pb_median;
    if (ratio <= 0.7) valuation += 18;
    else if (ratio <= 0.9) valuation += 10;
    else if (ratio <= 1.1) valuation += 3;
    else if (ratio >= 1.6) valuation -= 18;
    else valuation -= 8;
  }

  let quality = 50;
  const margin = f.profitMargin != null ? f.profitMargin : f.revenue && f.netProfit ? f.netProfit / f.revenue : null;
  if (margin != null && b.profit_margin_benchmark != null) quality += margin >= b.profit_margin_benchmark ? 12 : -8;
  if (f.totalAssets != null && f.totalLiabilities != null && f.totalAssets > 0) {
    const debtRatio = f.totalLiabilities / f.totalAssets;
    quality += debtRatio <= (b.debt_ratio_warn ?? 0.6) ? 12 : -10;
  }
  if (f.operatingCashflow != null) quality += f.operatingCashflow > 0 ? 15 : -12;
  if (f.netProfit != null && f.totalAssets != null && f.totalLiabilities != null) {
    const equity = f.totalAssets - f.totalLiabilities;
    if (equity > 0) {
      const roe = (f.netProfit / equity) * 100;
      quality += roe >= (b.roe_benchmark ?? 12) ? 10 : -6;
    }
  }

  let growth = 50;
  if (f.revenueGrowthYoy != null) {
    if (f.revenueGrowthYoy >= 20) growth += 22;
    else if (f.revenueGrowthYoy >= 10) growth += 14;
    else if (f.revenueGrowthYoy >= 0) growth += 6;
    else growth -= 12;
  }
  if (f.earningsGrowthYoy != null) growth += f.earningsGrowthYoy >= 0 ? 8 : -8;

  let technicals = 50;
  if (t.rsi != null) {
    if (t.rsi >= 40 && t.rsi <= 65) technicals += 12;
    else if (t.rsi > 70) technicals -= 8;
    else if (t.rsi < 30) technicals += 5;
  }
  if (t.changeRatio != null) technicals += t.changeRatio > 0 ? 6 : -4;
  if (t.change5d != null) technicals += t.change5d > 0 ? 8 : -6;

  let sentiment = 50;
  if (s.itemCount != null) sentiment += Math.min(10, s.itemCount * 2);
  if (s.latestTickerSentiment != null && typeof s.latestTickerSentiment === "number") sentiment += s.latestTickerSentiment > 0 ? 8 : -6;
  if (x.itemCount != null) sentiment += Math.min(8, x.itemCount);

  const weights = { valuation: 0.3, quality: 0.25, growth: 0.2, technicals: 0.15, sentiment: 0.1 };
  const score = {
    valuation: clampScore(valuation),
    quality: clampScore(quality),
    growth: clampScore(growth),
    technicals: clampScore(technicals),
    sentiment: clampScore(sentiment),
  };
  const composite = clampScore(
    score.valuation * weights.valuation +
      score.quality * weights.quality +
      score.growth * weights.growth +
      score.technicals * weights.technicals +
      score.sentiment * weights.sentiment,
  );

  return {
    weights,
    score,
    composite,
    grade: gradeFromScore(composite),
  };
}

function calcSafetyMargin(payload, scorecard, benchmarks, market) {
  const q = payload.quote?.parsed || {};
  const f = payload.fundamentals?.parsed || {};
  const b = pickSectorBenchmarks(benchmarks, market);
  const currentPrice = q.price;
  if (currentPrice == null || currentPrice <= 0) {
    return { margin: null, verdict: "无法计算（缺少价格）" };
  }
  const currentPe = f.pe;
  if (currentPe == null || currentPe <= 0 || !b.pe_median) {
    return { margin: null, verdict: "无法计算（缺少PE或行业基准）" };
  }
  const intrinsic = currentPrice * (b.pe_median / currentPe);
  const conservative = intrinsic * 0.8;
  const margin = conservative > 0 ? ((conservative - currentPrice) / conservative) * 100 : null;
  const verdict = margin == null ? "无法判断" : margin >= 15 ? "存在显著安全边际" : margin >= 5 ? "存在安全边际" : margin >= -5 ? "估值大致合理" : "估值偏贵";
  return {
    currentPrice,
    currentPe,
    industryPeMedian: b.pe_median,
    intrinsicValue: intrinsic,
    conservativeValue: conservative,
    margin,
    verdict,
    confidenceAdjust: scorecard.composite >= 70 ? "high" : "medium",
  };
}

function detectChaseRisk(payload) {
  const q = payload.quote?.parsed || {};
  const t = payload.technicals?.parsed || {};
  const s = payload.sentiment?.parsed || {};
  const change5d = t.change5d;
  const change1d = q.percentChange;
  const volumeRatio = t.volumeRatio;
  let classification = "事件驱动型";
  let signal = "可买入";
  let risk = "low";
  if ((change5d != null && change5d >= 10) || (change1d != null && change1d >= 5) || (volumeRatio != null && volumeRatio >= 1.8)) {
    classification = "交易回踩型";
    signal = "需谨慎/回避";
    risk = "high";
  } else if ((change5d != null && change5d >= 5) || (change1d != null && change1d >= 3) || (volumeRatio != null && volumeRatio >= 1.5)) {
    classification = "交易回踩型-轻度";
    signal = "需谨慎，可关注回踩机会";
    risk = "medium";
  }
  const hasEvent = (s.itemCount || 0) > 0;
  return {
    classification,
    signal,
    risk,
    hasEvent,
    metrics: { change5d, change1d, volumeRatio, newsCount: s.itemCount ?? 0 },
  };
}

function generateRecommendation(scorecard, safetyMargin, chaseRisk) {
  let signal = "持有";
  if (scorecard.composite >= 75 && chaseRisk.risk === "low" && (safetyMargin.margin ?? -999) >= 5) signal = "买入";
  else if (chaseRisk.risk === "high") signal = "回避追高";
  else if (scorecard.composite < 50) signal = "观望";
  return {
    signal,
    horizon: "中期(3-6个月)",
    scenarios: {
      bullMarket: signal === "回避追高" ? "等待回踩后再参与" : "可分批加仓并跟踪量价确认",
      bearMarket: "控制仓位，采用分批建仓与止损纪律",
      sideways: "高抛低吸，等待催化事件进一步验证",
    },
  };
}

const REPORTIFY_CUSTOM_MAX_BLOCKS = 6;
const REPORTIFY_CUSTOM_MAX_CHARS_PER_BLOCK = 12000;

function extractReportifyCustomBlocks(inputText) {
  const text = String(inputText || "");
  const matches = text.match(/<reportify-custom[\s\S]*?<\/reportify-custom>/gi);
  if (!matches || matches.length === 0) return [];
  return matches.slice(0, REPORTIFY_CUSTOM_MAX_BLOCKS);
}

function normalizeNewlines(text) {
  return String(text || "").replace(/\r\n?/g, "\n");
}

function maxConsecutiveCharRun(text, ch) {
  const s = String(text || "");
  let max = 0;
  let cur = 0;
  for (let i = 0; i < s.length; i++) {
    if (s[i] === ch) {
      cur += 1;
      if (cur > max) max = cur;
    } else {
      cur = 0;
    }
  }
  return max;
}

function toFencedCodeBlock(content, info = "text") {
  const body = normalizeNewlines(content);
  const maxTicks = maxConsecutiveCharRun(body, "`");
  const fenceLen = Math.max(3, maxTicks + 1);
  const fence = "`".repeat(fenceLen);
  return `${fence}${info}\n${body}\n${fence}`;
}

function formatReportifyCustomBlocksSafe(inputText) {
  const blocks = extractReportifyCustomBlocks(inputText);
  if (blocks.length === 0) return [];
  const lines = [];
  lines.push("## reportify-custom（安全呈现）");
  lines.push("> 以下内容来自原始输入。为降低 XSS 风险，已按纯文本代码块输出（不会作为 Markdown/HTML 执行）。");
  for (const rawBlock of blocks) {
    const redacted = redactSecrets(rawBlock);
    const clipped =
      redacted.length > REPORTIFY_CUSTOM_MAX_CHARS_PER_BLOCK
        ? `${redacted.slice(0, REPORTIFY_CUSTOM_MAX_CHARS_PER_BLOCK)}\n...[truncated]...`
        : redacted;
    lines.push("");
    lines.push(toFencedCodeBlock(clipped, "reportify-custom"));
  }
  return lines;
}

function formatMarkdown(result) {
  const { symbol, market, mode, data, quality, evolution, analysis } = result;
  const q = data.quote?.parsed || {};
  const f = data.fundamentals?.parsed || {};
  const t = data.technicals?.parsed || {};
  const s = data.sentiment?.parsed || {};
  const x = data.x_sentiment?.parsed || {};
  const scorecard = analysis?.scorecard || {};
  const safetyMargin = analysis?.safetyMargin || {};
  const chaseRisk = analysis?.chaseRisk || {};
  const recommendation = analysis?.recommendation || {};
  const now = new Date().toISOString();
  const evidenceMode = Boolean(result?.runtime?.evidenceMode);
  const lines = [];

  lines.push(`# ${symbol} 深度投资分析报告`);
  lines.push(`> 数据截止时间: ${now}`);
  lines.push(`> 市场: ${market} | 模式: ${mode} | 质量置信度: ${quality.confidence}`);
  lines.push("");
  lines.push("## 核心结论");
  lines.push(`- 综合评级: ${scorecard.grade ?? "N/A"} (${scorecard.composite ?? "N/A"}/100)`);
  lines.push(`- 投资信号: ${recommendation.signal ?? "N/A"}`);
  lines.push(`- 时序分类: ${chaseRisk.classification ?? "N/A"}（${chaseRisk.signal ?? "N/A"}）`);
  lines.push(`- 安全边际: ${formatPct(safetyMargin.margin)}，结论: ${safetyMargin.verdict ?? "N/A"}`);
  lines.push("");

  lines.push("## 一、实时行情与交易状态");
  lines.push(`- 最新价: ${formatNum(q.price)} | 当日涨跌: ${formatPct(q.percentChange)} | 成交量: ${formatNum(q.volume, 0)}`);
  lines.push(`- 近5日涨跌: ${formatPct(t.change5d)} | 成交量比(今/前5均): ${formatNum(t.volumeRatio)}`);
  lines.push(`- 52周区间: ${formatNum(f.week52Low)} - ${formatNum(f.week52High)}`);
  lines.push("");

  lines.push("## 二、基本面核心数据");
  lines.push(`- 公司: ${f.name ?? "N/A"} | 报告期: ${f.reportPeriod ?? f.latestQuarter ?? "N/A"}`);
  lines.push(
    `- 行业/主营: ${f.industry ?? "N/A"} / ${f.mainBusiness ?? "N/A"}`,
  );
  if (Array.isArray(f.tags) && f.tags.length > 0) {
    lines.push(`- 标签: ${f.tags.join("、")}`);
  }
  lines.push(
    `- 营收/净利润: ${formatAmountByMarket(f.revenue, market)} / ${formatAmountByMarket(f.netProfit, market)}`,
  );
  lines.push(
    `- 总资产/总负债: ${formatAmountByMarket(f.totalAssets, market)} / ${formatAmountByMarket(f.totalLiabilities, market)}`,
  );
  lines.push(
    `- 经营现金流: ${formatAmountByMarket(f.operatingCashflow, market)} | 利润率: ${formatRatioPct(f.profitMargin)}`,
  );
  lines.push(`- 估值: PE ${formatNum(f.pe)} | PB ${formatNum(f.pb)} | 市值 ${formatAmountByMarket(f.marketCap, market)}`);
  lines.push("");

  lines.push("## 三、多维度评分");
  lines.push(`- 估值: ${scorecard.score?.valuation ?? "N/A"} (权重30%)`);
  lines.push(`- 财务质量: ${scorecard.score?.quality ?? "N/A"} (权重25%)`);
  lines.push(`- 成长性: ${scorecard.score?.growth ?? "N/A"} (权重20%)`);
  lines.push(`- 技术面: ${scorecard.score?.technicals ?? "N/A"} (权重15%)`);
  lines.push(`- 情绪面: ${scorecard.score?.sentiment ?? "N/A"} (权重10%)`);
  lines.push(`- 综合分: ${scorecard.composite ?? "N/A"} -> ${scorecard.grade ?? "N/A"}`);
  lines.push("");

  lines.push("## 四、事件时序与追高风险");
  lines.push(`- 分类: ${chaseRisk.classification ?? "N/A"}`);
  lines.push(`- 发布前5日涨幅: ${formatPct(chaseRisk.metrics?.change5d)}`);
  lines.push(`- 发布前1日/当日涨幅: ${formatPct(chaseRisk.metrics?.change1d)}`);
  lines.push(`- 成交量异常比: ${formatNum(chaseRisk.metrics?.volumeRatio)} (>=1.5通常视为异常)`);
  lines.push(`- 近期新闻条数: ${chaseRisk.metrics?.newsCount ?? "N/A"}`);
  lines.push(`- 结论: ${chaseRisk.signal ?? "N/A"}`);
  lines.push("");

  lines.push("## 五、情绪与资讯精华");
  lines.push(`- 新闻条数: ${s.itemCount ?? "N/A"} | 最新标题: ${s.latestHeadline ?? "N/A"}`);
  lines.push(`- 研报/新闻情绪值: ${s.latestTickerSentiment ?? "N/A"}`);
  lines.push(`- X热度: ${x.itemCount ?? "N/A"} | 热门内容: ${x.topPostText ?? "N/A"}`);
  if (result?.runtime?.includeSourceUrls && s.fullContentFileUrl) lines.push(`- 资讯源URL: ${s.fullContentFileUrl}`);
  lines.push("");

  lines.push("## 六、情景化策略");
  lines.push(`- 牛市: ${recommendation.scenarios?.bullMarket ?? "N/A"}`);
  lines.push(`- 熊市: ${recommendation.scenarios?.bearMarket ?? "N/A"}`);
  lines.push(`- 震荡市: ${recommendation.scenarios?.sideways ?? "N/A"}`);
  lines.push(`- 建议周期: ${recommendation.horizon ?? "N/A"}`);
  lines.push("");

  lines.push("## 七、风险提示");
  for (const warning of quality.warnings || []) lines.push(`- ${warning}`);
  for (const gap of data?.fundamentals?.dataGaps || []) lines.push(`- ${gap}`);
  lines.push("- 事件驱动型信号也不能保证一定上涨，需结合基本面和市场环境综合判断。");
  lines.push("- 交易回踩型不代表股票一定下跌，只是短期风险较高，可等待回调后再介入。");
  lines.push("- 本分析基于公开信息与历史时序关系，不构成投资建议。");
  lines.push("- 投资者应设置止损并自担风险。");
  lines.push("");

  lines.push("## 八、系统透明度");
  lines.push(`- 工具链路由: ${JSON.stringify(evolution?.route_source || {})}`);
  lines.push(`- 参数模板命中次数: ${evolution?.template_hits ?? 0}`);
  lines.push(`- 本次新学习工具数: ${evolution?.new_tools_learned?.length ?? 0}`);
  lines.push("");

  if (evidenceMode) {
    lines.push("## 九、数据字段明细（可用字段全展示）");
    lines.push("");
    appendFieldDetails(lines, "### Quote Parsed Fields", q, market, ["raw"]);
    appendFieldDetails(lines, "### Fundamentals Parsed Fields", f, market, ["raw"]);
    appendFieldDetails(lines, "### Technicals Parsed Fields", t, market, ["raw"]);
    appendFieldDetails(lines, "### Sentiment Parsed Fields", s, market, ["raw"]);
    appendFieldDetails(lines, "### X Sentiment Parsed Fields", x, market, ["raw"]);
    appendRawSnapshot(lines, "### Quote Raw Snapshot", q.raw, market, 30);
    appendRawSnapshot(lines, "### Fundamentals Raw Snapshot", f.raw, market, 35);
    appendRawSnapshot(lines, "### Technicals Raw Snapshot", t.raw, market, 25);
  }

  const customSection = formatReportifyCustomBlocksSafe(result?.runtime?.resolvedInput?.original);
  if (customSection.length > 0) {
    lines.push("");
    lines.push(...customSection);
  }
  return lines.join("\n");
}

function capabilitiesForMode(mode) {
  if (mode === "basic") return ["quote", "fundamentals"];
  if (mode === "fundamental") return ["quote", "fundamentals", "sentiment", "x_sentiment"];
  if (mode === "technical") return ["quote", "technicals", "sentiment", "x_sentiment"];
  return ["quote", "fundamentals", "technicals", "sentiment", "x_sentiment"];
}

function historyDateRange(days = 45) {
  const end = new Date();
  const start = new Date(Date.now() - days * 24 * 60 * 60 * 1000);
  const fmt = (d) => d.toISOString().slice(0, 10);
  return { start: fmt(start), end: fmt(end) };
}

function latestCompletedReportPeriod() {
  const now = new Date();
  const month = now.getMonth() + 1;
  let year = now.getFullYear();
  let period = "0930";
  if (month <= 4) {
    year -= 1;
    period = "0930";
  } else if (month <= 8) {
    period = "0331";
  } else if (month <= 10) {
    period = "0630";
  } else {
    period = "0930";
  }
  return { year: String(year), period };
}

function mergeFundamentalFields(base, extra) {
  const result = { ...(base || {}) };
  if ((result.industry == null || result.industry === "") && extra?.industry) result.industry = extra.industry;
  if ((result.mainBusiness == null || result.mainBusiness === "") && extra?.mainBusiness) {
    result.mainBusiness = extra.mainBusiness;
  }
  if ((!Array.isArray(result.tags) || result.tags.length === 0) && Array.isArray(extra?.tags) && extra.tags.length > 0) {
    result.tags = extra.tags;
  }
  const fields = [
    "symbol",
    "name",
    "marketCap",
    "pe",
    "forwardPe",
    "pb",
    "ps",
    "profitMargin",
    "revenueGrowthYoy",
    "earningsGrowthYoy",
    "week52High",
    "week52Low",
    "latestQuarter",
    "statementType",
    "reportPeriod",
    "revenue",
    "netProfit",
    "totalAssets",
    "totalLiabilities",
    "operatingCashflow",
  ];
  for (const key of fields) {
    if ((result[key] == null || result[key] === "") && extra?.[key] != null && extra[key] !== "") {
      result[key] = extra[key];
    }
  }
  return result;
}

async function fetchThsStatementParsed(symbol, market, statementType, options) {
  const report = latestCompletedReportPeriod();
  const params = {
    statement_type: statementType,
    codes: toThsCode(symbol, market),
    year: report.year,
    period: report.period,
    type: "1",
  };
  const raw = await executeTool("ths_ifind.financial_statements.v1", null, params, options.maxSize, options.timeoutMs);
  if (!isToolCallSuccessful(raw)) return null;
  const parsed = parseCapability("fundamentals", raw);
  if (!parsed) return null;
  if (!parsed.reportPeriod) parsed.reportPeriod = `${report.year}-${report.period}`;
  return { parsed, params };
}

async function fetchThsCompanyBasicsParsed(symbol, market, options) {
  const params = { codes: toThsCode(symbol, market) };
  const raw = await executeTool("ths_ifind.company_basics.v1", null, params, options.maxSize, options.timeoutMs);
  if (!isToolCallSuccessful(raw)) return null;
  const parsed = parseCapability("fundamentals", raw);
  if (!parsed) return null;
  return { parsed, params };
}

async function enrichCnHkFundamentals(symbol, market, output, options) {
  const base = output?.fundamentals?.parsed || {};
  let merged = { ...base };
  const supplementary = [];
  const dataGaps = [];

  try {
    const basics = await fetchThsCompanyBasicsParsed(symbol, market, options);
    if (basics?.parsed) {
      merged = mergeFundamentalFields(merged, basics.parsed);
      if (!merged.industry && basics.parsed.industry) merged.industry = basics.parsed.industry;
      if (!merged.mainBusiness && basics.parsed.mainBusiness) merged.mainBusiness = basics.parsed.mainBusiness;
      if ((!Array.isArray(merged.tags) || merged.tags.length === 0) && Array.isArray(basics.parsed.tags)) {
        merged.tags = basics.parsed.tags;
      }
      supplementary.push({ statement: "company_basics", params: basics.params, ok: true });
    } else {
      supplementary.push({ statement: "company_basics", ok: false, error: "empty result" });
      dataGaps.push("公司画像字段（行业/主营/标签）获取不完整，已尝试 company_basics 补齐。");
    }
  } catch (error) {
    supplementary.push({ statement: "company_basics", ok: false, error: redactSecrets(error.message) });
    dataGaps.push("公司画像字段（行业/主营/标签）获取失败，数据源或参数可能受限。");
  }

  if (merged.revenue == null || merged.netProfit == null) {
    try {
      const income = await fetchThsStatementParsed(symbol, market, "income", options);
      if (income?.parsed) {
        const beforeRevenue = merged.revenue;
        const beforeNetProfit = merged.netProfit;
        merged = mergeFundamentalFields(merged, income.parsed);
        const filled = beforeRevenue == null ? merged.revenue != null : beforeNetProfit == null ? merged.netProfit != null : false;
        supplementary.push({ statement: "income", params: income.params, ok: true, filled });
      } else {
        supplementary.push({ statement: "income", ok: false, error: "empty result" });
      }
    } catch (error) {
      supplementary.push({ statement: "income", ok: false, error: redactSecrets(error.message) });
    }
  }

  if (merged.totalAssets == null || merged.totalLiabilities == null) {
    try {
      const balance = await fetchThsStatementParsed(symbol, market, "balance", options);
      if (balance?.parsed) {
        const beforeAssets = merged.totalAssets;
        const beforeLiab = merged.totalLiabilities;
        merged = mergeFundamentalFields(merged, balance.parsed);
        supplementary.push({
          statement: "balance",
          params: balance.params,
          ok: true,
          filled: (beforeAssets == null && merged.totalAssets != null) || (beforeLiab == null && merged.totalLiabilities != null),
        });
      }
    } catch (error) {
      supplementary.push({ statement: "balance", ok: false, error: redactSecrets(error.message) });
    }
  }
  if (merged.operatingCashflow == null) {
    try {
      const cash = await fetchThsStatementParsed(symbol, market, "cash_flow", options);
      if (cash?.parsed) {
        const beforeCash = merged.operatingCashflow;
        merged = mergeFundamentalFields(merged, cash.parsed);
        supplementary.push({
          statement: "cash_flow",
          params: cash.params,
          ok: true,
          filled: beforeCash == null && merged.operatingCashflow != null,
        });
      }
    } catch (error) {
      supplementary.push({ statement: "cash_flow", ok: false, error: redactSecrets(error.message) });
    }
  }

  const quote = output?.quote?.parsed || {};
  merged = mergeFundamentalFields(merged, {
    marketCap: quote.marketCap,
    pe: quote.pe,
    pb: quote.pb,
  });

  if (!output.fundamentals) output.fundamentals = { success: false, parsed: {} };
  output.fundamentals.parsed = merged;
  const missingIncome = merged.revenue == null || merged.netProfit == null;
  const missingCashflow = merged.operatingCashflow == null;
  if (market === "HK" && missingIncome) {
    dataGaps.push("港股利润表字段（营收/净利润）当前在部分工具返回空值，已自动回退仍未补全。");
  }
  if (market === "HK" && missingCashflow) {
    dataGaps.push("港股现金流字段当前在部分工具返回空值，已自动回退仍未补全。");
  }
  if ((merged.industry == null || merged.mainBusiness == null) && ["CN", "HK"].includes(market)) {
    dataGaps.push("公司画像字段（行业/主营）存在空缺，已调用 company_basics 但数据源未完全返回。");
  }
  if (dataGaps.length > 0) {
    output.fundamentals.dataGaps = [...new Set(dataGaps)];
  }
  if (supplementary.length > 0) {
    output.fundamentals.supplementary = supplementary;
  }
}

function capabilityQueries(capability, market) {
  const queries = [CAPABILITY_QUERIES[capability]];
  if (capability === "x_sentiment") {
    queries.push("X Finance domain hot topics API");
  }
  if (capability === "sentiment" && ["CN", "HK"].includes(market)) {
    queries.unshift("caidazi A股 港股 研报 新闻 公众号 搜索");
    queries.push("xiaosu 股票 新闻 事件 联网搜索 API");
  }
  if (["CN", "HK"].includes(market) && CN_HK_QUERY_HINTS[capability]) {
    queries.push(CN_HK_QUERY_HINTS[capability]);
  }
  return queries;
}

function rankAndFilterCandidates(candidates, capability, market) {
  let ranked = rankTools([...candidates])
    .filter((tool) => isToolCompatibleForCapability(tool?.tool_id, capability, market))
    .sort(
      (a, b) =>
        (b._score || 0) +
        marketCapabilityBoost(b, capability, market) -
        ((a._score || 0) + marketCapabilityBoost(a, capability, market)),
    );
  ranked = prioritizeCandidatesByMarket(ranked, capability, market);
  if (capability === "fundamentals" && ["CN", "HK"].includes(market)) {
    ranked = ranked.sort((a, b) => {
      const p = thsFundamentalPriority(b?.tool_id) - thsFundamentalPriority(a?.tool_id);
      if (p !== 0) return p;
      return (b._score || 0) - (a._score || 0);
    });
  }
  if (capability === "x_sentiment") {
    ranked = ranked.filter((tool) => {
      const id = tool?.tool_id || "";
      return X_SENTIMENT_TOOL_PREFIXES.some((prefix) => id.startsWith(prefix));
    });
    ranked = ranked.sort((a, b) => {
      const aId = a.tool_id || "";
      const bId = b.tool_id || "";
      const aPrimary = aId.startsWith("x_developer.2.tweets.search.recent") ? 1 : 0;
      const bPrimary = bId.startsWith("x_developer.2.tweets.search.recent") ? 1 : 0;
      if (aPrimary !== bPrimary) return bPrimary - aPrimary;
      return (b._score || 0) - (a._score || 0);
    });
  }
  if (capability === "sentiment" && ["CN", "HK"].includes(market)) {
    const caidaziOnly = ranked.filter((tool) => isCaidaziTool(tool?.tool_id));
    if (caidaziOnly.length > 0) {
      caidaziOnly.sort((a, b) => {
        const p = caidaziPriority(b?.tool_id) - caidaziPriority(a?.tool_id);
        if (p !== 0) return p;
        return (b._score || 0) - (a._score || 0);
      });
      ranked = [...caidaziOnly, ...ranked.filter((tool) => !isCaidaziTool(tool?.tool_id))];
    }
  }
  return ranked;
}

async function searchByToolPrefix(prefix, capability, options) {
  const query = `${prefix} ${capability} API`;
  const res = await searchTools(query, Math.max(options.limit, 8), options.timeoutMs);
  const matched = (res.results || []).filter((tool) => String(tool?.tool_id || "").startsWith(prefix));
  return { matched, searchId: res.search_id };
}

async function searchByToolChain(capability, options) {
  const chains = await loadToolChains();
  const market = options.market;
  const mapping = chains?.[capability] || {};
  const prefixes =
    mapping?.[market] ||
    mapping?.GLOBAL ||
    (capability === "x_sentiment" ? mapping?.ALL : null) ||
    [];
  if (!Array.isArray(prefixes) || prefixes.length === 0) {
    return { ranked: [], searchId: null, routeSource: "none", preferredPrefixes: [] };
  }
  const all = [];
  let firstSearchId = null;
  for (const prefix of prefixes) {
    try {
      const result = await searchByToolPrefix(prefix, capability, options);
      if (!firstSearchId) firstSearchId = result.searchId;
      all.push(...result.matched);
    } catch {
      // ignore and continue chain fallback
    }
  }
  const unique = new Map();
  for (const tool of all) {
    const key = tool.tool_id;
    if (!unique.has(key) || scoreTool(tool) > scoreTool(unique.get(key))) unique.set(key, tool);
  }
  const ranked = rankAndFilterCandidates([...unique.values()], capability, market);
  return { ranked, searchId: firstSearchId, routeSource: "chain", preferredPrefixes: prefixes };
}

async function searchAndRankByCapability(capability, options) {
  const all = [];
  let chosenSearchId = null;
  for (const query of capabilityQueries(capability, options.market)) {
    const res = await searchTools(query, options.limit, options.timeoutMs);
    chosenSearchId = chosenSearchId || res.search_id;
    for (const tool of res.results || []) {
      all.push(tool);
    }
  }
  const bestById = new Map();
  for (const tool of all) {
    const key = tool.tool_id;
    if (!bestById.has(key) || scoreTool(tool) > scoreTool(bestById.get(key))) {
      bestById.set(key, tool);
    }
  }
  const ranked = rankAndFilterCandidates([...bestById.values()], capability, options.market);
  return { ranked, searchId: chosenSearchId };
}

async function runSingleAnalysis(symbol, options) {
  const resolvedInput = await resolveRequestedSymbol(symbol, options.market);
  const effectiveMarket = resolvedInput.market;
  const candidates = normalizeSymbols(resolvedInput.symbol, effectiveMarket);
  let selectedSymbol = candidates[0];
  const output = { quote: null, fundamentals: null, technicals: null, sentiment: null, x_sentiment: null };
  const evolutionSummary = {
    template_hits: 0,
    new_tools_learned: [],
    route_source: {},
  };

  const activeCapabilities = capabilitiesForMode(options.mode);

  for (const candidate of candidates) {
    selectedSymbol = candidate;
    let foundAny = false;
    for (const capability of activeCapabilities) {
      let ranked = [];
      let searchId = null;
      let routeSource = "chain";
      let preferredPrefixes = [];
      const runtimeOptions = { ...options, market: effectiveMarket };
      const chained = await searchByToolChain(capability, runtimeOptions);
      ranked = chained.ranked;
      searchId = chained.searchId;
      routeSource = chained.routeSource;
      preferredPrefixes = chained.preferredPrefixes || [];
      if (ranked.length === 0) {
        const search = await searchAndRankByCapability(capability, runtimeOptions);
        ranked = search.ranked;
        searchId = search.searchId;
        routeSource = "fallback";
      }
      evolutionSummary.route_source[capability] = routeSource;
      if (ranked.length === 0) {
        output[capability] = { success: false, reason: "no tools found", attempts: [] };
        continue;
      }
      foundAny = true;
      const executed = await executeWithFallback(
        ranked,
        searchId,
        (tool) =>
          buildParamsForCapability(capability, candidate, options.mode, tool, effectiveMarket, {
            originalInput: resolvedInput.original,
            evolutionState: options.evolutionState,
            templateHitCollector: evolutionSummary,
          }),
        options,
        {
          capability,
          market: effectiveMarket,
          symbol: candidate,
          successValidator: (raw) => isParsedDataUsable(capability, parseCapability(capability, raw)),
        },
      );
      output[capability] = {
        ...executed,
        rankedTop: ranked.slice(0, 3).map((t) => t.tool_id),
        preferredPrefixes,
        routeSource,
      };
      if (executed.success) {
        output[capability].parsed = sanitizeParsedCapability(
          parseCapability(capability, executed.successfulResult),
          options,
        );
      }
      delete output[capability].successfulResult;
    }
    if (foundAny) break;
  }

  if (["CN", "HK"].includes(effectiveMarket)) {
    await enrichCnHkFundamentals(selectedSymbol, effectiveMarket, output, options);
  }

  const quality = summarizeQualityV2(output);
  const benchmarks = await loadSectorBenchmarks();
  const scorecard = buildScorecardV2(output, benchmarks, effectiveMarket);
  const safetyMargin = calcSafetyMargin(output, scorecard, benchmarks, effectiveMarket);
  const chaseRisk = detectChaseRiskV2(output);
  const recommendation = generateRecommendation(scorecard, safetyMargin, chaseRisk);
  const financialQuality = buildFinancialQuality(output, benchmarks, effectiveMarket);
  const valuationFrame = buildValuationFrame(output, scorecard, benchmarks, effectiveMarket);
  const events = options.eventRadar
    ? extractEvents(output.sentiment?.parsed, output.x_sentiment?.parsed, {
        maxEvents: Math.max(5, Math.min(12, Number(options.eventWindowDays || 7))),
      })
    : [];
  const eventRadar = {
    view: options.eventView || "timeline",
    events,
    themes: (options.eventView || "timeline") === "theme" ? clusterEventsByTheme(events) : [],
    ideas: buildEventRadarIdeas(events, selectedSymbol, effectiveMarket),
    universe: options.eventUniverse || "global",
  };
  const thesis = buildThesis(output, effectiveMarket, scorecard, valuationFrame, financialQuality, eventRadar);
  const playbooks = buildPlaybooks(
    { scorecard, valuationFrame, chaseRisk, thesis, eventRadar },
    {
      horizon: options.horizon,
      risk: options.risk,
      style: options.style,
      actionable: options.actionable,
    },
  );
  evolutionSummary.new_tools_learned = [...new Set(options.newlyLearnedTools || [])];
  const dataSources = buildDataSourcesSummary(output);
  return {
    symbol: selectedSymbol,
    market: effectiveMarket,
    mode: options.mode,
    data: output,
    dataSources,
    quality,
    analysis: {
      scorecard,
      safetyMargin,
      chaseRisk,
      recommendation,
      financialQuality,
      valuationFrame,
      thesis,
      eventRadar,
      playbooks,
    },
    evolution: evolutionSummary,
    runtime: {
      includeSourceUrls: Boolean(options.includeSourceUrls),
      evidenceMode: Boolean(options.evidenceMode),
      evolutionEnabled: Boolean(options.evolutionEnabled),
      summaryOnly: Boolean(options.summaryOnly),
      resolvedInput: {
        original: resolvedInput.original,
        symbol: resolvedInput.symbol,
        market: resolvedInput.market,
        resolvedBy: resolvedInput.resolvedBy,
      },
    },
    meta: {
      note: "Analysis delegated to OpenClaw LLM via SKILL.md Single Stock Analysis Guide",
      guide: "Single Stock Analysis Guide",
    },
  };
}

function parseCapability(capability, raw) {
  return parseCapabilityV2(capability, raw);
}

function sanitizeParsedCapability(parsed, options) {
  if (!parsed || typeof parsed !== "object") return parsed;
  const cleaned = { ...parsed };
  if (!options?.includeSourceUrls) {
    delete cleaned.fullContentFileUrl;
  }
  return cleaned;
}

function providerFromToolId(toolId) {
  const id = String(toolId || "").trim();
  if (!id) return "unknown";
  return id.split(".")[0] || "unknown";
}

function buildDataSourcesSummary(output) {
  const rows = Object.entries(output || {})
    .filter(([, value]) => value?.success && value?.selectedTool?.tool_id)
    .map(([capability, value]) => ({
      capability,
      provider: providerFromToolId(value.selectedTool.tool_id),
      toolId: value.selectedTool.tool_id,
      route: value.routeSource || "unknown",
    }));
  const dedup = new Map();
  for (const row of rows) {
    const key = `${row.capability}#${row.toolId}`;
    if (!dedup.has(key)) dedup.set(key, row);
  }
  return [...dedup.values()];
}

function buildDefaultParamsForCapability(capability, symbol, mode, tool, market, context = {}) {
  const toolId = tool?.tool_id || "";
  const thsCode = toThsCode(symbol, market);
  const base = String(symbol || "").toUpperCase().replace(/\.(US|HK|SH|SZ|SS)$/, "");
  const originalInput = String(context.originalInput || "").trim();
  const keyword = hasCjk(originalInput) ? originalInput : hasCjk(symbol) ? String(symbol) : base;
  const caidaziTicker = market === "HK" ? base.replace(/^0+/, "").padStart(4, "0") : base;
  const recentStart = historyDateRange(120).start;
  const report = latestCompletedReportPeriod();

  if (toolId.startsWith("ths_ifind.real_time_quotation")) {
    return { codes: thsCode };
  }
  if (toolId.startsWith("ths_ifind.company_basics")) {
    return { codes: thsCode };
  }
  if (toolId.startsWith("ths_ifind.financial_statements")) {
    return { statement_type: "income", codes: thsCode, year: report.year, period: report.period, type: "1" };
  }
  if (toolId.startsWith("ths_ifind.income_statement")) {
    return { codes: thsCode, year: report.year, period: report.period, type: "1" };
  }
  if (toolId.startsWith("ths_ifind.balance_sheet")) {
    return { codes: thsCode, year: report.year, period: report.period, type: "1" };
  }
  if (toolId.startsWith("ths_ifind.cash_flow_statement")) {
    return { codes: thsCode, year: report.year, period: report.period, type: "1" };
  }
  if (toolId.startsWith("ths_ifind.history_quotation")) {
    const range = historyDateRange(45);
    return { codes: thsCode, startdate: range.start, enddate: range.end, interval: "D" };
  }
  if (toolId.startsWith("finnhub.news")) {
    return { category: "general" };
  }
  if (toolId.startsWith("caidazi.search.hybrid_v2.query")) {
    return {
      input: keyword,
      ticker: caidaziTicker,
      sourceType: "report,news,wechat",
      size: 5,
      highlight: "true",
      sortOrder: "desc",
      publishTimeStart: recentStart,
      timeSensitive: true,
    };
  }
  if (toolId.startsWith("caidazi.news.query")) {
    return {
      input: keyword,
      ticker: caidaziTicker,
      size: 5,
      highlight: "true",
      sortOrder: "desc",
      publishTimeStart: recentStart,
    };
  }
  if (toolId.startsWith("caidazi.report.query")) {
    return {
      input: keyword,
      tsCode: caidaziTicker,
      size: 5,
      highlight: "true",
      sortOrder: "desc",
      publishDateStart: recentStart,
    };
  }
  if (toolId.startsWith("caidazi.search.hybrid.list")) {
    return { input: keyword };
  }
  if (toolId.startsWith("x_developer.2.tweets.search.recent")) {
    return {
      query: `(${base} OR $${base}) lang:en -is:retweet`,
      max_results: 20,
      sort_order: "relevancy",
    };
  }
  if (toolId.startsWith("qveris_social.x_domain_new_posts")) {
    return { domains: ["Finance"], limit: 20 };
  }
  if (toolId.startsWith("qveris_social.x_domain_hot_topics")) {
    return { domains: ["Finance"], limit: 20, min_engagement: 30 };
  }
  if (toolId.startsWith("qveris_social.x_domain_hot_events")) {
    return { domains: ["Finance"] };
  }

  if (capability === "quote") {
    return { symbol };
  }
  if (capability === "fundamentals") {
    return { function: "OVERVIEW", symbol };
  }
  if (capability === "technicals") {
    const interval = mode === "technical" ? "daily" : "daily";
    return { function: "RSI", symbol, interval, series_type: "close", time_period: 14 };
  }
  if (capability === "sentiment") {
    return { function: "NEWS_SENTIMENT", tickers: symbol, sort: "LATEST", limit: 10 };
  }
  if (capability === "x_sentiment") {
    return {
      query: `(${base} OR $${base}) lang:en -is:retweet`,
      max_results: 20,
      sort_order: "relevancy",
    };
  }
  return { symbol };
}

function buildParamsForCapability(capability, symbol, mode, tool, market, context = {}) {
  const toolId = tool?.tool_id || "";
  const thsCode = toThsCode(symbol, market);
  const base = String(symbol || "").toUpperCase().replace(/\.(US|HK|SH|SZ|SS)$/, "");
  const originalInput = String(context.originalInput || "").trim();
  const keyword = hasCjk(originalInput) ? originalInput : hasCjk(symbol) ? String(symbol) : base;
  const caidaziTicker = market === "HK" ? base.replace(/^0+/, "").padStart(4, "0") : base;
  const recentStart = historyDateRange(120).start;
  const history = historyDateRange(45);
  const report = latestCompletedReportPeriod();
  const paramContext = {
    symbol,
    mode,
    market,
    thsCode,
    base,
    keyword,
    caidaziTicker,
    recentStart,
    history,
    report,
  };
  const template = getEvolutionTemplate(context.evolutionState, toolId, market);
  if (template) {
    const interpolated = interpolateTemplate(template, paramContext);
    if (context.templateHitCollector) {
      context.templateHitCollector.template_hits = (context.templateHitCollector.template_hits || 0) + 1;
    }
    return { params: interpolated, paramContext };
  }
  const params = buildDefaultParamsForCapability(capability, symbol, mode, tool, market, context);
  return { params, paramContext };
}

function parseArgs(argv) {
  const args = argv.slice(2);
  if (args.length === 0 || args.includes("--help") || args.includes("-h")) return { help: true };
  const command = args[0];
  const parsed = {
    command,
    market: "GLOBAL",
    mode: "comprehensive",
    format: "markdown",
    limit: 10,
    maxSize: 30000,
    timeoutMs: 25000,
    maxAttemptsPerPhase: 3,
    includeSourceUrls: false,
    evidenceMode: false,
    evolutionEnabled: true,
    actionable: false,
    skipQuestionnaire: false,
    summaryOnly: false,
    eventRadar: true,
    eventWindowDays: 7,
    eventUniverse: "global",
    eventView: "timeline",
    horizon: null,
    risk: null,
    style: null,
  };

  for (let i = 1; i < args.length; i++) {
    const key = args[i];
    if (key === "--symbol" && i + 1 < args.length) parsed.symbol = args[++i];
    else if (key === "--symbols" && i + 1 < args.length) parsed.symbols = args[++i];
    else if (key === "--market" && i + 1 < args.length) parsed.market = args[++i].toUpperCase();
    else if (key === "--mode" && i + 1 < args.length) parsed.mode = args[++i];
    else if (key === "--format" && i + 1 < args.length) parsed.format = args[++i];
    else if (key === "--type" && i + 1 < args.length) parsed.type = args[++i];
    else if (key === "--action" && i + 1 < args.length) parsed.watchAction = args[++i];
    else if (key === "--bucket" && i + 1 < args.length) parsed.bucket = args[++i];
    else if (key === "--max-items" && i + 1 < args.length) parsed.maxItems = Number(args[++i]) || 8;
    else if (key === "--limit" && i + 1 < args.length) parsed.limit = Number(args[++i]) || 10;
    else if (key === "--max-size" && i + 1 < args.length) parsed.maxSize = Number(args[++i]) || 30000;
    else if (key === "--timeout" && i + 1 < args.length) parsed.timeoutMs = (Number(args[++i]) || 25) * 1000;
    else if (key === "--include-source-urls") parsed.includeSourceUrls = true;
    else if (key === "--evidence") parsed.evidenceMode = true;
    else if (key === "--no-evolution") parsed.evolutionEnabled = false;
    else if (key === "--actionable") parsed.actionable = true;
    else if (key === "--skip-questionnaire") parsed.skipQuestionnaire = true;
    else if (key === "--summary-only") parsed.summaryOnly = true;
    else if (key === "--event-radar") parsed.eventRadar = true;
    else if (key === "--no-event-radar") parsed.eventRadar = false;
    else if (key === "--event-window-days" && i + 1 < args.length) parsed.eventWindowDays = Number(args[++i]) || 7;
    else if (key === "--event-universe" && i + 1 < args.length) parsed.eventUniverse = String(args[++i]).toLowerCase();
    else if (key === "--event-view" && i + 1 < args.length) parsed.eventView = String(args[++i]).toLowerCase();
    else if (key === "--horizon" && i + 1 < args.length) parsed.horizon = String(args[++i]).toLowerCase();
    else if (key === "--risk" && i + 1 < args.length) parsed.risk = String(args[++i]).toLowerCase();
    else if (key === "--style" && i + 1 < args.length) parsed.style = String(args[++i]).toLowerCase();
  }
  return parsed;
}

function formatRoutedMarkdown(result) {
  if (!result || typeof result !== "object") return String(result ?? "");
  if (result.mode === "watch") {
    const lines = ["# Watchlist 管理", `- 操作: ${result.action}`];
    const holdings = result.watchlist?.holdings || [];
    const watchlist = result.watchlist?.watchlist || [];
    lines.push("", "## 持仓");
    if (holdings.length === 0) lines.push("- (空)");
    for (const item of holdings) lines.push(`- ${item.symbol} (${item.market})`);
    lines.push("", "## 关注");
    if (watchlist.length === 0) lines.push("- (空)");
    for (const item of watchlist) lines.push(`- ${item.symbol} (${item.market})`);
    return lines.join("\n");
  }
  if (result.mode === "brief") {
    const lines = [`# ${result.type === "evening" ? "晚报" : "早报"}`, `- 生成时间: ${result.generatedAt}`];
    lines.push(`- 覆盖: 持仓 ${result.coverage?.holdings || 0} | 关注 ${result.coverage?.watchlist || 0}`);
    lines.push(`- 市场情绪: ${result.marketOverview?.sentiment || "unknown"}`);
    lines.push("", "## 市场概览");
    for (const idx of result.marketOverview?.indices || []) {
      if (idx.error) lines.push(`- ${idx.name}(${idx.symbol}): 数据失败 - ${idx.error}`);
      else lines.push(`- ${idx.name}(${idx.symbol}): ${idx.price ?? "N/A"} / ${idx.percentChange ?? "N/A"}%`);
    }
    lines.push("", "## 热点摘要");
    for (const item of result.highlights || []) {
      const tickerStr = item.tickers?.length ? ` | ${item.tickers.join(", ")}` : "";
      const categoryStr = item.category ? ` [${item.category}]` : "";
      lines.push(`- ${item.title}${categoryStr}${tickerStr}`);
      lines.push(`  - 来源: ${item.source}${item.publishTime ? ` | ${item.publishTime}` : ""}`);
    }
    lines.push("", "## 标的摘要");
    for (const row of result.reports || []) {
      if (row.error) lines.push(`- ${row.symbol} (${row.market}): 失败 - ${row.error}`);
      else lines.push(`- ${row.symbol} (${row.market}): ${row.price ?? "N/A"} / ${row.percentChange ?? "N/A"}% / ${row.grade} / ${row.signal} / 风险 ${row.risk}`);
    }
    lines.push("", "---");
    lines.push("*分析建议：请 OpenClaw 根据 SKILL.md 中的 Daily Brief Analysis Guide 输出专业且精炼的早晚报（包含投资逻辑与操作建议）*");
    return lines.join("\n");
  }
  if (result.mode === "radar") {
    const lines = ["# 行业热点雷达", `- 生成时间: ${result.generatedAt}`, `- 热点数: ${result.topicCount || 0}`];
    lines.push(`- 数据源数: ${result.meta?.sourceCount || 0}`);
    lines.push("", "## 热点详情");
    for (const t of result.topics || []) {
      const tickerStr = t.tickers?.length ? ` | 相关: ${t.tickers.join(", ")}` : "";
      const sentimentStr = t.sentiment != null ? ` | 情绪: ${t.sentiment.toFixed(2)}` : "";
      const categoryStr = t.category ? ` | 分类: ${t.category}` : "";
      lines.push(`- **${t.title || "未命名主题"}**`);
      lines.push(`  - 来源: ${t.source || "unknown"}${categoryStr}${tickerStr}${sentimentStr}`);
      if (t.publishTime) lines.push(`  - 时间: ${t.publishTime}`);
    }
    lines.push("", "## 数据源状态");
    for (const s of result.meta?.sourceStats || []) {
      lines.push(`- ${s.source}: ${s.ok ? "OK" : "FAIL"} / count=${s.count}`);
    }
    lines.push("", "---");
    lines.push("*分析建议：请 OpenClaw 根据 SKILL.md 中的 Hot Topic Analysis Guide 进行主题聚合与投资分析*");
    return lines.join("\n");
  }
  return JSON.stringify(result, null, 2);
}

function printHelp() {
  console.log(`Stock Copilot Pro

Usage:
  node scripts/stock_copilot_pro.mjs analyze --symbol AAPL [options]
  node scripts/stock_copilot_pro.mjs compare --symbols AAPL,MSFT [options]

Options:
  --market US|HK|CN|GLOBAL   default GLOBAL
  --mode basic|fundamental|technical|comprehensive   default comprehensive
  --format markdown|json|chat default markdown
  --action list|add|remove   for watch command
  --bucket holdings|watchlist for watch command
  --type morning|evening     for brief command
  --max-items N              max symbols in brief
  --limit N                  search results per capability (default 10)
  --max-size N               max response size bytes (default 30000)
  --timeout N                timeout seconds (default 25)
  --include-source-urls      include provider full-content URLs in report
  --evidence                 include full parsed/raw evidence sections in report
  --horizon short|mid|long   investment horizon preference
  --risk low|mid|high        risk preference
  --style value|balanced|growth|trading
                             preferred investment style
  --actionable               include execution-oriented strategy rules
  --skip-questionnaire       skip default preference questionnaire
  --summary-only             render summary-first compact report
  --event-window-days N      event window in days (default 7)
  --event-universe global|same_market
                             event radar universe scope
  --event-view timeline|theme
                             event output style
  --no-evolution             disable reading/writing .evolution state
  --help                     show this message
`);
}

async function main() {
  const args = parseArgs(process.argv);
  if (args.help) {
    printHelp();
    return;
  }
  args.evolutionState = args.evolutionEnabled ? await loadEvolutionState() : null;
  args.newlyLearnedTools = [];

  if (hasCommand(args.command)) {
    const result = await dispatchCommand(args.command, args, {
      analyzeSymbol: async (symbol, runArgs) => runSingleAnalysis(symbol, runArgs),
    });
    if (args.format === "json") {
      console.log(JSON.stringify(result, null, 2));
      return;
    }
    if (args.format === "chat" && result?.mode === "brief" && Array.isArray(result.reports)) {
      const chatReports = result.reports.filter((x) => !x.error).map((x) => ({
        symbol: x.symbol,
        market: x.market,
        analysis: { scorecard: { grade: x.grade }, recommendation: { signal: x.signal }, chaseRisk: { risk: x.risk } },
      }));
      console.log(
        chatReports
          .map((r) => `${buildDecisionCard(r).asText}`)
          .join("\n"),
      );
      return;
    }
    console.log(formatRoutedMarkdown(result));
    return;
  }

  if (args.command === "analyze") {
    if (!args.symbol) throw new Error("analyze requires --symbol");
    const preferences = parsePreferences(args);
    if (!args.skipQuestionnaire && !preferences.hasAny) {
      const questionnaireResult = {
        questionnaire: buildQuestionnaire(),
        runtime: {
          summaryOnly: Boolean(args.summaryOnly),
          resolvedInput: { original: args.symbol },
        },
      };
      if (args.format === "json") console.log(JSON.stringify(questionnaireResult, null, 2));
      else console.log(formatMarkdownV2(questionnaireResult));
      return;
    }
    const result = await runSingleAnalysis(args.symbol, args);
    result.evolution.new_tools_learned = [...new Set(args.newlyLearnedTools)];
    if (args.evolutionEnabled && args.evolutionState) await saveEvolutionState(args.evolutionState);
    if (args.format === "json") console.log(JSON.stringify(result, null, 2));
    else if (args.format === "chat") console.log(JSON.stringify(formatForChat(result), null, 2));
    else console.log(formatMarkdownV2(result));
    return;
  }

  if (args.command === "compare") {
    if (!args.symbols) throw new Error("compare requires --symbols");
    const symbols = args.symbols.split(",").map((s) => s.trim()).filter(Boolean);
    const reports = [];
    for (const s of symbols) {
      reports.push(await runSingleAnalysis(s, args));
    }
    if (args.evolutionEnabled && args.evolutionState) await saveEvolutionState(args.evolutionState);
    if (args.format === "json") {
      console.log(
        JSON.stringify(
          {
            mode: "compare",
            market: args.market,
            reports,
            evolution: { new_tools_learned: [...new Set(args.newlyLearnedTools)] },
          },
          null,
          2,
        ),
      );
    } else if (args.format === "chat") {
      console.log(
        JSON.stringify(
          {
            mode: "compare-chat",
            reports: reports.map((r) => ({
              symbol: r.symbol,
              market: r.market,
              decisionCard: buildDecisionCard(r),
              chat: formatForChat(r),
            })),
          },
          null,
          2,
        ),
      );
    } else {
      for (const report of reports) {
        report.evolution.new_tools_learned = [...new Set(args.newlyLearnedTools)];
        console.log(formatMarkdownV2(report));
        console.log("\n---\n");
      }
    }
    return;
  }

  throw new Error(`Unknown command: ${args.command}`);
}

function isDirectExecution() {
  const argvPath = process.argv?.[1] ? path.resolve(process.argv[1]) : "";
  return argvPath === __filename;
}

if (isDirectExecution()) {
  main().catch((err) => {
    if (err.name === "AbortError") {
      console.error("Error: request timeout");
    } else {
      console.error(`Error: ${redactSecrets(err.message)}`);
    }
    process.exit(1);
  });
}

export {
  extractReportifyCustomBlocks,
  formatReportifyCustomBlocksSafe,
  toFencedCodeBlock,
  normalizeNewlines,
  maxConsecutiveCharRun,
  isDirectExecution,
  formatMarkdown,
};

