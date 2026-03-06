/**
 * HTTP Aggregator - Simple funding rate comparison
 * Uses only HTTP APIs (no SDK complications)
 */

import axios from 'axios';

interface FundingRate {
  exchange: string;
  symbol: string;
  price: number;
  fundingRate: number;  // As decimal (e.g., 0.0001 = 0.01%)
  fundingRateApy: number;
  nextFundingTime?: number;
  longPayShort: boolean;
}

interface ArbitrageOpportunity {
  symbol: string;
  dexRate: FundingRate;
  cexRate: FundingRate;
  spreadApy: number;  // APY difference
  direction: 'long_dex_short_cex' | 'long_cex_short_dex';
  estimatedApy: number;
}

// Drift precision constants
const FUNDING_RATE_PRECISION = 1e9;
const PRICE_PRECISION = 1e6;

export class HttpAggregator {
  private markets = ['SOL', 'BTC', 'ETH'];
  
  async getDriftFunding(): Promise<FundingRate[]> {
    const rates: FundingRate[] = [];
    
    for (const market of this.markets) {
      try {
        const response = await axios.get(
          `https://data.api.drift.trade/fundingRates?marketName=${market}-PERP`
        );
        
        const latest = response.data.fundingRates.slice(-1)[0];
        if (!latest) continue;
        
        // Funding rate is in quote asset per base unit, normalized by FUNDING_RATE_PRECISION
        // Convert to percentage: (fundingRate / precision) / price * 100
        const price = Number(latest.oraclePriceTwap) / PRICE_PRECISION;
        const rawRate = Number(latest.fundingRate) / FUNDING_RATE_PRECISION;
        const hourlyRatePct = (rawRate / price) * 100;  // Hourly rate as percentage
        const apy = hourlyRatePct * 24 * 365;  // Convert to APY %
        
        rates.push({
          exchange: 'Drift',
          symbol: market,
          price,
          fundingRate: hourlyRatePct / 100,  // As decimal
          fundingRateApy: apy,
          longPayShort: rawRate > 0,
        });
      } catch (e) {
        console.error(`Failed to fetch Drift ${market}:`, e);
      }
    }
    
    return rates;
  }
  
  async getBinanceFunding(): Promise<FundingRate[]> {
    const rates: FundingRate[] = [];
    
    for (const market of this.markets) {
      try {
        const symbol = `${market}USDT`;
        
        // Get funding rate
        const fundingResponse = await axios.get(
          `https://fapi.binance.com/fapi/v1/fundingRate?symbol=${symbol}&limit=1`
        );
        
        // Get current price
        const priceResponse = await axios.get(
          `https://fapi.binance.com/fapi/v1/ticker/price?symbol=${symbol}`
        );
        
        const funding = fundingResponse.data[0];
        const price = parseFloat(priceResponse.data.price);
        
        // Binance funding is per 8 hours
        const eightHourRate = parseFloat(funding.fundingRate);
        const hourlyRate = eightHourRate / 8;
        const apy = eightHourRate * 3 * 365 * 100;  // 3x per day * 365 days
        
        rates.push({
          exchange: 'Binance',
          symbol: market,
          price,
          fundingRate: hourlyRate,
          fundingRateApy: apy,
          nextFundingTime: funding.fundingTime,
          longPayShort: eightHourRate > 0,
        });
      } catch (e) {
        console.error(`Failed to fetch Binance ${market}:`, e);
      }
    }
    
    return rates;
  }
  
  async findArbitrageOpportunities(minSpreadApy: number = 5): Promise<ArbitrageOpportunity[]> {
    const [driftRates, binanceRates] = await Promise.all([
      this.getDriftFunding(),
      this.getBinanceFunding(),
    ]);
    
    const opportunities: ArbitrageOpportunity[] = [];
    
    for (const dex of driftRates) {
      const cex = binanceRates.find(r => r.symbol === dex.symbol);
      if (!cex) continue;
      
      const spreadApy = Math.abs(dex.fundingRateApy - cex.fundingRateApy);
      
      if (spreadApy >= minSpreadApy) {
        // Determine optimal direction
        // If DEX rate > CEX rate: Short DEX, Long CEX (receive high rate, pay low rate)
        // If CEX rate > DEX rate: Short CEX, Long DEX
        const direction = dex.fundingRateApy > cex.fundingRateApy
          ? 'long_cex_short_dex' as const
          : 'long_dex_short_cex' as const;
        
        // Estimated APY after funding payments
        // When long_cex_short_dex: receive DEX short, pay CEX long
        // When long_dex_short_cex: receive CEX short, pay DEX long
        const estimatedApy = direction === 'long_cex_short_dex'
          ? dex.fundingRateApy - cex.fundingRateApy  // Receive DEX short funding, pay CEX long
          : cex.fundingRateApy - dex.fundingRateApy;
        
        opportunities.push({
          symbol: dex.symbol,
          dexRate: dex,
          cexRate: cex,
          spreadApy,
          direction,
          estimatedApy: Math.abs(estimatedApy),
        });
      }
    }
    
    return opportunities.sort((a, b) => b.spreadApy - a.spreadApy);
  }
  
  async printSummary(): Promise<void> {
    console.log('\n' + '='.repeat(80));
    console.log('📊 FUNDING RATE COMPARISON: DRIFT vs BINANCE');
    console.log('='.repeat(80));
    
    const [driftRates, binanceRates] = await Promise.all([
      this.getDriftFunding(),
      this.getBinanceFunding(),
    ]);
    
    console.log('\n📈 CURRENT RATES:\n');
    console.log('Symbol     | Drift APY      | Binance APY    | Spread     | Direction');
    console.log('-'.repeat(80));
    
    for (const dex of driftRates) {
      const cex = binanceRates.find(r => r.symbol === dex.symbol);
      if (!cex) continue;
      
      const spread = Math.abs(dex.fundingRateApy - cex.fundingRateApy);
      const dexDir = dex.longPayShort ? '🔴 L→S' : '🟢 S→L';
      const cexDir = cex.longPayShort ? '🔴 L→S' : '🟢 S→L';
      
      console.log(
        `${dex.symbol.padEnd(10)} | ` +
        `${dex.fundingRateApy.toFixed(2).padStart(8)}% ${dexDir} | ` +
        `${cex.fundingRateApy.toFixed(2).padStart(8)}% ${cexDir} | ` +
        `${spread.toFixed(2).padStart(6)}% | ` +
        (dex.fundingRateApy > cex.fundingRateApy ? 'Short DEX' : 'Long DEX')
      );
    }
    
    console.log('\n🎯 ARBITRAGE OPPORTUNITIES (>5% APY spread):\n');
    
    const opps = await this.findArbitrageOpportunities(5);
    
    if (opps.length === 0) {
      console.log('No significant opportunities found.');
    } else {
      for (const opp of opps) {
        console.log(`${opp.symbol}: ${opp.spreadApy.toFixed(2)}% spread`);
        console.log(`  Strategy: ${opp.direction.replace(/_/g, ' ')}`);
        console.log(`  Est. APY: ${opp.estimatedApy.toFixed(2)}%\n`);
      }
    }
    
    console.log('='.repeat(80));
    console.log(`Last updated: ${new Date().toISOString()}`);
  }
}

// CLI entrypoint
if (require.main === module) {
  const aggregator = new HttpAggregator();
  aggregator.printSummary().catch(console.error);
}
