/**
 * Drift-Only Funding Rate Aggregator
 * Uses /contracts endpoint - no SDK needed
 */

import axios from 'axios';

interface DriftContract {
  ticker_id: string;
  base_currency: string;
  last_price: string;
  funding_rate: string;
  next_funding_rate: string;
  open_interest: string;
  base_volume: string;
}

interface FundingOpportunity {
  symbol: string;
  price: number;
  fundingRate: number;  // Hourly %
  fundingApy: number;   // Annual %
  direction: 'long_pays' | 'short_pays';
  openInterest: number;
  volume24h: number;
  strategy: string;
}

export class DriftAggregator {
  private apiUrl = 'https://data.api.drift.trade';
  
  async getAllContracts(): Promise<DriftContract[]> {
    const response = await axios.get(`${this.apiUrl}/contracts`);
    return response.data.contracts.filter((c: any) => 
      c.ticker_id.endsWith('-PERP') && 
      c.funding_rate !== 'N/A' &&
      c.funding_rate !== '0'
    );
  }
  
  async getTopFundingOpportunities(minApy: number = 50): Promise<FundingOpportunity[]> {
    const contracts = await this.getAllContracts();
    
    const opportunities: FundingOpportunity[] = contracts.map(c => {
      const fundingRate = parseFloat(c.funding_rate);
      const fundingApy = fundingRate * 24 * 365 * 100;  // Convert hourly to APY %
      const price = parseFloat(c.last_price);
      const openInterest = parseFloat(c.open_interest) * price;
      const volume24h = parseFloat(c.base_volume) * price;
      
      return {
        symbol: c.ticker_id,
        price,
        fundingRate: fundingRate * 100,  // As percentage
        fundingApy,
        direction: fundingRate > 0 ? 'long_pays' : 'short_pays',
        openInterest,
        volume24h,
        strategy: fundingRate > 0 
          ? '🔴 SHORT to receive funding' 
          : '🟢 LONG to receive funding',
      };
    });
    
    // Filter by minimum APY and sort by absolute funding
    return opportunities
      .filter(o => Math.abs(o.fundingApy) >= minApy)
      .sort((a, b) => Math.abs(b.fundingApy) - Math.abs(a.fundingApy));
  }
  
  async findDeltaNeutralPairs(): Promise<any[]> {
    const opps = await this.getTopFundingOpportunities(20);
    
    const pairs: any[] = [];
    
    // Find pairs where one is positive and one is negative
    const longs = opps.filter(o => o.direction === 'short_pays');  // Go long
    const shorts = opps.filter(o => o.direction === 'long_pays');  // Go short
    
    for (const longOpp of longs.slice(0, 5)) {
      for (const shortOpp of shorts.slice(0, 5)) {
        const netApy = Math.abs(longOpp.fundingApy) + Math.abs(shortOpp.fundingApy);
        
        pairs.push({
          long: longOpp.symbol,
          short: shortOpp.symbol,
          longApy: longOpp.fundingApy,
          shortApy: shortOpp.fundingApy,
          netApy,
          strategy: `Long ${longOpp.symbol} + Short ${shortOpp.symbol}`,
        });
      }
    }
    
    return pairs.sort((a, b) => b.netApy - a.netApy).slice(0, 10);
  }
  
  async printSummary(): Promise<void> {
    console.log('\n' + '═'.repeat(80));
    console.log('⚡ DRIFT FUNDING RATE SCANNER');
    console.log('═'.repeat(80));
    
    const opps = await this.getTopFundingOpportunities(100);
    
    console.log('\n🔥 TOP FUNDING OPPORTUNITIES (>100% APY):\n');
    console.log('Symbol                | Price      | Hourly %   | APY        | Strategy');
    console.log('─'.repeat(80));
    
    for (const opp of opps.slice(0, 15)) {
      const priceStr = opp.price < 1 
        ? opp.price.toFixed(6) 
        : opp.price.toFixed(2);
      
      console.log(
        `${opp.symbol.padEnd(20)} | ` +
        `$${priceStr.padStart(9)} | ` +
        `${opp.fundingRate.toFixed(4).padStart(9)}% | ` +
        `${opp.fundingApy.toFixed(0).padStart(8)}% | ` +
        `${opp.strategy}`
      );
    }
    
    console.log('\n🎯 DELTA-NEUTRAL PAIR STRATEGIES:\n');
    
    const pairs = await this.findDeltaNeutralPairs();
    
    for (const pair of pairs.slice(0, 5)) {
      console.log(`📊 ${pair.strategy}`);
      console.log(`   Long APY: ${pair.longApy.toFixed(0)}% | Short APY: ${pair.shortApy.toFixed(0)}%`);
      console.log(`   Net APY: ${pair.netApy.toFixed(0)}%\n`);
    }
    
    console.log('═'.repeat(80));
    console.log(`Last updated: ${new Date().toISOString()}`);
    console.log('⚠️  High APY = High risk. Check liquidity before trading.');
  }
}

// CLI entrypoint
if (require.main === module) {
  const aggregator = new DriftAggregator();
  aggregator.printSummary().catch(console.error);
}
