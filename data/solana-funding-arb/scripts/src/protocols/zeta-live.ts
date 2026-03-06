/**
 * Zeta Markets - Live SDK Integration
 * 
 * Real-time funding rates from Zeta using official SDK
 * https://zeta.markets
 */

import { Connection } from '@solana/web3.js';
import { Exchange, Network, utils } from '@zetamarkets/sdk';
import { logger } from '../utils/logger';

export interface ZetaLiveFundingRate {
  market: string;
  fundingRate: number;
  fundingRateApy: number;
  longPayShort: boolean;
  price: number;
  openInterest: number;
}

export class ZetaLive {
  name = 'zeta-live';
  private connection: Connection;
  private initialized = false;

  constructor(rpcUrl: string) {
    this.connection = new Connection(rpcUrl, 'confirmed');
  }

  async initialize(): Promise<void> {
    if (this.initialized) return;
    
    try {
      await Exchange.load({
        network: Network.MAINNET,
        connection: this.connection,
        opts: utils.defaultCommitment(),
        loadFromStore: true,
      });
      this.initialized = true;
      logger.info('Zeta SDK initialized');
    } catch (error: any) {
      logger.error(`Zeta init error: ${error.message}`);
      throw error;
    }
  }

  async getFundingRates(): Promise<ZetaLiveFundingRate[]> {
    try {
      if (!this.initialized) {
        await this.initialize();
      }

      const fundingRates: ZetaLiveFundingRate[] = [];
      const markets = Exchange.getPerpMarkets();
      
      for (const market of markets) {
        const fundingInfo = Exchange.getPerpFundingInfo(market.marketIndex);
        if (!fundingInfo) continue;
        
        const fundingRate = fundingInfo.fundingRate;
        const fundingRateApy = fundingRate * 24 * 365 * 100;
        const price = Exchange.getMarkPrice(market.marketIndex);
        
        fundingRates.push({
          market: `ZETA:${market.marketIndex}-PERP`,
          fundingRate,
          fundingRateApy,
          longPayShort: fundingRate > 0,
          price,
          openInterest: market.openInterest * price
        });
      }

      fundingRates.sort((a, b) => Math.abs(b.fundingRateApy) - Math.abs(a.fundingRateApy));
      
      return fundingRates;
    } catch (error: any) {
      logger.error(`Zeta funding rates error: ${error.message}`);
      return [];
    }
  }

  async disconnect(): Promise<void> {
    if (this.initialized) {
      await Exchange.close();
      this.initialized = false;
    }
  }
}
