import crypto from 'node:crypto';
import { STABLECOINS } from './utils.js';

const BINANCE_API_URL = 'https://api.binance.com';
const BINANCE_FAPI_URL = 'https://fapi.binance.com';
const BINANCE_DAPI_URL = 'https://dapi.binance.com';

export interface WalletAsset {
  symbol: string;
  name: string;
  quantity: number;
  type: 'CRYPTO' | 'CASH';
  currency: 'USD';
}

// ─── Signature ──────────────────────────────────────────────────────

export function createSignature(queryString: string, apiSecret: string): string {
  return crypto.createHmac('sha256', apiSecret).update(queryString).digest('hex');
}

async function signedRequest(
  baseUrl: string,
  path: string,
  apiKey: string,
  apiSecret: string,
  method: 'GET' | 'POST' = 'GET',
  extraParams: Record<string, string> = {},
): Promise<Response> {
  const timestamp = Date.now();
  const params = new URLSearchParams({ ...extraParams, timestamp: String(timestamp) });
  const queryString = params.toString();
  const signature = createSignature(queryString, apiSecret);

  const url = `${baseUrl}${path}?${queryString}&signature=${signature}`;
  return fetch(url, { method, headers: { 'X-MBX-APIKEY': apiKey } });
}

// ─── Account Fetchers ───────────────────────────────────────────────

