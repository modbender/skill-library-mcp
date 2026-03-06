// ─── Asset Types (ported from src/types/asset.ts) ───────────────────

export type AssetType = 'CRYPTO' | 'ASHARE' | 'USSTOCK' | 'HKSTOCK' | 'CASH';
export type Currency = 'USD' | 'CNY' | 'HKD';

export interface AssetSource {
  type: 'manual' | 'binance' | 'wallet' | 'ibkr';
  walletConfigId?: string;
  walletName?: string;
  chain?: string;
}

export interface Transaction {
  id: string;
  date: number; // timestamp
  type: 'BUY' | 'SELL' | 'ADJUST';
  quantity: number;
  price: number;
  note?: string;
}

export interface Asset {
  id: string;
  type: AssetType;
  symbol: string;
  name: string;
  quantity: number;
  avgPrice: number;
  currentPrice: number;
  currency: Currency;
  transactions: Transaction[];
  source?: AssetSource;
}

export interface Portfolio {
  id: string;
  name: string;
  assets: Asset[];
}

export interface ExchangeRates {
  USD: number;
  CNY: number;
  HKD: number;
  BTC?: number;
}

export interface DataFile {
  version: number;
  currentPortfolioId: string;
  displayCurrency: Currency;
  exchangeRates: ExchangeRates;
  lastPriceRefresh: string | null;
  portfolios: Portfolio[];
}

export interface UserProfile {
  age: number;
  riskTolerance: 'Conservative' | 'Moderate' | 'Aggressive' | 'Growth';
  monthlyCashFlow: number;
  investmentGoal: string;
  maxDrawdown: number;
}

export interface WalletConfig {
  id: string;
  type: 'binance' | 'ibkr' | 'wallet';
  name: string;
  // binance
  apiKey?: string;
  apiSecret?: string;
  // ibkr
  token?: string;
  queryId?: string;
  // wallet
  address?: string;
  chains?: string[];
}

export interface ConfigFile {
  wallets: WalletConfig[];
  userProfile?: UserProfile;
}

// ─── Constants ──────────────────────────────────────────────────────

export const STABLECOINS = new Set([
  'USDT', 'USDC', 'BUSD', 'TUSD', 'USDP', 'DAI', 'FRAX',
  'FDUSD', 'PYUSD', 'USD1', 'USDD', 'GUSD', 'LUSD', 'SUSD',
  'USDS', 'U', 'RWUSD', 'BFUSD',
]);

export const COINGECKO_MAP: Record<string, string> = {
  'BTC': 'bitcoin',
  'ETH': 'ethereum',
  'SOL': 'solana',
  'BNB': 'binancecoin',
  'XRP': 'ripple',
  'ADA': 'cardano',
  'DOGE': 'dogecoin',
  'DOT': 'polkadot',
  'AVAX': 'avalanche-2',
  'LINK': 'chainlink',
  'MATIC': 'matic-network',
};

export const DEFAULT_FX_RATES: ExchangeRates = {
  USD: 1,
  CNY: 7.24,
  HKD: 7.8,
};

// ─── FX Helpers ─────────────────────────────────────────────────────

export function convertToDisplayCurrency(
  amount: number,
  fromCurrency: Currency,
  displayCurrency: Currency,
  rates: ExchangeRates,
): number {
  if (fromCurrency === displayCurrency) return amount;
  // Convert to USD first, then to display currency
  const amountInUsd = amount / rates[fromCurrency];
  return amountInUsd * rates[displayCurrency];
}

export function formatCurrency(amount: number, currency: Currency): string {
  const symbols: Record<Currency, string> = { USD: '$', CNY: '¥', HKD: 'HK$' };
  return `${symbols[currency]}${amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export function generateId(): string {
  return Math.random().toString(36).substring(2, 10) + Date.now().toString(36);
}

// ─── Asset Detection (ported from priceController.ts) ───────────────

export function detectAssetDetails(
  quoteType: string,
  exchange: string,
  symbol: string,
): { type: AssetType; currency: Currency } | null {
  const q = quoteType?.toUpperCase();
  const ex = exchange?.toUpperCase();
  const s = symbol?.toUpperCase();

  if (s === 'USD' || s === 'CNY' || s === 'HKD') {
    return { type: 'CASH', currency: s as Currency };
  }
  if (q === 'CURRENCY') return null;
  if (q === 'CRYPTOCURRENCY' || s?.includes('-USD') || s?.includes('-BTC')) {
    return { type: 'CRYPTO', currency: 'USD' };
  }

  // A-Shares
  if (ex === 'SHG' || ex === 'SHE' || s.endsWith('.SS') || s.endsWith('.SZ')) {
    return { type: 'ASHARE', currency: 'CNY' };
  }
  // HK Stocks
  if (ex === 'HKG' || s.endsWith('.HK')) {
    return { type: 'HKSTOCK', currency: 'HKD' };
  }
  // US Stocks & ETFs
  const usExchanges = ['NYQ', 'NAS', 'NMS', 'NGM', 'ASE', 'PCX', 'BTS', 'NYS', 'BATS'];
  if (
    q === 'EQUITY' || q === 'ETF' || q === 'ETP' || q === 'INDEX' || q === 'MUTUALFUND' ||
    usExchanges.includes(ex) ||
    (!s.includes('.') && (q === 'EQUITY' || q === 'ETF'))
  ) {
    return { type: 'USSTOCK', currency: 'USD' };
  }
  return null;
}
