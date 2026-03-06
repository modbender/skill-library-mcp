/**
 * Multi-DEX Funding Rate Aggregator
 * Uses CoinGecko derivatives API for Drift + Flash Trade
 * Uses Drift API directly for more detailed data
 */

import axios from 'axios';

interface FundingRate {
  exchange: string;
  symbol: string;
  price: number;
  fundingRate: number;  // Hourly rate as decimal
  fundingRateApy: number;
  openInterest: number;
  volume24h: number;
  lastUpdated: number;
}

interface ArbitrageOpportunity {
  symbol: string;
  longExchange: string;
  shortExchange: string;
  longRate: FundingRate;
  shortRate: FundingRate;
  spreadApy: number;
  netApy: number;
}

export class MultiDexAggregator {
  // CoinGecko provides data for both Drift and Flash Trade
  private cgUrl = 'https://api.coingecko.com/api/v3/derivatives';
  // Drift direct API for more accurate data
  private driftUrl = 'https://data.api.drift.trade/contracts';
  
  // Common symbols across DEXes
  private targetSymbols = ['SOL', 'BTC', 'ETH', 'WIF', 'JUP', 'JTO', 'BONK'];
  
  async getDriftRates(): Promise<FundingRate[]> {
    try {
      const response = await axios.get(this.driftUrl);
      const contracts = response.data.contracts.filter((c: any) => 
        c.ticker_id.endsWith('-PERP') && 
        c.funding_rate !== 'N/A' &&
        c.funding_rate !== '0' &&
        parseFloat(c.open_interest) > 0
      );
      
      return contracts.map((c: any) => {
        const price = parseFloat(c.last_price);
        const fundingRate = parseFloat(c.funding_rate);
        const fundingRateApy = fundingRate * 24 * 365 * 100;
        
        return {
          exchange: 'Drift',
          symbol: c.ticker_id.replace('-PERP', ''),
          price,
          fundingRate,
          fundingRateApy,
          openInterest: parseFloat(c.open_interest) * price,
          volume24h: parseFloat(c.base_volume) * price,
          lastUpdated: Date.now(),
        };
      });
    } catch (e) {
      console.error('Failed to fetch Drift rates:', e);
      return [];
    }
  }
  
  async getFlashTradeRates(): Promise<FundingRate[]> {
    try {
      const response = await axios.get(this.cgUrl);
      const flashContracts = response.data.filter((c: any) => 
        c.market === 'Flash Trade' && 
        c.funding_rate !== null
      );
      
      return flashContracts.map((c: any) => {
        // CoinGecko funding rates are already normalized
        // Flash Trade uses 1-hour funding intervals
        const fundingRate = c.funding_rate;
        const fundingRateApy = fundingRate * 24 * 365 * 100;
        
        return {
          exchange: 'Flash',
          symbol: c.symbol.split('/')[0],  // "SOL/USD" -> "SOL"
          price: parseFloat(c.price),
          fundingRate,
          fundingRateApy,
          openInterest: c.open_interest || 0,
          volume24h: c.volume_24h || 0,
          lastUpdated: c.last_traded_at * 1000,
        };
      });
    } catch (e) {
      console.error('Failed to fetch Flash Trade rates:', e);
      return [];
    }
  }
  
  async getGMTradeRates(): Promise<FundingRate[]> {
    try {
      const response = await axios.get(this.cgUrl);
      const gmContracts = response.data.filter((c: any) => 
        c.market.includes('GMTrade') && 
        c.funding_rate !== null
      );
      
      // Group by base symbol and take first (they have multiple collateral types)
      const symbolMap = new Map<string, any>();
      for (const c of gmContracts) {
        const symbol = c.symbol.split('/')[0];
        if (!symbolMap.has(symbol)) {
          symbolMap.set(symbol, c);
        }
      }
      
      return Array.from(symbolMap.values()).map((c: any) => {
        const fundingRate = c.funding_rate;
        const fundingRateApy = fundingRate * 24 * 365 * 100;
        
        return {
          exchange: 'GMTrade',
          symbol: c.symbol.split('/')[0],
          price: parseFloat(c.price),
          fundingRate,
          fundingRateApy,
          openInterest: c.open_interest || 0,
          volume24h: c.volume_24h || 0,
          lastUpdated: c.last_traded_at * 1000,
        };
      });
    } catch (e) {
      console.error('Failed to fetch GMTrade rates:', e);
      return [];
    }
  }
  
  async getAllRates(): Promise<FundingRate[]> {
    const [driftRates, flashRates, gmRates] = await Promise.all([
      this.getDriftRates(),
      this.getFlashTradeRates(),
      this.getGMTradeRates(),
    ]);
    
    return [...driftRates, ...flashRates, ...gmRates];
  }
  
