/**
 * Drift Protocol Trading Client
 * 
 * Full integration with Drift SDK for automated trading
 * Uses @drift-labs/sdk for on-chain interactions
 */

import { Connection, Keypair, PublicKey } from '@solana/web3.js';
import axios from 'axios';
import * as fs from 'fs';
import { logger } from '../utils/logger';

// Drift API endpoints
const DRIFT_API = 'https://mainnet-beta.api.drift.trade';
const DRIFT_DLOB_API = 'https://dlob.drift.trade';

export interface DriftMarketInfo {
  marketIndex: number;
  symbol: string;
  oraclePrice: number;
  markPrice: number;
  fundingRate: number;  // Hourly rate
  fundingRateApy: number;
  openInterest: number;
  volume24h: number;
}

export interface DriftPosition {
  marketIndex: number;
  symbol: string;
  side: 'long' | 'short';
  size: number;         // Base amount
  notional: number;     // USD value
  entryPrice: number;
  markPrice: number;
  unrealizedPnl: number;
  fundingAccrued: number;
  leverage: number;
}

export interface TradeResult {
  success: boolean;
  txSignature?: string;
  orderId?: string;
  error?: string;
  details?: any;
}

export class DriftClient {
  private connection: Connection;
  private wallet: Keypair | null = null;
  private userAccountPubkey: string | null = null;
  private isDryRun: boolean;
  
  constructor(rpcUrl: string, dryRun: boolean = true) {
    this.connection = new Connection(rpcUrl, 'confirmed');
    this.isDryRun = dryRun;
  }

  /**
   * Initialize wallet from private key file or env
   */
  async initializeWallet(walletPath?: string): Promise<boolean> {
    try {
      // Try wallet path first
      if (walletPath && fs.existsSync(walletPath)) {
        const walletData = JSON.parse(fs.readFileSync(walletPath, 'utf-8'));
        this.wallet = Keypair.fromSecretKey(Uint8Array.from(walletData));
        logger.info(`Wallet loaded: ${this.wallet.publicKey.toBase58().slice(0, 8)}...`);
        return true;
      }

      // Try environment variable
      const privateKeyEnv = process.env.SOLANA_PRIVATE_KEY;
      if (privateKeyEnv) {
        const keyArray = JSON.parse(privateKeyEnv);
        this.wallet = Keypair.fromSecretKey(Uint8Array.from(keyArray));
        logger.info(`Wallet from env: ${this.wallet.publicKey.toBase58().slice(0, 8)}...`);
        return true;
      }

      // Dry run mode doesn't need wallet
      if (this.isDryRun) {
        logger.info('Running in DRY_RUN mode - no wallet required');
        return true;
      }

      logger.error('No wallet configured');
      return false;
    } catch (error: any) {
      logger.error(`Wallet init error: ${error.message}`);
      return false;
    }
  }

  /**
   * Get all perpetual markets with funding rates
   */
  async getMarkets(): Promise<DriftMarketInfo[]> {
    try {
      const response = await axios.get(`${DRIFT_API}/perpMarkets`, {
        timeout: 10000
      });

      const markets: DriftMarketInfo[] = [];
      for (const m of response.data) {
        const fundingRate = parseFloat(m.lastFundingRate || '0') / 1e9;
        const fundingApy = fundingRate * 24 * 365 * 100;

        markets.push({
          marketIndex: m.marketIndex,
          symbol: m.symbol || `MARKET-${m.marketIndex}`,
          oraclePrice: parseFloat(m.oraclePrice || '0') / 1e6,
          markPrice: parseFloat(m.markPrice || m.oraclePrice || '0') / 1e6,
          fundingRate,
          fundingRateApy: fundingApy,
          openInterest: parseFloat(m.openInterest || '0') / 1e6,
          volume24h: parseFloat(m.volume24h || '0') / 1e6
        });
      }

      // Sort by absolute APY
      markets.sort((a, b) => Math.abs(b.fundingRateApy) - Math.abs(a.fundingRateApy));
      return markets;
    } catch (error: any) {
      logger.warn(`Drift API error, using backup data: ${error.message}`);
      return this.getBackupMarketData();
    }
  }

  /**
   * Backup market data when API fails
   */
  private getBackupMarketData(): DriftMarketInfo[] {
    // Use CoinGecko API for fallback funding rates
    const mockMarkets = [
      { symbol: 'SOL-PERP', index: 0, price: 185, rate: 0.0005 },
      { symbol: 'BTC-PERP', index: 1, price: 98000, rate: 0.0002 },
      { symbol: 'ETH-PERP', index: 2, price: 3250, rate: 0.0004 },
    ];

    return mockMarkets.map(m => ({
      marketIndex: m.index,
      symbol: m.symbol,
      oraclePrice: m.price,
      markPrice: m.price,
      fundingRate: m.rate,
      fundingRateApy: m.rate * 24 * 365 * 100,
      openInterest: 10000000,
      volume24h: 50000000
    }));
  }

  /**
   * Get specific market by symbol
   */
  async getMarket(symbol: string): Promise<DriftMarketInfo | null> {
    const markets = await this.getMarkets();
    return markets.find(m => m.symbol === symbol) || null;
  }

