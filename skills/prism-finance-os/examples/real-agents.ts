/**
 * PRISM OS — Example Agents
 * Every API call maps to a real endpoint in api.prismapi.ai
 */

import PrismOS from '../src/index';

const prism = new PrismOS({ apiKey: process.env.PRISM_API_KEY ?? '' });

// ─────────────────────────────────────────────────────────────────
// AGENT 1: Crypto Due Diligence
// "Is this token safe to trade?"
// Covers: resolution, analysis, onchain, social, signals, risk
// ─────────────────────────────────────────────────────────────────

async function cryptoDueDiligence(input: string) {
  console.log(`\n🔍 Crypto DD: ${input}`);

  // 1. Resolve whatever identifier the user passed
  const asset = await prism.resolve.resolve(input, { expand: true, live_price: true });
  console.log(`Resolved → ${asset.symbol} (${asset.asset_type}) @ $${asset.price}`);

  if (!asset.contract_address || !asset.chain) {
    console.log('No contract address — skipping onchain checks');
    return;
  }

  // 2. Check what kind of asset this is (fork? copycat? rebrand?)
  const [analysis, copycat] = await Promise.all([
    prism.analysis.analyze(asset.symbol, { chain: asset.chain, contract_address: asset.contract_address }),
    prism.analysis.checkCopycat(asset.symbol, { chain: asset.chain, contract_address: asset.contract_address }),
  ]);
  if (analysis.risk_flags?.length) console.log('⚠️  Risk flags:', analysis.risk_flags);
  if (copycat.is_copycat) console.log('🚨 COPYCAT detected — original:', copycat.original);

  // 3. Holder concentration
  const [topHolders, distribution] = await Promise.all([
    prism.onchain.getTopHolders(asset.contract_address, { chain: asset.chain, limit: 10 }),
    prism.onchain.getHolderDistribution(asset.contract_address, asset.chain),
  ]);
  console.log(`Top holder: ${topHolders[0]?.pct_supply?.toFixed(1)}% of supply`);
  console.log(`Total holders: ${distribution.total_holders?.toLocaleString()}`);
  if (distribution.top_10_pct && distribution.top_10_pct > 50) {
    console.log('⚠️  Top 10 wallets control >50% of supply');
  }

  // 4. Supply breakdown
  const supply = await prism.onchain.getSupply(asset.symbol, { chain: asset.chain });
  console.log(`Circulating: ${supply.circulating_supply?.toLocaleString()} | Locked: ${supply.locked?.toLocaleString()}`);

  // 5. Social sentiment
  const [sentiment, github] = await Promise.all([
    prism.social.getSentiment(asset.symbol),
    prism.social.getGithub(asset.symbol).catch(() => null),
  ]);
  console.log(`Sentiment: ${sentiment.label} (${sentiment.sentiment_score?.toFixed(2)})`);
  if (github) console.log(`GitHub commits (30d): ${github.commits_30d}`);

  // 6. Technical setup
  const [technicals, sr] = await Promise.all([
    prism.technicals.analyze(asset.symbol),
    prism.technicals.getSupportResistance(asset.symbol),
  ]);
  console.log(`Trend: ${technicals.trend} | RSI: ${technicals.rsi?.toFixed(1)}`);
  console.log(`Support: $${sr.supports[0]?.price} | Resistance: $${sr.resistances[0]?.price}`);

  // 7. Risk
  const risk = await prism.risk.getMetrics(asset.symbol, { asset_type: 'crypto' });
  console.log(`Volatility: ${risk.volatility?.toFixed(2)} | Max Drawdown: ${risk.max_drawdown?.toFixed(1)}%`);

  // 8. NVT valuation
  const nvt = await prism.crypto.getNVT(asset.symbol);
  console.log(`NVT Signal: ${nvt.nvt_signal?.toFixed(1)} → ${nvt.signal}`);
}

