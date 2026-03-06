/**
 * PRISM OS — Universal Finance Agent Examples
 * Every call below maps to a REAL endpoint on api.prismapi.ai
 *
 * 4 agents: Equity Analyst | Macro Trader | Multi-Asset PM | Crypto/DeFi
 */

import PrismOS from '../src/index';

const prism = new PrismOS({
  apiKey: process.env.PRISM_API_KEY ?? 'prism_demo_key',
  baseUrl: 'https://api.prismapi.ai',
});

// ─────────────────────────────────────────────
// AGENT 1: EQUITY ANALYST
// "Give me a full read on NVDA"
// Endpoints: /stocks/* + /technicals/* + /signals/* + /valuation/* + /news/*
// ─────────────────────────────────────────────

async function equityAnalystAgent(ticker: string) {
  console.log(`\n📈 Equity Analyst — ${ticker}\n`);

  // 1. Snapshot: quote + fundamentals in parallel
  const [quote, fundamentals, valuationRatios] = await Promise.all([
    prism.stocks.getQuote(ticker),
    prism.stocks.getFundamentals(ticker),
    prism.stocks.getValuationRatios(ticker),
  ]);

  console.log(`Price: $${quote.price} (${quote.change_percent > 0 ? '+' : ''}${quote.change_percent?.toFixed(2)}%)`);
  console.log(`Market Cap: $${(quote.market_cap / 1e9).toFixed(1)}B`);
  console.log(`P/E: ${valuationRatios.pe?.toFixed(1)}x | EV/EBITDA: ${valuationRatios.ev_ebitda?.toFixed(1)}x`);
  console.log(`Revenue Growth YoY: ${fundamentals.revenue_growth_yoy?.toFixed(1)}%`);
  console.log(`Net Margin: ${fundamentals.net_margin?.toFixed(1)}%`);

  // 2. Earnings history + next quarter estimate
  const earnings = await prism.stocks.getEarnings(ticker, 4);
  const beatCount = earnings.filter((e: any) => e.eps_actual > e.eps_estimate).length;
  console.log(`\nEarnings beat rate (4Q): ${beatCount}/4`);
  const latestEarnings = earnings[0];
  if (latestEarnings) {
    const surprise = ((latestEarnings.eps_actual - latestEarnings.eps_estimate) / Math.abs(latestEarnings.eps_estimate) * 100);
    console.log(`Last quarter EPS surprise: ${surprise > 0 ? '+' : ''}${surprise.toFixed(1)}%`);
  }

  // 3. Wall Street consensus
  const ratings = await prism.stocks.getAnalystRatings(ticker);
  console.log(`\nAnalyst consensus: ${ratings.consensus_rating}`);
  console.log(`Average price target: $${ratings.price_target_avg}`);
  console.log(`Buy/Hold/Sell: ${ratings.buy_count}/${ratings.hold_count}/${ratings.sell_count}`);

  // 4. Institutional + insider activity
  const [institutional, insiders] = await Promise.all([
    prism.stocks.getInstitutional(ticker),
    prism.stocks.getInsiders(ticker),
  ]);
  const instChange = institutional[0]?.shares_change;
  console.log(`\nInstitutional net change: ${instChange > 0 ? '+' : ''}${instChange?.toLocaleString()} shares`);
  const recentInsiderBuys = insiders.filter((i: any) => i.transaction_type === 'Purchase').length;
  console.log(`Insider purchases (recent): ${recentInsiderBuys}`);

  // 5. Technicals
  const [technicals, supportResistance, trend] = await Promise.all([
    prism.technicals.getFull(ticker, 'daily'),
    prism.technicals.getSupportResistance(ticker),
    prism.technicals.getTrend(ticker, 'daily'),
  ]);
  console.log(`\nTrend: ${trend.trend} | RSI: ${technicals.rsi?.toFixed(1)}`);
  console.log(`Support: $${supportResistance.support?.[0]?.price} | Resistance: $${supportResistance.resistance?.[0]?.price}`);

  // 6. Signals
  const signals = await prism.signals.getSummary({ symbols: [ticker] });
  console.log(`Signal summary: ${JSON.stringify(signals[ticker] ?? {})}`);

  // 7. DCF
  const dcf = await prism.stocks.getDCF(ticker, { growthRate: 0.15, discountRate: 0.10 });
  console.log(`\nDCF intrinsic value: $${dcf.intrinsic_value?.toFixed(0)}`);
  console.log(`Upside/downside: ${dcf.upside_pct > 0 ? '+' : ''}${dcf.upside_pct?.toFixed(1)}%`);

  // 8. News sentiment
  const news = await prism.news.getStocks(ticker, 5);
  console.log(`\nLatest news: "${news[0]?.title?.slice(0, 60)}..."`);

  // 9. Peers for context
  const peers = await prism.stocks.getPeers(ticker);
  const peersStr = peers.slice(0, 4).join(', ');
  const peerQuotes = await prism.stocks.getBatchQuotes(peers.slice(0, 4));
  console.log(`\nPeer comparison (${peersStr}):`);
  peerQuotes.forEach((pq: any) => console.log(`  ${pq.symbol}: $${pq.price} (${pq.change_percent?.toFixed(1)}%)`));
}

