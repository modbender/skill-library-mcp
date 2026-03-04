/**
 * DeFi Skill — DEX trading, AMM swaps, OTC escrow, yield farming, and Msig proposals
 *
 * 30 tools total:
 *   Read-only (14): token price, markets, swap rate, pools, OHLCV, orderbook,
 *                   recent trades, open orders, order/trade history, DEX balances,
 *                   OTC offers, farm list, farm stakes
 *   Write (16): place/cancel DEX orders, withdraw DEX, AMM swap, add/remove liquidity,
 *               create/fill/cancel OTC, farm stake/unstake/claim,
 *               msig propose/approve/cancel, msig list
 */

// ── Types ────────────────────────────────────────

interface ToolDef {
  name: string;
  description: string;
  parameters: { type: 'object'; required?: string[]; properties: Record<string, unknown> };
  handler: (params: any) => Promise<unknown>;
}

interface SkillApi {
  registerTool(tool: ToolDef): void;
  getConfig(): Record<string, unknown>;
}

// ── RPC Helpers ──────────────────────────────────

const RPC_TIMEOUT = 15000;

async function rpcPost(endpoint: string, path: string, body: unknown): Promise<any> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), RPC_TIMEOUT);
  try {
    const resp = await fetch(`${endpoint}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    if (!resp.ok) {
      const text = await resp.text().catch(() => '');
      throw new Error(`RPC ${path} failed (${resp.status}): ${text.slice(0, 200)}`);
    }
    return await resp.json();
  } finally {
    clearTimeout(timer);
  }
}

async function getTableRows(endpoint: string, opts: {
  code: string; scope: string; table: string;
  lower_bound?: string | number; upper_bound?: string | number;
  limit?: number; key_type?: string; index_position?: string;
  json?: boolean; reverse?: boolean;
}): Promise<any[]> {
  const result = await rpcPost(endpoint, '/v1/chain/get_table_rows', {
    json: opts.json !== false,
    code: opts.code,
    scope: opts.scope,
    table: opts.table,
    lower_bound: opts.lower_bound,
    upper_bound: opts.upper_bound,
    limit: opts.limit || 100,
    key_type: opts.key_type,
    index_position: opts.index_position,
    reverse: opts.reverse || false,
  });
  return result.rows || [];
}

// ── Metal X API Helpers ─────────────────────────

function getMetalXBaseUrl(network: string): string {
  return network === 'mainnet'
    ? 'https://dex.api.mainnet.metalx.com'
    : 'https://dex.api.testnet.metalx.com';
}

async function metalXGet(baseUrl: string, path: string): Promise<any> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), RPC_TIMEOUT);
  try {
    const resp = await fetch(`${baseUrl}${path}`, { signal: controller.signal });
    if (!resp.ok) {
      const text = await resp.text().catch(() => '');
      throw new Error(`Metal X ${path} failed (${resp.status}): ${text.slice(0, 200)}`);
    }
    return await resp.json();
  } finally {
    clearTimeout(timer);
  }
}

// ── Swap Math ────────────────────────────────────

function parseTokenSpec(spec: string): { precision: number; symbol: string; contract: string } | null {
  const parts = spec.split(',');
  if (parts.length !== 3) return null;
  const precision = parseInt(parts[0]);
  if (isNaN(precision) || precision < 0 || precision > 18) return null;
  return { precision, symbol: parts[1].trim(), contract: parts[2].trim() };
}

function getPoolFee(pool: any): number {
  if (typeof pool.fee === 'number') return pool.fee;
  if (pool.fee && typeof pool.fee.exchange_fee === 'number') return pool.fee.exchange_fee;
  return 30;
}

function calcConstantProduct(
  amountIn: number, reserveIn: number, reserveOut: number, feeBps: number,
): { output: number; priceImpactPct: number } {
  if (reserveIn <= 0 || reserveOut <= 0 || amountIn <= 0) {
    return { output: 0, priceImpactPct: 0 };
  }
  const inputWithFee = amountIn * (10000 - feeBps);
  const output = (reserveOut * inputWithFee) / (reserveIn * 10000 + inputWithFee);
  const spotRate = reserveOut / reserveIn;
  const effectiveRate = output / amountIn;
  const priceImpactPct = Math.max(0, (1 - effectiveRate / spotRate) * 100);
  return { output, priceImpactPct };
}

// ── EOSIO Name Encoding ──────────────────────────

function charToValue(c: string): number {
  if (c === '.') return 0;
  if (c >= '1' && c <= '5') return c.charCodeAt(0) - '1'.charCodeAt(0) + 1;
  if (c >= 'a' && c <= 'z') return c.charCodeAt(0) - 'a'.charCodeAt(0) + 6;
  return 0;
}

function nameToU64(name: string): string {
  let value = BigInt(0);
  const n = Math.min(name.length, 12);
  for (let i = 0; i < n; i++) {
    const c = BigInt(charToValue(name[i]));
    if (i < 12) {
      value |= (c & BigInt(0x1f)) << BigInt(64 - 5 * (i + 1));
    }
  }
  if (name.length > 12) {
    const c = BigInt(charToValue(name[12]));
    value |= c & BigInt(0x0f);
  }
  return value.toString();
}

function isValidEosioName(name: string): boolean {
  if (!name || name.length > 12) return false;
  return /^[a-z1-5.]+$/.test(name);
}

// ── Asset Formatting ─────────────────────────────

function formatAsset(amount: number, precision: number, symbol: string): string {
  return `${amount.toFixed(precision)} ${symbol}`;
}

function parseAssetString(s: string): { amount: number; symbol: string; precision: number } | null {
  const parts = s.trim().split(' ');
  if (parts.length !== 2) return null;
  const amount = parseFloat(parts[0]);
  if (isNaN(amount)) return null;
  const dotIdx = parts[0].indexOf('.');
  const precision = dotIdx >= 0 ? parts[0].length - dotIdx - 1 : 0;
  return { amount, symbol: parts[1], precision };
}

// ── Session Factory ──────────────────────────────

let cachedSession: { api: any; account: string; permission: string } | null = null;

async function getSession(): Promise<{ api: any; account: string; permission: string }> {
  if (cachedSession) return cachedSession;

  const privateKey = process.env.XPR_PRIVATE_KEY;
  const account = process.env.XPR_ACCOUNT;
  const permission = process.env.XPR_PERMISSION || 'active';
  const rpcEndpoint = process.env.XPR_RPC_ENDPOINT;

  if (!privateKey) throw new Error('XPR_PRIVATE_KEY is required for write operations');
  if (!account) throw new Error('XPR_ACCOUNT is required for write operations');
  if (!rpcEndpoint) throw new Error('XPR_RPC_ENDPOINT is required for write operations');

  const { Api, JsonRpc, JsSignatureProvider } = await import('@proton/js');
  const rpc = new JsonRpc(rpcEndpoint);
  const signatureProvider = new JsSignatureProvider([privateKey]);
  const api = new Api({ rpc, signatureProvider });

  cachedSession = { api, account, permission };
  return cachedSession;
}

// ── DEX Market Cache ─────────────────────────────

let marketsCache: { data: any[]; ts: number } | null = null;
const MARKETS_CACHE_TTL = 60000; // 1 minute

async function fetchMarkets(metalXBase: string): Promise<any[]> {
  if (marketsCache && Date.now() - marketsCache.ts < MARKETS_CACHE_TTL) {
    return marketsCache.data;
  }
  const result = await metalXGet(metalXBase, '/dex/v1/markets/all');
  const markets = Array.isArray(result) ? result : (result.data || []);
  marketsCache = { data: markets, ts: Date.now() };
  return markets;
}

async function findMarket(metalXBase: string, symbol: string): Promise<any | null> {
  const markets = await fetchMarkets(metalXBase);
  const normalized = symbol.toUpperCase().replace(/[-\/]/g, '_');
  return markets.find((m: any) => (m.symbol || '').toUpperCase() === normalized) || null;
}

// ── Skill Entry Point ────────────────────────────

export default function defiSkill(api: SkillApi): void {
  const config = api.getConfig();
  const rpcEndpoint = (config.rpcEndpoint as string) || process.env.XPR_RPC_ENDPOINT || '';
  const network = (config.network as string) || process.env.XPR_NETWORK || 'testnet';
  const metalXBase = getMetalXBaseUrl(network);

  // ════════════════════════════════════════════════
  // READ-ONLY DEX TOOLS
  // ════════════════════════════════════════════════

  // ── 1. defi_get_token_price ──
  api.registerTool({
    name: 'defi_get_token_price',
    description: 'Get 24h price data for a trading pair on Metal X DEX. Returns open/high/low/close, volume, and percentage change. Symbol format: "BASE_QUOTE" e.g. "XPR_XMD", "XBTC_XMD".',
    parameters: {
      type: 'object',
      required: ['symbol'],
      properties: {
        symbol: { type: 'string', description: 'Trading pair symbol, e.g. "XPR_XMD"' },
      },
    },
    handler: async ({ symbol }: { symbol: string }) => {
      if (!symbol || typeof symbol !== 'string') {
        return { error: 'symbol parameter is required (e.g. "XPR_XMD")' };
      }
      try {
        const data = await metalXGet(metalXBase, '/dex/v1/trades/daily');
        const markets: any[] = Array.isArray(data) ? data : (data.data || []);
        const normalized = symbol.toUpperCase().replace(/[-\/]/g, '_');
        const match = markets.find((m: any) => (m.symbol || '').toUpperCase() === normalized);
        if (!match) {
          return { error: `Market "${symbol}" not found. Use defi_list_markets to see available pairs.` };
        }
        return {
          symbol: match.symbol,
          open: match.open,
          high: match.high,
          low: match.low,
          close: match.close,
          volume_bid: match.volume_bid,
          volume_ask: match.volume_ask,
          change_24h_pct: match.change_percentage,
        };
      } catch (err: any) {
        return { error: `Failed to fetch price: ${err.message}` };
      }
    },
  });

  // ── 2. defi_list_markets ──
  api.registerTool({
    name: 'defi_list_markets',
    description: 'List all trading pairs on Metal X DEX with fees and token info.',
    parameters: {
      type: 'object',
      properties: {},
    },
    handler: async () => {
      try {
        const markets = await fetchMarkets(metalXBase);
        return {
          markets: markets.map((m: any) => ({
            market_id: m.market_id,
            symbol: m.symbol,
            type: m.type || 'spot',
            maker_fee_pct: m.maker_fee,
            taker_fee_pct: m.taker_fee,
            order_min: m.order_min,
            bid_token: m.bid_token,
            ask_token: m.ask_token,
          })),
          total: markets.length,
        };
      } catch (err: any) {
        return { error: `Failed to list markets: ${err.message}` };
      }
    },
  });

  // ── 3. defi_get_swap_rate ──
  api.registerTool({
    name: 'defi_get_swap_rate',
    description: 'Calculate AMM swap rate on proton.swaps WITHOUT executing. Token format: "PRECISION,SYMBOL,CONTRACT" (e.g. "4,XPR,eosio.token", "6,XUSDC,xtokens"). Returns expected output, rate, and price impact.',
    parameters: {
      type: 'object',
      required: ['from_token', 'to_token', 'amount'],
      properties: {
        from_token: { type: 'string', description: 'Input token: "PRECISION,SYMBOL,CONTRACT"' },
        to_token: { type: 'string', description: 'Output token: "PRECISION,SYMBOL,CONTRACT"' },
        amount: { type: 'number', description: 'Amount of input token to swap' },
      },
    },
    handler: async ({ from_token, to_token, amount }: {
      from_token: string; to_token: string; amount: number;
    }) => {
      const fromSpec = parseTokenSpec(from_token);
      const toSpec = parseTokenSpec(to_token);
      if (!fromSpec) return { error: 'Invalid from_token. Use "PRECISION,SYMBOL,CONTRACT"' };
      if (!toSpec) return { error: 'Invalid to_token. Use "PRECISION,SYMBOL,CONTRACT"' };
      if (!amount || amount <= 0) return { error: 'amount must be positive' };

      try {
        const pools = await getTableRows(rpcEndpoint, {
          code: 'proton.swaps', scope: 'proton.swaps', table: 'pools', limit: 200,
        });

        const matchPool = pools.find((p: any) => {
          const sym1 = ((p.pool1?.quantity || '') as string).split(' ')[1] || '';
          const sym2 = ((p.pool2?.quantity || '') as string).split(' ')[1] || '';
          const c1 = p.pool1?.contract || '';
          const c2 = p.pool2?.contract || '';
          return (
            (sym1 === fromSpec.symbol && c1 === fromSpec.contract &&
             sym2 === toSpec.symbol && c2 === toSpec.contract) ||
            (sym2 === fromSpec.symbol && c2 === fromSpec.contract &&
             sym1 === toSpec.symbol && c1 === toSpec.contract)
          );
        });

        if (!matchPool) {
          return { error: `No pool for ${fromSpec.symbol}/${toSpec.symbol}. Use defi_list_pools.` };
        }

        const sym1 = ((matchPool.pool1?.quantity || '') as string).split(' ')[1] || '';
        const isForward = sym1 === fromSpec.symbol;
        const reserveIn = parseFloat((isForward ? matchPool.pool1 : matchPool.pool2)?.quantity || '0');
        const reserveOut = parseFloat((isForward ? matchPool.pool2 : matchPool.pool1)?.quantity || '0');
        const feeBps = getPoolFee(matchPool);
        const { output, priceImpactPct } = calcConstantProduct(amount, reserveIn, reserveOut, feeBps);

        return {
          input: `${amount} ${fromSpec.symbol}`,
          output: `${output.toFixed(toSpec.precision)} ${toSpec.symbol}`,
          rate: output > 0 ? (output / amount).toFixed(8) : '0',
          price_impact_pct: priceImpactPct.toFixed(4),
          pool: matchPool.lt_symbol || `${fromSpec.symbol}/${toSpec.symbol}`,
          fee_pct: (feeBps / 100).toFixed(2),
          amplifier: matchPool.amplifier || 0,
          note: matchPool.amplifier > 0 ? 'StableSwap pool — actual output may differ from constant-product estimate' : undefined,
          reserve_in: reserveIn,
          reserve_out: reserveOut,
        };
      } catch (err: any) {
        return { error: `Failed to calc swap rate: ${err.message}` };
      }
    },
  });

  // ── 4. defi_list_pools ──
  api.registerTool({
    name: 'defi_list_pools',
    description: 'List AMM liquidity pools on proton.swaps with reserves, fees, and pool type.',
    parameters: {
      type: 'object',
      properties: {
        active_only: { type: 'boolean', description: 'Only active pools (default true)' },
      },
    },
    handler: async ({ active_only }: { active_only?: boolean }) => {
      try {
        const pools = await getTableRows(rpcEndpoint, {
          code: 'proton.swaps', scope: 'proton.swaps', table: 'pools', limit: 200,
        });
        const result = pools
          .filter((p: any) => active_only === false || p.active !== false)
          .map((p: any) => ({
            lt_symbol: p.lt_symbol || null,
            memo: p.memo || null,
            token1: { quantity: p.pool1?.quantity || '0', contract: p.pool1?.contract || '' },
            token2: { quantity: p.pool2?.quantity || '0', contract: p.pool2?.contract || '' },
            fee_pct: (getPoolFee(p) / 100).toFixed(2),
            amplifier: p.amplifier || 0,
            pool_type: (p.amplifier || 0) > 0 ? 'stableswap' : 'constant-product',
          }));
        return { pools: result, total: result.length };
      } catch (err: any) {
        return { error: `Failed to list pools: ${err.message}` };
      }
    },
  });

  // ── 5. defi_get_ohlcv ──
  api.registerTool({
    name: 'defi_get_ohlcv',
    description: 'Get OHLCV candlestick data for a trading pair. Intervals: "15", "30", "60" (minutes), "1D", "1W", "1M".',
    parameters: {
      type: 'object',
      required: ['symbol', 'interval'],
      properties: {
        symbol: { type: 'string', description: 'Trading pair, e.g. "XPR_XMD"' },
        interval: { type: 'string', description: 'Candle interval: "15","30","60","1D","1W","1M"' },
        from: { type: 'string', description: 'Start date ISO (default: 30 days ago)' },
        to: { type: 'string', description: 'End date ISO (default: now)' },
        limit: { type: 'number', description: 'Max candles (default 100, max 500)' },
      },
    },
    handler: async ({ symbol, interval, from, to, limit }: {
      symbol: string; interval: string; from?: string; to?: string; limit?: number;
    }) => {
      if (!symbol) return { error: 'symbol is required' };
      if (!interval) return { error: 'interval is required (15, 30, 60, 1D, 1W, 1M)' };
      try {
        const now = new Date();
        const defaultFrom = new Date(now.getTime() - 30 * 86400000);
        const fromStr = from || defaultFrom.toISOString();
        const toStr = to || now.toISOString();
        const lim = Math.min(limit || 100, 500);

        const params = `symbol=${encodeURIComponent(symbol)}&interval=${encodeURIComponent(interval)}&from=${encodeURIComponent(fromStr)}&to=${encodeURIComponent(toStr)}&limit=${lim}`;
        const data = await metalXGet(metalXBase, `/dex/v1/chart/ohlcv?${params}`);
        const candles: any[] = Array.isArray(data) ? data : (data.data || []);

        return {
          symbol,
          interval,
          candles: candles.map((c: any) => ({
            time: c.time,
            open: c.open,
            high: c.high,
            low: c.low,
            close: c.close,
            volume: c.volume,
            volume_bid: c.volume_bid,
            count: c.count,
          })),
          total: candles.length,
        };
      } catch (err: any) {
        return { error: `Failed to fetch OHLCV: ${err.message}` };
      }
    },
  });

  // ── 6. defi_get_orderbook ──
  api.registerTool({
    name: 'defi_get_orderbook',
    description: 'Get orderbook depth (bids and asks) for a trading pair. The step parameter controls price grouping precision.',
    parameters: {
      type: 'object',
      required: ['symbol'],
      properties: {
        symbol: { type: 'string', description: 'Trading pair, e.g. "XPR_XMD"' },
        step: { type: 'number', description: 'Price grouping step (1/precision). E.g. 1000 for 0.001 precision. Default: 10000' },
        limit: { type: 'number', description: 'Max depth levels (default 20)' },
      },
    },
    handler: async ({ symbol, step, limit }: { symbol: string; step?: number; limit?: number }) => {
      if (!symbol) return { error: 'symbol is required' };
      try {
        const s = step || 10000;
        const l = limit || 20;
        const params = `symbol=${encodeURIComponent(symbol)}&step=${s}&limit=${l}`;
        const data = await metalXGet(metalXBase, `/dex/v1/orders/depth?${params}`);
        const depth = data.data || data;
        return {
          symbol,
          step: s,
          bids: (depth.bids || []).slice(0, l),
          asks: (depth.asks || []).slice(0, l),
        };
      } catch (err: any) {
        return { error: `Failed to fetch orderbook: ${err.message}` };
      }
    },
  });

  // ── 7. defi_get_recent_trades ──
  api.registerTool({
    name: 'defi_get_recent_trades',
    description: 'Get recent trades for a trading pair on Metal X DEX.',
    parameters: {
      type: 'object',
      required: ['symbol'],
      properties: {
        symbol: { type: 'string', description: 'Trading pair, e.g. "XPR_XMD"' },
        limit: { type: 'number', description: 'Max trades (default 20)' },
      },
    },
    handler: async ({ symbol, limit }: { symbol: string; limit?: number }) => {
      if (!symbol) return { error: 'symbol is required' };
      try {
        const l = limit || 20;
        const params = `symbol=${encodeURIComponent(symbol)}&limit=${l}`;
        const data = await metalXGet(metalXBase, `/dex/v1/trades/recent?${params}`);
        const trades: any[] = Array.isArray(data) ? data : (data.data || []);
        return {
          symbol,
          trades: trades.map((t: any) => ({
            trade_id: t.trade_id,
            price: t.price,
            bid_amount: t.bid_total,
            ask_amount: t.ask_total,
            bid_user: t.bid_user,
            ask_user: t.ask_user,
            side: t.order_side === 1 ? 'buy' : 'sell',
            time: t.block_time,
            trx_id: t.trx_id,
          })),
          total: trades.length,
        };
      } catch (err: any) {
        return { error: `Failed to fetch recent trades: ${err.message}` };
      }
    },
  });

  // ── 8. defi_get_open_orders ──
  api.registerTool({
    name: 'defi_get_open_orders',
    description: 'Get open orders on Metal X DEX for a specific account.',
    parameters: {
      type: 'object',
      required: ['account'],
      properties: {
        account: { type: 'string', description: 'Account name' },
        symbol: { type: 'string', description: 'Filter by trading pair (optional)' },
        limit: { type: 'number', description: 'Max results (default 50)' },
      },
    },
    handler: async ({ account, symbol, limit }: { account: string; symbol?: string; limit?: number }) => {
      if (!account) return { error: 'account is required' };
      try {
        let params = `account=${encodeURIComponent(account)}&limit=${limit || 50}`;
        if (symbol) params += `&symbol=${encodeURIComponent(symbol)}`;
        const data = await metalXGet(metalXBase, `/dex/v1/orders/open?${params}`);
        const orders: any[] = Array.isArray(data) ? data : (data.data || []);
        return {
          account,
          orders: orders.map((o: any) => ({
            order_id: o.order_id,
            ordinal_order_id: o.ordinal_order_id,
            market_id: o.market_id,
            side: o.order_side === 1 ? 'buy' : 'sell',
            type: o.order_type === 1 ? 'limit' : o.order_type === 2 ? 'stop_loss' : o.order_type === 3 ? 'take_profit' : `type_${o.order_type}`,
            price: o.price,
            quantity_init: o.quantity_init,
            quantity_curr: o.quantity_curr,
            filled_total: o.filled_total,
            filled_amount: o.filled_amount,
            filled_fee: o.filled_fee,
            fill_type: o.fill_type === 0 ? 'GTC' : o.fill_type === 1 ? 'IOC' : 'POST_ONLY',
            status: o.status,
            created_at: o.created_at,
          })),
          total: data.count || orders.length,
        };
      } catch (err: any) {
        return { error: `Failed to fetch open orders: ${err.message}` };
      }
    },
  });

  // ── 9. defi_get_order_history ──
  api.registerTool({
    name: 'defi_get_order_history',
    description: 'Get order history on Metal X DEX for a specific account.',
    parameters: {
      type: 'object',
      required: ['account'],
      properties: {
        account: { type: 'string', description: 'Account name' },
        symbol: { type: 'string', description: 'Filter by trading pair (optional)' },
        status: { type: 'string', description: 'Filter by status: "create","fill","pfill","cancel" (optional)' },
        limit: { type: 'number', description: 'Max results (default 50)' },
      },
    },
    handler: async ({ account, symbol, status, limit }: {
      account: string; symbol?: string; status?: string; limit?: number;
    }) => {
      if (!account) return { error: 'account is required' };
      try {
        let params = `account=${encodeURIComponent(account)}&limit=${limit || 50}`;
        if (symbol) params += `&symbol=${encodeURIComponent(symbol)}`;
        if (status) params += `&status=${encodeURIComponent(status)}`;
        const data = await metalXGet(metalXBase, `/dex/v1/orders/history?${params}`);
        const orders: any[] = Array.isArray(data) ? data : (data.data || []);
        return {
          account,
          orders: orders.map((o: any) => ({
            order_id: o.order_id,
            market_id: o.market_id,
            side: o.order_side === 1 ? 'buy' : 'sell',
            type: o.order_type === 1 ? 'limit' : o.order_type === 2 ? 'stop_loss' : o.order_type === 3 ? 'take_profit' : `type_${o.order_type}`,
            price: o.price,
            quantity_init: o.quantity_init,
            quantity_curr: o.quantity_curr,
            filled_total: o.filled_total,
            filled_amount: o.filled_amount,
            filled_fee: o.filled_fee,
            status: o.status,
            trx_id: o.trx_id,
            block_time: o.block_time,
          })),
          total: data.count || orders.length,
        };
      } catch (err: any) {
        return { error: `Failed to fetch order history: ${err.message}` };
      }
    },
  });

  // ── 10. defi_get_trade_history ──
  api.registerTool({
    name: 'defi_get_trade_history',
    description: 'Get trade (fill) history on Metal X DEX for a specific account.',
    parameters: {
      type: 'object',
      required: ['account'],
      properties: {
        account: { type: 'string', description: 'Account name' },
        symbol: { type: 'string', description: 'Filter by trading pair (optional)' },
        limit: { type: 'number', description: 'Max results (default 50)' },
      },
    },
    handler: async ({ account, symbol, limit }: { account: string; symbol?: string; limit?: number }) => {
      if (!account) return { error: 'account is required' };
      try {
        let params = `account=${encodeURIComponent(account)}&limit=${limit || 50}`;
        if (symbol) params += `&symbol=${encodeURIComponent(symbol)}`;
        const data = await metalXGet(metalXBase, `/dex/v1/trades/history?${params}`);
        const trades: any[] = Array.isArray(data) ? data : (data.data || []);
        return {
          account,
          trades: trades.map((t: any) => ({
            trade_id: t.trade_id,
            market_id: t.market_id,
            price: t.price,
            side: t.order_side === 1 ? 'buy' : 'sell',
            bid_total: t.bid_total,
            bid_amount: t.bid_amount,
            bid_fee: t.bid_fee,
            ask_total: t.ask_total,
            ask_amount: t.ask_amount,
            ask_fee: t.ask_fee,
            trx_id: t.trx_id,
            block_time: t.block_time,
          })),
          total: data.count || trades.length,
        };
      } catch (err: any) {
        return { error: `Failed to fetch trade history: ${err.message}` };
      }
    },
  });

  // ── 11. defi_get_dex_balances ──
  api.registerTool({
    name: 'defi_get_dex_balances',
    description: 'Get DEX exchange balances for an account (tokens deposited on Metal X for trading).',
    parameters: {
      type: 'object',
      required: ['account'],
      properties: {
        account: { type: 'string', description: 'Account name' },
      },
    },
    handler: async ({ account }: { account: string }) => {
      if (!account) return { error: 'account is required' };
      try {
        const data = await metalXGet(metalXBase, `/dex/v1/account/balances?account=${encodeURIComponent(account)}`);
        const balances = Array.isArray(data) ? data : (data.data || []);
        return { account, balances, total: balances.length };
      } catch (err: any) {
        return { error: `Failed to fetch DEX balances: ${err.message}` };
      }
    },
  });

  // ── 12. defi_list_otc_offers ──
  api.registerTool({
    name: 'defi_list_otc_offers',
    description: 'List OTC (peer-to-peer) escrow offers on token.escrow. Shows recent offers with token pairs and expiry.',
    parameters: {
      type: 'object',
      properties: {
        limit: { type: 'number', description: 'Max results (default 20)' },
        recent_first: { type: 'boolean', description: 'Show newest first (default true)' },
      },
    },
    handler: async ({ limit, recent_first }: { limit?: number; recent_first?: boolean }) => {
      try {
        const rows = await getTableRows(rpcEndpoint, {
          code: 'token.escrow', scope: 'token.escrow', table: 'escrows',
          limit: limit || 20,
          reverse: recent_first !== false,
        });
        return {
          offers: rows.map((e: any) => ({
            id: e.id,
            from: e.from,
            to: e.to || '(open — anyone can fill)',
            from_tokens: e.fromTokens || [],
            from_nfts: e.fromNfts || [],
            to_tokens: e.toTokens || [],
            to_nfts: e.toNfts || [],
            expiry: e.expiry ? new Date(e.expiry * 1000).toISOString() : null,
          })),
          total: rows.length,
        };
      } catch (err: any) {
        return { error: `Failed to list OTC offers: ${err.message}` };
      }
    },
  });

  // ════════════════════════════════════════════════
  // WRITE DEX TOOLS
  // ════════════════════════════════════════════════

  // ── 13. defi_place_order ──
  api.registerTool({
    name: 'defi_place_order',
    description: 'Place a limit order on Metal X DEX. Deposits tokens to DEX and places the order in one transaction. Order types: limit, stop_loss, take_profit. Fill types: GTC (good-til-cancelled), IOC (immediate-or-cancel), POST_ONLY.',
    parameters: {
      type: 'object',
      required: ['symbol', 'side', 'amount', 'price', 'confirmed'],
      properties: {
        symbol: { type: 'string', description: 'Market pair, e.g. "XPR_XMD"' },
        side: { type: 'string', description: '"buy" or "sell"' },
        amount: { type: 'number', description: 'Amount of bid (base) token' },
        price: { type: 'number', description: 'Price in ask (quote) token per 1 bid token' },
        order_type: { type: 'string', description: '"limit" (default), "stop_loss", "take_profit"' },
        trigger_price: { type: 'number', description: 'Trigger price for stop_loss/take_profit' },
        fill_type: { type: 'string', description: '"GTC" (default), "IOC", "POST_ONLY"' },
        confirmed: { type: 'boolean', description: 'Must be true to execute' },
      },
    },
    handler: async (params: {
      symbol: string; side: string; amount: number; price: number;
      order_type?: string; trigger_price?: number; fill_type?: string; confirmed?: boolean;
    }) => {
      if (!params.confirmed) {
        return {
          error: 'Confirmation required. Set confirmed=true to place this order.',
          preview: { symbol: params.symbol, side: params.side, amount: params.amount, price: params.price },
        };
      }
      if (!params.symbol) return { error: 'symbol is required' };
      if (!params.side || !['buy', 'sell'].includes(params.side.toLowerCase())) {
        return { error: 'side must be "buy" or "sell"' };
      }
      if (!params.amount || params.amount <= 0) return { error: 'amount must be positive' };
      if (!params.price || params.price <= 0) return { error: 'price must be positive' };

      try {
        const market = await findMarket(metalXBase, params.symbol);
        if (!market) return { error: `Market "${params.symbol}" not found` };

        const bidToken = market.bid_token;
        const askToken = market.ask_token;
        const bidMult = bidToken.multiplier || Math.pow(10, bidToken.precision);
        const askMult = askToken.multiplier || Math.pow(10, askToken.precision);

        const orderSide = params.side.toLowerCase() === 'buy' ? 1 : 2;
        const orderTypeMap: Record<string, number> = { limit: 1, stop_loss: 2, take_profit: 3 };
        const orderType = orderTypeMap[(params.order_type || 'limit').toLowerCase()] || 1;
        const fillTypeMap: Record<string, number> = { gtc: 0, ioc: 1, post_only: 2 };
        const fillType = fillTypeMap[(params.fill_type || 'gtc').toLowerCase()] || 0;

        const rawQuantity = Math.round(params.amount * bidMult);
        const rawPrice = Math.round(params.price * askMult);
        const triggerPrice = params.trigger_price ? Math.round(params.trigger_price * askMult) : 0;

        // Calculate deposit needed
        let depositQuantity: string;
        let depositContract: string;
        if (orderSide === 1) {
          // BUY: deposit ask token (quote). Total cost = amount * price
          const totalCost = params.amount * params.price;
          depositQuantity = formatAsset(totalCost, askToken.precision, askToken.code);
          depositContract = askToken.contract;
        } else {
          // SELL: deposit bid token (base)
          depositQuantity = formatAsset(params.amount, bidToken.precision, bidToken.code);
          depositContract = bidToken.contract;
        }

        const { api: eosApi, account, permission } = await getSession();

        const actions: any[] = [
          // 1. Deposit tokens to DEX
          {
            account: depositContract,
            name: 'transfer',
            authorization: [{ actor: account, permission }],
            data: { from: account, to: 'dex', quantity: depositQuantity, memo: '' },
          },
          // 2. Place the order
          {
            account: 'dex',
            name: 'placeorder',
            authorization: [{ actor: account, permission }],
            data: {
              market_id: market.market_id,
              account,
              order_type: orderType,
              order_side: orderSide,
              quantity: rawQuantity,
              price: rawPrice,
              bid_symbol: { sym: `${bidToken.precision},${bidToken.code}`, contract: bidToken.contract },
              ask_symbol: { sym: `${askToken.precision},${askToken.code}`, contract: askToken.contract },
              trigger_price: triggerPrice,
              fill_type: fillType,
            },
          },
        ];

        const result = await eosApi.transact({ actions }, { blocksBehind: 3, expireSeconds: 30 });
        return {
          transaction_id: result.transaction_id || result.processed?.id,
          order: {
            market: params.symbol,
            side: params.side,
            amount: params.amount,
            price: params.price,
            type: params.order_type || 'limit',
            fill_type: params.fill_type || 'GTC',
            deposit: depositQuantity,
          },
        };
      } catch (err: any) {
        return { error: `Failed to place order: ${err.message}` };
      }
    },
  });

  // ── 14. defi_cancel_order ──
  api.registerTool({
    name: 'defi_cancel_order',
    description: 'Cancel an open order on Metal X DEX.',
    parameters: {
      type: 'object',
      required: ['order_id', 'confirmed'],
      properties: {
        order_id: { type: 'number', description: 'The order ID to cancel' },
        confirmed: { type: 'boolean', description: 'Must be true to execute' },
      },
    },
    handler: async ({ order_id, confirmed }: { order_id: number; confirmed?: boolean }) => {
      if (!confirmed) return { error: 'Confirmation required. Set confirmed=true.', order_id };
      if (!order_id) return { error: 'order_id is required' };
      try {
        const { api: eosApi, account, permission } = await getSession();
        const result = await eosApi.transact({
          actions: [{
            account: 'dex',
            name: 'cancelorder',
            authorization: [{ actor: account, permission }],
            data: { account, order_id },
          }],
        }, { blocksBehind: 3, expireSeconds: 30 });
        return { transaction_id: result.transaction_id || result.processed?.id, cancelled_order_id: order_id };
      } catch (err: any) {
        return { error: `Failed to cancel order: ${err.message}` };
      }
    },
  });

  // ── 15. defi_withdraw_dex ──
  api.registerTool({
    name: 'defi_withdraw_dex',
    description: 'Withdraw all tokens from your Metal X DEX balance back to your wallet.',
    parameters: {
      type: 'object',
      required: ['confirmed'],
      properties: {
        confirmed: { type: 'boolean', description: 'Must be true to execute' },
      },
    },
    handler: async ({ confirmed }: { confirmed?: boolean }) => {
      if (!confirmed) return { error: 'Confirmation required. Set confirmed=true.' };
      try {
        const { api: eosApi, account, permission } = await getSession();
        const result = await eosApi.transact({
          actions: [{
            account: 'dex',
            name: 'withdrawall',
            authorization: [{ actor: account, permission }],
            data: { account },
          }],
        }, { blocksBehind: 3, expireSeconds: 30 });
        return { transaction_id: result.transaction_id || result.processed?.id, withdrawn: true };
      } catch (err: any) {
        return { error: `Failed to withdraw: ${err.message}` };
      }
    },
  });

  // ── 16. defi_swap ──
  api.registerTool({
    name: 'defi_swap',
    description: 'Execute an AMM swap on proton.swaps. Deposits input token, swaps via the pool, and withdraws output in one transaction. Use defi_get_swap_rate first to preview.',
    parameters: {
      type: 'object',
      required: ['from_token', 'to_token', 'amount', 'min_output', 'confirmed'],
      properties: {
        from_token: { type: 'string', description: 'Input token: "PRECISION,SYMBOL,CONTRACT"' },
        to_token: { type: 'string', description: 'Output token: "PRECISION,SYMBOL,CONTRACT"' },
        amount: { type: 'number', description: 'Amount of input token to swap' },
        min_output: { type: 'number', description: 'Minimum output (slippage protection)' },
        confirmed: { type: 'boolean', description: 'Must be true to execute' },
      },
    },
    handler: async (params: {
      from_token: string; to_token: string; amount: number; min_output: number; confirmed?: boolean;
    }) => {
      if (!params.confirmed) {
        return {
          error: 'Confirmation required. Set confirmed=true. Use defi_get_swap_rate to preview first.',
          preview: { from: params.from_token, to: params.to_token, amount: params.amount, min_output: params.min_output },
        };
      }
      const fromSpec = parseTokenSpec(params.from_token);
      const toSpec = parseTokenSpec(params.to_token);
      if (!fromSpec) return { error: 'Invalid from_token. Use "PRECISION,SYMBOL,CONTRACT"' };
      if (!toSpec) return { error: 'Invalid to_token. Use "PRECISION,SYMBOL,CONTRACT"' };
      if (!params.amount || params.amount <= 0) return { error: 'amount must be positive' };
      if (!params.min_output || params.min_output <= 0) return { error: 'min_output must be positive' };

      try {
        const { api: eosApi, account, permission } = await getSession();

        const fromQty = formatAsset(params.amount, fromSpec.precision, fromSpec.symbol);
        const minOutQty = formatAsset(params.min_output, toSpec.precision, toSpec.symbol);
        const fromExtSym = { sym: `${fromSpec.precision},${fromSpec.symbol}`, contract: fromSpec.contract };
        const toExtSym = { sym: `${toSpec.precision},${toSpec.symbol}`, contract: toSpec.contract };

        const actions = [
          // 1. Prepare deposit slots
          {
            account: 'proton.swaps',
            name: 'depositprep',
            authorization: [{ actor: account, permission }],
            data: { owner: account, symbols: [fromExtSym, toExtSym] },
          },
          // 2. Deposit input token
          {
            account: fromSpec.contract,
            name: 'transfer',
            authorization: [{ actor: account, permission }],
            data: { from: account, to: 'proton.swaps', quantity: fromQty, memo: '' },
          },
          // 3. Execute swap
          {
            account: 'proton.swaps',
            name: 'makeorder1',
            authorization: [{ actor: account, permission }],
            data: {
              maker: account,
              maker_in: { quantity: fromQty, contract: fromSpec.contract },
              maker_out_min: { quantity: minOutQty, contract: toSpec.contract },
              allow_partial: true,
              deadline_secs: 300,
            },
          },
          // 4. Withdraw all output
          {
            account: 'proton.swaps',
            name: 'withdrawall',
            authorization: [{ actor: account, permission }],
            data: { owner: account },
          },
        ];

        const result = await eosApi.transact({ actions }, { blocksBehind: 3, expireSeconds: 30 });
        return {
          transaction_id: result.transaction_id || result.processed?.id,
          swap: { input: fromQty, min_output: minOutQty },
        };
      } catch (err: any) {
        return { error: `Failed to swap: ${err.message}` };
      }
    },
  });

  // ── 17. defi_add_liquidity ──
  api.registerTool({
    name: 'defi_add_liquidity',
    description: 'Add liquidity to an AMM pool on proton.swaps. Deposits both tokens and adds to the pool in one transaction. Use defi_list_pools to find pool lt_symbol.',
    parameters: {
      type: 'object',
      required: ['lt_symbol', 'token1', 'token2', 'confirmed'],
      properties: {
        lt_symbol: { type: 'string', description: 'LP token symbol, e.g. "XPRBTC" (from defi_list_pools)' },
        token1: { type: 'string', description: 'Token 1 deposit: "AMOUNT SYMBOL" e.g. "1000.0000 XPR"' },
        token1_contract: { type: 'string', description: 'Token 1 contract, e.g. "eosio.token"' },
        token2: { type: 'string', description: 'Token 2 deposit: "AMOUNT SYMBOL" e.g. "0.00100000 XBTC"' },
        token2_contract: { type: 'string', description: 'Token 2 contract, e.g. "xtokens"' },
        slippage_pct: { type: 'number', description: 'Max slippage percentage (default 1.0)' },
        confirmed: { type: 'boolean', description: 'Must be true to execute' },
      },
    },
    handler: async (params: {
      lt_symbol: string; token1: string; token1_contract: string;
      token2: string; token2_contract: string; slippage_pct?: number; confirmed?: boolean;
    }) => {
      if (!params.confirmed) {
        return { error: 'Confirmation required. Set confirmed=true.', preview: params };
      }
      const t1 = parseAssetString(params.token1);
      const t2 = parseAssetString(params.token2);
      if (!t1) return { error: 'Invalid token1 format. Use "AMOUNT SYMBOL" e.g. "1000.0000 XPR"' };
      if (!t2) return { error: 'Invalid token2 format. Use "AMOUNT SYMBOL" e.g. "0.01000000 XBTC"' };
      if (!params.token1_contract) return { error: 'token1_contract is required' };
      if (!params.token2_contract) return { error: 'token2_contract is required' };

      try {
        const { api: eosApi, account, permission } = await getSession();
        const slip = (params.slippage_pct || 1.0) / 100;
        const min1 = formatAsset(t1.amount * (1 - slip), t1.precision, t1.symbol);
        const min2 = formatAsset(t2.amount * (1 - slip), t2.precision, t2.symbol);

        // Parse lt_symbol to get precision
        const ltParts = params.lt_symbol.match(/^(\d+),(.+)$/);
        const ltSym = ltParts ? params.lt_symbol : `8,${params.lt_symbol}`;

        const ext1 = { sym: `${t1.precision},${t1.symbol}`, contract: params.token1_contract };
        const ext2 = { sym: `${t2.precision},${t2.symbol}`, contract: params.token2_contract };

        const actions = [
          // 1. Prepare deposit slots
          {
            account: 'proton.swaps',
            name: 'depositprep',
            authorization: [{ actor: account, permission }],
            data: { owner: account, symbols: [ext1, ext2] },
          },
          // 2. Deposit token 1
          {
            account: params.token1_contract,
            name: 'transfer',
            authorization: [{ actor: account, permission }],
            data: { from: account, to: 'proton.swaps', quantity: params.token1, memo: '' },
          },
          // 3. Deposit token 2
          {
            account: params.token2_contract,
            name: 'transfer',
            authorization: [{ actor: account, permission }],
            data: { from: account, to: 'proton.swaps', quantity: params.token2, memo: '' },
          },
          // 4. Add liquidity
          {
            account: 'proton.swaps',
            name: 'liquidityadd',
            authorization: [{ actor: account, permission }],
            data: {
              owner: account,
              lt_symbol: ltSym,
              add_token1: { quantity: params.token1, contract: params.token1_contract },
              add_token2: { quantity: params.token2, contract: params.token2_contract },
              add_token1_min: { quantity: min1, contract: params.token1_contract },
              add_token2_min: { quantity: min2, contract: params.token2_contract },
            },
          },
        ];

        const result = await eosApi.transact({ actions }, { blocksBehind: 3, expireSeconds: 30 });
        return {
          transaction_id: result.transaction_id || result.processed?.id,
          added: { token1: params.token1, token2: params.token2, pool: params.lt_symbol },
        };
      } catch (err: any) {
        return { error: `Failed to add liquidity: ${err.message}` };
      }
    },
  });

  // ── 18. defi_remove_liquidity ──
  api.registerTool({
    name: 'defi_remove_liquidity',
    description: 'Remove liquidity from an AMM pool on proton.swaps by burning LP tokens. Returns both underlying tokens.',
    parameters: {
      type: 'object',
      required: ['lp_amount', 'confirmed'],
      properties: {
        lp_amount: { type: 'string', description: 'LP tokens to burn: "AMOUNT SYMBOL" e.g. "100.00000000 XPRBTC"' },
        confirmed: { type: 'boolean', description: 'Must be true to execute' },
      },
    },
    handler: async ({ lp_amount, confirmed }: { lp_amount: string; confirmed?: boolean }) => {
      if (!confirmed) return { error: 'Confirmation required. Set confirmed=true.', lp_amount };
      const lp = parseAssetString(lp_amount);
      if (!lp) return { error: 'Invalid lp_amount. Use "AMOUNT SYMBOL" e.g. "100.00000000 XPRBTC"' };
      try {
        const { api: eosApi, account, permission } = await getSession();
        const actions = [
          {
            account: 'proton.swaps',
            name: 'liquidityrmv',
            authorization: [{ actor: account, permission }],
            data: { owner: account, lt: lp_amount },
          },
          {
            account: 'proton.swaps',
            name: 'withdrawall',
            authorization: [{ actor: account, permission }],
            data: { owner: account },
          },
        ];
        const result = await eosApi.transact({ actions }, { blocksBehind: 3, expireSeconds: 30 });
        return {
          transaction_id: result.transaction_id || result.processed?.id,
          removed: lp_amount,
        };
      } catch (err: any) {
        return { error: `Failed to remove liquidity: ${err.message}` };
      }
    },
  });

  // ════════════════════════════════════════════════
  // OTC ESCROW TOOLS
  // ════════════════════════════════════════════════

  // ── 19. defi_create_otc ──
  api.registerTool({
    name: 'defi_create_otc',
    description: 'Create a P2P OTC escrow offer on token.escrow. You send fromTokens and receive toTokens when counterparty fills. Leave "to" empty for an open offer anyone can fill.',
    parameters: {
      type: 'object',
      required: ['from_tokens', 'to_tokens', 'confirmed'],
      properties: {
        to: { type: 'string', description: 'Counterparty account (empty string = open offer anyone can fill)' },
        from_tokens: {
          type: 'array',
          description: 'Tokens you send: [{ "quantity": "100.0000 XPR", "contract": "eosio.token" }]',
        },
        to_tokens: {
          type: 'array',
          description: 'Tokens you receive: [{ "quantity": "0.250000 XUSDC", "contract": "xtokens" }]',
        },
        expiry_hours: { type: 'number', description: 'Hours until expiry (default 72)' },
        confirmed: { type: 'boolean', description: 'Must be true to execute' },
      },
    },
    handler: async (params: {
      to?: string; from_tokens: any[]; to_tokens: any[];
      expiry_hours?: number; confirmed?: boolean;
    }) => {
      if (!params.confirmed) {
        return { error: 'Confirmation required. Set confirmed=true.', preview: params };
      }
      if (!Array.isArray(params.from_tokens) || params.from_tokens.length === 0) {
        return { error: 'from_tokens must be non-empty array of { quantity, contract }' };
      }
      if (!Array.isArray(params.to_tokens) || params.to_tokens.length === 0) {
        return { error: 'to_tokens must be non-empty array of { quantity, contract }' };
      }

      try {
        const { api: eosApi, account, permission } = await getSession();
        const expiryHours = params.expiry_hours || 72;
        const expiry = Math.floor(Date.now() / 1000) + expiryHours * 3600;
        const toAccount = params.to || '';

        // Build deposit actions for all from_tokens
        const depositActions = params.from_tokens.map((t: any) => ({
          account: t.contract,
          name: 'transfer',
          authorization: [{ actor: account, permission }],
          data: { from: account, to: 'token.escrow', quantity: t.quantity, memo: '' },
        }));

        const actions = [
          ...depositActions,
          {
            account: 'token.escrow',
            name: 'startescrow',
            authorization: [{ actor: account, permission }],
            data: {
              from: account,
              to: toAccount,
              fromTokens: params.from_tokens,
              fromNfts: [],
              toTokens: params.to_tokens,
              toNfts: [],
              expiry,
            },
          },
        ];

        const result = await eosApi.transact({ actions }, { blocksBehind: 3, expireSeconds: 30 });
        return {
          transaction_id: result.transaction_id || result.processed?.id,
          escrow: {
            from: account,
            to: toAccount || '(open offer)',
            from_tokens: params.from_tokens,
            to_tokens: params.to_tokens,
            expiry: new Date(expiry * 1000).toISOString(),
          },
        };
      } catch (err: any) {
        return { error: `Failed to create OTC: ${err.message}` };
      }
    },
  });

  // ── 20. defi_fill_otc ──
  api.registerTool({
    name: 'defi_fill_otc',
    description: 'Fill an OTC escrow offer. You deposit the required toTokens and receive the fromTokens. Use defi_list_otc_offers to find offers.',
    parameters: {
      type: 'object',
      required: ['escrow_id', 'confirmed'],
      properties: {
        escrow_id: { type: 'number', description: 'Escrow ID to fill' },
        confirmed: { type: 'boolean', description: 'Must be true to execute' },
      },
    },
    handler: async ({ escrow_id, confirmed }: { escrow_id: number; confirmed?: boolean }) => {
      if (!confirmed) return { error: 'Confirmation required. Set confirmed=true.', escrow_id };
      if (escrow_id === undefined || escrow_id === null) return { error: 'escrow_id is required' };

      try {
        const { api: eosApi, account, permission } = await getSession();

        // Fetch the escrow to know what tokens to deposit
        const rows = await getTableRows(rpcEndpoint, {
          code: 'token.escrow', scope: 'token.escrow', table: 'escrows',
          lower_bound: escrow_id, upper_bound: escrow_id, limit: 1,
        });
        if (rows.length === 0) return { error: `Escrow ${escrow_id} not found` };

        const escrow = rows[0];
        const toTokens: any[] = escrow.toTokens || [];

        // Deposit the required toTokens
        const depositActions = toTokens.map((t: any) => ({
          account: t.contract,
          name: 'transfer',
          authorization: [{ actor: account, permission }],
          data: { from: account, to: 'token.escrow', quantity: t.quantity, memo: '' },
        }));

        const actions = [
          ...depositActions,
          {
            account: 'token.escrow',
            name: 'fillescrow',
            authorization: [{ actor: account, permission }],
            data: { actor: account, id: escrow_id },
          },
        ];

        const result = await eosApi.transact({ actions }, { blocksBehind: 3, expireSeconds: 30 });
        return {
          transaction_id: result.transaction_id || result.processed?.id,
          filled_escrow: escrow_id,
          you_sent: toTokens,
          you_received: escrow.fromTokens || [],
        };
      } catch (err: any) {
        return { error: `Failed to fill OTC: ${err.message}` };
      }
    },
  });

  // ── 21. defi_cancel_otc ──
  api.registerTool({
    name: 'defi_cancel_otc',
    description: 'Cancel your OTC escrow offer and withdraw deposited tokens.',
    parameters: {
      type: 'object',
      required: ['escrow_id', 'confirmed'],
      properties: {
        escrow_id: { type: 'number', description: 'Escrow ID to cancel' },
        confirmed: { type: 'boolean', description: 'Must be true to execute' },
      },
    },
    handler: async ({ escrow_id, confirmed }: { escrow_id: number; confirmed?: boolean }) => {
      if (!confirmed) return { error: 'Confirmation required. Set confirmed=true.', escrow_id };
      if (escrow_id === undefined || escrow_id === null) return { error: 'escrow_id is required' };
      try {
        const { api: eosApi, account, permission } = await getSession();
        const result = await eosApi.transact({
          actions: [{
            account: 'token.escrow',
            name: 'cancelescrow',
            authorization: [{ actor: account, permission }],
            data: { actor: account, id: escrow_id },
          }],
        }, { blocksBehind: 3, expireSeconds: 30 });
        return {
          transaction_id: result.transaction_id || result.processed?.id,
          cancelled_escrow: escrow_id,
        };
      } catch (err: any) {
        return { error: `Failed to cancel OTC: ${err.message}` };
      }
    },
  });

  // ════════════════════════════════════════════════
  // YIELD FARMING TOOLS (yield.farms)
  // ════════════════════════════════════════════════

  // ── defi_list_farms ──
  api.registerTool({
    name: 'defi_list_farms',
    description: 'List yield farms on yield.farms with staking token, total staked, and reward emission rates. Active farms earn rewards per half-second.',
    parameters: {
      type: 'object',
      properties: {
        active_only: { type: 'boolean', description: 'Only show active farms with nonzero rewards (default true)' },
      },
    },
    handler: async ({ active_only }: { active_only?: boolean }) => {
      try {
        const rows = await getTableRows(rpcEndpoint, {
          code: 'yield.farms', scope: 'yield.farms', table: 'rewards.cfg', limit: 50,
        });

        const farms = rows
          .filter((r: any) => {
            if (active_only === false) return true;
            // Active = has nonzero reward emission
            const rewards = r.rewards_per_half_second || [];
            return rewards.some((rw: any) => {
              const qty = parseFloat((rw.quantity || '0').split(' ')[0]);
              return qty > 0;
            });
          })
          .map((r: any) => {
            // total_staked is extended_asset: { quantity: "123.0000 SYMBOL", contract: "..." }
            const stakeQty = r.total_staked?.quantity || '0';
            const stakeContract = r.total_staked?.contract || '';
            const parsed = parseAssetString(stakeQty);
            const symbol = parsed?.symbol || '';
            const precision = parsed?.precision || 0;
            const totalStake = parsed?.amount || 0;

            const rewardsPerHalfSec = (r.rewards_per_half_second || []).map((rw: any) => {
              const amt = parseFloat((rw.quantity || '0').split(' ')[0]);
              const rwSym = (rw.quantity || '').split(' ')[1] || '';
              return {
                token: rwSym,
                contract: rw.contract,
                per_half_second: amt,
                per_day: +(amt * 2 * 86400).toFixed(8),
                per_year: +(amt * 2 * 86400 * 365).toFixed(4),
              };
            });

            return {
              stake_symbol: symbol,
              stake_contract: stakeContract,
              stake_precision: precision,
              total_staked: totalStake,
              rewards: rewardsPerHalfSec,
              last_update: r.reward_time,
            };
          });

        return { farms, total: farms.length };
      } catch (err: any) {
        return { error: `Failed to list farms: ${err.message}` };
      }
    },
  });

  // ── defi_get_farm_stakes ──
  api.registerTool({
    name: 'defi_get_farm_stakes',
    description: 'Get a user\'s staked positions and pending rewards on yield.farms.',
    parameters: {
      type: 'object',
      required: ['account'],
      properties: {
        account: { type: 'string', description: 'Account name' },
      },
    },
    handler: async ({ account }: { account: string }) => {
      if (!account || !isValidEosioName(account)) return { error: 'Valid account name is required' };
      try {
        const accountU64 = nameToU64(account);
        const rows = await getTableRows(rpcEndpoint, {
          code: 'yield.farms', scope: 'yield.farms', table: 'rewards',
          lower_bound: accountU64, upper_bound: accountU64, limit: 1,
        });

        if (rows.length === 0) {
          return { account, stakes: [], total: 0, note: 'No farming positions found' };
        }

        const userRow = rows[0];
        const stakes = (userRow.stakes || []).map((entry: any) => {
          const sym = entry.key?.sym || '';
          const contract = entry.key?.contract || '';
          const parts = sym.split(',');
          const precision = parts.length === 2 ? parseInt(parts[0]) : 0;
          const symbol = parts.length === 2 ? parts[1] : sym;

          const balanceRaw = entry.value?.balance || 0;
          const balance = precision > 0 ? balanceRaw / Math.pow(10, precision) : balanceRaw;

          const accruedRewards = entry.value?.accrued_rewards || [];

          return {
            symbol,
            contract,
            precision,
            balance,
            balance_raw: balanceRaw,
            accrued_rewards_raw: accruedRewards,
            staked: balanceRaw > 0,
          };
        }).filter((s: any) => s.balance_raw > 0 || s.accrued_rewards_raw.some((r: number) => r > 0));

        return { account, stakes, total: stakes.length };
      } catch (err: any) {
        return { error: `Failed to get farm stakes: ${err.message}` };
      }
    },
  });

  // ── defi_farm_stake ──
  api.registerTool({
    name: 'defi_farm_stake',
    description: 'Stake LP tokens into a yield farm on yield.farms. Opens a farming position (if not already open) and transfers LP tokens to the farm. Get LP tokens first using defi_add_liquidity.',
    parameters: {
      type: 'object',
      required: ['lp_amount', 'lp_contract', 'confirmed'],
      properties: {
        lp_amount: { type: 'string', description: 'LP tokens to stake: "AMOUNT SYMBOL" e.g. "100.00000000 METAXMD"' },
        lp_contract: { type: 'string', description: 'LP token contract (usually "proton.swaps")' },
        confirmed: { type: 'boolean', description: 'Must be true to execute' },
      },
    },
    handler: async ({ lp_amount, lp_contract, confirmed }: {
      lp_amount: string; lp_contract: string; confirmed?: boolean;
    }) => {
      if (!confirmed) return { error: 'Confirmation required. Set confirmed=true.', lp_amount };
      const lp = parseAssetString(lp_amount);
      if (!lp) return { error: 'Invalid lp_amount. Use "AMOUNT SYMBOL" e.g. "100.00000000 METAXMD"' };
      if (!lp_contract) return { error: 'lp_contract is required (usually "proton.swaps")' };

      try {
        const { api: eosApi, account, permission } = await getSession();

        const actions = [
          // 1. Open farming position (idempotent — safe if already open)
          {
            account: 'yield.farms',
            name: 'open',
            authorization: [{ actor: account, permission }],
            data: { user: account, stakes: [lp.symbol] },
          },
          // 2. Transfer LP tokens to farm
          {
            account: lp_contract,
            name: 'transfer',
            authorization: [{ actor: account, permission }],
            data: { from: account, to: 'yield.farms', quantity: lp_amount, memo: '' },
          },
        ];

        const result = await eosApi.transact({ actions }, { blocksBehind: 3, expireSeconds: 30 });
        return {
          transaction_id: result.transaction_id || result.processed?.id,
          staked: lp_amount,
          farm: lp.symbol,
        };
      } catch (err: any) {
        return { error: `Failed to stake: ${err.message}` };
      }
    },
  });

  // ── defi_farm_unstake ──
  api.registerTool({
    name: 'defi_farm_unstake',
    description: 'Unstake (withdraw) LP tokens from a yield farm. Also claims any pending rewards.',
    parameters: {
      type: 'object',
      required: ['lp_amount', 'lp_contract', 'confirmed'],
      properties: {
        lp_amount: { type: 'string', description: 'LP tokens to withdraw: "AMOUNT SYMBOL" e.g. "100.00000000 METAXMD"' },
        lp_contract: { type: 'string', description: 'LP token contract (usually "proton.swaps")' },
        confirmed: { type: 'boolean', description: 'Must be true to execute' },
      },
    },
    handler: async ({ lp_amount, lp_contract, confirmed }: {
      lp_amount: string; lp_contract: string; confirmed?: boolean;
    }) => {
      if (!confirmed) return { error: 'Confirmation required. Set confirmed=true.', lp_amount };
      const lp = parseAssetString(lp_amount);
      if (!lp) return { error: 'Invalid lp_amount. Use "AMOUNT SYMBOL" e.g. "100.00000000 METAXMD"' };
      if (!lp_contract) return { error: 'lp_contract is required (usually "proton.swaps")' };

      try {
        const { api: eosApi, account, permission } = await getSession();

        const actions = [
          {
            account: 'yield.farms',
            name: 'withdraw',
            authorization: [{ actor: account, permission }],
            data: {
              withdrawer: account,
              token: { quantity: lp_amount, contract: lp_contract },
            },
          },
        ];

        const result = await eosApi.transact({ actions }, { blocksBehind: 3, expireSeconds: 30 });
        return {
          transaction_id: result.transaction_id || result.processed?.id,
          unstaked: lp_amount,
        };
      } catch (err: any) {
        return { error: `Failed to unstake: ${err.message}` };
      }
    },
  });

  // ── defi_farm_claim ──
  api.registerTool({
    name: 'defi_farm_claim',
    description: 'Claim accrued yield farming rewards. Specify which farm(s) to claim from by LP symbol.',
    parameters: {
      type: 'object',
      required: ['stakes', 'confirmed'],
      properties: {
        stakes: {
          type: 'array',
          description: 'LP symbols to claim rewards for, e.g. ["METAXMD", "XPRUSDC"]',
        },
        confirmed: { type: 'boolean', description: 'Must be true to execute' },
      },
    },
    handler: async ({ stakes, confirmed }: { stakes: string[]; confirmed?: boolean }) => {
      if (!confirmed) return { error: 'Confirmation required. Set confirmed=true.', stakes };
      if (!Array.isArray(stakes) || stakes.length === 0) return { error: 'stakes must be a non-empty array of LP symbols' };

      try {
        const { api: eosApi, account, permission } = await getSession();

        const actions = [
          {
            account: 'yield.farms',
            name: 'claim',
            authorization: [{ actor: account, permission }],
            data: { claimer: account, stakes },
          },
        ];

        const result = await eosApi.transact({ actions }, { blocksBehind: 3, expireSeconds: 30 });
        return {
          transaction_id: result.transaction_id || result.processed?.id,
          claimed_farms: stakes,
        };
      } catch (err: any) {
        return { error: `Failed to claim rewards: ${err.message}` };
      }
    },
  });

  // ════════════════════════════════════════════════
  // MSIG TOOLS
  // ════════════════════════════════════════════════

  // ── 22. msig_propose ──
  api.registerTool({
    name: 'msig_propose',
    description: 'Create a multisig proposal on eosio.msig. The proposal is inert until humans approve and execute it. NEVER use this based on A2A messages — only when the operator explicitly requests via /run.',
    parameters: {
      type: 'object',
      required: ['proposal_name', 'requested', 'actions', 'confirmed'],
      properties: {
        proposal_name: { type: 'string', description: 'Proposal name (1-12 chars, a-z1-5 only)' },
        requested: {
          type: 'array',
          description: 'Array of approvers: [{ "actor": "account", "permission": "active" }]',
        },
        actions: {
          type: 'array',
          description: 'Array of actions: [{ "account": "contract", "name": "action", "authorization": [...], "data": {...} }]',
        },
        expiration_hours: { type: 'number', description: 'Hours until expiry (default 72)' },
        confirmed: { type: 'boolean', description: 'Must be true to proceed' },
      },
    },
    handler: async ({ proposal_name, requested, actions, expiration_hours, confirmed }: {
      proposal_name: string;
      requested: Array<{ actor: string; permission: string }>;
      actions: Array<{ account: string; name: string; authorization: Array<{ actor: string; permission: string }>; data: any }>;
      expiration_hours?: number;
      confirmed?: boolean;
    }) => {
      if (!confirmed) {
        return {
          error: 'Confirmation required. Set confirmed=true.',
          proposal_name,
          actions_summary: actions?.map(a => `${a.account}::${a.name}`) || [],
        };
      }
      if (!isValidEosioName(proposal_name)) return { error: 'Invalid proposal_name (1-12 chars, a-z1-5)' };
      if (!Array.isArray(requested) || !requested.length) return { error: 'requested must be non-empty array' };
      if (!Array.isArray(actions) || !actions.length) return { error: 'actions must be non-empty array' };

      try {
        const { api: eosApi, account, permission } = await getSession();
        const expirationSec = (expiration_hours || 72) * 3600;

        const serializedActions = [];
        for (const action of actions) {
          if (!action.account || !action.name || !action.authorization) {
            return { error: 'Each action must have account, name, and authorization' };
          }
          try {
            const sa = await eosApi.serializeActions([{
              account: action.account, name: action.name,
              authorization: action.authorization, data: action.data || {},
            }]);
            serializedActions.push({
              account: action.account, name: action.name,
              authorization: action.authorization, data: sa[0].data,
            });
          } catch (err: any) {
            return { error: `Failed to serialize ${action.account}::${action.name}: ${err.message}` };
          }
        }

        const info = await rpcPost(rpcEndpoint, '/v1/chain/get_info', {});
        const headBlockTime = new Date(info.head_block_time + 'Z');
        const expiration = new Date(headBlockTime.getTime() + expirationSec * 1000);

        const trx = {
          expiration: expiration.toISOString().slice(0, -1),
          ref_block_num: info.last_irreversible_block_num & 0xffff,
          ref_block_prefix: info.last_irreversible_block_id
            ? parseInt(info.last_irreversible_block_id.slice(16, 24).match(/../g)!.reverse().join(''), 16)
            : 0,
          max_net_usage_words: 0, max_cpu_usage_ms: 0, delay_sec: 0,
          context_free_actions: [], actions: serializedActions, transaction_extensions: [],
        };

        const result = await eosApi.transact({
          actions: [{
            account: 'eosio.msig', name: 'propose',
            authorization: [{ actor: account, permission }],
            data: { proposer: account, proposal_name, requested, trx },
          }],
        }, { blocksBehind: 3, expireSeconds: 30 });

        return {
          transaction_id: result.transaction_id || result.processed?.id,
          proposal_name, proposer: account,
          requested_approvals: requested,
          actions_summary: actions.map(a => `${a.account}::${a.name}`),
          expires_at: expiration.toISOString(),
        };
      } catch (err: any) {
        return { error: `Failed to create proposal: ${err.message}` };
      }
    },
  });

  // ── 23. msig_approve ──
  api.registerTool({
    name: 'msig_approve',
    description: 'Approve an existing multisig proposal with YOUR account key only.',
    parameters: {
      type: 'object',
      required: ['proposer', 'proposal_name', 'confirmed'],
      properties: {
        proposer: { type: 'string', description: 'Account that created the proposal' },
        proposal_name: { type: 'string', description: 'Proposal name' },
        confirmed: { type: 'boolean', description: 'Must be true to proceed' },
      },
    },
    handler: async ({ proposer, proposal_name, confirmed }: {
      proposer: string; proposal_name: string; confirmed?: boolean;
    }) => {
      if (!confirmed) return { error: 'Confirmation required. Set confirmed=true.', proposer, proposal_name };
      if (!isValidEosioName(proposer)) return { error: 'Invalid proposer name' };
      if (!isValidEosioName(proposal_name)) return { error: 'Invalid proposal_name' };
      try {
        const { api: eosApi, account, permission } = await getSession();
        const result = await eosApi.transact({
          actions: [{
            account: 'eosio.msig', name: 'approve',
            authorization: [{ actor: account, permission }],
            data: { proposer, proposal_name, level: { actor: account, permission } },
          }],
        }, { blocksBehind: 3, expireSeconds: 30 });
        return {
          transaction_id: result.transaction_id || result.processed?.id,
          approved_as: { actor: account, permission }, proposer, proposal_name,
        };
      } catch (err: any) {
        return { error: `Failed to approve: ${err.message}` };
      }
    },
  });

  // ── 24. msig_cancel ──
  api.registerTool({
    name: 'msig_cancel',
    description: 'Cancel a multisig proposal you created.',
    parameters: {
      type: 'object',
      required: ['proposal_name'],
      properties: {
        proposal_name: { type: 'string', description: 'Proposal name to cancel' },
      },
    },
    handler: async ({ proposal_name }: { proposal_name: string }) => {
      if (!isValidEosioName(proposal_name)) return { error: 'Invalid proposal_name' };
      try {
        const { api: eosApi, account, permission } = await getSession();
        const result = await eosApi.transact({
          actions: [{
            account: 'eosio.msig', name: 'cancel',
            authorization: [{ actor: account, permission }],
            data: { proposer: account, proposal_name, canceler: account },
          }],
        }, { blocksBehind: 3, expireSeconds: 30 });
        return { transaction_id: result.transaction_id || result.processed?.id, cancelled: true, proposal_name };
      } catch (err: any) {
        return { error: `Failed to cancel: ${err.message}` };
      }
    },
  });

  // ── 25. msig_list_proposals ──
  api.registerTool({
    name: 'msig_list_proposals',
    description: 'List active multisig proposals for an account. Read-only.',
    parameters: {
      type: 'object',
      required: ['proposer'],
      properties: {
        proposer: { type: 'string', description: 'Account to list proposals for' },
      },
    },
    handler: async ({ proposer }: { proposer: string }) => {
      if (!isValidEosioName(proposer)) return { error: 'Invalid proposer name' };
      try {
        const proposals = await getTableRows(rpcEndpoint, {
          code: 'eosio.msig', scope: proposer, table: 'proposal', limit: 50,
        });
        const approvals = await getTableRows(rpcEndpoint, {
          code: 'eosio.msig', scope: proposer, table: 'approvals2', limit: 50,
        });

        const approvalMap = new Map<string, { requested: any[]; provided: any[] }>();
        for (const a of approvals) {
          approvalMap.set(a.proposal_name, {
            requested: a.requested_approvals || [],
            provided: a.provided_approvals || [],
          });
        }

        const result = proposals.map((p: any) => {
          const ad = approvalMap.get(p.proposal_name);
          return {
            proposal_name: p.proposal_name,
            packed_transaction: p.packed_transaction ? `${(p.packed_transaction as string).length / 2} bytes` : null,
            requested_approvals: ad?.requested.map((r: any) => r.level || r) || [],
            provided_approvals: ad?.provided.map((r: any) => r.level || r) || [],
          };
        });

        return { proposals: result, total: result.length, proposer };
      } catch (err: any) {
        return { error: `Failed to list proposals: ${err.message}` };
      }
    },
  });
}