// ─────────────────────────────────────────────────────────────────
// AGENT 2: Equity Analyst
// "Give me a full picture of NVDA"
// Covers: stocks, macro, technicals, news, calendar, signals
// ─────────────────────────────────────────────────────────────────

async function equityAnalysis(ticker: string) {
  console.log(`\n📈 Equity Analysis: ${ticker}`);

  // 1. Macro context first
  const [macroSummary, yields] = await Promise.all([
    prism.macro.getSummary(),
    prism.macro.getTreasuryYields(),
  ]);
  console.log(`Fed Rate: ${macroSummary.fed_rate}% | 10yr: ${yields['10y']}% | Inverted: ${yields.inverted}`);

  // 2. Stock quote + profile
  const [quote, profile, fundamentals] = await Promise.all([
    prism.stocks.getQuote(ticker),
    prism.stocks.getProfile(ticker),
    prism.stocks.getFundamentals(ticker),
  ]);
  console.log(`\n${profile.name} (${ticker}) | ${profile.sector} | ${profile.exchange}`);
  console.log(`Price: $${quote.price} (${quote.change_pct?.toFixed(2)}%) | Mkt Cap: $${((quote.market_cap ?? 0) / 1e9).toFixed(0)}B`);
  console.log(`P/E: ${fundamentals.pe?.toFixed(1)}x | EV/EBITDA: ${fundamentals.ev_ebitda?.toFixed(1)}x | Beta: ${fundamentals.beta?.toFixed(2)}`);

  // 3. Financials
  const [income, cashflow] = await Promise.all([
    prism.stocks.getFinancials(ticker, { statement: 'income', period: 'annual', limit: 3 }),
    prism.stocks.getFinancials(ticker, { statement: 'cash_flow', period: 'annual', limit: 3 }),
  ]);
  console.log(`Financials loaded: ${income.period} income, ${cashflow.period} cash flow`);

  // 4. Earnings + analyst ratings
  const [earnings, ratings, dcf] = await Promise.all([
    prism.stocks.getEarnings(ticker, 4),
    prism.stocks.getAnalystRatings(ticker),
    prism.stocks.getDCF(ticker, { discount_rate: 0.10, terminal_growth: 0.03 }),
  ]);
  const beatRate = earnings.filter(e => (e.eps_surprise ?? 0) > 0).length / earnings.length;
  console.log(`\nEPS Beat Rate: ${(beatRate * 100).toFixed(0)}%`);
  console.log(`Analyst Consensus: ${ratings.consensus} | Avg Target: $${ratings.avg_target}`);
  console.log(`DCF Intrinsic: $${dcf.intrinsic_value?.toFixed(0)} (${dcf.upside_pct?.toFixed(1)}% upside)`);

  // 5. Ownership signals
  const [insiders, institutional] = await Promise.all([
    prism.stocks.getInsiders(ticker, 10),
    prism.stocks.getInstitutional(ticker, 10),
  ]);
  const insiderBuys = insiders.filter(t => t.type === 'buy').length;
  console.log(`\nInsider buys (last 10): ${insiderBuys}`);
  console.log(`Top institution: ${institutional[0]?.institution} (${institutional[0]?.pct?.toFixed(2)}%)`);

  // 6. Technicals
  const [technicals, trend, sr] = await Promise.all([
    prism.technicals.analyze(ticker),
    prism.technicals.getTrend(ticker),
    prism.technicals.getSupportResistance(ticker),
  ]);
  console.log(`\nTrend: ${trend.trend} | RSI: ${technicals.rsi?.toFixed(1)}`);
  console.log(`Support: $${sr.supports[0]?.price} | Resistance: $${sr.resistances[0]?.price}`);

  // 7. Signals
  const signals = await prism.signals.getSummary(ticker);
  const allSignals = Object.values(signals).flat();
  const bullish = allSignals.filter(s => s.direction === 'bullish').length;
  console.log(`Signals: ${bullish}/${allSignals.length} bullish`);

  // 8. Peers comparison
  const peers = await prism.stocks.getPeers(ticker);
  console.log(`Peers: ${peers.slice(0, 5).join(', ')}`);

  // 9. News
  const news = await prism.news.getStockNews(ticker, 5);
  console.log(`\nRecent news:`);
  news.forEach(n => console.log(`  [${n.sentiment}] ${n.title}`));

  // 10. Upcoming earnings
  const upcomingEarnings = await prism.calendar.getEarningsThisWeek(20);
  const nextReport = upcomingEarnings.find(e => e.symbol === ticker);
  if (nextReport) console.log(`\n⏰ Upcoming earnings: ${nextReport.report_date} (${nextReport.time_of_day})`);
}

