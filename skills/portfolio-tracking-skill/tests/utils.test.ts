import { describe, it, expect } from 'vitest';
import {
  STABLECOINS,
  COINGECKO_MAP,
  DEFAULT_FX_RATES,
  convertToDisplayCurrency,
  formatCurrency,
  generateId,
  detectAssetDetails,
} from '../scripts/utils.js';

describe('STABLECOINS', () => {
  it('should contain common stablecoins', () => {
    expect(STABLECOINS.has('USDT')).toBe(true);
    expect(STABLECOINS.has('USDC')).toBe(true);
    expect(STABLECOINS.has('BUSD')).toBe(true);
    expect(STABLECOINS.has('DAI')).toBe(true);
    expect(STABLECOINS.has('FDUSD')).toBe(true);
  });

  it('should contain BFUSD and RWUSD as stablecoins', () => {
    expect(STABLECOINS.has('BFUSD')).toBe(true);
    expect(STABLECOINS.has('RWUSD')).toBe(true);
  });

  it('should not contain non-stablecoins', () => {
    expect(STABLECOINS.has('BTC')).toBe(false);
    expect(STABLECOINS.has('ETH')).toBe(false);
    expect(STABLECOINS.has('SOL')).toBe(false);
  });
});

describe('COINGECKO_MAP', () => {
  it('should map common crypto symbols to CoinGecko IDs', () => {
    expect(COINGECKO_MAP['BTC']).toBe('bitcoin');
    expect(COINGECKO_MAP['ETH']).toBe('ethereum');
    expect(COINGECKO_MAP['SOL']).toBe('solana');
    expect(COINGECKO_MAP['MATIC']).toBe('matic-network');
  });
});

describe('convertToDisplayCurrency', () => {
  const rates = { USD: 1, CNY: 7.24, HKD: 7.8 };

  it('should return same amount when currencies match', () => {
    expect(convertToDisplayCurrency(100, 'USD', 'USD', rates)).toBe(100);
    expect(convertToDisplayCurrency(724, 'CNY', 'CNY', rates)).toBe(724);
  });

  it('should convert CNY to USD', () => {
    const result = convertToDisplayCurrency(724, 'CNY', 'USD', rates);
    expect(result).toBeCloseTo(100, 1);
  });

  it('should convert USD to CNY', () => {
    const result = convertToDisplayCurrency(100, 'USD', 'CNY', rates);
    expect(result).toBeCloseTo(724, 1);
  });

  it('should convert HKD to USD', () => {
    const result = convertToDisplayCurrency(780, 'HKD', 'USD', rates);
    expect(result).toBeCloseTo(100, 1);
  });

  it('should convert CNY to HKD', () => {
    const result = convertToDisplayCurrency(724, 'CNY', 'HKD', rates);
    expect(result).toBeCloseTo(780, 1);
  });
});

describe('formatCurrency', () => {
  it('should format USD', () => {
    expect(formatCurrency(1234.56, 'USD')).toBe('$1,234.56');
  });

  it('should format CNY', () => {
    expect(formatCurrency(1234.56, 'CNY')).toBe('¥1,234.56');
  });

  it('should format HKD', () => {
    expect(formatCurrency(1234.56, 'HKD')).toBe('HK$1,234.56');
  });

  it('should handle zero', () => {
    expect(formatCurrency(0, 'USD')).toBe('$0.00');
  });
});

describe('generateId', () => {
  it('should return a non-empty string', () => {
    const id = generateId();
    expect(id.length).toBeGreaterThan(0);
  });

  it('should return unique IDs', () => {
    const ids = new Set(Array.from({ length: 100 }, () => generateId()));
    expect(ids.size).toBe(100);
  });
});

describe('detectAssetDetails', () => {
  it('should detect cash currencies', () => {
    expect(detectAssetDetails('', '', 'USD')).toEqual({ type: 'CASH', currency: 'USD' });
    expect(detectAssetDetails('', '', 'CNY')).toEqual({ type: 'CASH', currency: 'CNY' });
    expect(detectAssetDetails('', '', 'HKD')).toEqual({ type: 'CASH', currency: 'HKD' });
  });

  it('should filter out currency quote types', () => {
    expect(detectAssetDetails('CURRENCY', 'CCY', 'EURUSD=X')).toBeNull();
  });

  it('should detect cryptocurrencies', () => {
    expect(detectAssetDetails('CRYPTOCURRENCY', '', 'BTC-USD')).toEqual({ type: 'CRYPTO', currency: 'USD' });
    expect(detectAssetDetails('EQUITY', '', 'ETH-USD')).toEqual({ type: 'CRYPTO', currency: 'USD' });
  });

  it('should detect A-Shares', () => {
    expect(detectAssetDetails('EQUITY', 'SHG', '600519.SS')).toEqual({ type: 'ASHARE', currency: 'CNY' });
    expect(detectAssetDetails('EQUITY', 'SHE', '000001.SZ')).toEqual({ type: 'ASHARE', currency: 'CNY' });
  });

  it('should detect HK Stocks', () => {
    expect(detectAssetDetails('EQUITY', 'HKG', '0700.HK')).toEqual({ type: 'HKSTOCK', currency: 'HKD' });
  });

  it('should detect US Stocks', () => {
    expect(detectAssetDetails('EQUITY', 'NAS', 'AAPL')).toEqual({ type: 'USSTOCK', currency: 'USD' });
    expect(detectAssetDetails('ETF', 'NYQ', 'SPY')).toEqual({ type: 'USSTOCK', currency: 'USD' });
    expect(detectAssetDetails('MUTUALFUND', 'NAS', 'VFIAX')).toEqual({ type: 'USSTOCK', currency: 'USD' });
  });

  it('should return null for unrecognized assets', () => {
    expect(detectAssetDetails('FUTURE', 'CME', 'CL=F')).toBeNull();
  });
});
