// ./workspace/tools/finance_lite/brief.mjs
// Finance Lite: Macro (FRED CSV) + Benchmarks + Watchlist + critical headlines
//
// Commands:
//   node brief.mjs brief
//   node brief.mjs macro
//   node brief.mjs list
//   node brief.mjs add TSLA
//   node brief.mjs add QQQ bench
//   node brief.mjs remove TSLA
//   node brief.mjs ticker NVDA
//   node brief.mjs nvda   (alias for ticker NVDA)
//
// Env:
//   FINNHUB_API_KEY
//   NASDAQ_DATALINK_API_KEY (or NASDAQ_DATA_LINK_API_KEY)

import fs from "fs";
import path from "path";
import process from "process";
import { execFileSync } from "child_process";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const ROOT_DIR = path.dirname(__filename);

function syncEventsAndCalendarAfterWatchlistChange() {
  // Slim public bundle: events/calendar sync intentionally disabled.
  return [];
}

const FINNHUB = "https://finnhub.io/api/v1";
const FINNHUB_KEY = process.env.FINNHUB_API_KEY;

const NASDAQ_KEY =
  process.env.NASDAQ_DATALINK_API_KEY || process.env.NASDAQ_DATA_LINK_API_KEY;

if (!FINNHUB_KEY) {
  console.error("Missing FINNHUB_API_KEY in environment.");
  process.exit(2);
}

const CACHE_DIR = path.join(ROOT_DIR, ".cache");
fs.mkdirSync(CACHE_DIR, { recursive: true });

const WATCHLIST_PATH = path.join(ROOT_DIR, "watchlist.json");

const SIDECAR_CACHE_DIR = path.join(CACHE_DIR, "sidecar");
const SIDECAR_MAX_AGE_MIN = 60;
fs.mkdirSync(SIDECAR_CACHE_DIR, { recursive: true });

function parseIsoMs(s) {
  const t = Date.parse(s);
  return Number.isFinite(t) ? t : null;
}

function readSidecarCache(ticker, maxAgeMinutes = SIDECAR_MAX_AGE_MIN) {
  const t = normalizeTicker(ticker);
  const fp = path.join(SIDECAR_CACHE_DIR, `${t}.json`);
  try {
    const raw = fs.readFileSync(fp, "utf8");
    const obj = JSON.parse(raw);

    // Required fields
    if (normalizeTicker(obj.ticker) !== t) return null;
    if (typeof obj.source !== "string" || !obj.source.startsWith("http")) return null;

    const asOfMs = parseIsoMs(obj.asOf);
    if (!asOfMs) return null;

    const ageMin = (Date.now() - asOfMs) / 60000;
    if (ageMin > maxAgeMinutes) return null;

    // Normalizers
    const toNum = (v) => {
      if (v === null || v === undefined) return null;
      if (typeof v === "number") return Number.isFinite(v) ? v : null;
      const n = Number(String(v).replace(/[^0-9.\-]/g, ""));
      return Number.isFinite(n) ? n : null;
    };

    const out = {
      ticker: t,
      asOf: obj.asOf,
      source: obj.source,
      price: toNum(obj.price),
      changePct: toNum(obj.changePct),
      prevClose: toNum(obj.prevClose),
      volume: toNum(obj.volume),
      avgVolume3m: typeof obj.avgVolume3m === "string" ? obj.avgVolume3m : null,
      marketCap: typeof obj.marketCap === "string" ? obj.marketCap : null,
      range52w: typeof obj.range52w === "string" ? obj.range52w : null,
      shortFloat: typeof obj.shortFloat === "string" ? obj.shortFloat : null,
      targetPrice: typeof obj.targetPrice === "string" ? obj.targetPrice : null,
      notes: Array.isArray(obj.notes) ? obj.notes.map(String) : []
    };

    // Must have something useful
    const hasUseful =
      Number.isFinite(out.price) ||
      out.marketCap ||
      out.shortFloat ||
      out.targetPrice ||
      out.range52w ||
      out.avgVolume3m ||
      Number.isFinite(out.volume);

    if (!hasUseful) return null;

    return out;
  } catch {
    return null;
  }
}

