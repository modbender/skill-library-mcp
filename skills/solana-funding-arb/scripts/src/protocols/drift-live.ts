/**
 * Drift Protocol - Live SDK Integration
 * 
 * Real-time funding rates from Drift using official SDK
 * https://drift.trade
 */

import { Connection, PublicKey } from '@solana/web3.js';
import { 
  DriftClient, 
  PerpMarkets,
  initialize,
  DriftEnv,
  MarketType,
  getMarketOrderParams,
  PositionDirection,
  BN
} from '@drift-labs/sdk';
import { logger } from '../utils/logger';

export interface DriftLiveFundingRate {
  market: string;
  marketIndex: number;
  fundingRate: number;
  fundingRateApy: number;
  longPayShort: boolean;
  oraclePrice: number;
  markPrice: number;
  openInterest: number;
}

export class DriftLive {
  name = 'drift-live';
  private connection: Connection;
  private driftClient: DriftClient | null = null;
  private initialized = false;
  private env: DriftEnv;

  constructor(rpcUrl: string, env: DriftEnv = 'mainnet-beta') {
    this.connection = new Connection(rpcUrl, 'confirmed');
    this.env = env;
  }

  async initialize(): Promise<void> {
    if (this.initialized) return;
    
    try {
      // Initialize SDK config
      const sdkConfig = initialize({ env: this.env });
      
      // Create read-only client (no wallet needed for reading)
      this.driftClient = new DriftClient({
        connection: this.connection,
        wallet: {
          publicKey: PublicKey.default,
          signTransaction: async (tx) => tx,
          signAllTransactions: async (txs) => txs,
        },
        env: this.env,
      });
      
      await this.driftClient.subscribe();
      this.initialized = true;
      logger.info('Drift SDK initialized');
    } catch (error: any) {
      logger.error(`Drift init error: ${error.message}`);
      throw error;
    }
  }

  async getFundingRates(): Promise<DriftLiveFundingRate[]> {
    try {
      if (!this.initialized) {
        await this.initialize();
      }
      
      if (!this.driftClient) {
        throw new Error('Drift client not initialized');
      }

      const perpMarkets = this.driftClient.getPerpMarketAccounts();
      const fundingRates: DriftLiveFundingRate[] = [];

      for (const market of perpMarkets) {
        const marketIndex = market.marketIndex;
        const marketName = PerpMarkets[this.env]?.find(m => m.marketIndex === marketIndex)?.symbol || `PERP-${marketIndex}`;
        
        // Get funding rate (already per hour on Drift)
        const lastFundingRate = market.amm.lastFundingRate.toNumber() / 1e9;
        const fundingRateApy = lastFundingRate * 24 * 365 * 100;
        
        // Oracle and mark prices
        const oraclePrice = market.amm.historicalOracleData.lastOraclePrice.toNumber() / 1e6;
        const markPrice = market.amm.lastMarkPriceTwap.toNumber() / 1e6;
        
        // Open interest
        const openInterest = market.amm.baseAssetAmountWithAmm.abs().toNumber() / 1e9 * oraclePrice;

        fundingRates.push({
          market: marketName,
          marketIndex,
          fundingRate: lastFundingRate,
          fundingRateApy,
          longPayShort: lastFundingRate > 0,
          oraclePrice,
          markPrice,
          openInterest
        });
      }

      // Sort by APY
      fundingRates.sort((a, b) => Math.abs(b.fundingRateApy) - Math.abs(a.fundingRateApy));
      
      return fundingRates;
    } catch (error: any) {
      logger.error(`Drift funding rates error: ${error.message}`);
      return [];
    }
  }

  async disconnect(): Promise<void> {
    if (this.driftClient) {
      await this.driftClient.unsubscribe();
      this.initialized = false;
    }
  }
}