// ─────────────────────────────────────────────
// AGENT 2: MACRO TRADER
// "What's the US macro picture and how should I be positioned?"
// Endpoints: /macro/* + /market/* + /historical/* + /technicals/*
// ─────────────────────────────────────────────

async function macroTraderAgent() {
  console.log('\n🌍 Macro Trader Agent\n');

  // 1. Full macro summary in one call
  const summary = await prism.macro.getSummary();
  console.log('=== MACRO SNAPSHOT ===');
  console.log(`Fed Rate: ${summary.fed_rate?.value}%`);
  console.log(`CPI YoY: ${summary.inflation?.cpi_yoy}%`);
  console.log(`GDP Growth: ${summary.gdp?.growth_rate}%`);
  console.log(`Unemployment: ${summary.unemployment?.rate}%`);

  // 2. Treasury yield curve — key recession indicator
  const yields = await prism.macro.getTreasuryYields();
  const twoYear = yields.find((y: any) => y.maturity === '2Y')?.yield;
  const tenYear = yields.find((y: any) => y.maturity === '10Y')?.yield;
  const spread = (tenYear - twoYear);
  console.log(`\n2s10s Spread: ${spread > 0 ? '+' : ''}${spread?.toFixed(2)}bps`);
  console.log(`Yield curve ${spread < 0 ? '⚠️ INVERTED' : '✅ Normal'}`);

  // 3. Market sentiment
  const [fearGreed, overview] = await Promise.all([
    prism.market.getFearGreed(),
    prism.market.getOverview(),
  ]);
  console.log(`\nFear & Greed: ${fearGreed.value} (${fearGreed.classification})`);
  console.log(`S&P 500: ${overview.sp500?.value} (${overview.sp500?.change_pct?.toFixed(2)}%)`);

  // 4. Cross-asset correlations
  const correlations = await prism.market.getCorrelations(
    ['SPY', 'GLD', 'BTC', 'TLT', 'DXY'], 90
  );
  console.log(`\nCorrelation: SPY/GLD = ${correlations.matrix?.SPY?.GLD?.toFixed(2)}`);
  console.log(`Correlation: SPY/BTC = ${correlations.matrix?.SPY?.BTC?.toFixed(2)}`);
  console.log(`Correlation: SPY/TLT = ${correlations.matrix?.SPY?.TLT?.toFixed(2)}`);

  // 5. Forex — dollar strength matters for everything
  const fxQuotes = await prism.forex.getAll();
  const eurusd = fxQuotes.find((q: any) => q.symbol === 'EURUSD');
  const usdjpy = fxQuotes.find((q: any) => q.symbol === 'USDJPY');
  console.log(`\nEUR/USD: ${eurusd?.price?.toFixed(4)} (${eurusd?.change_pct?.toFixed(2)}%)`);
  console.log(`USD/JPY: ${usdjpy?.price?.toFixed(2)} (${usdjpy?.change_pct?.toFixed(2)}%)`);

  // 6. Commodities — inflation + growth signal
  const commodities = await prism.commodities.getAll();
  const gold = commodities.find((c: any) => c.symbol === 'GCUSD');
  const oil = commodities.find((c: any) => c.symbol === 'CLUSD');
  console.log(`\nGold: $${gold?.price?.toFixed(0)} (${gold?.change_pct?.toFixed(2)}%)`);
  console.log(`WTI Oil: $${oil?.price?.toFixed(2)} (${oil?.change_pct?.toFixed(2)}%)`);

  // 7. Performance comparison — how did risk assets do recently?
  const comparison = await prism.historical.compare(
    ['SPY', 'TLT', 'GLD', 'BTC'], 30
  );
  console.log('\n30-day returns:');
  Object.entries(comparison.returns ?? {}).forEach(([symbol, ret]: [string, any]) => {
    console.log(`  ${symbol}: ${ret > 0 ? '+' : ''}${ret?.toFixed(2)}%`);
  });

  // 8. Signals across macro-relevant ETFs
  const macroSignals = await prism.signals.getMomentum({
    symbols: ['SPY', 'TLT', 'GLD', 'UUP'],
  });
  console.log('\nMomentum signals:');
  macroSignals.forEach((s: any) => {
    console.log(`  ${s.symbol}: ${s.signal} (RSI: ${s.rsi?.toFixed(1)})`);
  });

  // 9. Economic calendar — what's coming?
  const today = new Date().toISOString().split('T')[0];
  const nextWeek = new Date(Date.now() + 7 * 86400 * 1000).toISOString().split('T')[0];
  const events = await prism.calendar.getEconomic(today, nextWeek);
  console.log(`\nUpcoming events (7d): ${events.length}`);
  events.slice(0, 3).forEach((e: any) => {
    console.log(`  ${e.date}: ${e.name} (impact: ${e.impact})`);
  });
}