function fmtSidecarEnrichedLine(sc) {
  // compact one-liner
  const parts = [];
  parts.push(`${sc.ticker} (sidecar ${sc.asOf.slice(11, 16)}Z)`);
  if (Number.isFinite(sc.price)) parts.push(`Price ${sc.price}`);
  if (Number.isFinite(sc.changePct)) parts.push(`Chg ${sc.changePct > 0 ? "+" : ""}${sc.changePct}%`);
  if (Number.isFinite(sc.volume)) parts.push(`Vol ${sc.volume.toLocaleString()}`);
  if (sc.avgVolume3m) parts.push(`AvgVol(3m) ${sc.avgVolume3m}`);
  if (sc.marketCap) parts.push(`MktCap ${sc.marketCap}`);
  if (sc.range52w) parts.push(`52W ${sc.range52w}`);
  if (sc.shortFloat) parts.push(`Short ${sc.shortFloat}`);
  if (sc.targetPrice) parts.push(`Target ${sc.targetPrice}`);
  return `- ${parts.join(" | ")}\n  Source: ${sc.source}`;
}

const MACRO_EXPLAIN = {
  inflation: {
    why:
      "Inflation gauges track price pressures. Hot inflation tends to keep interest rates higher for longer (valuation headwind, especially for growth/tech), while cooling inflation eases rate pressure and usually supports risk assets.",
    metrics: [
      "CPI: Consumer Price Index—prices paid by consumers (headline includes food+energy).",
      "Core CPI: CPI excluding food+energy—smoother read on underlying inflation trend.",
      "PCE: Personal Consumption Expenditures price index—broader inflation gauge tied to consumer spending; uses different weights than CPI.",
      "Core PCE: PCE excluding food+energy—Fed’s preferred core inflation measure for policy."
    ]
  },
  labor: {
    why:
      "Labor data indicates how tight the job market is and whether wage growth could keep inflation sticky. Strong labor can be rate-negative if it implies inflation persistence; weakening labor can be rate-positive (cuts narrative) but becomes equity-negative if it signals recession risk.",
    metrics: [
      "UNRATE: Unemployment rate—share of labor force unemployed (a broad slack indicator).",
      "NFP (PAYEMS): Nonfarm payrolls—monthly job gains/losses (growth momentum / labor demand).",
      "AHE: Average hourly earnings—wage growth proxy (feeds services inflation concerns).",
      "Claims (ICSA): Initial jobless claims—weekly layoffs signal; reacts faster than monthly reports."
    ]
  },
  growth: {
    why:
      "Growth indicators reflect demand and business momentum. Strong growth supports earnings, but if it comes with hot inflation it can be bearish via higher rates; weak growth can lift rate-cut hopes but hurts if it implies falling earnings.",
    metrics: [
      "Real GDP (GDPC1): Inflation-adjusted output—slow-moving but big-picture growth trend.",
      "Retail (RSAFS): Retail sales—consumer demand proxy; surprises can move cyclicals.",
      "ISM Mfg (NAPM): Manufacturing PMI—survey-based activity gauge (above/below 50 is expansion/contraction).",
      "ISM Svcs (NAPMNMI): Services PMI—services activity gauge; important because services dominate the economy."
    ]
  },
  ratesRisk: {
    why:
      "Rates are the discount rate for equities and a key driver of valuation. The 2Y embeds Fed path expectations; the 10Y reflects longer-run growth/inflation + term premium. Curve shifts and VIX spikes often signal regime/risk changes.",
    metrics: [
      "FFR (DFF): Effective fed funds rate—overnight policy rate actually trading in the market.",
      "2Y (DGS2): 2-year Treasury yield—most sensitive to expected Fed policy changes.",
      "10Y (DGS10): 10-year Treasury yield—longer-term rate affecting mortgages and equity discounting.",
      "VIX (VIXCLS): Implied volatility on S&P 500—risk appetite / hedging demand gauge.",
      "10Y–2Y: Yield curve slope—quick read on policy tightness / growth expectations."
    ]
  },
  housing: {
    why:
      "Housing is rate-sensitive and often leads the cycle. Falling mortgage rates can revive housing activity and confidence; rising rates can choke demand. Markets watch housing because it transmits monetary policy into the real economy quickly.",
    metrics: [
      "Starts (HOUST): Housing starts—new residential construction (real-economy demand signal).",
      "Permits (PERMIT): Building permits—forward-looking pipeline indicator (leads starts).",
      "30Y Mtg (MORTGAGE30US): 30-year mortgage rate—key affordability driver affecting housing demand."
    ]
  }
};

function fmtPct(x) {
  return (x >= 0 ? "+" : "") + (x * 100).toFixed(2) + "%";
}

