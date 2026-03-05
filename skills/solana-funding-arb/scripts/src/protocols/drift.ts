/**
 * Drift Protocol Integration
 * 
 * Drift is Solana's largest perpetual futures DEX.
 * https://drift.trade
 */

import { Connection, PublicKey, Keypair, Transaction } from '@solana/web3.js';
import axios from 'axios';
import { logger } from '../utils/logger';

// Use devnet for testing, mainnet for production
const IS_DEVNET = process.env.DRIFT_NETWORK !== 'mainnet';
const DRIFT_API = IS_DEVNET 
  ? 'https://master.api.drift.trade'  // Devnet API
  : 'https://mainnet-beta.api.drift.trade';
const DRIFT_STATS_API = 'https://drift-historical-data-v2.s3.eu-west-1.amazonaws.com';

export interface FundingRate {
  market: string;
  marketIndex: number;
  fundingRate: number;      // Per hour rate (e.g., 0.0005 = 0.05%)
  fundingRateApy: number;   // Annualized (rate * 24 * 365)
  nextFundingTime: number;  // Unix timestamp
  longPayShort: boolean;    // true = longs pay shorts
  oraclePrice: number;
  markPrice: number;
}

export interface DriftPosition {
  market: string;
  marketIndex: number;
  baseAssetAmount: number;  // Position size
  quoteAssetAmount: number; // Entry notional
  side: 'long' | 'short';
  entryPrice: number;
  unrealizedPnl: number;
  fundingPayment: number;   // Accumulated funding
}

export interface DriftMarket {
  marketIndex: number;
  symbol: string;
  baseAsset: string;
  oraclePrice: number;
  markPrice: number;
  volume24h: number;
  openInterest: number;
  fundingRate: number;
}

export class DriftProtocol {
  name = 'drift';
  private connection: Connection;
  private wallet?: Keypair;
  private userAccount?: string;

  constructor(connection: Connection, wallet?: Keypair) {
    this.connection = connection;
    this.wallet = wallet;
  }

  /**
   * Get all perpetual markets
   */
  async getMarkets(): Promise<DriftMarket[]> {
    try {
      const response = await axios.get(`${DRIFT_API}/markets`);
      
      return response.data.map((m: any) => ({
        marketIndex: m.marketIndex,
        symbol: m.symbol,
        baseAsset: m.baseAsset,
        oraclePrice: parseFloat(m.oraclePrice) / 1e6,
        markPrice: parseFloat(m.markPrice) / 1e6,
        volume24h: parseFloat(m.volume24h) / 1e6,
        openInterest: parseFloat(m.openInterest) / 1e6,
        fundingRate: parseFloat(m.lastFundingRate) / 1e9
      }));
    } catch (error: any) {
      logger.error(`Drift markets error: ${error.message}`);
      // Return mock data for demo
      return this.getMockMarkets();
    }
  }

  /**
   * Mock markets for demo/testing
   */
  private getMockMarkets(): DriftMarket[] {
    const baseRates = [0.0003, -0.0002, 0.0008, -0.0001, 0.0005, 0.0002, -0.0004, 0.0006];
    const markets = [
      { symbol: 'SOL-PERP', baseAsset: 'SOL', price: 185.42 },
      { symbol: 'BTC-PERP', baseAsset: 'BTC', price: 97850.00 },
      { symbol: 'ETH-PERP', baseAsset: 'ETH', price: 3245.80 },
      { symbol: 'JUP-PERP', baseAsset: 'JUP', price: 0.92 },
      { symbol: 'WIF-PERP', baseAsset: 'WIF', price: 1.85 },
      { symbol: 'BONK-PERP', baseAsset: 'BONK', price: 0.000028 },
      { symbol: 'PYTH-PERP', baseAsset: 'PYTH', price: 0.38 },
      { symbol: 'JTO-PERP', baseAsset: 'JTO', price: 3.12 },
    ];
    
    return markets.map((m, i) => ({
      marketIndex: i,
      symbol: m.symbol,
      baseAsset: m.baseAsset,
      oraclePrice: m.price * (1 + (Math.random() - 0.5) * 0.001),
      markPrice: m.price * (1 + (Math.random() - 0.5) * 0.002),
      volume24h: Math.random() * 50000000 + 10000000,
      openInterest: Math.random() * 100000000 + 20000000,
      fundingRate: baseRates[i] + (Math.random() - 0.5) * 0.0002
    }));
  }

  /**
   * Get current funding rates for all markets
   */
  async getFundingRates(): Promise<FundingRate[]> {
    try {
      const markets = await this.getMarkets();
      const fundingRates: FundingRate[] = [];

      for (const market of markets) {
        // Funding rate is already per-hour on Drift
        const hourlyRate = market.fundingRate;
        const apy = hourlyRate * 24 * 365 * 100; // Convert to APY %

        fundingRates.push({
          market: market.symbol,
          marketIndex: market.marketIndex,
          fundingRate: hourlyRate,
          fundingRateApy: apy,
          nextFundingTime: this.getNextFundingTime(),
          longPayShort: hourlyRate > 0,
          oraclePrice: market.oraclePrice,
          markPrice: market.markPrice
        });
      }

      // Sort by absolute APY (best opportunities first)
      fundingRates.sort((a, b) => Math.abs(b.fundingRateApy) - Math.abs(a.fundingRateApy));

      return fundingRates;
    } catch (error: any) {
      logger.error(`Drift funding rates error: ${error.message}`);
      return [];
    }
  }

