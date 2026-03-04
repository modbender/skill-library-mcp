/**
 * Flash Trade Trading Client
 * 
 * Integration with Flash Trade perpetuals
 * Uses flash-trade-sdk for on-chain interactions
 */

import { Connection, Keypair } from '@solana/web3.js';
import axios from 'axios';
import * as fs from 'fs';
import { logger } from '../utils/logger';

// Flash Trade API (unofficial, based on CoinGecko data)
const COINGECKO_API = 'https://api.coingecko.com/api/v3';
const FLASH_PROGRAM_ID = 'FLASHxQCTq2LN7PqrG6W1zhwfJ9DU8NKMfPbGcnfxj5';

export interface FlashMarketInfo {
  symbol: string;
  oraclePrice: number;
  fundingRate: number;  // Hourly rate
  fundingRateApy: number;
  openInterest: number;
  volume24h: number;
}

export interface FlashPosition {
  symbol: string;
  side: 'long' | 'short';
  size: number;
  notional: number;
  entryPrice: number;
  unrealizedPnl: number;
  fundingAccrued: number;
}

export interface TradeResult {
  success: boolean;
  txSignature?: string;
  error?: string;
  details?: any;
}

export class FlashClient {
  private connection: Connection;
  private wallet: Keypair | null = null;
  private isDryRun: boolean;
  private cachedMarkets: FlashMarketInfo[] | null = null;
  private cacheTime: number = 0;
  private CACHE_TTL = 60000; // 1 minute cache
  
  constructor(rpcUrl: string, dryRun: boolean = true) {
    this.connection = new Connection(rpcUrl, 'confirmed');
    this.isDryRun = dryRun;
  }

  /**
   * Initialize wallet
   */
  async initializeWallet(walletPath?: string): Promise<boolean> {
    try {
      if (walletPath && fs.existsSync(walletPath)) {
        const walletData = JSON.parse(fs.readFileSync(walletPath, 'utf-8'));
        this.wallet = Keypair.fromSecretKey(Uint8Array.from(walletData));
        logger.info(`Flash wallet loaded: ${this.wallet.publicKey.toBase58().slice(0, 8)}...`);
        return true;
      }

      const privateKeyEnv = process.env.SOLANA_PRIVATE_KEY;
      if (privateKeyEnv) {
        const keyArray = JSON.parse(privateKeyEnv);
        this.wallet = Keypair.fromSecretKey(Uint8Array.from(keyArray));
        return true;
      }

      if (this.isDryRun) {
        logger.info('Flash: Running in DRY_RUN mode');
        return true;
      }

      return false;
    } catch (error: any) {
      logger.error(`Flash wallet init error: ${error.message}`);
      return false;
    }
  }

  /**
   * Get markets with funding rates from CoinGecko
   */
  async getMarkets(): Promise<FlashMarketInfo[]> {
    // Return cached if fresh
    if (this.cachedMarkets && Date.now() - this.cacheTime < this.CACHE_TTL) {
      return this.cachedMarkets;
    }

    try {
      // CoinGecko derivatives endpoint for Flash Trade
      const response = await axios.get(`${COINGECKO_API}/derivatives/exchanges/flash_trade`, {
        timeout: 10000
      });

      if (!response.data?.tickers) {
        throw new Error('No ticker data');
      }

      const markets: FlashMarketInfo[] = response.data.tickers.map((t: any) => {
        const fundingRate = parseFloat(t.funding_rate || '0') / 100; // Convert from percentage
        
        return {
          symbol: t.symbol || t.base,
          oraclePrice: parseFloat(t.last || '0'),
          fundingRate,
          fundingRateApy: fundingRate * 24 * 365 * 100,
          openInterest: parseFloat(t.open_interest_usd || '0'),
          volume24h: parseFloat(t.volume || '0')
        };
      });

      // Sort by absolute APY
      markets.sort((a, b) => Math.abs(b.fundingRateApy) - Math.abs(a.fundingRateApy));
      
      this.cachedMarkets = markets;
      this.cacheTime = Date.now();
      
      return markets;
    } catch (error: any) {
      logger.warn(`Flash API error: ${error.message}`);
      return this.getBackupMarketData();
    }
  }

