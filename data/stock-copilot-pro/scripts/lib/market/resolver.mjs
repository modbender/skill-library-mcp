import { executeTool, searchTools } from "../infra/qveris-client.mjs";

const THS_CODE_CONVERTER_TOOL_ID = "ths_ifind.code_converter.v1";
const CODE_CONVERTER_TIMEOUT_MS = 5000;

const DEFAULT_COMPANY_SYMBOL_ALIASES = {
  特变电工: { symbol: "600089.SH", market: "CN" },
  英伟达: { symbol: "NVDA", market: "US" },
  腾讯: { symbol: "0700.HK", market: "HK" },
  腾讯控股: { symbol: "0700.HK", market: "HK" },
  贵州茅台: { symbol: "600519.SH", market: "CN" },
};

export function hasCjk(text) {
  return /[\u3400-\u9FFF]/.test(String(text || ""));
}

export function normalizeAliasKey(value) {
  return String(value || "")
    .trim()
    .replace(/[（(]\s*[0-9A-Za-z._-]+\s*[)）]/g, "")
    .replace(/\s+/g, "");
}

export function extractTickerFromText(value) {
  const raw = String(value || "").trim();
  const withSuffix = raw.match(/([0-9]{4,6}\.(?:HK|SH|SZ|SS))/i);
  if (withSuffix?.[1]) return withSuffix[1].toUpperCase();
  const sixDigits = raw.match(/\b([0-9]{6})\b/);
  if (sixDigits?.[1]) return sixDigits[1];
  const fourDigits = raw.match(/\b([0-9]{4})\b/);
  if (fourDigits?.[1]) return fourDigits[1];
  return null;
}

export function inferMarketFromSymbol(value) {
  const raw = String(value || "").trim().toUpperCase();
  if (!raw) return "GLOBAL";
  if (raw.endsWith(".HK") || /^[0-9]{4,5}$/.test(raw)) return "HK";
  if (/\.(SH|SZ|SS)$/.test(raw) || /^[0-9]{6}$/.test(raw)) return "CN";
  if (raw.endsWith(".US") || /^[A-Z]{1,6}$/.test(raw)) return "US";
  if (hasCjk(raw)) return "CN";
  return "GLOBAL";
}

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
    for (const v of seed) variants.add(`${v}-W`);
  }
  return [...variants];
}

function extractBestCodeFromConverterRows(rows, preferredMarket) {
  const candidates = [];
  for (const row of rows || []) {
    const thscodeValues = row?.table?.thscode;
    if (!Array.isArray(thscodeValues)) continue;
    for (const item of thscodeValues) {
      for (const code of splitCandidateCodes(item)) candidates.push(code);
    }
  }
  if (candidates.length === 0) return null;
  const unique = [...new Set(candidates)];
  unique.sort((a, b) => scoreCandidateCode(b, preferredMarket) - scoreCandidateCode(a, preferredMarket));
  return normalizeResolvedCode(unique[0], preferredMarket);
}

export async function resolveCompanyNameViaQveris(companyName, preferredMarket = "GLOBAL") {
  try {
    const nameVariants = generateResolverNameVariants(companyName, preferredMarket);
    if (nameVariants.length === 0) return null;
    const searchRes = await searchTools("ths_ifind 证券代码转换 code converter", 5, CODE_CONVERTER_TIMEOUT_MS);
    const searchId = searchRes?.search_id;
    if (!searchId) return null;
    for (const name of nameVariants) {
      const params = { mode: "secname", secname: name, isexact: "0" };
      const result = await executeTool(THS_CODE_CONVERTER_TOOL_ID, searchId, params, 20480, CODE_CONVERTER_TIMEOUT_MS);
      if (!result?.success) continue;
      const data = result?.result?.data;
      if (!Array.isArray(data) || data.length === 0) continue;
      const resolvedSymbol = extractBestCodeFromConverterRows(data, preferredMarket);
      if (resolvedSymbol) {
        if (preferredMarket !== "GLOBAL" && !isCodeMatchingMarket(resolvedSymbol, preferredMarket)) continue;
        return resolvedSymbol;
      }
    }
    return null;
  } catch {
    return null;
  }
}

export async function resolveRequestedSymbol(input, preferredMarket = "GLOBAL", aliasMap = DEFAULT_COMPANY_SYMBOL_ALIASES) {
  const original = String(input || "").trim();
  const aliasKey = normalizeAliasKey(original);
  const alias = aliasMap[aliasKey];
  if (alias) {
    return {
      original,
      symbol: alias.symbol,
      market: preferredMarket !== "GLOBAL" ? preferredMarket : alias.market,
      resolvedBy: "alias",
    };
  }

  const extractedTicker = extractTickerFromText(original);
  if (extractedTicker) {
    const market = preferredMarket !== "GLOBAL" ? preferredMarket : inferMarketFromSymbol(extractedTicker);
    return { original, symbol: extractedTicker, market, resolvedBy: "ticker-extract" };
  }

  if (hasCjk(original) && !/[0-9]/.test(original)) {
    const dynamicSymbol = await resolveCompanyNameViaQveris(original, preferredMarket);
    if (dynamicSymbol) {
      const market = preferredMarket !== "GLOBAL" ? preferredMarket : inferMarketFromSymbol(dynamicSymbol);
      return { original, symbol: dynamicSymbol, market, resolvedBy: "qveris-code-converter" };
    }
  }

  const inferred = preferredMarket !== "GLOBAL" ? preferredMarket : inferMarketFromSymbol(original);
  return { original, symbol: original, market: inferred, resolvedBy: hasCjk(original) ? "cjk-default" : "input" };
}

export function normalizeSymbols(input, market) {
  const raw = (input || "").trim();
  if (!raw) return [];
  const candidates = new Set([raw.toUpperCase()]);
  const upper = raw.toUpperCase();

  if (market === "US") {
    candidates.add(upper.replace(/\.US$/, ""));
    candidates.add(`${upper.replace(/\.US$/, "")}.US`);
  } else if (market === "HK") {
    const core = upper.replace(/\.HK$/, "").replace(/^0+/, "") || "0";
    candidates.add(`${core}.HK`);
    candidates.add(`${core.padStart(4, "0")}.HK`);
    candidates.add(core.padStart(4, "0"));
  } else if (market === "CN") {
    const core = upper.replace(/\.(SS|SH|SZ)$/, "");
    candidates.add(`${core}.SS`);
    candidates.add(`${core}.SH`);
    candidates.add(`${core}.SZ`);
  } else {
    candidates.add(`${upper}.US`);
    if (/^\d+$/.test(upper)) {
      candidates.add(`${upper}.HK`);
      candidates.add(`${upper}.SS`);
      candidates.add(`${upper}.SZ`);
    }
  }

  return [...candidates];
}

export function toThsCode(symbol, market) {
  const upper = (symbol || "").toUpperCase();
  if (upper.includes(".")) return upper;
  if (market === "CN") {
    if (upper.startsWith("6")) return `${upper}.SH`;
    return `${upper}.SZ`;
  }
  if (market === "HK") {
    return `${upper.replace(/^0+/, "").padStart(4, "0")}.HK`;
  }
  return upper;
}

export { DEFAULT_COMPANY_SYMBOL_ALIASES };