function ymd(d) {
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

function isoNow() {
  return new Date().toISOString();
}

function cachePath(key) {
  return path.join(CACHE_DIR, key.replace(/[^a-zA-Z0-9._-]/g, "_") + ".json");
}

async function cached(key, ttlSec, fetcher) {
  const fp = cachePath(key);
  try {
    const raw = fs.readFileSync(fp, "utf8");
    const obj = JSON.parse(raw);
    if (obj?.ts && (Date.now() - obj.ts) / 1000 < ttlSec) return obj.data;
  } catch {}
  const data = await fetcher();
  fs.writeFileSync(fp, JSON.stringify({ ts: Date.now(), data }, null, 2));
  return data;
}

function sma(arr, n) {
  if (!arr || arr.length < n) return null;
  let s = 0;
  for (let i = arr.length - n; i < arr.length; i++) s += arr[i];
  return s / n;
}

async function fetchJson(url) {
  const res = await fetch(url, {
    headers: {
      accept: "application/json",
      "user-agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    },
  });
  const ct = (res.headers.get("content-type") || "").toLowerCase();
  const text = await res.text();
  if (!res.ok) throw new Error(`HTTP ${res.status} ${url} :: ${text.slice(0, 120)}`);
  if (!ct.includes("application/json")) {
    throw new Error(`Non-JSON response for ${url} (content-type=${ct}) :: ${text.slice(0, 120)}`);
  }
  return JSON.parse(text);
}

function curlText(url) {
  return execFileSync("curl", ["-sS", url], { encoding: "utf8" });
}

function curlJson(url) {
  const out = curlText(url).trim();
  if (out.startsWith("<")) {
    throw new Error(`HTML response (blocked) for ${url} :: ${out.slice(0, 120)}`);
  }
  return JSON.parse(out);
}

// ---------------------- Watchlist ----------------------

function normalizeTicker(s) {
  return (s ?? "").toString().trim().toUpperCase();
}

function isValidTicker(t) {
  // conservative: US tickers + ETFs + some symbols (., -, =, ^)
  return /^[A-Z0-9.\-^=]{1,12}$/.test(t);
}

function loadWatchlist() {
  try {
    const raw = fs.readFileSync(WATCHLIST_PATH, "utf8");
    const obj = JSON.parse(raw);
    const benchmarks = Array.isArray(obj.benchmarks) ? obj.benchmarks.map(normalizeTicker) : ["SPY", "GLD"];
    const watchlist = Array.isArray(obj.watchlist) ? obj.watchlist.map(normalizeTicker) : ["NVDA"];
    return { version: obj.version ?? 1, benchmarks, watchlist, updatedAt: obj.updatedAt ?? null };
  } catch {
    return { version: 1, benchmarks: ["SPY", "GLD"], watchlist: ["NVDA"], updatedAt: null };
  }
}

function saveWatchlist(wl) {
  const out = {
    version: 1,
    benchmarks: Array.from(new Set((wl.benchmarks ?? []).map(normalizeTicker))).filter(Boolean),
    watchlist: Array.from(new Set((wl.watchlist ?? []).map(normalizeTicker))).filter(Boolean),
    updatedAt: isoNow(),
  };
  fs.mkdirSync(path.dirname(WATCHLIST_PATH), { recursive: true });
  fs.writeFileSync(WATCHLIST_PATH, JSON.stringify(out, null, 2));
  return out;
}

// ---------------------- FRED (macro) ----------------------

const FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=";

const MACRO = {
  inflation: [
    { label: "CPI", id: "CPIAUCSL" },
    { label: "Core CPI", id: "CPILFESL" },
    { label: "PCE", id: "PCEPI" },
    { label: "Core PCE", id: "PCEPILFE" },
  ],
  labor: [
    { label: "UNRATE", id: "UNRATE" },
    { label: "NFP", id: "PAYEMS" },
    { label: "AHE", id: "CES0500000003" },
    { label: "Claims", id: "ICSA" },
  ],
  growth: [
    { label: "Real GDP", id: "GDPC1" },
    { label: "Retail", id: "RSAFS" },
    { label: "ISM Mfg", id: "NAPM" },
    { label: "ISM Svcs", id: "NAPMNMI" },
  ],
  ratesRisk: [
    { label: "FFR", id: "DFF" },
    { label: "2Y", id: "DGS2" },
    { label: "10Y", id: "DGS10" },
    { label: "VIX", id: "VIXCLS" },
  ],
  housing: [
    { label: "Starts", id: "HOUST" },
    { label: "Permits", id: "PERMIT" },
    { label: "30Y Mtg", id: "MORTGAGE30US" },
  ],
};

function parseFredCsvLastN(csvText, n = 3) {
  const lines = csvText.trim().split("\n");
  if (lines.length <= 1) return [];
  const data = [];
  for (let i = 1; i < lines.length; i++) {
    const [date, value] = lines[i].split(",");
    if (!date || value === undefined) continue;
    const v = value.trim();
    if (v === "." || v === "") continue;
    const num = Number(v);
    if (!Number.isFinite(num)) continue;
    data.push({ date: date.trim(), value: num });
  }
  return data.slice(-n);
}

async function fredSeries(id) {
  return await cached(`fred_${id}`, 6 * 3600, async () => {
    const url = `${FRED}${encodeURIComponent(id)}`;
    const csv = curlText(url);
    const last3 = parseFredCsvLastN(csv, 3);
    return { id, last3 };
  });
}

function fmtTrendArrow(vals) {
  if (vals.length < 3) return "";
  if (vals[2] > vals[1] && vals[1] > vals[0]) return "↑↑";
  if (vals[2] < vals[1] && vals[1] < vals[0]) return "↓↓";
  return "↕";
}

async function macroLine(item) {
  try {
    const s = await fredSeries(item.id);
    const vals = s.last3.map((x) => x.value);
    const latest = vals.at(-1);
    const prior = vals.length >= 2 ? vals.at(-2) : null;
    const arrow = fmtTrendArrow(vals);
    if (latest === undefined) return `${item.label}: (unavailable)`;
    return `${item.label} ${latest}${prior !== null ? ` (prev ${prior})` : ""} ${arrow}`;
  } catch {
    return `${item.label}: (unavailable)`;
  }
}

function curve10y2y(dgs10, dgs2) {
  const a = dgs10?.last3?.at(-1)?.value;
  const b = dgs2?.last3?.at(-1)?.value;
  if (!Number.isFinite(a) || !Number.isFinite(b)) return null;
  return a - b;
}

// ---------------------- Nasdaq Data Link (benchmarks trend) ----------------------

async function nasdaqEtfFund(ticker) {
  if (!NASDAQ_KEY) return null;
  const url =
    `https://data.nasdaq.com/api/v3/datatables/ETFG/FUND.json` +
    `?ticker=${encodeURIComponent(ticker)}` +
    `&api_key=${encodeURIComponent(NASDAQ_KEY)}`;
  return await cached(`nasdaq_etfg_fund_${ticker}`, 24 * 3600, async () => curlJson(url));
}

function extractNavSeries(etfgResp, n = 140) {
  const rows = etfgResp?.datatable?.data;
  if (!Array.isArray(rows) || rows.length === 0) return [];
  const sliced = rows.slice(Math.max(0, rows.length - n));
  return sliced
    .map((r) => ({
      date: r[0],
      nav: typeof r[3] === "number" ? r[3] : Number(r[3]),
    }))
    .filter((x) => Number.isFinite(x.nav));
}

function computeTrendFromSeries(symbol, lastPrice, series) {
  const navs = series.map((x) => x.nav);
  const ma20 = sma(navs, 20);
  const ma50 = sma(navs, 50);
  const r5d = navs.length >= 6 ? (navs.at(-1) - navs.at(-6)) / navs.at(-6) : null;

  const above20 = (lastPrice && ma20) ? lastPrice > ma20 : null;
  const above50 = (lastPrice && ma50) ? lastPrice > ma50 : null;

  return { symbol, last: lastPrice ?? (navs.at(-1) ?? null), chg1d: null, r5d, ma20, ma50, above20, above50 };
}

// ---------------------- Finnhub (quotes/news) ----------------------

async function quote(symbol) {
  return await cached(`quote_${symbol}`, 60, async () => {
    const url = `${FINNHUB}/quote?symbol=${encodeURIComponent(symbol)}&token=${encodeURIComponent(FINNHUB_KEY)}`;
    return fetchJson(url);
  });
}

async function marketNews() {
  return await cached("market_news_general", 30 * 60, async () => {
    const url = `${FINNHUB}/news?category=general&token=${encodeURIComponent(FINNHUB_KEY)}`;
    return fetchJson(url);
  });
}

async function companyNews(symbol) {
  const to = new Date();
  const from = new Date(Date.now() - 7 * 86400 * 1000);
  return await cached(`company_news_${symbol}_${ymd(from)}_${ymd(to)}`, 30 * 60, async () => {
    const url =
      `${FINNHUB}/company-news` +
      `?symbol=${encodeURIComponent(symbol)}` +
      `&from=${encodeURIComponent(ymd(from))}` +
      `&to=${encodeURIComponent(ymd(to))}` +
      `&token=${encodeURIComponent(FINNHUB_KEY)}`;
    return fetchJson(url);
  });
}

// ---------------------- Formatting ----------------------

function computeQuoteOnly(symbol, q) {
  const last = q?.c ?? null;
  const prev = q?.pc ?? null;
  const chg1d = (last && prev) ? (last - prev) / prev : null;
  return { symbol, last, chg1d };
}

function fmtBenchLine(m) {
  const base = `${m.symbol}: ${m.last ? m.last.toFixed(2) : "?"} (${m.chg1d !== null ? fmtPct(m.chg1d) : "?"} 1D`;
  const r5 = m.r5d !== null ? `, ${fmtPct(m.r5d)} 5D` : "";
  const ma =
    (m.ma20 && m.ma50)
      ? `) | MA20 ${m.ma20.toFixed(2)} ${m.above20 ? "↑" : "↓"} | MA50 ${m.ma50.toFixed(2)} ${m.above50 ? "↑" : "↓"}`
      : `)`;
  return base + r5 + ma;
}

function fmtBenchMetricLine(m) {
  if (!m || m.unavailable) return `${m?.symbol ?? "?"}: (unavailable)`;
  if (m.r5d != null || (m.ma20 && m.ma50)) return fmtBenchLine(m);
  return `${m.symbol}: ${m.last ? m.last.toFixed(2) : "?"} (${m.chg1d !== null ? fmtPct(m.chg1d) : "?"} 1D)`;
}

async function buildBenchMetrics(benchmarks) {
  const b = (benchmarks ?? []).map(normalizeTicker).filter(Boolean);

  const benchQuotes = await Promise.all(b.map(t => quote(t).catch(() => null)));
  const benchFunds  = await Promise.all(b.map(t => nasdaqEtfFund(t).catch(() => null)));

  return b.map((t, i) => {
    const q = benchQuotes[i];
    if (!q) return { symbol: t, unavailable: true };

    const chg1d = (q.c && q.pc) ? (q.c - q.pc) / q.pc : null;

    const fund = benchFunds[i];
    const series = fund ? extractNavSeries(fund, 140) : [];
    if (series.length) {
      const trend = computeTrendFromSeries(t, q.c, series);
      trend.chg1d = chg1d;
      return trend;
    }

    return {
      symbol: t,
      last: q.c ?? null,
      chg1d,
      r5d: null,
      ma20: null,
      ma50: null,
      above20: null,
      above50: null
    };
  });
}

function benchNotables(benchMetrics, thresholdPct = 0.01) {
  const movers = [];
  for (const m of benchMetrics) {
    if (!m || m.chg1d == null) continue;
    if (Math.abs(m.chg1d) >= thresholdPct) {
      movers.push(`${m.symbol} ${fmtPct(m.chg1d)}`);
    }
  }
  return movers;
}

function riskSignalFromSpyGold(spy, gld) {
  if (!spy || !gld || spy.chg1d == null || gld.chg1d == null) return null;

  // simple heuristic
  if (spy.chg1d < -0.005 && gld.chg1d > 0.005) return "Risk-off tilt (SPY down, gold up).";
  if (spy.chg1d > 0.005 && gld.chg1d < -0.005) return "Risk-on tilt (SPY up, gold down).";
  if (Math.abs(spy.chg1d) < 0.003 && Math.abs(gld.chg1d) < 0.003) return "Quiet tape (SPY and gold relatively flat).";
  return "Mixed signals (no clear risk-on/off read from SPY vs gold).";
}

function fmtTickerLine(m) {
  return `${m.symbol}: ${m.last ? m.last.toFixed(2) : "?"} (${m.chg1d !== null ? fmtPct(m.chg1d) : "?"} 1D)`;
}

function topHeadlines(items, n = 3, filterFn = null) {
  const arr = Array.isArray(items) ? items : [];
  const filtered = filterFn ? arr.filter(filterFn) : arr;
  return filtered
    .filter((x) => x?.headline || x?.title)
    .slice(0, n)
    .map((x) => {
      const title = (x.headline ?? x.title ?? "").toString().trim();
      const src = (x.source ?? x.site ?? "").toString().trim();
      const t = x.datetime ? new Date(x.datetime * 1000) : null;
      const when = t ? t.toISOString().slice(11, 16) + "Z" : "";
      return `- ${title}${src ? ` (${src})` : ""}${when ? ` [${when}]` : ""}`;
    });
}

function isTickerRelevantFactory(ticker) {
  const t = ticker.toLowerCase();
  const map = {
    NVDA: ["nvidia", "nvda", "gpu", "cuda", "h100", "blackwell", "geforce", "data center"],
  };
  const keys = map[ticker] ?? [t.toLowerCase()];
  return (item) => {
    const title = ((item?.headline ?? item?.title) ?? "").toString().toLowerCase();
    return keys.some(k => title.includes(k));
  };
}

// ---------------------- Main ----------------------

async function buildMacro(mode, mktNews) {
  const macro = { inflation: [], labor: [], growth: [], ratesRisk: [], housing: [], curve: null };

  const [dgs2, dgs10] = await Promise.all([
    fredSeries("DGS2").catch(() => null),
    fredSeries("DGS10").catch(() => null),
  ]);
  macro.curve = (dgs10 && dgs2) ? curve10y2y(dgs10, dgs2) : null;

  async function fillCategory(key) {
    for (const item of MACRO[key]) macro[key].push(await macroLine(item));
  }

  await Promise.all([
    fillCategory("inflation"),
    fillCategory("labor"),
    fillCategory("growth"),
    fillCategory("ratesRisk"),
    fillCategory("housing"),
  ]);

  const out = [];
  out.push("📌 Macro (latest, prev, trend)");

  function pushMacroSection(title, metricsLine, explainObj) {
    out.push("");
    out.push(title);
    out.push(metricsLine);
    out.push(explainObj.why);

    const defs =
      mode === "macro"
        ? explainObj.metrics
        : explainObj.metrics.slice(0, Math.min(3, explainObj.metrics.length));

    for (const d of defs) out.push(`- ${d}`);
  }

  const inflationLine = macro.inflation.join(" | ");
  const laborLine = macro.labor.join(" | ");
  const growthLine = macro.growth.join(" | ");
  const ratesLine =
    `${macro.ratesRisk.join(" | ")}` +
    `${macro.curve !== null ? ` | 10Y–2Y ${macro.curve.toFixed(2)}` : ""}`;
  const housingLine = macro.housing.join(" | ");

  pushMacroSection("Inflation", inflationLine, MACRO_EXPLAIN.inflation);
  pushMacroSection("Labor", laborLine, MACRO_EXPLAIN.labor);
  pushMacroSection("Growth", growthLine, MACRO_EXPLAIN.growth);
  pushMacroSection("Rates / Risk", ratesLine, MACRO_EXPLAIN.ratesRisk);
  pushMacroSection("Housing", housingLine, MACRO_EXPLAIN.housing);

  out.push("");
  out.push("🗞️ Macro/Market headlines");
  out.push(...topHeadlines(mktNews, 3));

  return out.join("\n");
}

async function buildTickerView(ticker) {
  const t = normalizeTicker(ticker);
  const q = await quote(t);
  const m = computeQuoteOnly(t, q);
  const news = await companyNews(t);

  const out = [];
  out.push(`🧠 ${t} snapshot`);
  out.push(fmtTickerLine({ symbol: t, ...m }));
  out.push("");
  out.push(`🗞️ ${t} headlines`);
  out.push(...topHeadlines(news, 3, isTickerRelevantFactory(t)));
  out.push("");
  // Sidecar-enriched (if present and fresh)
  const sc = readSidecarCache(t, 60);
  if (sc) {
    out.push("");
    out.push("✨ Enriched (sidecar, <=60m)");
    out.push(fmtSidecarEnrichedLine(sc));
  } else {
    out.push("");
    out.push("✨ Enriched (sidecar, <=60m)");
    out.push("(missing/stale — sidecar step should refresh this)");
  }

  out.push("");
  out.push("⚠️ Decision-support only.");
  return out.join("\n");
}

async function buildBrief() {
  const wl = loadWatchlist();
  const today = new Date();
  const header = `📈 Finance Lite — ${ymd(today)} (PT)`;

  const [mktNews] = await Promise.all([marketNews()]);

  // Macro block
  const macroText = await buildMacro("brief", mktNews);

  // Benchmarks: quote + (if possible) Nasdaq trend for ETFs
  const benchmarks = wl.benchmarks.length ? wl.benchmarks : ["SPY", "GLD"];

  const benchMetrics = await buildBenchMetrics(benchmarks);
  const benchLines = benchMetrics.map(fmtBenchMetricLine);

  // Watchlist tickers: quote-only (finnhub candles blocked)
  const watch = wl.watchlist ?? [];
  const watchQuotes = await Promise.all(watch.map(t => quote(t).catch(() => null)));
  const watchLines = watch.map((t, i) => {
    const q = watchQuotes[i];
    if (!q) return `${t}: (unavailable)`;
    const m = computeQuoteOnly(t, q);
    return fmtTickerLine({ symbol: t, ...m });
  });

  // NVDA headlines (or first watchlist ticker if NVDA not present)
  const headlineTicker = watch.includes("NVDA") ? "NVDA" : (watch[0] ?? null);
  const tickerNews = headlineTicker ? await companyNews(headlineTicker).catch(() => []) : [];

  const out = [];
  out.push(header);
  out.push("");
  out.push(macroText);

  out.push("");
  out.push("📊 Benchmarks");
  out.push(...benchLines);

    // Critical benchmark summary
  const spyM = benchMetrics.find(x => x?.symbol === "SPY");
  const gldM = benchMetrics.find(x => x?.symbol === "GLD");

  const signal = riskSignalFromSpyGold(spyM, gldM);
  if (signal) out.push(`Signal: ${signal}`);

  const movers = benchNotables(benchMetrics, 0.01);
  if (movers.length) out.push(`Notables: ${movers.join(" | ")}`);

  out.push("");
  out.push("👀 Watchlist");
    // Enriched (sidecar) summaries: all benchmarks + top 3 watchlist
  const top3Watch = (watch ?? []).slice(0, 3);
  const enrichTickers = Array.from(new Set([...(benchmarks ?? []), ...top3Watch].map(normalizeTicker))).filter(Boolean);

  out.push("");
  out.push("✨ Enriched (sidecar, <=60m)");
  if (!enrichTickers.length) {
    out.push("(none)");
  } else {
    for (const tk of enrichTickers) {
      const sc = readSidecarCache(tk, 60);
      if (sc) out.push(fmtSidecarEnrichedLine(sc));
      else out.push(`- ${tk}: (missing/stale — sidecar step should refresh)`);
    }
  }
  if (watchLines.length) out.push(...watchLines);
  else out.push("(empty — use: /finance_lite add <TICKER>)");

  out.push("");
  out.push("🗞️ Critical headlines");
  out.push("Market:");
  out.push(...topHeadlines(mktNews, 3));
  if (headlineTicker) {
    out.push(`${headlineTicker}:`);
    out.push(...topHeadlines(tickerNews, 3, isTickerRelevantFactory(headlineTicker)));
  }

  out.push("");
  out.push("Note: Benchmarks trend uses Nasdaq ETFG/FUND (daily lag) when available. Watchlist is quote-only (Finnhub candles blocked).");
  out.push("⚠️ Decision-support only; watch upcoming macro events & earnings.");

  return out.join("\n");
}

async function main() {
  const cmd = (process.argv[2] ?? "brief").toLowerCase();

  // If command looks like a ticker (e.g., NVDA, MSFT, TSLA), treat as ticker view
  if (isValidTicker(process.argv[2]) && process.argv.length === 3) {
    const t = normalizeTicker(process.argv[2]);
    console.log(await buildTickerView(t));
    return;
  }

  if (cmd === "brief") {
    console.log(await buildBrief());
    return;
  }

  if (cmd === "macro") {
    const mktNews = await marketNews();
    const today = new Date();
    const header = `📈 Finance Lite — ${ymd(today)} (PT)`;
    console.log([header, "", await buildMacro("macro", mktNews)].join("\n"));
    return;
  }

  if (cmd === "bench" || cmd === "benchmarks") {
    const wl = loadWatchlist();
    const benchmarks = wl.benchmarks ?? [];
    const today = new Date();
    const header = `📈 Finance Lite — ${ymd(today)} (PT)`;

    const out = [];
    out.push(header);
    out.push("");
    out.push("📊 Benchmarks (critical)");

    if (!benchmarks.length) {
      out.push("(empty — use: /finance_lite add <TICKER> bench)");
      console.log(out.join("\n"));
      return;
    }

    const benchMetrics = await buildBenchMetrics(benchmarks);
    out.push(...benchMetrics.map(fmtBenchMetricLine));

    const movers = benchNotables(benchMetrics, 0.01);
    if (movers.length) out.push(`Notables: ${movers.join(" | ")}`);

    // Only print risk-on/off signal if SPY + GLD exist in *your* benchmarks list
    const spyM = benchMetrics.find(x => x?.symbol === "SPY");
    const gldM = benchMetrics.find(x => x?.symbol === "GLD");
    const signal = riskSignalFromSpyGold(spyM, gldM);
    if (signal) out.push(`Signal: ${signal}`);

    out.push("");
    out.push("Tip: add/remove benchmarks with `/finance_lite add <TICKER> bench` and `/finance_lite remove <TICKER>`.");
    console.log(out.join("\n"));
    return;
  }

  if (cmd === "ticker") {
    const t = process.argv[3];
    if (!t) { console.log("Usage: ticker <TICKER>"); return; }
    console.log(await buildTickerView(t));
    return;
  }

  if (cmd === "list") {
    const wl = loadWatchlist();
    console.log(`Benchmarks: ${wl.benchmarks.join(", ") || "(none)"}`);
    console.log(`Watchlist: ${wl.watchlist.join(", ") || "(empty)"}`);
    return;
  }


  if (cmd === "add") {
    const t = normalizeTicker(process.argv[3]);
    const kind = (process.argv[4] ?? "").toLowerCase();
    if (!t) { console.log("Usage: add <TICKER> [bench]"); return; }
    if (!isValidTicker(t)) { console.log(`Invalid ticker format: ${t}`); return; }

    // Validate by fetching quote
    try {
      const q = await quote(t);
      if (!(q && (Number.isFinite(q.c) || Number.isFinite(q.pc)))) {
        console.log(`Could not validate ticker via quote: ${t}`);
        return;
      }
    } catch {
      console.log(`Could not validate ticker via quote: ${t}`);
      return;
    }

    const wl = loadWatchlist();
    const inBench = wl.benchmarks.includes(t);
    const inWatch = wl.watchlist.includes(t);
    if (inBench || inWatch) {
      console.log(`${t} already tracked (${inBench ? "benchmarks" : "watchlist"}).`);
      return;
    }

    if (kind === "bench" || kind === "benchmark") wl.benchmarks.push(t);
    else wl.watchlist.push(t);

    const saved = saveWatchlist(wl);
    console.log(`Added ${t} to ${kind === "bench" || kind === "benchmark" ? "benchmarks" : "watchlist"}.`);
    console.log(`Benchmarks: ${saved.benchmarks.join(", ") || "(none)"}`);
    console.log(`Watchlist: ${saved.watchlist.join(", ") || "(empty)"}`);

    const syncLogs = syncEventsAndCalendarAfterWatchlistChange();
    syncLogs.forEach(x => console.log(x));
    return;
  }

  if (cmd === "remove" || cmd === "rm" || cmd === "del") {
    const t = normalizeTicker(process.argv[3]);
    if (!t) { console.log("Usage: remove <TICKER>"); return; }

    const wl = loadWatchlist();
    const beforeB = wl.benchmarks.length;
    const beforeW = wl.watchlist.length;
    wl.benchmarks = wl.benchmarks.filter(x => x !== t);
    wl.watchlist = wl.watchlist.filter(x => x !== t);

    if (wl.benchmarks.length === beforeB && wl.watchlist.length === beforeW) {
      console.log(`${t} was not in watchlist.`);
      return;
    }
    const saved = saveWatchlist(wl);
    console.log(`Removed ${t}.`);
    console.log(`Benchmarks: ${saved.benchmarks.join(", ") || "(none)"}`);
    console.log(`Watchlist: ${saved.watchlist.join(", ") || "(empty)"}`);

    const syncLogs = syncEventsAndCalendarAfterWatchlistChange();
    syncLogs.forEach(x => console.log(x));
    return;
  }

  console.log(
    "Unknown command. Use: brief | macro | bench | list | add <TICKER> [bench] | remove <TICKER> | ticker <TICKER> | nvda"
  );
}

main().catch((e) => {
  console.error("Finance Lite error:", e?.message ?? e);
  process.exit(1);
});