// ─────────────────────────────────────────────
// AGENT 3: MULTI-ASSET PORTFOLIO MANAGER
// "Analyze my portfolio and show risk/return"
// Endpoints: /risk/* + /historical/* + /technicals/* + /signals/*
// ─────────────────────────────────────────────

async function portfolioManagerAgent() {
  console.log('\n💼 Multi-Asset Portfolio Manager\n');

  const portfolio = [
    { symbol: 'AAPL',  weight: 0.15, assetType: 'stock'  },
    { symbol: 'MSFT',  weight: 0.10, assetType: 'stock'  },
    { symbol: 'NVDA',  weight: 0.10, assetType: 'stock'  },
    { symbol: 'SPY',   weight: 0.20, assetType: 'etf'    },
    { symbol: 'TLT',   weight: 0.10, assetType: 'etf'    },
    { symbol: 'GLD',   weight: 0.10, assetType: 'etf'    },
    { symbol: 'BTC',   weight: 0.15, assetType: 'crypto' },
    { symbol: 'ETH',   weight: 0.10, assetType: 'crypto' },
  ];

  const symbols = portfolio.map(p => p.symbol);

  // 1. Portfolio-level risk
  const portfolioRisk = await prism.risk.analyzePortfolio(portfolio);
  console.log('Portfolio Risk:');
  console.log(`  Volatility: ${portfolioRisk.volatility?.toFixed(2)}%`);
  console.log(`  Sharpe Ratio: ${portfolioRisk.sharpe_ratio?.toFixed(2)}`);
  console.log(`  95% VaR (1d): ${portfolioRisk.var_95?.toFixed(2)}%`);
  console.log(`  Max Drawdown: ${portfolioRisk.max_drawdown?.toFixed(2)}%`);

  // 2. Cross-asset correlations (diversification check)
  const correlations = await prism.market.getCorrelations(symbols, 90);
  console.log('\nKey correlations (90d):');
  console.log(`  AAPL/MSFT: ${correlations.matrix?.AAPL?.MSFT?.toFixed(2)}`);
  console.log(`  SPY/TLT: ${correlations.matrix?.SPY?.TLT?.toFixed(2)}`);
  console.log(`  BTC/ETH: ${correlations.matrix?.BTC?.ETH?.toFixed(2)}`);
  console.log(`  SPY/BTC: ${correlations.matrix?.SPY?.BTC?.toFixed(2)}`);

  // 3. Historical returns comparison
  const returns = await prism.historical.compare(symbols, 365);
  console.log('\n1-year returns:');
  Object.entries(returns.returns ?? {}).forEach(([symbol, ret]: [string, any]) => {
    const position = portfolio.find(p => p.symbol === symbol);
    const contribution = ret * (position?.weight ?? 0);
    console.log(`  ${symbol}: ${ret > 0 ? '+' : ''}${ret?.toFixed(1)}% (contrib: ${contribution?.toFixed(2)}%)`);
  });

  // 4. Volatility per asset
  const volPromises = symbols.map(s => prism.historical.getVolatility(s, 30));
  const vols = await Promise.all(volPromises);
  console.log('\n30-day realized volatility:');
  symbols.forEach((s, i) => {
    console.log(`  ${s}: ${vols[i]?.volatility?.toFixed(1)}%`);
  });

  // 5. Signals for rebalancing cues
  const signalSummary = await prism.signals.getSummary({ symbols });
  console.log('\nSignals (rebalancing cues):');
  Object.entries(signalSummary).forEach(([symbol, signal]: [string, any]) => {
    if (signal?.action !== 'hold') {
      console.log(`  ${symbol}: ${signal?.action?.toUpperCase()} — ${signal?.reason}`);
    }
  });

  // 6. Earnings calendar risk (stocks only)
  const today = new Date().toISOString().split('T')[0];
  const nextMonth = new Date(Date.now() + 30 * 86400 * 1000).toISOString().split('T')[0];
  const earnings = await prism.calendar.getEarnings(today, nextMonth);
  const relevantEarnings = earnings.filter((e: any) =>
    ['AAPL', 'MSFT', 'NVDA'].includes(e.symbol)
  );
  console.log('\nUpcoming earnings (portfolio stocks):');
  relevantEarnings.forEach((e: any) => {
    console.log(`  ${e.symbol}: ${e.report_date} (est. EPS: ${e.eps_estimate})`);
  });
}

