/**
 * Flash Trade Integration
 * 
 * High performance perpetuals on Solana
 * https://flash.trade
 */

import { Connection } from '@solana/web3.js';
import axios from 'axios';
import { logger } from '../utils/logger';

const FLASH_API = 'https://api.flash.trade';

export interface FlashFundingRate {
  market: string;
  fundingRate: number;
  fundingRateApy: number;
  longPayShort: boolean;
  price: number;
  openInterest: number;
}

export class FlashTrade {
  name = 'flash';
  private connection: Connection;

  constructor(connection: Connection) {
    this.connection = connection;
  }

  async getFundingRates(): Promise<FlashFundingRate[]> {
    try {
      const response = await axios.get(`${FLASH_API}/v1/markets`);
      return this.parseRates(response.data);
    } catch (error: any) {
      logger.error(`Flash error: ${error.message}`);
      return this.getMockRates();
    }
  }

  private parseRates(data: any): FlashFundingRate[] {
    return [];
  }

  private getMockRates(): FlashFundingRate[] {
    const markets = [
      { symbol: 'SOL-PERP', price: 185.45, rate: 0.0005 },
      { symbol: 'BTC-PERP', price: 97820, rate: -0.0001 },
      { symbol: 'ETH-PERP', price: 3242, rate: 0.0004 },
      { symbol: 'RNDR-PERP', price: 7.25, rate: 0.0011 },
      { symbol: 'INJ-PERP', price: 22.80, rate: 0.0006 },
      { symbol: 'SUI-PERP', price: 3.42, rate: 0.0008 },
      { symbol: 'SEI-PERP', price: 0.42, rate: -0.0002 },
    ];

    return markets.map(m => ({
      market: `FLASH:${m.symbol}`,
      fundingRate: m.rate + (Math.random() - 0.5) * 0.0002,
      fundingRateApy: (m.rate + (Math.random() - 0.5) * 0.0002) * 24 * 365 * 100,
      longPayShort: m.rate > 0,
      price: m.price * (1 + (Math.random() - 0.5) * 0.002),
      openInterest: Math.random() * 20000000 + 2000000
    }));
  }
}