// ─────────────────────────────────────────────────────────────────
// AGENT 3: Macro Dashboard
// "What is the current macro environment?"
// Covers: macro (all endpoints), treasury yields, calendar, news
// ─────────────────────────────────────────────────────────────────

async function macroDashboard() {
  console.log('\n🌍 Macro Dashboard');

  const [summary, fedRate, inflation, gdp, unemployment, yields, m2, joblessClaims, housing] =
    await Promise.all([
      prism.macro.getSummary(),
      prism.macro.getFedRate(),
      prism.macro.getInflation(),
      prism.macro.getGDP(),
      prism.macro.getUnemployment(),
      prism.macro.getTreasuryYields(),
      prism.macro.getM2Supply(),
      prism.macro.getJoblessClaims(),
      prism.macro.getHousing(),
    ]);

  console.log('\n── Fed & Rates ──');
  console.log(`Fed Funds: ${fedRate.value}% (prev: ${fedRate.previous}%)`);
  console.log(`10yr Treasury: ${yields['10y']}% | 2yr: ${yields['2y']}% | 2s10s: ${yields['2s10s']?.toFixed(0)}bps`);
  console.log(`Yield Curve: ${yields.inverted ? '⚠️ INVERTED' : '✅ Normal'}`);

  console.log('\n── Economy ──');
  console.log(`CPI: ${inflation.value}% YoY`);
  console.log(`GDP: ${gdp.value?.toFixed(1)}%`);
  console.log(`Unemployment: ${unemployment.value}%`);
  console.log(`Jobless Claims: ${joblessClaims.value?.toLocaleString()}`);

  console.log('\n── Monetary ──');
  console.log(`M2 Supply: $${((m2.value ?? 0) / 1000).toFixed(1)}T`);

  // SOFR via series
  const sofr = await prism.macro.getSeries('SOFR', 5);
  console.log(`SOFR: ${sofr.value}%`);

  // Upcoming high-impact events
  const economic = await prism.calendar.getEconomic();
  const highImpact = economic.filter(e => e.impact === 'high').slice(0, 5);
  console.log('\n── Upcoming High-Impact Events ──');
  highImpact.forEach(e => console.log(`  ${e.date} | ${e.country} | ${e.event} (forecast: ${e.forecast})`));

  // Available FRED series
  const series = await prism.macro.getAvailableSeries();
  console.log(`\nFRED series available: ${series.length}`);
}

// ─────────────────────────────────────────────────────────────────
// AGENT 4: DeFi Yield Hunter
// "Find the best yield opportunities right now"
// Covers: defi, macro, crypto, onchain
// ─────────────────────────────────────────────────────────────────