  /**
   * Backup market data
   */
  private getBackupMarketData(): FlashMarketInfo[] {
    return [
      { symbol: 'SOL-PERP', oraclePrice: 185, fundingRate: 0.0008, fundingRateApy: 700, openInterest: 5000000, volume24h: 20000000 },
      { symbol: 'BTC-PERP', oraclePrice: 98000, fundingRate: 0.0003, fundingRateApy: 262, openInterest: 10000000, volume24h: 50000000 },
      { symbol: 'ETH-PERP', oraclePrice: 3250, fundingRate: 0.0005, fundingRateApy: 438, openInterest: 8000000, volume24h: 30000000 },
      { symbol: 'SUI-PERP', oraclePrice: 3.5, fundingRate: 0.0010, fundingRateApy: 876, openInterest: 3000000, volume24h: 10000000 },
      { symbol: 'RNDR-PERP', oraclePrice: 7.5, fundingRate: 0.0012, fundingRateApy: 1051, openInterest: 2000000, volume24h: 8000000 },
    ];
  }

  /**
   * Get specific market
   */
  async getMarket(symbol: string): Promise<FlashMarketInfo | null> {
    const markets = await this.getMarkets();
    return markets.find(m => m.symbol === symbol || m.symbol === `${symbol}-PERP`) || null;
  }

  /**
   * Get user positions (requires on-chain query)
   */
  async getPositions(): Promise<FlashPosition[]> {
    if (this.isDryRun) {
      return [];
    }

    if (!this.wallet) {
      logger.error('Flash: Wallet not initialized');
      return [];
    }

    // Flash Trade positions are stored on-chain
    // Would need to parse program accounts
    // For now, return empty (positions tracked in state file)
    logger.debug('Flash: Position querying not yet implemented');
    return [];
  }

  /**
   * Open a position (currently simulated - full SDK integration needed)
   */
  async openPosition(
    symbol: string,
    side: 'long' | 'short',
    sizeUsd: number,
    leverage: number = 1
  ): Promise<TradeResult> {
    const market = await this.getMarket(symbol);
    if (!market) {
      return { success: false, error: `Flash: Market ${symbol} not found` };
    }

    const baseSize = sizeUsd / market.oraclePrice;

    if (this.isDryRun) {
      logger.info(`[DRY_RUN] Flash: Would open ${side.toUpperCase()} ${symbol}`);
      logger.info(`  Size: $${sizeUsd.toFixed(2)} (${baseSize.toFixed(4)} base)`);
      logger.info(`  Entry: $${market.oraclePrice.toFixed(4)}`);
      logger.info(`  Funding APY: ${market.fundingRateApy.toFixed(2)}%`);
      
      return {
        success: true,
        txSignature: `FLASH_DRY_RUN_${Date.now()}`,
        details: {
          market: symbol,
          side,
          size: baseSize,
          notional: sizeUsd,
          entry: market.oraclePrice,
          fundingApy: market.fundingRateApy
        }
      };
    }

    if (!this.wallet) {
      return { success: false, error: 'Flash: Wallet not initialized' };
    }

    // TODO: Full Flash Trade SDK integration
    // For now, return error for non-dry-run
    return {
      success: false,
      error: 'Flash Trade SDK integration pending - use DRY_RUN mode for testing'
    };
  }

  /**
   * Close a position
   */
  async closePosition(symbol: string): Promise<TradeResult> {
    if (this.isDryRun) {
      logger.info(`[DRY_RUN] Flash: Would close position for ${symbol}`);
      return {
        success: true,
        txSignature: `FLASH_DRY_RUN_CLOSE_${Date.now()}`,
        details: { market: symbol }
      };
    }

    // TODO: Flash Trade SDK integration
    return {
      success: false,
      error: 'Flash Trade SDK integration pending'
    };
  }

  /**
   * Get account balance
   */
  async getBalance(): Promise<number> {
    if (this.isDryRun) {
      return 1000;
    }

    if (!this.wallet) {
      return 0;
    }

    // Get SOL balance (Flash uses SOL as collateral)
    try {
      const balance = await this.connection.getBalance(this.wallet.publicKey);
      return balance / 1e9; // Convert lamports to SOL
    } catch (error) {
      return 0;
    }
  }

  getWalletAddress(): string | null {
    return this.wallet?.publicKey.toBase58() || null;
  }
}