  async findCrossExchangeArbitrage(minSpreadApy: number = 10): Promise<ArbitrageOpportunity[]> {
    const [driftRates, flashRates] = await Promise.all([
      this.getDriftRates(),
      this.getFlashTradeRates(),
    ]);
    
    const opportunities: ArbitrageOpportunity[] = [];
    
    // Find matching symbols
    for (const drift of driftRates) {
      const flash = flashRates.find(f => f.symbol === drift.symbol);
      if (!flash) continue;
      
      const spread = Math.abs(drift.fundingRateApy - flash.fundingRateApy);
      if (spread < minSpreadApy) continue;
      
      // Determine which exchange to long/short
      // If Drift rate > Flash rate: Short Drift (receive high), Long Flash (pay low)
      // If Flash rate > Drift rate: Short Flash (receive high), Long Drift (pay low)
      const driftHigher = drift.fundingRateApy > flash.fundingRateApy;
      
      const longExchange = driftHigher ? 'Flash' : 'Drift';
      const shortExchange = driftHigher ? 'Drift' : 'Flash';
      const longRate = driftHigher ? flash : drift;
      const shortRate = driftHigher ? drift : flash;
      
      // Net APY = what we receive from shorting - what we pay for longing
      // When we short the higher rate, we receive that rate
      // When we long the lower rate, we pay if positive, receive if negative
      const netApy = Math.abs(shortRate.fundingRateApy) - longRate.fundingRateApy;
      
      opportunities.push({
        symbol: drift.symbol,
        longExchange,
        shortExchange,
        longRate,
        shortRate,
        spreadApy: spread,
        netApy: Math.abs(netApy),
      });
    }
    
    return opportunities.sort((a, b) => b.spreadApy - a.spreadApy);
  }
  
  async printComparison(): Promise<void> {
    console.log('\n' + '═'.repeat(100));
    console.log('⚡ SOLANA DEX FUNDING RATE COMPARISON: DRIFT vs FLASH vs GMTRADE');
    console.log('═'.repeat(100));
    
    const [driftRates, flashRates, gmRates] = await Promise.all([
      this.getDriftRates(),
      this.getFlashTradeRates(),
      this.getGMTradeRates(),
    ]);
    
    // Find common symbols
    const driftSymbols = new Set(driftRates.map(r => r.symbol));
    const flashSymbols = new Set(flashRates.map(r => r.symbol));
    const commonSymbols = [...driftSymbols].filter(s => flashSymbols.has(s));
    
    console.log(`\nCommon symbols: ${commonSymbols.length}`);
    console.log('\n📊 SIDE-BY-SIDE COMPARISON:\n');
    console.log('Symbol     | Drift APY      | Flash APY      | Spread     | Arbitrage');
    console.log('─'.repeat(90));
    
    for (const symbol of commonSymbols.slice(0, 15)) {
      const drift = driftRates.find(r => r.symbol === symbol)!;
      const flash = flashRates.find(r => r.symbol === symbol)!;
      
      const spread = Math.abs(drift.fundingRateApy - flash.fundingRateApy);
      const arbDir = drift.fundingRateApy > flash.fundingRateApy 
        ? 'Long Flash, Short Drift'
        : 'Long Drift, Short Flash';
      
      const driftClass = drift.fundingRateApy > 0 ? '🔴' : '🟢';
      const flashClass = flash.fundingRateApy > 0 ? '🔴' : '🟢';
      
      console.log(
        `${symbol.padEnd(10)} | ` +
        `${driftClass} ${drift.fundingRateApy.toFixed(2).padStart(8)}% | ` +
        `${flashClass} ${flash.fundingRateApy.toFixed(2).padStart(8)}% | ` +
        `${spread.toFixed(2).padStart(8)}% | ` +
        `${spread > 10 ? '✨ ' + arbDir : '-'}`
      );
    }
    
    console.log('\n🎯 TOP CROSS-DEX ARBITRAGE OPPORTUNITIES:\n');
    
    const opps = await this.findCrossExchangeArbitrage(5);
    
    if (opps.length === 0) {
      console.log('No significant opportunities (>5% spread) found.');
    } else {
      for (const opp of opps.slice(0, 5)) {
        console.log(`${opp.symbol}: ${opp.spreadApy.toFixed(2)}% spread`);
        console.log(`  📈 Long ${opp.longExchange} @ ${opp.longRate.fundingRateApy.toFixed(2)}% APY`);
        console.log(`  📉 Short ${opp.shortExchange} @ ${opp.shortRate.fundingRateApy.toFixed(2)}% APY`);
        console.log(`  💰 Estimated Net APY: ${opp.netApy.toFixed(2)}%`);
        console.log();
      }
    }
    
    console.log('═'.repeat(100));
    console.log(`Drift: ${driftRates.length} | Flash: ${flashRates.length} | GMTrade: ${gmRates.length} markets`);
    console.log(`Last updated: ${new Date().toISOString()}`);
  }
}

// CLI
if (require.main === module) {
  const agg = new MultiDexAggregator();
  agg.printComparison().catch(console.error);
}