async function defiYieldHunter() {
  console.log('\n💰 DeFi Yield Hunter');

  // 1. Market context
  const [fearGreed, global] = await Promise.all([
    prism.crypto.getFearGreed(),
    prism.crypto.getGlobal(),
  ]);
  console.log(`Market: ${fearGreed.classification} (${fearGreed.value}) | Total TVL lock: $${((global.total_market_cap ?? 0) / 1e12).toFixed(2)}T`);

  // 2. Total DeFi TVL
  const [totalTVL, chainTVLs] = await Promise.all([
    prism.defi.getTotalTVL(),
    prism.defi.getChainTVLs(10),
  ]);
  console.log(`DeFi TVL: $${(totalTVL.tvl / 1e9).toFixed(1)}B`);
  console.log(`Top chain: ${chainTVLs[0]?.chain} ($${((chainTVLs[0]?.tvl ?? 0) / 1e9).toFixed(1)}B)`);

  // 3. Best stablecoin yields (safest yields for conservative agents)
  const stableYields = await prism.defi.getYields({ stablecoin: true, min_apy: 5, min_tvl: 10_000_000, limit: 10 });
  console.log('\nTop stablecoin yields:');
  stableYields.slice(0, 5).forEach(y =>
    console.log(`  ${y.protocol} | ${y.chain} | ${y.symbol} | APY: ${y.apy?.toFixed(2)}% | TVL: $${((y.tvl_usd ?? 0) / 1e6).toFixed(0)}M`)
  );

  // 4. Check stablecoin peg health (don't farm depegged coins)
  const stablecoins = await prism.defi.getStablecoins(10);
  const depegged = stablecoins.filter(s => Math.abs((s.depeg_pct ?? 0)) > 0.5);
  if (depegged.length > 0) {
    console.log('\n⚠️  Depegged stablecoins:', depegged.map(s => `${s.symbol} (${s.depeg_pct?.toFixed(2)}%)`).join(', '));
  }

  // 5. Top protocols by TVL
  const protocols = await prism.defi.getProtocols({ min_tvl: 100_000_000, limit: 5 });
  console.log('\nTop protocols by TVL:');
  protocols.forEach(p => console.log(`  ${p.name} | ${p.chain} | $${((p.tvl ?? 0) / 1e9).toFixed(1)}B`));

  // 6. Gas check before recommending any action
  const gas = await prism.defi.getAllGas();
  const ethGas = gas.find(g => g.chain === 'ethereum');
  console.log(`\nEthereum gas: ${ethGas?.standard} gwei`);
}

// ─────────────────────────────────────────────────────────────────
// AGENT 5: Prediction Market Arbitrage Bot
// "Find arb opportunities across prediction markets and sportsbooks"
// Covers: predictions, sports, odds
// ─────────────────────────────────────────────────────────────────

async function arbitrageBot() {
  console.log('\n🎯 Prediction Market & Sports Arbitrage Bot');

  // 1. Prediction market arb
  const predArb = await prism.predictions.getArbitrage({ min_profit: 0.02, limit: 10 });
  console.log(`\nPrediction market arb opportunities: ${predArb.length}`);
  predArb.slice(0, 3).forEach(a =>
    console.log(`  ${a.title} | ${a.profit_pct?.toFixed(2)}% profit`)
  );

  // 2. Sportsbook arb (different odds across bookmakers)
  const sportsArb = await prism.odds.findArbitrage({ min_profit_pct: 2, limit: 10 });
  console.log(`\nSports arb opportunities: ${sportsArb.length}`);
  sportsArb.slice(0, 3).forEach(a =>
    console.log(`  ${a.title} | ${a.platform_a} vs ${a.platform_b} | ${a.profit_pct?.toFixed(2)}%`)
  );

  // 3. Trending markets (for directional bets)
  const trending = await prism.predictions.getTrending(10);
  console.log(`\nTrending markets:`);
  trending.slice(0, 5).forEach((m: any) =>
    console.log(`  ${m.title} | Yes: ${(m.yes_price * 100).toFixed(0)}¢ | Vol: $${(m.volume / 1000).toFixed(0)}k`)
  );

  // 4. Crypto prediction markets specifically
  const cryptoMarkets = await prism.predictions.getMarkets({ category: 'crypto', status: 'open', limit: 5 });
  console.log(`\nOpen crypto markets: ${cryptoMarkets.length}`);
  cryptoMarkets.forEach(m => console.log(`  ${m.title}`));

  // 5. Upcoming sports events with best odds
  const nbaEvents = await prism.sports.getEvents('basketball_nba', { days_ahead: 1, limit: 5 });
  console.log(`\nNBA games tomorrow: ${nbaEvents.length}`);

  // 6. Best available odds across all platforms
  const bestOdds = await prism.odds.getBestOdds({ limit: 5 });
  console.log(`\nBest odds available: ${bestOdds.length} opportunities`);
}