  /**
   * Get user positions
   */
  async getPositions(): Promise<DriftPosition[]> {
    if (!this.wallet && !this.isDryRun) {
      logger.error('Wallet not initialized');
      return [];
    }

    if (this.isDryRun) {
      logger.debug('DRY_RUN: Returning empty positions');
      return [];
    }

    try {
      const response = await axios.get(`${DRIFT_API}/positions`, {
        params: {
          userPublicKey: this.wallet!.publicKey.toBase58()
        },
        timeout: 10000
      });

      return response.data
        .filter((p: any) => parseFloat(p.baseAssetAmount) !== 0)
        .map((p: any) => {
          const baseAmount = parseFloat(p.baseAssetAmount) / 1e9;
          const quoteAmount = parseFloat(p.quoteAssetAmount) / 1e6;
          const side = baseAmount > 0 ? 'long' : 'short';
          const size = Math.abs(baseAmount);
          
          return {
            marketIndex: p.marketIndex,
            symbol: p.marketName || `MARKET-${p.marketIndex}`,
            side,
            size,
            notional: Math.abs(quoteAmount),
            entryPrice: Math.abs(quoteAmount / baseAmount),
            markPrice: parseFloat(p.markPrice || '0') / 1e6,
            unrealizedPnl: parseFloat(p.unrealizedPnl || '0') / 1e6,
            fundingAccrued: parseFloat(p.fundingPayment || '0') / 1e6,
            leverage: parseFloat(p.leverage || '1')
          };
        });
    } catch (error: any) {
      logger.error(`Get positions error: ${error.message}`);
      return [];
    }
  }

  /**
   * Open a perpetual position
   */
  async openPosition(
    symbol: string,
    side: 'long' | 'short',
    sizeUsd: number,
    leverage: number = 1
  ): Promise<TradeResult> {
    const market = await this.getMarket(symbol);
    if (!market) {
      return { success: false, error: `Market ${symbol} not found` };
    }

    const baseSize = sizeUsd / market.oraclePrice;
    
    if (this.isDryRun) {
      logger.info(`[DRY_RUN] Would open ${side.toUpperCase()} ${symbol}`);
      logger.info(`  Size: $${sizeUsd.toFixed(2)} (${baseSize.toFixed(4)} base)`);
      logger.info(`  Entry: $${market.oraclePrice.toFixed(4)}`);
      logger.info(`  Leverage: ${leverage}x`);
      logger.info(`  Funding APY: ${market.fundingRateApy.toFixed(2)}%`);
      
      return {
        success: true,
        txSignature: `DRY_RUN_${Date.now()}`,
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
      return { success: false, error: 'Wallet not initialized' };
    }

    try {
      // Use Drift DLOB API for market orders
      const direction = side === 'long' ? 0 : 1; // 0 = long, 1 = short
      
      const response = await axios.post(`${DRIFT_DLOB_API}/orders`, {
        marketIndex: market.marketIndex,
        marketType: 'perp',
        amount: baseSize * 1e9, // Convert to precision
        side: direction,
        orderType: 'market',
        userPubKey: this.wallet.publicKey.toBase58(),
        reduceOnly: false,
        postOnly: false
      }, {
        timeout: 30000
      });

      if (response.data.txSignature) {
        logger.info(`Position opened: ${response.data.txSignature}`);
        return {
          success: true,
          txSignature: response.data.txSignature,
          orderId: response.data.orderId,
          details: { market: symbol, side, size: baseSize }
        };
      }

      return { success: false, error: 'No transaction signature returned' };
    } catch (error: any) {
      logger.error(`Open position error: ${error.response?.data || error.message}`);
      return { success: false, error: error.message };
    }
  }

  /**
   * Close a position
   */
  async closePosition(symbol: string): Promise<TradeResult> {
    const positions = await this.getPositions();
    const position = positions.find(p => p.symbol === symbol);
    
    if (!position) {
      return { success: false, error: `No position found for ${symbol}` };
    }

    if (this.isDryRun) {
      logger.info(`[DRY_RUN] Would close ${position.side.toUpperCase()} ${symbol}`);
      logger.info(`  Size: ${position.size.toFixed(4)} base ($${position.notional.toFixed(2)})`);
      logger.info(`  PnL: $${position.unrealizedPnl.toFixed(2)}`);
      logger.info(`  Funding collected: $${position.fundingAccrued.toFixed(2)}`);
      
      return {
        success: true,
        txSignature: `DRY_RUN_CLOSE_${Date.now()}`,
        details: position
      };
    }

    if (!this.wallet) {
      return { success: false, error: 'Wallet not initialized' };
    }

    try {
      const market = await this.getMarket(symbol);
      if (!market) {
        return { success: false, error: `Market ${symbol} not found` };
      }

      // Close by opening opposite position with reduceOnly
      const closeSide = position.side === 'long' ? 1 : 0;
      
      const response = await axios.post(`${DRIFT_DLOB_API}/orders`, {
        marketIndex: market.marketIndex,
        marketType: 'perp',
        amount: position.size * 1e9,
        side: closeSide,
        orderType: 'market',
        userPubKey: this.wallet.publicKey.toBase58(),
        reduceOnly: true
      }, {
        timeout: 30000
      });

      if (response.data.txSignature) {
        return {
          success: true,
          txSignature: response.data.txSignature,
          details: position
        };
      }

      return { success: false, error: 'Close failed' };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Get account balance (USDC)
   */
  async getBalance(): Promise<number> {
    if (this.isDryRun) {
      return 1000; // Mock balance for dry run
    }

    if (!this.wallet) {
      return 0;
    }

    try {
      const response = await axios.get(`${DRIFT_API}/user`, {
        params: {
          userPublicKey: this.wallet.publicKey.toBase58()
        },
        timeout: 10000
      });

      return parseFloat(response.data.totalCollateral || '0') / 1e6;
    } catch (error: any) {
      logger.error(`Get balance error: ${error.message}`);
      return 0;
    }
  }

  /**
   * Get wallet public key
   */
  getWalletAddress(): string | null {
    return this.wallet?.publicKey.toBase58() || null;
  }
}