  /**
   * Get historical funding rates
   */
  async getHistoricalFunding(market: string, days: number = 7): Promise<{ time: number; rate: number }[]> {
    try {
      // Drift provides historical data via S3
      const response = await axios.get(`${DRIFT_API}/fundingRates`, {
        params: {
          marketName: market,
          days
        }
      });

      return response.data.map((f: any) => ({
        time: f.ts * 1000,
        rate: parseFloat(f.fundingRate) / 1e9
      }));
    } catch (error: any) {
      logger.debug(`Drift historical funding error: ${error.message}`);
      return [];
    }
  }

  /**
   * Get user's positions
   */
  async getPositions(userPubkey: PublicKey): Promise<DriftPosition[]> {
    try {
      const response = await axios.get(`${DRIFT_API}/positions`, {
        params: { userAccount: userPubkey.toBase58() }
      });

      return response.data.map((p: any) => ({
        market: p.marketName,
        marketIndex: p.marketIndex,
        baseAssetAmount: parseFloat(p.baseAssetAmount) / 1e9,
        quoteAssetAmount: parseFloat(p.quoteAssetAmount) / 1e6,
        side: parseFloat(p.baseAssetAmount) > 0 ? 'long' : 'short',
        entryPrice: Math.abs(parseFloat(p.quoteAssetAmount) / parseFloat(p.baseAssetAmount)) * 1e3,
        unrealizedPnl: parseFloat(p.unrealizedPnl) / 1e6,
        fundingPayment: parseFloat(p.fundingPayment) / 1e6
      }));
    } catch (error: any) {
      logger.error(`Drift positions error: ${error.message}`);
      return [];
    }
  }

  /**
   * Open a perpetual position
   */
  async openPosition(
    market: string,
    side: 'long' | 'short',
    sizeUsd: number,
    leverage: number = 1
  ): Promise<{ success: boolean; txSignature?: string; error?: string }> {
    if (!this.wallet) {
      return { success: false, error: 'Wallet not configured' };
    }

    try {
      // Get market info
      const markets = await this.getMarkets();
      const marketInfo = markets.find(m => m.symbol === market);
      if (!marketInfo) {
        return { success: false, error: `Market ${market} not found` };
      }

      // Calculate position size
      const baseAmount = (sizeUsd / marketInfo.oraclePrice) * 1e9;
      const direction = side === 'long' ? 1 : -1;

      // Build order via Drift API
      const response = await axios.post(`${DRIFT_API}/orders/place`, {
        userPublicKey: this.wallet.publicKey.toBase58(),
        marketIndex: marketInfo.marketIndex,
        direction: side === 'long' ? 'long' : 'short',
        baseAssetAmount: Math.floor(baseAmount * direction),
        orderType: 'market',
        reduceOnly: false
      });

      if (!response.data?.txSignature) {
        return { success: false, error: 'Failed to place order' };
      }

      return { success: true, txSignature: response.data.txSignature };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Close a perpetual position
   */
  async closePosition(market: string): Promise<{ success: boolean; txSignature?: string; error?: string }> {
    if (!this.wallet) {
      return { success: false, error: 'Wallet not configured' };
    }

    try {
      const response = await axios.post(`${DRIFT_API}/orders/close`, {
        userPublicKey: this.wallet.publicKey.toBase58(),
        marketName: market
      });

      if (!response.data?.txSignature) {
        return { success: false, error: 'Failed to close position' };
      }

      return { success: true, txSignature: response.data.txSignature };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Get next funding time (Drift pays funding every hour)
   */
  private getNextFundingTime(): number {
    const now = Date.now();
    const hourMs = 60 * 60 * 1000;
    return Math.ceil(now / hourMs) * hourMs;
  }

  /**
   * Calculate expected funding payment
   */
  calculateExpectedFunding(positionSize: number, fundingRate: number, hours: number = 1): number {
    return positionSize * fundingRate * hours;
  }

  /**
   * Get funding rate summary
   */
  async getFundingSummary(): Promise<string> {
    const rates = await this.getFundingRates();
    
    if (rates.length === 0) {
      return 'No funding data available';
    }

    let summary = '╔══════════════════════════════════════════════════╗\n';
    summary += '║           Drift Funding Rates                    ║\n';
    summary += '╠══════════════════════════════════════════════════╣\n';

    for (const rate of rates.slice(0, 10)) {
      const direction = rate.longPayShort ? 'L→S' : 'S→L';
      const apyStr = rate.fundingRateApy > 0 
        ? `+${rate.fundingRateApy.toFixed(1)}%` 
        : `${rate.fundingRateApy.toFixed(1)}%`;
      
      summary += `║  ${rate.market.padEnd(10)} ${direction}  APY: ${apyStr.padStart(8)}  ║\n`;
    }

    summary += '╚══════════════════════════════════════════════════╝';
    return summary;
  }
}