// ─────────────────────────────────────────────
// AGENT 4: CRYPTO + DEFI YIELD AGENT
// "Find the best yield opportunities and check whale activity"
// Endpoints: /defi/* + /dex/* + /onchain/* + /crypto/* + /social/*
// ─────────────────────────────────────────────

async function cryptoDeFiAgent() {
  console.log('\n🔮 Crypto/DeFi Agent\n');

  // 1. Market context
  const [global, fearGreed] = await Promise.all([
    prism.crypto.getGlobal(),
    prism.market.getFearGreed(),
  ]);
  console.log(`Global crypto market cap: $${(global.total_market_cap / 1e12).toFixed(2)}T`);
  console.log(`BTC dominance: ${global.btc_dominance?.toFixed(1)}%`);
  console.log(`Fear & Greed: ${fearGreed.value} (${fearGreed.classification})`);

  // 2. Best yield opportunities
  const yields = await prism.defi.getYields({
    minApy: 8,
    minTvl: 5_000_000,
    limit: 10,
  });
  console.log('\nTop yield opportunities:');
  yields.slice(0, 5).forEach((y: any) => {
    console.log(`  ${y.project} (${y.chain}): ${y.apy?.toFixed(1)}% APY — TVL $${(y.tvl / 1e6).toFixed(0)}M`);
  });

  // 3. Stablecoin yields (lower risk)
  const stableYields = await prism.defi.getYields({
    stablecoin: true,
    minApy: 5,
    limit: 5,
  });
  console.log('\nStablecoin yields:');
  stableYields.forEach((y: any) => {
    console.log(`  ${y.symbol} on ${y.project}: ${y.apy?.toFixed(1)}% APY`);
  });

  // 4. Funding rate arbitrage
  const btcFunding = await prism.defi.getFundingRatesAll('BTC');
  const ethFunding = await prism.defi.getFundingRatesAll('ETH');
  console.log('\nFunding rates:');
  btcFunding.slice(0, 3).forEach((f: any) => {
    console.log(`  BTC/${f.exchange}: ${(f.funding_rate * 100).toFixed(4)}% (${(f.funding_rate * 100 * 3 * 365).toFixed(1)}% annualized)`);
  });

  // 5. Whale movements
  const whales = await prism.onchain.getWhaleMovements({
    address: '0xdAC17F958D2ee523a2206206994597C13D831ec7', // USDT
    chain: 'eth',
    minValueUsd: 1_000_000,
    limit: 5,
  });
  console.log('\nRecent whale moves (USDT):');
  whales.slice(0, 3).forEach((w: any) => {
    console.log(`  ${w.direction}: $${(w.value_usd / 1e6).toFixed(1)}M — ${w.from?.slice(0, 8)} → ${w.to?.slice(0, 8)}`);
  });

  // 6. Social sentiment on top assets
  const [btcSentiment, ethSentiment] = await Promise.all([
    prism.social.getSentiment('BTC'),
    prism.social.getSentiment('ETH'),
  ]);
  console.log(`\nBTC sentiment: ${btcSentiment.sentiment} (score: ${btcSentiment.score})`);
  console.log(`ETH sentiment: ${ethSentiment.sentiment} (score: ${ethSentiment.score})`);

  // 7. Trending + prediction markets alignment
  const [trending, predictions] = await Promise.all([
    prism.crypto.getTrendingAll({ limit: 5 }),
    prism.predictions.getMarkets({ category: 'crypto', sort: 'volume', limit: 5 }),
  ]);
  console.log('\nTrending tokens:');
  trending.slice(0, 3).forEach((t: any) => {
    console.log(`  ${t.symbol}: ${t.source} (rank: ${t.rank})`);
  });
  console.log('\nTop crypto prediction markets:');
  predictions.slice(0, 3).forEach((p: any) => {
    console.log(`  "${p.question?.slice(0, 50)}..."`);
    console.log(`    Yes: ${(p.yes_price * 100).toFixed(0)}% | Volume: $${(p.volume / 1e3).toFixed(0)}K`);
  });

  // 8. DeFi protocol health check
  const totalTVL = await prism.defi.getTotalTVL();
  const chainTVLs = await prism.defi.getChainTVLs();
  console.log(`\nTotal DeFi TVL: $${(totalTVL.tvl / 1e9).toFixed(1)}B`);
  chainTVLs.slice(0, 3).forEach((c: any) => {
    console.log(`  ${c.name}: $${(c.tvl / 1e9).toFixed(1)}B`);
  });
}

// ─────────────────────────────────────────────
// RUN
// ─────────────────────────────────────────────

(async () => {
  try {
    console.log('═'.repeat(60));
    console.log(' PRISM OS — Real API Finance Agent Showcase');
    console.log(' All endpoints are LIVE at api.prismapi.ai');
    console.log('═'.repeat(60));

    await equityAnalystAgent('NVDA');
    await macroTraderAgent();
    await portfolioManagerAgent();
    await cryptoDeFiAgent();

    console.log('\n✅ All agents complete');
  } catch (err) {
    console.error('Error:', err);
  }
})();
