/**
 * PRISM OS — Example Agent: Yield Optimizer
 *
 * This is what a real agent using PRISM OS looks like.
 * It: scans yields → risk-checks → moves capital to best opportunity
 *
 * Run: npx ts-node examples/yield-optimizer-agent.ts
 */

import PrismOS from '../src/index';

const prism = new PrismOS({
  apiKey: process.env.PRISM_API_KEY ?? 'prism_demo_key',
  environment: 'mock',
  cache: { enabled: true, ttl: 30 },
});

// ─────────────────────────────────────────────
// YIELD OPTIMIZER AGENT
// ─────────────────────────────────────────────

interface YieldOpportunity {
  protocol: string;
  asset: string;
  apy: number;
  tvl: number;
  risk: 'low' | 'medium' | 'high';
  type: string;
}

async function yieldOptimizerAgent(
  walletAddress: string,
  minApy: number = 8,
  maxRiskScore: number = 40
): Promise<void> {
  console.log('\n🔮 PRISM OS — Yield Optimizer Agent\n');
  console.log(`Wallet: ${walletAddress}`);
  console.log(`Target: APY > ${minApy}%, Risk < ${maxRiskScore}/100\n`);

  // ─── STEP 1: SEE — Gather intelligence ───

  console.log('📊 [See] Fetching market context...');
  const [globalMetrics, fearGreed] = await Promise.all([
    prism.market.getGlobalMetrics(),
    prism.market.getFearGreedIndex(),
  ]);

  console.log(`  Total DeFi TVL: $${(globalMetrics.defiTVL / 1e9).toFixed(1)}B`);
  console.log(`  Market Sentiment: ${fearGreed.label} (${fearGreed.value}/100)`);

  // ─── STEP 2: SEE — Get current positions ───

  console.log('\n💼 [See] Scanning current portfolio...');

  // Resolve assets we care about
  const assets = await prism.assets.batchResolve(['ETH', 'USDC', 'SOL', 'stETH']);
  console.log(`  Resolved ${assets.filter((a) => a.prismId).length}/${assets.length} assets`);

  // Get ETH price
  const ethPrice = await prism.market.getPrice('ETH');
  console.log(`  ETH: $${ethPrice.price.toLocaleString()} (${ethPrice.change24h >= 0 ? '+' : ''}${ethPrice.change24h?.toFixed(2)}% 24h)`);

  // ─── STEP 3: SEE — Find best yields for USDC ───

  console.log('\n🌾 [See] Scanning yield opportunities for USDC...');
  const usdcYields = await prism.assets.getRelatedYields('prism:ethereum:usdc');

  console.log(`  Found ${usdcYields.length} yield opportunities`);

  // Filter by our thresholds
  const viableYields = usdcYields
    .filter((y) => y.apy >= minApy && y.risk !== 'high')
    .sort((a, b) => b.apy - a.apy);

  console.log(`  Viable opportunities (APY ≥ ${minApy}%, not high risk): ${viableYields.length}`);

  // ─── STEP 4: THINK — Risk check the top opportunities ───

  console.log('\n⚠️  [Think] Risk-checking top opportunities...');

  const approvedOpportunities: Array<YieldOpportunity & { riskScore: number }> = [];

  for (const yieldOpp of viableYields.slice(0, 5)) {
    process.stdout.write(`  Checking ${yieldOpp.protocol} (${yieldOpp.apy.toFixed(1)}% APY)... `);

    try {
      const counterpartyRisk = await prism.risk.getCounterpartyRisk(yieldOpp.protocol);

      if (counterpartyRisk.score <= maxRiskScore) {
        console.log(`✅ PASS (risk: ${counterpartyRisk.score}/100)`);
        approvedOpportunities.push({ ...yieldOpp, riskScore: counterpartyRisk.score });
      } else {
        console.log(`❌ FAIL (risk: ${counterpartyRisk.score}/100 — too high)`);
      }
    } catch {
      console.log(`⚠️  SKIP (risk check unavailable)`);
    }
  }

  if (approvedOpportunities.length === 0) {
    console.log('\n⛔ No opportunities passed risk checks. Holding USDC.');
    return;
  }

  // ─── STEP 5: THINK — Select best opportunity ───

  const best = approvedOpportunities[0];
  console.log(`\n🎯 [Think] Best opportunity identified:`);
  console.log(`  Protocol: ${best.protocol}`);
  console.log(`  APY: ${best.apy.toFixed(2)}%`);
  console.log(`  TVL: $${(best.tvl / 1e6).toFixed(1)}M`);
  console.log(`  Risk Score: ${best.riskScore}/100`);
  console.log(`  Type: ${best.type}`);

  // ─── STEP 6: THINK — Check prediction markets for macro risk ───

  console.log('\n🔮 [Think] Checking prediction market signals...');
  const cryptoMarkets = await prism.predictions.getMarkets({
    category: 'crypto',
    status: 'open',
    minVolume: 100000,
  });

  const bearishMarkets = cryptoMarkets.filter((m) => m.yesPrice > 0.6 &&
    (m.title.toLowerCase().includes('crash') || m.title.toLowerCase().includes('bear'))
  );

  if (bearishMarkets.length > 0) {
    console.log(`  ⚠️  ${bearishMarkets.length} bearish signal(s) in prediction markets`);
    console.log(`  Reducing position size by 50%`);
  } else {
    console.log(`  ✅ No major bearish signals detected`);
  }

  // ─── STEP 7: ACT — Dry run first ───

  const positionSize = bearishMarkets.length > 0 ? '500' : '1000';

  console.log(`\n🔍 [Act] Simulating execution (amount: $${positionSize} USDC)...`);

  const swapSimulation = await prism.dex.simulateSwap({
    fromQuery: 'USDC',
    toQuery: best.asset,
    amount: positionSize,
    amountIsHuman: true,
    chain: best.chain as any ?? 'ethereum',
  });

  console.log(`  Will succeed: ${swapSimulation.willSucceed ? '✅' : '❌'}`);
  console.log(`  Expected output: ${swapSimulation.expectedOutput}`);
  console.log(`  Price impact: ${(swapSimulation.priceImpact * 100).toFixed(3)}%`);
  console.log(`  Gas estimate: $${swapSimulation.gasEstimate}`);

  if (swapSimulation.warnings.length > 0) {
    console.log(`  ⚠️  Warnings: ${swapSimulation.warnings.join(', ')}`);
  }

  // ─── STEP 8: ACT — Execute (demo: just logs) ───

  if (!swapSimulation.willSucceed) {
    console.log('\n❌ Simulation failed. Aborting.');
    return;
  }

  console.log('\n⚡ [Act] Ready for execution...');
  console.log(`  (In production: prism.execute.batch([swap, deposit_to_${best.protocol}]))`);

  // Production batch example:
  /*
  const result = await prism.execute.batch([
    {
      id: 'swap_usdc_to_target',
      module: 'dex',
      method: 'executeSwap',
      params: { fromQuery: 'USDC', toQuery: best.asset, amount: positionSize, chain: 'ethereum' }
    },
    {
      id: 'deposit_to_protocol',
      module: 'defi',
      method: 'deposit',
      params: { protocol: best.protocol, asset: best.asset, amount: 'from:swap_usdc_to_target' },
      dependsOn: ['swap_usdc_to_target']
    },
    {
      id: 'set_exit_alert',
      module: 'risk',
      method: 'watchProtocol',
      params: { slug: best.protocol, config: { webhookUrl: process.env.WEBHOOK_URL } },
      dependsOn: ['deposit_to_protocol']
    }
  ])
  */

  // ─── STEP 9: MONITOR — Set up alerts ───

  console.log('\n🔔 [Monitor] Setting up alerts...');
  const watchResult = await prism.risk.watchProtocol(best.protocol, {
    webhookUrl: process.env.WEBHOOK_URL ?? 'https://my-agent.example.com/alerts',
    liquidityDropThreshold: 0.2,
    channels: ['webhook'],
  });
  console.log(`  Alert set: ${watchResult.watchId} (${watchResult.status})`);

  // ─── SUMMARY ───

  console.log('\n' + '─'.repeat(50));
  console.log('✅ AGENT EXECUTION SUMMARY');
  console.log('─'.repeat(50));
  console.log(`Opportunity: ${best.protocol} @ ${best.apy.toFixed(2)}% APY`);
  console.log(`Position Size: $${positionSize} USDC`);
  console.log(`Risk Score: ${best.riskScore}/100`);
  console.log(`Macro Sentiment: ${fearGreed.label}`);
  console.log(`Alerts: Active`);
  console.log('─'.repeat(50) + '\n');
}

