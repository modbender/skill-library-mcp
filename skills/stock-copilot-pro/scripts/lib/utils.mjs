export function clampScore(value) {
  if (!Number.isFinite(value)) return 50;
  return Math.max(0, Math.min(100, Math.round(value)));
}

export function toNumber(value) {
  if (value == null || value === "") return null;
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

export function formatNum(value, digits = 2) {
  if (value == null || !Number.isFinite(value)) return "N/A";
  return Number(value).toFixed(digits);
}

export function formatPct(value, digits = 2) {
  if (value == null || !Number.isFinite(value)) return "N/A";
  return `${Number(value).toFixed(digits)}%`;
}

export function formatRatioPct(value, digits = 2) {
  if (value == null || !Number.isFinite(value)) return "N/A";
  const n = Number(value);
  const pct = Math.abs(n) <= 1 ? n * 100 : n;
  return `${pct.toFixed(digits)}%`;
}

export function formatAmountByMarket(value, market, digits = 2) {
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

export function parseDateLike(value) {
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

export function isStale(value, days = 5) {
  const date = parseDateLike(value);
  if (!date) return false;
  const diffMs = Date.now() - date.getTime();
  return diffMs > days * 24 * 60 * 60 * 1000;
}

export function gradeFromScore(score) {
  if (score >= 85) return "A";
  if (score >= 75) return "B+";
  if (score >= 65) return "B";
  if (score >= 55) return "C+";
  if (score >= 45) return "C";
  return "D";
}

export function normalizeNewlines(text) {
  return String(text || "").replace(/\r\n?/g, "\n");
}

export function maxConsecutiveCharRun(text, ch) {
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

export function toFencedCodeBlock(content, info = "text") {
  const body = normalizeNewlines(content);
  const maxTicks = maxConsecutiveCharRun(body, "`");
  const fenceLen = Math.max(3, maxTicks + 1);
  const fence = "`".repeat(fenceLen);
  return `${fence}${info}\n${body}\n${fence}`;
}

