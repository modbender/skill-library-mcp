/**
 * SolArb Funding Rate Scanner CLI
 * 
 * Scan for funding rate arbitrage opportunities.
 */

import { Connection, Keypair } from '@solana/web3.js';
import { DriftProtocol } from '../protocols/drift';
import { logger } from '../utils/logger';

const RPC_URL = process.env.SOLANA_RPC || 'https://api.mainnet-beta.solana.com';
const MIN_APY = 20; // Minimum 20% APY to show

interface Opportunity {
  market: string;
  fundingApy: number;
  strategy: string;
  dailyReturn: number;
  hourlyPayment: number;
}

async function scan() {
  console.log(`
╔══════════════════════════════════════════════════════════╗
║           SolArb Funding Rate Scanner                    ║
╠══════════════════════════════════════════════════════════╣
║  Scanning Drift Protocol for funding opportunities...    ║
╚══════════════════════════════════════════════════════════╝
  `);

  const connection = new Connection(RPC_URL, 'confirmed');
  const drift = new DriftProtocol(connection);

  try {
    // Get all funding rates
    console.log('📡 Fetching funding rates from Drift...\n');
    const rates = await drift.getFundingRates();

    if (rates.length === 0) {
      console.log('❌ No funding data available');
      return;
    }

    // Display all rates
    console.log('╔═══════════════════════════════════════════════════════════════╗');
    console.log('║                  Current Funding Rates                        ║');
    console.log('╠═══════════════════════════════════════════════════════════════╣');
    console.log('║  Market       │ Rate/hr   │ APY       │ Direction             ║');
    console.log('╠═══════════════════════════════════════════════════════════════╣');

    for (const rate of rates.slice(0, 15)) {
      const rateStr = `${(rate.fundingRate * 100).toFixed(4)}%`;
      const apyStr = `${rate.fundingRateApy > 0 ? '+' : ''}${rate.fundingRateApy.toFixed(1)}%`;
      const direction = rate.longPayShort ? 'Longs → Shorts' : 'Shorts → Longs';
      
      console.log(`║  ${rate.market.padEnd(12)} │ ${rateStr.padStart(9)} │ ${apyStr.padStart(9)} │ ${direction.padEnd(18)} ║`);
    }

    console.log('╚═══════════════════════════════════════════════════════════════╝');

    // Find opportunities
    const opportunities: Opportunity[] = [];

    for (const rate of rates) {
      if (Math.abs(rate.fundingRateApy) >= MIN_APY) {
        // Strategy: go opposite of funding payers
        const strategy = rate.longPayShort 
          ? 'SHORT perp + LONG spot'
          : 'LONG perp + SHORT spot';

        opportunities.push({
          market: rate.market,
          fundingApy: rate.fundingRateApy,
          strategy,
          dailyReturn: rate.fundingRateApy / 365,
          hourlyPayment: rate.fundingRate * 1000 // per $1000
        });
      }
    }

    console.log('\n');

    if (opportunities.length === 0) {
      console.log('═══════════════════════════════════════════════════════════════');
      console.log('                    NO OPPORTUNITIES');
      console.log('═══════════════════════════════════════════════════════════════');
      console.log(`\n❌ No markets with funding APY > ${MIN_APY}%`);
      console.log('   Market is efficient right now. Keep monitoring!\n');
    } else {
      console.log('═══════════════════════════════════════════════════════════════');
      console.log('                 🎯 ARBITRAGE OPPORTUNITIES                     ');
      console.log('═══════════════════════════════════════════════════════════════');
      
      opportunities.sort((a, b) => Math.abs(b.fundingApy) - Math.abs(a.fundingApy));

      for (const opp of opportunities) {
        const daily1k = Math.abs(opp.dailyReturn) * 10; // $1000 position
        const monthly1k = daily1k * 30;

        console.log(`\n   📊 ${opp.market}`);
        console.log(`   ├─ Strategy: ${opp.strategy}`);
        console.log(`   ├─ APY: ${opp.fundingApy > 0 ? '+' : ''}${opp.fundingApy.toFixed(1)}%`);
        console.log(`   ├─ Daily: ~${opp.dailyReturn.toFixed(3)}%`);
        console.log(`   └─ Returns on $1000:`);
        console.log(`      • Hourly: $${Math.abs(opp.hourlyPayment).toFixed(4)}`);
        console.log(`      • Daily:  $${daily1k.toFixed(2)}`);
        console.log(`      • Monthly: $${monthly1k.toFixed(2)}`);
      }

      console.log('\n═══════════════════════════════════════════════════════════════');
      console.log('\n💡 To execute, run: npm start');
    }

    console.log('\n');

  } catch (error: any) {
    logger.error(`Scan failed: ${error.message}`);
    console.log('\nTip: Make sure you have a valid RPC endpoint configured.');
  }
}

scan().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