// ─────────────────────────────────────────────
// PREDICTION MARKET TRADING AGENT
// ─────────────────────────────────────────────

async function predictionMarketAgent(targetAsset: string): Promise<void> {
  console.log('\n🎲 PRISM OS — Prediction Market Alpha Agent\n');

  // 1. Find all prediction markets for target asset
  const markets = await prism.predictions.getMarketsByAsset(targetAsset);
  console.log(`Found ${markets.length} markets for ${targetAsset}`);

  // 2. Find implied move from prediction markets
  const impliedMove = await prism.predictions.getImpliedMove(targetAsset);
  console.log(`\nImplied Move:`);
  console.log(`  Upside: +${impliedMove.impliedUpside.toFixed(1)}%`);
  console.log(`  Downside: -${impliedMove.impliedDownside.toFixed(1)}%`);

  // 3. Check for cross-platform arb
  const arb = await prism.predictions.getArbitrageOpps();
  if (arb.length > 0) {
    console.log(`\n💰 Arb opportunities found:`);
    arb.slice(0, 3).forEach((a) => {
      console.log(`  ${a.event}: ${a.arbPct.toFixed(2)}% arb between ${a.venue1} and ${a.venue2}`);
    });
  }

  // 4. Get AI strategy recommendation for top market
  if (markets.length > 0) {
    const topMarket = markets[0];
    const strategy = await prism.predictions.agentBet(topMarket.marketId, 'sharp_follow');
    console.log(`\n🤖 Agent Bet Strategy for "${topMarket.title}":`);
    console.log(`  Side: ${strategy.recommendedSide.toUpperCase()}`);
    console.log(`  Size: $${strategy.recommendedSize}`);
    console.log(`  Expected Value: ${strategy.expectedValue.toFixed(3)}`);
    console.log(`  Reasoning: ${strategy.reasoning.join(', ')}`);
  }
}

// ─────────────────────────────────────────────
// RUN
// ─────────────────────────────────────────────

(async () => {
  try {
    // Check SDK health
    const { status, latencyMs } = await prism.ping();
    console.log(`PRISM OS status: ${status} (${latencyMs}ms)`);

    // Print tool manifest (for OpenClaw registration)
    const manifest = prism.getToolManifest();
    console.log(`Tool manifest: ${manifest.tools.length} tools registered`);

    // Run agents
    await yieldOptimizerAgent('0xYourWalletHere', 8, 40);
    await predictionMarketAgent('ETH');

  } catch (err) {
    console.error('Agent error:', err);
    process.exit(1);
  }
})();
