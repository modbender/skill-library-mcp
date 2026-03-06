/**
 * Mango Markets v4 - Live SDK Integration
 * 
 * Real-time funding rates from Mango using official SDK
 * https://mango.markets
 */

import { Connection, PublicKey } from '@solana/web3.js';
import { MangoClient, MANGO_V4_ID } from '@blockworks-foundation/mango-v4';
import { logger } from '../utils/logger';

export interface MangoLiveFundingRate {
  market: string;
  fundingRate: number;
  fundingRateApy: number;
  longPayShort: boolean;
  price: number;
  openInterest: number;
}

export class MangoLive {
  name = 'mango-live';
  private connection: Connection;
  private client: MangoClient | null = null;
  private initialized = false;

  constructor(rpcUrl: string) {
    this.connection = new Connection(rpcUrl, 'confirmed');
  }

  async initialize(): Promise<void> {
    if (this.initialized) return;
    
    try {
      this.client = MangoClient.connect(
        this.connection,
        'mainnet-beta',
        MANGO_V4_ID['mainnet-beta']
      );
      this.initialized = true;
      logger.info('Mango SDK initialized');
    } catch (error: any) {
      logger.error(`Mango init error: ${error.message}`);
      throw error;
    }
  }

  async getFundingRates(): Promise<MangoLiveFundingRate[]> {
    try {
      if (!this.initialized) {
        await this.initialize();
      }
      
      if (!this.client) {
        throw new Error('Mango client not initialized');
      }

      const group = await this.client.getGroup(
        new PublicKey('78b8f4cGCwmZ9ysPFMWLaLTkkaYnUjwMJYStWe5RBER')
      );
      
      const fundingRates: MangoLiveFundingRate[] = [];
      
      for (const perpMarket of group.perpMarketsMapByMarketIndex.values()) {
        const fundingRate = perpMarket.getInstantaneousFundingRateUi();
        const fundingRateApy = fundingRate * 24 * 365 * 100;
        const price = perpMarket.uiPrice;
        
        fundingRates.push({
          market: `MANGO:${perpMarket.name}`,
          fundingRate: fundingRate / 100,
          fundingRateApy,
          longPayShort: fundingRate > 0,
          price,
          openInterest: perpMarket.openInterest.toNumber() * price
        });
      }

      fundingRates.sort((a, b) => Math.abs(b.fundingRateApy) - Math.abs(a.fundingRateApy));
      
      return fundingRates;
    } catch (error: any) {
      logger.error(`Mango funding rates error: ${error.message}`);
      return [];
    }
  }
}
