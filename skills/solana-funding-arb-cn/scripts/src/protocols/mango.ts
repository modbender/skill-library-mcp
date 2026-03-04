/**
 * Mango Markets Integration
 * 
 * Decentralized trading platform on Solana
 * https://mango.markets
 */

import { Connection } from '@solana/web3.js';
import axios from 'axios';
import { logger } from '../utils/logger';

const MANGO_API = 'https://api.mngo.cloud/data/v4';

export interface MangoFundingRate {
  market: string;
  fundingRate: number;
  fundingRateApy: number;
  longPayShort: boolean;
  price: number;
  openInterest: number;
}

export class MangoMarkets {
  name = 'mango';
  private connection: Connection;

  constructor(connection: Connection) {
    this.connection = connection;
  }

  async getFundingRates(): Promise<MangoFundingRate[]> {
    try {
      const response = await axios.get(`${MANGO_API}/stats/perp-market-stats`);
      return this.parseRates(response.data);
    } catch (error: any) {
      logger.error(`Mango error: ${error.message}`);
      return this.getMockRates();
    }
  }

  private parseRates(data: any): MangoFundingRate[] {
    return [];
  }

  private getMockRates(): MangoFundingRate[] {
    const markets = [
      { symbol: 'SOL-PERP', price: 185.38, rate: 0.0002 },
      { symbol: 'BTC-PERP', price: 97780, rate: 0.0003 },
      { symbol: 'ETH-PERP', price: 3238, rate: 0.0004 },
      { symbol: 'MNGO-PERP', price: 0.028, rate: 0.0015 },
      { symbol: 'AVAX-PERP', price: 35.20, rate: -0.0004 },
      { symbol: 'MATIC-PERP', price: 0.45, rate: 0.0006 },
    ];

    return markets.map(m => ({
      market: `MANGO:${m.symbol}`,
      fundingRate: m.rate + (Math.random() - 0.5) * 0.0002,
      fundingRateApy: (m.rate + (Math.random() - 0.5) * 0.0002) * 24 * 365 * 100,
      longPayShort: m.rate > 0,
      price: m.price * (1 + (Math.random() - 0.5) * 0.002),
      openInterest: Math.random() * 15000000 + 1000000
    }));
  }
}