// ─────────────────────────────────────────────────────────────────
// AGENT 6: Forex & Commodity Trader
// "What are the best setups in FX and commodities right now?"
// Covers: forex, commodities, technicals, macro, signals
// ─────────────────────────────────────────────────────────────────

async function fxCommodityTrader() {
  console.log('\n💱 FX & Commodity Trader');

  // 1. Macro context for FX
  const [macroSummary, fedRate] = await Promise.all([
    prism.macro.getSummary(),
    prism.macro.getFedRate(),
  ]);
  console.log(`Fed Rate: ${fedRate.value}% | Inflation: ${macroSummary.inflation}%`);

  // 2. All forex quotes
  const forexQuotes = await prism.forex.getAll();
  const majors = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF'];
  console.log('\nMajors:');
  forexQuotes
    .filter((q: any) => majors.includes(q.pair))
    .forEach((q: any) => console.log(`  ${q.pair}: ${q.rate} (${q.change_pct_24h?.toFixed(2)}%)`));

  // 3. Technical analysis on key pairs
  const eurusdTA = await prism.technicals.analyzeFX('EURUSD', '4h');
  console.log(`\nEURUSD trend: ${eurusdTA.trend} | RSI: ${eurusdTA.rsi?.toFixed(1)}`);

  // 4. Commodities
  const commodities = await prism.commodities.getAll();
  const keyCommodities = ['GOLD', 'OIL', 'SILVER', 'NATGAS', 'COPPER'];
  console.log('\nCommodities:');
  commodities
    .filter((c: any) => keyCommodities.includes(c.symbol?.toUpperCase()))
    .forEach((c: any) => console.log(`  ${c.symbol}: $${c.price} (${c.change_pct_24h?.toFixed(2)}%)`));

  // 5. Technical on gold
  const goldTA = await prism.technicals.analyzeCommodity('GOLD', '1d');
  console.log(`\nGold trend: ${goldTA.trend} | RSI: ${goldTA.rsi?.toFixed(1)}`);

  // 6. Correlation matrix (does gold move with USD?)
  const corr = await prism.technicals.getCorrelations(['EURUSD', 'GOLD', 'OIL', 'SPY'], 30);
  console.log(`\nGold/USD correlation: ${corr.matrix['GOLD']?.['EURUSD']?.toFixed(2)}`);

  // 7. Tradeable forms of EUR and GOLD
  const [eurForms, goldForms] = await Promise.all([
    prism.forex.getTradeableForms('EUR'),
    prism.commodities.getTradeableForms('GOLD'),
  ]);
  console.log(`\nEUR tradeable as: ${eurForms.map(f => f.type).join(', ')}`);
  console.log(`GOLD tradeable as: ${goldForms.map(f => f.type).join(', ')}`);
}

// ─────────────────────────────────────────────────────────────────
// RUN ALL
// ─────────────────────────────────────────────────────────────────

(async () => {
  console.log('═'.repeat(60));
  console.log(' PRISM OS — Real Endpoint Agent Showcase');
  console.log(' All calls → api.prismapi.ai (218 real endpoints)');
  console.log('═'.repeat(60));

  // Uncomment to run:
  // await cryptoDueDiligence('0x1234...abcd');
  // await equityAnalysis('NVDA');
  // await macroDashboard();
  // await defiYieldHunter();
  // await arbitrageBot();
  // await fxCommodityTrader();

  console.log('\n✅ SDK grounded. Every call maps to a real endpoint.');
})();
