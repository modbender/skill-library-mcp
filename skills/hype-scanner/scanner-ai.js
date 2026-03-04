/**
 * scanner-ai.js — אריה 🦁 v2 עם מוח Ollama
 * שלב 1: סריקה גולמית (rule-based, מהיר)
 * שלב 2: ניתוח Ollama (qwen2.5:32b) לכל קנדידט
 * שלב 3: רק אמיתיים עוברים — alert ליורי
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

const ALERTS_FILE = path.join(__dirname, 'alerts.json');
const STATE_FILE = path.join(__dirname, 'scanner-state.json');
const LOG_FILE = path.join(__dirname, 'scanner-ai.log');
const OLLAMA_URL = 'http://localhost:11434';
const OLLAMA_MODEL = 'qwen3:32b';

const CONFIG = {
  minHypeScore: 3,           // סף נמוך — Ollama יסנן את הרעש
  minSources: 1,             // Ollama יחליט
  volumeSpikeThreshold: 200,
  subreddits: ['wallstreetbets', 'CryptoCurrency', 'SatoshiStreetBets', 'memecoins', 'pennystocks'],
  redditMinScore: 50,
  alertCooldownHours: 3,
};

// ===== Utils =====

function log(msg) {
  const line = `[${new Date().toISOString()}] ${msg}`;
  console.log(line);
  fs.appendFileSync(LOG_FILE, line + '\n');
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function fetchJSON(url, options = {}) {
  return new Promise((resolve, reject) => {
    const lib = url.startsWith('https') ? https : http;
    const req = lib.get(url, {
      headers: { 'User-Agent': 'AriHypeScanner/2.0', ...options.headers },
      timeout: 20000
    }, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch (e) { reject(new Error(`Parse error: ${data.slice(0, 100)}`)); }
      });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('Timeout')); });
  });
}

function postJSON(url, body) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(body);
    const urlObj = new URL(url);
    const options = {
      hostname: urlObj.hostname,
      port: urlObj.port || 80,
      path: urlObj.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data)
      },
      timeout: 120000  // 2 דקות ל-Ollama
    };
    const req = http.request(options, (res) => {
      let result = '';
      res.on('data', c => result += c);
      res.on('end', () => {
        try { resolve(JSON.parse(result)); }
        catch { resolve({ response: result }); }
      });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('Ollama timeout')); });
    req.write(data);
    req.end();
  });
}

function loadState() {
  try { return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8')); }
  catch { return { seenAlerts: {}, lastScan: null }; }
}

function saveState(state) {
  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

function loadAlerts() {
  try { return JSON.parse(fs.readFileSync(ALERTS_FILE, 'utf8')); }
  catch { return []; }
}

function saveAlert(alert) {
  const alerts = loadAlerts();
  alerts.unshift(alert);
  if (alerts.length > 200) alerts.splice(200);
  fs.writeFileSync(ALERTS_FILE, JSON.stringify(alerts, null, 2));
}

// ===== Scanners =====

async function scanReddit() {
  const mentions = {};
  for (const sub of CONFIG.subreddits) {
    try {
      const data = await fetchJSON(`https://www.reddit.com/r/${sub}/hot.json?limit=50`);
      for (const post of (data?.data?.children || [])) {
        const p = post.data;
        if (p.score < CONFIG.redditMinScore) continue;
        const tickers = extractTickers(`${p.title} ${p.selftext || ''}`);
        for (const t of tickers) {
          if (!mentions[t]) mentions[t] = { count: 0, totalScore: 0, posts: [] };
          mentions[t].count++;
          mentions[t].totalScore += p.score;
          if (mentions[t].posts.length < 5)
            mentions[t].posts.push({ title: p.title.slice(0, 120), score: p.score, comments: p.num_comments, sub });
        }
      }
      await sleep(600);
    } catch (e) { log(`Reddit ${sub}: ${e.message}`); }
  }
  return mentions;
}

async function scanCoinGecko() {
  try {
    const data = await fetchJSON('https://api.coingecko.com/api/v3/search/trending');
    return (data?.coins || []).map(c => ({
      ticker: c.item.symbol.toUpperCase(),
      name: c.item.name,
      rank: c.item.market_cap_rank,
      source: 'coingecko'
    }));
  } catch (e) { log(`CoinGecko: ${e.message}`); return []; }
}

async function scanDexScreener() {
  try {
    // שלב 1: קבל top boosted tokens
    const boosts = await fetchJSON('https://api.dexscreener.com/token-boosts/top/v1');
    if (!Array.isArray(boosts) || boosts.length === 0) return [];

    // שלב 2: קבל פרטים בbatches של 30
    const addresses = boosts.slice(0, 30).map(b => b.tokenAddress).join(',');
    const data = await fetchJSON(`https://api.dexscreener.com/latest/dex/tokens/${addresses}`);
    const pairs = data?.pairs || [];

    const results = [];
    const seen = new Set();

    for (const pair of pairs) {
      const ticker = pair.baseToken?.symbol?.toUpperCase();
      if (!ticker || seen.has(ticker)) continue;
      seen.add(ticker);

      const priceChange1h = parseFloat(pair.priceChange?.h1 || 0);
      const priceChange24h = parseFloat(pair.priceChange?.h24 || 0);
      const volumeUsd24h = parseFloat(pair.volume?.h24 || 0);
      const volumeUsd1h = parseFloat(pair.volume?.h1 || 0);

      // סנן — רק עם תנועה משמעותית
      if (Math.abs(priceChange1h) < 10 && volumeUsd24h < 50000) continue;

      results.push({
        ticker,
        name: pair.baseToken?.name || ticker,
        chain: pair.chainId,
        priceChange1h,
        priceChange24h,
        volumeUsd1h,
        volumeUsd24h,
        pairAge: pair.pairCreatedAt ? Math.floor((Date.now() - pair.pairCreatedAt) / 3600000) : null,
        source: 'dexscreener'
      });
    }

    return results;
  } catch (e) { log(`DEXScreener: ${e.message}`); return []; }
}

async function scanStockTwits() {
  try {
    const data = await fetchJSON('https://api.stocktwits.com/api/2/trending/symbols.json');
    return (data?.symbols || []).slice(0, 30).map(s => ({
      ticker: s.symbol,
      name: s.title,
      watchlist_count: s.watchlist_count,
      source: 'stocktwits'
    }));
  } catch (e) { log(`StockTwits: ${e.message}`); return []; }
}

// ===== Ticker utils =====

const SKIP = new Set(['THE','FOR','AND','NOT','BUT','ARE','WAS','HAS','ALL','ITS','GET','GOT','USE','NOW','NEW','TOP','HOW','WHO','WHY','CAN','DID','PUT','OUT','OFF','OWN','WAY','YET','YES','YOU','BIG','LOL','IMO','EPS','GDP','USA','NYSE','SEC','FED','CEO','IPO','ATH','ATL','DD','RH','WSB','AI','US','IT','IS','IN','ON','AT','BE','DO','NO','SO','OR','IF','BY','UP']);

function extractTickers(text) {
  const tickers = new Set();
  const dollarRe = /\$([A-Z]{2,6})\b/g;
  let m;
  while ((m = dollarRe.exec(text)) !== null)
    if (!SKIP.has(m[1])) tickers.add(m[1]);
  return Array.from(tickers);
}

// ===== Ollama Analysis =====

async function analyzeWithOllama(candidate) {
  const prompt = `You are Ari, a professional crypto and stock market hype analyst. 
Analyze this market signal and decide if it's a REAL trading opportunity or just noise.

## Signal Data:
Ticker: ${candidate.ticker}
Hype Score: ${candidate.rawScore}/10
Sources detected: ${candidate.sources.join(', ')}

${candidate.reddit ? `Reddit:
- Mentions in last hour: ${candidate.reddit.count}
- Total upvotes: ${candidate.reddit.totalScore}
- Top posts: ${candidate.reddit.posts.slice(0,3).map(p => `"${p.title}" (${p.score}↑, r/${p.sub})`).join(' | ')}` : ''}

${candidate.coingecko ? `CoinGecko: Currently trending (rank ${candidate.coingecko.rank || 'N/A'})` : ''}

${candidate.dex ? `DEXScreener:
- 1h price change: ${candidate.dex.priceChange1h}%
- 24h price change: ${candidate.dex.priceChange24h}%
- 1h volume USD: $${candidate.dex.volumeUsd1h?.toLocaleString()}
- Pair age: ${candidate.dex.pairAge !== null ? candidate.dex.pairAge + 'h' : 'unknown'}
- Chain: ${candidate.dex.chain}` : ''}

${candidate.stocktwits ? `StockTwits: Trending (watchlists: ${candidate.stocktwits.watchlist_count})` : ''}

## Your Analysis Task:
1. Is this signal REAL or NOISE? (Consider: multiple sources, momentum, volume, post quality)
2. What's the RISK level? (rug pull risk, pump & dump, legitimate project)
3. What's the OPPORTUNITY? (entry timing, potential upside)
4. VERDICT: SEND_ALERT or IGNORE

Respond in this EXACT JSON format:
{
  "verdict": "SEND_ALERT" or "IGNORE",
  "confidence": 1-10,
  "risk": "LOW" or "MEDIUM" or "HIGH" or "CRITICAL",
  "opportunity": "brief one-liner",
  "reasoning": "2-3 sentences",
  "suggested_action": "brief what to do"
}

Be strict. Only SEND_ALERT for genuinely strong signals. Most signals should be IGNORED.`;

  try {
    log(`🧠 Ollama מנתח ${candidate.ticker}...`);
    const response = await postJSON(`${OLLAMA_URL}/api/generate`, {
      model: OLLAMA_MODEL,
      prompt,
      stream: false,
      options: { temperature: 0.3, num_predict: 400 }
    });

    const text = response.response || '';
    // חלץ JSON מהתשובה
    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      log(`Ollama תשובה לא ב-JSON עבור ${candidate.ticker}`);
      return null;
    }

    const analysis = JSON.parse(jsonMatch[0]);
    log(`🦁 ${candidate.ticker}: ${analysis.verdict} (confidence: ${analysis.confidence}/10, risk: ${analysis.risk})`);
    return analysis;
  } catch (e) {
    log(`Ollama error עבור ${candidate.ticker}: ${e.message}`);
    return null;
  }
}

// ===== Main =====

async function runScan() {
  log('🔍 אריה v2 מתחיל סריקה (עם מוח Ollama)...');
  const state = loadState();

  // סריקה מקבילה
  const [redditMentions, cgTrending, dexData, stwitsData] = await Promise.all([
    scanReddit(),
    scanCoinGecko(),
    scanDexScreener(),
    scanStockTwits(),
  ]);

  log(`Reddit: ${Object.keys(redditMentions).length} | CoinGecko: ${cgTrending.length} | DEX: ${dexData.length} | StockTwits: ${stwitsData.length}`);

  // איסוף כל tickers
  const allTickers = new Set([
    ...Object.keys(redditMentions),
    ...cgTrending.map(c => c.ticker),
    ...dexData.map(d => d.ticker),
    ...stwitsData.map(s => s.ticker),
  ]);

  // בנה קנדידטים
  const candidates = [];
  for (const ticker of allTickers) {
    const sources = [];
    let rawScore = 0;

    const reddit = redditMentions[ticker];
    const cg = cgTrending.find(c => c.ticker === ticker);
    const dex = dexData.find(d => d.ticker === ticker);
    const st = stwitsData.find(s => s.ticker === ticker);

    if (reddit && reddit.count >= 2) { sources.push('reddit'); rawScore += Math.min(4, reddit.count * 0.8); }
    if (cg) { sources.push('coingecko'); rawScore += 3; }
    if (dex) {
      const absChange = Math.abs(dex.priceChange1h);
      const volScore = dex.volumeUsd24h > 1000000 ? 2 : dex.volumeUsd24h > 100000 ? 1 : 0;
      const changeScore = absChange > 50 ? 4 : absChange > 20 ? 3 : absChange > 10 ? 2 : 0;
      if (changeScore > 0 || volScore > 0) {
        sources.push('dexscreener');
        rawScore += changeScore + volScore;
      }
    }
    if (st) { sources.push('stocktwits'); rawScore += 2; }

    if (rawScore < CONFIG.minHypeScore) continue;

    // בדוק cooldown
    const lastAlert = state.seenAlerts[ticker];
    if (lastAlert && Date.now() - lastAlert < CONFIG.alertCooldownHours * 3600000) continue;

    candidates.push({ ticker, rawScore, sources, reddit, coingecko: cg, dex, stocktwits: st });
  }

  log(`🎯 ${candidates.length} קנדידטים עוברים לניתוח Ollama`);

  const alerts = [];
  for (const candidate of candidates) {
    const analysis = await analyzeWithOllama(candidate);

    if (!analysis || analysis.verdict !== 'SEND_ALERT') continue;
    if (analysis.confidence < 6) continue; // דורש confidence בינוני לפחות

    const alert = {
      ticker: candidate.ticker,
      hype_score: Math.round(candidate.rawScore * 10) / 10,
      ai_confidence: analysis.confidence,
      risk: analysis.risk,
      opportunity: analysis.opportunity,
      reasoning: analysis.reasoning,
      suggested_action: analysis.suggested_action,
      sources: candidate.sources,
      reddit_details: candidate.reddit ? {
        mentions: candidate.reddit.count,
        total_score: candidate.reddit.totalScore,
        top_post: candidate.reddit.posts[0]?.title
      } : null,
      dex_details: candidate.dex ? {
        chain: candidate.dex.chain,
        priceChange1h: candidate.dex.priceChange1h,
        volumeUsd1h: candidate.dex.volumeUsd1h,
        pairAge: candidate.dex.pairAge
      } : null,
      urgency: analysis.confidence >= 9 ? '🚨' : analysis.confidence >= 7 ? '🔴' : '🟡',
      timestamp: new Date().toISOString(),
      status: 'pending',
      analyzed_by: OLLAMA_MODEL
    };

    saveAlert(alert);
    state.seenAlerts[candidate.ticker] = Date.now();
    alerts.push(alert);

    log(`✅ ALERT: ${alert.ticker} | AI: ${analysis.confidence}/10 | ${analysis.opportunity}`);
    await sleep(1000); // pause בין ניתוחים
  }

  state.lastScan = new Date().toISOString();
  saveState(state);

  if (alerts.length === 0) {
    log('✅ סריקה הושלמה — אין alertים חדשים');
  } else {
    log(`🚨 ${alerts.length} alertים חדשים אחרי ניתוח AI!`);
  }

  return alerts;
}

const { checkTrading } = require('./trading-monitor');

runScan().then(async (alerts) => {
  if (alerts.length > 0) {
    console.log('\n=== AI ALERTS ===');
    for (const a of alerts) {
      console.log(`${a.urgency} ${a.ticker} | AI: ${a.ai_confidence}/10 | ${a.opportunity}`);
    }
  }

  // בדוק מסחר — דווח רק אם יש שינוי
  try {
    const trading = await checkTrading();
    if (trading) {
      const tradingAlert = {
        ticker: '📊 Trading Update',
        type: 'trading',
        updates: trading.updates,
        equity: trading.equity,
        positions: trading.positions,
        urgency: '📊',
        timestamp: new Date().toISOString(),
        status: 'pending',
        sources: ['alpaca'],
      };
      const fs = require('fs');
      const existing = JSON.parse(fs.readFileSync(require('path').join(__dirname, 'alerts.json'), 'utf8'));
      existing.unshift(tradingAlert);
      if (existing.length > 200) existing.splice(200);
      fs.writeFileSync(require('path').join(__dirname, 'alerts.json'), JSON.stringify(existing, null, 2));
      log(`📊 Trading update: ${trading.updates.join(' | ')}`);
    }
  } catch (e) {
    log(`Trading monitor error: ${e.message}`);
  }

  process.exit(0);
}).catch(e => {
  log(`FATAL: ${e.message}`);
  process.exit(1);
});
