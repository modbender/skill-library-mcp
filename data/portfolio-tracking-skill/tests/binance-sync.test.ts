import { describe, it, expect, vi, beforeEach } from 'vitest';
import { createSignature, fetchBinanceBalances, validateBinanceCredentials } from '../scripts/binance-sync.js';
import { STABLECOINS } from '../scripts/utils.js';

const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

beforeEach(() => {
  mockFetch.mockReset();
});

describe('createSignature', () => {
  it('should create a valid HMAC-SHA256 signature', () => {
    const sig = createSignature('timestamp=1234567890', 'secret123');
    expect(sig).toMatch(/^[a-f0-9]{64}$/);
  });

  it('should produce different signatures for different secrets', () => {
    const sig1 = createSignature('timestamp=1234567890', 'secret1');
    const sig2 = createSignature('timestamp=1234567890', 'secret2');
    expect(sig1).not.toBe(sig2);
  });

  it('should produce different signatures for different data', () => {
    const sig1 = createSignature('timestamp=1111111111', 'secret');
    const sig2 = createSignature('timestamp=2222222222', 'secret');
    expect(sig1).not.toBe(sig2);
  });
});

describe('STABLECOINS classification', () => {
  it('should classify USDT as CASH', () => {
    expect(STABLECOINS.has('USDT')).toBe(true);
  });

  it('should classify USDC as CASH', () => {
    expect(STABLECOINS.has('USDC')).toBe(true);
  });

  it('should classify FDUSD as CASH', () => {
    expect(STABLECOINS.has('FDUSD')).toBe(true);
  });

  it('should not classify BTC as CASH', () => {
    expect(STABLECOINS.has('BTC')).toBe(false);
  });

  it('should not classify ETH as CASH', () => {
    expect(STABLECOINS.has('ETH')).toBe(false);
  });
});

describe('fetchBinanceBalances', () => {
  function mockSpotResponse(balances: Array<{ asset: string; free: string; locked: string }>) {
    return {
      ok: true,
      json: () => Promise.resolve({ balances }),
    };
  }

  function mockOptionalFailure() {
    return { ok: false, status: 403 };
  }

  it('should fetch and merge balances from all accounts', async () => {
    mockFetch.mockImplementation(async (url: string) => {
      if (url.includes('/api/v3/account')) {
        return mockSpotResponse([
          { asset: 'BTC', free: '1.0', locked: '0.5' },
          { asset: 'USDT', free: '1000', locked: '0' },
          { asset: 'LDBTC', free: '0.1', locked: '0' }, // LD prefix, should be skipped
        ]);
      }
      // All optional accounts return empty/fail
      return mockOptionalFailure();
    });

    const assets = await fetchBinanceBalances('key', 'secret');

    expect(assets).toHaveLength(2);
    const btc = assets.find(a => a.symbol === 'BTC');
    expect(btc).toBeDefined();
    expect(btc!.quantity).toBe(1.5);
    expect(btc!.type).toBe('CRYPTO');

    const usdt = assets.find(a => a.symbol === 'USDT');
    expect(usdt).toBeDefined();
    expect(usdt!.type).toBe('CASH');
    expect(usdt!.currency).toBe('USD');
  });

  it('should merge spot + funding balances', async () => {
    mockFetch.mockImplementation(async (url: string) => {
      if (url.includes('/api/v3/account')) {
        return mockSpotResponse([{ asset: 'BTC', free: '1.0', locked: '0' }]);
      }
      if (url.includes('/sapi/v1/asset/get-funding-asset')) {
        return {
          ok: true,
          json: () => Promise.resolve([{ asset: 'BTC', free: '0.5', locked: '0', freeze: '0' }]),
        };
      }
      return mockOptionalFailure();
    });

    const assets = await fetchBinanceBalances('key', 'secret');
    const btc = assets.find(a => a.symbol === 'BTC');
    expect(btc!.quantity).toBe(1.5); // 1.0 spot + 0.5 funding
  });

  it('should throw when spot account fails', async () => {
    mockFetch.mockImplementation(async () => ({
      ok: false,
      status: 401,
      text: () => Promise.resolve('Unauthorized'),
    }));

    await expect(fetchBinanceBalances('bad-key', 'bad-secret')).rejects.toThrow('Binance Spot API error');
  });

  it('should skip zero balances', async () => {
    mockFetch.mockImplementation(async (url: string) => {
      if (url.includes('/api/v3/account')) {
        return mockSpotResponse([
          { asset: 'BTC', free: '0', locked: '0' },
          { asset: 'ETH', free: '0.001', locked: '0' },
        ]);
      }
      return mockOptionalFailure();
    });

    const assets = await fetchBinanceBalances('key', 'secret');
    expect(assets).toHaveLength(1);
    expect(assets[0].symbol).toBe('ETH');
  });
});

describe('validateBinanceCredentials', () => {
  it('should return valid for successful response', async () => {
    mockFetch.mockResolvedValueOnce({ ok: true });

    const result = await validateBinanceCredentials('good-key', 'good-secret');
    expect(result.valid).toBe(true);
  });

  it('should return invalid for failed response', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      text: () => Promise.resolve('{"code":-2015,"msg":"Invalid API-key"}'),
    });

    const result = await validateBinanceCredentials('bad-key', 'bad-secret');
    expect(result.valid).toBe(false);
    expect(result.error).toContain('401');
  });

  it('should handle network errors', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Connection refused'));

    const result = await validateBinanceCredentials('key', 'secret');
    expect(result.valid).toBe(false);
    expect(result.error).toBe('Connection refused');
  });
});