async function fetchSpotBalances(apiKey: string, apiSecret: string): Promise<Map<string, number>> {
  const balances = new Map<string, number>();
  const response = await signedRequest(BINANCE_API_URL, '/api/v3/account', apiKey, apiSecret);

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Binance Spot API error: ${response.status} - ${error}`);
  }

  const data: { balances: Array<{ asset: string; free: string; locked: string }> } = await response.json();

  for (const b of data.balances) {
    const total = parseFloat(b.free) + parseFloat(b.locked);
    if (total > 0 && !b.asset.startsWith('LD')) {
      balances.set(b.asset, (balances.get(b.asset) ?? 0) + total);
    }
  }

  return balances;
}

async function fetchFundingBalances(apiKey: string, apiSecret: string): Promise<Map<string, number>> {
  const balances = new Map<string, number>();
  try {
    const response = await signedRequest(BINANCE_API_URL, '/sapi/v1/asset/get-funding-asset', apiKey, apiSecret, 'POST');
    if (!response.ok) return balances;

    const data: Array<{ asset: string; free: string; locked: string; freeze: string }> = await response.json();
    for (const b of data) {
      const total = parseFloat(b.free) + parseFloat(b.locked) + parseFloat(b.freeze);
      if (total > 0) balances.set(b.asset, (balances.get(b.asset) ?? 0) + total);
    }
  } catch { /* best-effort */ }
  return balances;
}

async function fetchEarnFlexibleBalances(apiKey: string, apiSecret: string): Promise<Map<string, number>> {
  const balances = new Map<string, number>();
  try {
    let current = 1;
    const size = 100;
    while (true) {
      const response = await signedRequest(
        BINANCE_API_URL, '/sapi/v1/simple-earn/flexible/position',
        apiKey, apiSecret, 'GET',
        { current: String(current), size: String(size) },
      );
      if (!response.ok) break;

      const data: { rows: Array<{ asset: string; totalAmount: string }>; total: number } = await response.json();
      for (const row of data.rows) {
        const amount = parseFloat(row.totalAmount);
        if (amount > 0) balances.set(row.asset, (balances.get(row.asset) ?? 0) + amount);
      }
      if (current * size >= data.total) break;
      current++;
    }
  } catch { /* best-effort */ }
  return balances;
}

async function fetchEarnLockedBalances(apiKey: string, apiSecret: string): Promise<Map<string, number>> {
  const balances = new Map<string, number>();
  try {
    let current = 1;
    const size = 100;
    while (true) {
      const response = await signedRequest(
        BINANCE_API_URL, '/sapi/v1/simple-earn/locked/position',
        apiKey, apiSecret, 'GET',
        { current: String(current), size: String(size) },
      );
      if (!response.ok) break;

      const data: { rows: Array<{ asset: string; amount: string }>; total: number } = await response.json();
      for (const row of data.rows) {
        const amount = parseFloat(row.amount);
        if (amount > 0) balances.set(row.asset, (balances.get(row.asset) ?? 0) + amount);
      }
      if (current * size >= data.total) break;
      current++;
    }
  } catch { /* best-effort */ }
  return balances;
}

async function fetchFuturesUsdtBalances(apiKey: string, apiSecret: string): Promise<Map<string, number>> {
  const balances = new Map<string, number>();
  try {
    const response = await signedRequest(BINANCE_FAPI_URL, '/fapi/v2/account', apiKey, apiSecret);
    if (!response.ok) return balances;

    const data: { assets: Array<{ asset: string; walletBalance: string }> } = await response.json();
    for (const a of data.assets) {
      const amount = parseFloat(a.walletBalance);
      if (amount > 0) balances.set(a.asset, (balances.get(a.asset) ?? 0) + amount);
    }
  } catch { /* best-effort */ }
  return balances;
}

async function fetchFuturesCoinBalances(apiKey: string, apiSecret: string): Promise<Map<string, number>> {
  const balances = new Map<string, number>();
  try {
    const response = await signedRequest(BINANCE_DAPI_URL, '/dapi/v1/account', apiKey, apiSecret);
    if (!response.ok) return balances;

    const data: { assets: Array<{ asset: string; walletBalance: string }> } = await response.json();
    for (const a of data.assets) {
      const amount = parseFloat(a.walletBalance);
      if (amount > 0) balances.set(a.asset, (balances.get(a.asset) ?? 0) + amount);
    }
  } catch { /* best-effort */ }
  return balances;
}

// ─── Public API ─────────────────────────────────────────────────────

export async function fetchBinanceBalances(apiKey: string, apiSecret: string): Promise<WalletAsset[]> {
  const [spotResult, ...optionalResults] = await Promise.allSettled([
    fetchSpotBalances(apiKey, apiSecret),
    fetchFundingBalances(apiKey, apiSecret),
    fetchEarnFlexibleBalances(apiKey, apiSecret),
    fetchEarnLockedBalances(apiKey, apiSecret),
    fetchFuturesUsdtBalances(apiKey, apiSecret),
    fetchFuturesCoinBalances(apiKey, apiSecret),
  ]);

  if (spotResult.status === 'rejected') throw spotResult.reason;

  const merged = new Map<string, number>(spotResult.value);
  for (const result of optionalResults) {
    if (result.status === 'fulfilled') {
      for (const [asset, qty] of result.value) {
        merged.set(asset, (merged.get(asset) ?? 0) + qty);
      }
    }
  }

  return Array.from(merged.entries()).map(([symbol, quantity]) => ({
    symbol,
    name: symbol,
    quantity,
    type: STABLECOINS.has(symbol) ? 'CASH' as const : 'CRYPTO' as const,
    currency: 'USD' as const,
  }));
}

export async function validateBinanceCredentials(apiKey: string, apiSecret: string): Promise<{ valid: boolean; error?: string }> {
  try {
    const timestamp = Date.now();
    const queryString = `timestamp=${timestamp}`;
    const signature = createSignature(queryString, apiSecret);

    const url = `${BINANCE_API_URL}/api/v3/account?${queryString}&signature=${signature}`;
    const response = await fetch(url, { method: 'GET', headers: { 'X-MBX-APIKEY': apiKey } });

    if (response.ok) return { valid: true };

    const errorText = await response.text();
    return { valid: false, error: `${response.status}: ${errorText}` };
  } catch (err: any) {
    return { valid: false, error: err.message };
  }
}

// ─── CLI Entry Point ────────────────────────────────────────────────

const command = process.argv[2];

if (command) {
  try {
    let result: unknown;

    switch (command) {
      case 'sync': {
        const apiKey = process.argv[3];
        const apiSecret = process.argv[4];
        if (!apiKey || !apiSecret) throw new Error('Usage: sync <apiKey> <apiSecret>');
        result = await fetchBinanceBalances(apiKey, apiSecret);
        break;
      }
      case 'validate': {
        const apiKey = process.argv[3];
        const apiSecret = process.argv[4];
        if (!apiKey || !apiSecret) throw new Error('Usage: validate <apiKey> <apiSecret>');
        result = await validateBinanceCredentials(apiKey, apiSecret);
        break;
      }
      default:
        result = { error: `Unknown command: ${command}` };
    }

    console.log(JSON.stringify(result));
  } catch (err: any) {
    console.log(JSON.stringify({ error: err.message }));
    process.exit(1);
  }
}
