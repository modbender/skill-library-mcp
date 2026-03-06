/**
 * XMD Skill — Metal Dollar stablecoin (xmd.token / xmd.treasury)
 *
 * Read-only tools use fetch-based RPC helpers (no signing).
 * Write tools create a session from env vars for signing transactions.
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

// ── Constants ────────────────────────────────────

const XMD_TOKEN = 'xmd.token';
const XMD_TREASURY = 'xmd.treasury';
const XMD_SYMBOL = 'XMD';
const XMD_PRECISION = 6;
const ORACLE_CONTRACT = 'oracles';

const MAINNET_RPC = 'https://xpr-mainnet-rpc.saltant.io';

// ── RPC Helper ───────────────────────────────────

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
  limit?: number; key_type?: string; json?: boolean;
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
  });
  return result.rows || [];
}

// ── Session Factory ──────────────────────────────

let cachedSession: { api: any; account: string; permission: string } | null = null;

async function getXmdSession(): Promise<{ api: any; account: string; permission: string }> {
  if (cachedSession) return cachedSession;

  const privateKey = process.env.XPR_PRIVATE_KEY;
  const account = process.env.XPR_ACCOUNT;
  const permission = process.env.XPR_PERMISSION || 'active';

  if (!privateKey) throw new Error('XPR_PRIVATE_KEY is required for XMD write operations');
  if (!account) throw new Error('XPR_ACCOUNT is required for XMD write operations');

  const { Api, JsonRpc, JsSignatureProvider } = await import('@proton/js');
  const rpc = new JsonRpc(MAINNET_RPC);
  const signatureProvider = new JsSignatureProvider([privateKey]);
  const api = new Api({ rpc, signatureProvider });

  cachedSession = { api, account, permission };
  return cachedSession;
}

// ── Helpers ──────────────────────────────────────

function parseExtSym(sym: any): { precision: number; symbol: string; contract: string } | null {
  if (!sym) return null;
  const symStr = sym.sym || '';
  const parts = symStr.split(',');
  if (parts.length !== 2) return null;
  return { precision: parseInt(parts[0]) || 0, symbol: parts[1].trim(), contract: sym.contract || '' };
}

function formatAsset(amount: number, precision: number, symbol: string): string {
  return `${amount.toFixed(precision)} ${symbol}`;
}

function parseQuantity(qty: string): { amount: number; symbol: string; precision: number } | null {
  const parts = qty.trim().split(' ');
  if (parts.length !== 2) return null;
  const decParts = parts[0].split('.');
  return {
    amount: parseFloat(parts[0]),
    symbol: parts[1],
    precision: decParts.length > 1 ? decParts[1].length : 0,
  };
}

async function getOraclePrice(endpoint: string, feedIndex: number): Promise<{ price: number; providers: any[] } | null> {
  try {
    const rows = await getTableRows(endpoint, {
      code: ORACLE_CONTRACT, scope: ORACLE_CONTRACT, table: 'data',
      lower_bound: feedIndex, upper_bound: feedIndex, limit: 1,
    });
    if (rows.length === 0) return null;
    const row = rows[0];
    const price = row.aggregate?.d_double ? parseFloat(row.aggregate.d_double) : 0;
    const providers = (row.points || []).map((p: any) => ({
      provider: p.provider,
      price: p.data?.d_double ? parseFloat(p.data.d_double) : 0,
      time: p.time,
    }));
    return { price, providers };
  } catch {
    return null;
  }
}

async function getOracleFeedName(endpoint: string, feedIndex: number): Promise<string | null> {
  try {
    const rows = await getTableRows(endpoint, {
      code: ORACLE_CONTRACT, scope: ORACLE_CONTRACT, table: 'feeds',
      lower_bound: feedIndex, upper_bound: feedIndex, limit: 1,
    });
    return rows.length > 0 ? rows[0].name || null : null;
  } catch {
    return null;
  }
}

// ── Skill Entry Point ────────────────────────────

export default function xmdSkill(api: SkillApi): void {
  const config = api.getConfig();
  const rpcEndpoint = MAINNET_RPC;

  // ════════════════════════════════════════════════
  // READ-ONLY TOOLS
  // ════════════════════════════════════════════════

  // ── 1. xmd_get_config ──
  api.registerTool({
    name: 'xmd_get_config',
    description: 'Get XMD treasury global configuration — paused state, fee account, minimum oracle price threshold for minting/redeeming.',
    parameters: {
      type: 'object',
      properties: {},
    },
    handler: async () => {
      try {
        const globals = await getTableRows(rpcEndpoint, {
          code: XMD_TREASURY, scope: XMD_TREASURY, table: 'xmdglobals', limit: 1,
        });

        if (globals.length === 0) return { error: 'XMD treasury globals not found' };

        const cfg = globals[0];
        return {
          is_paused: !!cfg.isPaused,
          fee_account: cfg.feeAccount,
          min_oracle_price: parseFloat(cfg.minOraclePrice),
          min_oracle_price_note: 'Collateral oracle price must be >= this value for mint/redeem to proceed',
          contracts: {
            token: XMD_TOKEN,
            treasury: XMD_TREASURY,
            oracles: ORACLE_CONTRACT,
          },
        };
      } catch (err: any) {
        return { error: `Failed to get XMD config: ${err.message}` };
      }
    },
  });

  // ── 2. xmd_list_collateral ──
  api.registerTool({
    name: 'xmd_list_collateral',
    description: 'List all supported XMD collateral tokens with mint/redeem status, fees, oracle prices, max treasury percent, and cumulative mint/redeem volumes.',
    parameters: {
      type: 'object',
      properties: {},
    },
    handler: async () => {
      try {
        const tokens = await getTableRows(rpcEndpoint, {
          code: XMD_TREASURY, scope: XMD_TREASURY, table: 'tokens', limit: 50,
        });

        const collateral = await Promise.all(tokens.map(async (t: any) => {
          const sym = parseExtSym(t.symbol);
          if (!sym) return null;

          // Fetch oracle price
          const oracle = await getOraclePrice(rpcEndpoint, t.oracleIndex);
          const feedName = await getOracleFeedName(rpcEndpoint, t.oracleIndex);

          const amountMinted = parseFloat(t.amountMinted) || 0;
          const amountRedeemed = parseFloat(t.amountRedeemed) || 0;

          return {
            symbol: sym.symbol,
            contract: sym.contract,
            precision: sym.precision,
            is_mint_enabled: !!t.isMintEnabled,
            is_redeem_enabled: !!t.isRedeemEnabled,
            mint_fee_pct: `${(parseFloat(t.mintFee) * 100).toFixed(2)}%`,
            redemption_fee_pct: `${(parseFloat(t.redemptionFee) * 100).toFixed(2)}%`,
            max_treasury_pct: `${parseFloat(t.maxTreasuryPercent).toFixed(0)}%`,
            oracle_feed_index: t.oracleIndex,
            oracle_feed_name: feedName,
            oracle_price: oracle?.price ?? null,
            is_liquidation_enabled: !!t.isLiquidationEnabled,
            total_minted: amountMinted.toFixed(2),
            total_redeemed: amountRedeemed.toFixed(2),
            net_outstanding: (amountMinted - amountRedeemed).toFixed(2),
          };
        }));

        return {
          collateral: collateral.filter(Boolean),
          total_types: collateral.filter(Boolean).length,
          note: 'To mint XMD, transfer a supported stablecoin to xmd.treasury with memo "mint". To redeem, transfer XMD with memo "redeem,SYMBOL".',
        };
      } catch (err: any) {
        return { error: `Failed to list collateral: ${err.message}` };
      }
    },
  });

  // ── 3. xmd_get_supply ──
  api.registerTool({
    name: 'xmd_get_supply',
    description: 'Get XMD total circulating supply and token stats.',
    parameters: {
      type: 'object',
      properties: {},
    },
    handler: async () => {
      try {
        const stats = await getTableRows(rpcEndpoint, {
          code: XMD_TOKEN, scope: XMD_SYMBOL, table: 'stat', limit: 1,
        });

        if (stats.length === 0) return { error: 'XMD token stats not found' };

        const stat = stats[0];
        const supply = parseQuantity(stat.supply);
        const maxSupply = parseQuantity(stat.max_supply);

        return {
          supply: stat.supply,
          supply_amount: supply?.amount ?? 0,
          max_supply: stat.max_supply,
          max_supply_note: maxSupply?.amount === 0 ? 'Unlimited (max_supply = 0)' : stat.max_supply,
          issuer: stat.issuer,
          precision: XMD_PRECISION,
          token_contract: XMD_TOKEN,
        };
      } catch (err: any) {
        return { error: `Failed to get XMD supply: ${err.message}` };
      }
    },
  });

  // ── 4. xmd_get_balance ──
  api.registerTool({
    name: 'xmd_get_balance',
    description: 'Check an account\'s XMD balance. Returns 0 if the account has no XMD.',
    parameters: {
      type: 'object',
      required: ['account'],
      properties: {
        account: { type: 'string', description: 'XPR Network account name' },
      },
    },
    handler: async ({ account }: { account: string }) => {
      if (!account) return { error: 'account is required' };

      try {
        const rows = await getTableRows(rpcEndpoint, {
          code: XMD_TOKEN, scope: account, table: 'accounts', limit: 10,
        });

        const xmdRow = rows.find((r: any) => {
          const parsed = parseQuantity(r.balance);
          return parsed?.symbol === XMD_SYMBOL;
        });

        const balance = xmdRow ? parseQuantity(xmdRow.balance) : null;

        return {
          account,
          balance: balance ? xmdRow.balance : formatAsset(0, XMD_PRECISION, XMD_SYMBOL),
          amount: balance?.amount ?? 0,
        };
      } catch (err: any) {
        return { error: `Failed to get balance: ${err.message}` };
      }
    },
  });

  // ── 5. xmd_get_treasury_reserves ──
  api.registerTool({
    name: 'xmd_get_treasury_reserves',
    description: 'Get current stablecoin reserves held by the XMD treasury, with USD valuations per collateral type and overall collateralization ratio.',
    parameters: {
      type: 'object',
      properties: {},
    },
    handler: async () => {
      try {
        // Get supported tokens config
        const tokens = await getTableRows(rpcEndpoint, {
          code: XMD_TREASURY, scope: XMD_TREASURY, table: 'tokens', limit: 50,
        });

        // Get XMD supply
        const stats = await getTableRows(rpcEndpoint, {
          code: XMD_TOKEN, scope: XMD_SYMBOL, table: 'stat', limit: 1,
        });
        const xmdSupply = stats.length > 0 ? parseQuantity(stats[0].supply)?.amount || 0 : 0;

        // For each collateral token, fetch treasury balance and oracle price
        let totalReservesUsd = 0;
        const reserves = await Promise.all(tokens.map(async (t: any) => {
          const sym = parseExtSym(t.symbol);
          if (!sym) return null;

          // Fetch treasury's balance of this token
          const balRows = await getTableRows(rpcEndpoint, {
            code: sym.contract, scope: XMD_TREASURY, table: 'accounts', limit: 50,
          });
          const balRow = balRows.find((r: any) => {
            const p = parseQuantity(r.balance);
            return p?.symbol === sym.symbol;
          });
          const balance = balRow ? parseQuantity(balRow.balance) : null;
          const balAmount = balance?.amount ?? 0;

          // Fetch oracle price
          const oracle = await getOraclePrice(rpcEndpoint, t.oracleIndex);
          const price = oracle?.price ?? 1.0;
          const usdValue = balAmount * price;
          totalReservesUsd += usdValue;

          // Calculate this token's share of treasury
          const treasuryPct = xmdSupply > 0 ? (usdValue / xmdSupply * 100) : 0;

          return {
            symbol: sym.symbol,
            contract: sym.contract,
            balance: balRow?.balance || formatAsset(0, sym.precision, sym.symbol),
            balance_amount: balAmount,
            oracle_price: price,
            usd_value: usdValue.toFixed(2),
            treasury_share_pct: `${treasuryPct.toFixed(1)}%`,
            max_treasury_pct: `${parseFloat(t.maxTreasuryPercent).toFixed(0)}%`,
          };
        }));

        const collateralizationRatio = xmdSupply > 0
          ? (totalReservesUsd / xmdSupply * 100)
          : 0;

        return {
          reserves: reserves.filter(Boolean),
          total_reserves_usd: `$${totalReservesUsd.toLocaleString('en-US', { maximumFractionDigits: 2 })}`,
          total_reserves_raw: totalReservesUsd,
          xmd_supply: formatAsset(xmdSupply, XMD_PRECISION, XMD_SYMBOL),
          xmd_supply_raw: xmdSupply,
          collateralization_ratio_pct: `${collateralizationRatio.toFixed(2)}%`,
          is_fully_collateralized: collateralizationRatio >= 100,
        };
      } catch (err: any) {
        return { error: `Failed to get treasury reserves: ${err.message}` };
      }
    },
  });

  // ── 6. xmd_get_oracle_price ──
  api.registerTool({
    name: 'xmd_get_oracle_price',
    description: 'Get the current oracle price for an XMD collateral token (e.g. XUSDC, XPAX, XPYUSD, MPD). Shows aggregate price and individual provider prices.',
    parameters: {
      type: 'object',
      required: ['symbol'],
      properties: {
        symbol: { type: 'string', description: 'Collateral token symbol (XUSDC, XPAX, XPYUSD, or MPD)' },
      },
    },
    handler: async ({ symbol }: { symbol: string }) => {
      if (!symbol) return { error: 'symbol is required (XUSDC, XPAX, XPYUSD, or MPD)' };
      const sym = symbol.toUpperCase();

      try {
        // Find the token in treasury config to get oracle index
        const tokens = await getTableRows(rpcEndpoint, {
          code: XMD_TREASURY, scope: XMD_TREASURY, table: 'tokens', limit: 50,
        });

        const token = tokens.find((t: any) => {
          const parsed = parseExtSym(t.symbol);
          return parsed?.symbol === sym;
        });

        if (!token) {
          const available = tokens.map((t: any) => parseExtSym(t.symbol)?.symbol).filter(Boolean);
          return { error: `Token "${sym}" not found. Available: ${available.join(', ')}` };
        }

        const feedName = await getOracleFeedName(rpcEndpoint, token.oracleIndex);
        const oracle = await getOraclePrice(rpcEndpoint, token.oracleIndex);

        if (!oracle) return { error: `Oracle data not available for feed index ${token.oracleIndex}` };

        return {
          symbol: sym,
          oracle_feed_index: token.oracleIndex,
          oracle_feed_name: feedName,
          aggregate_price: oracle.price,
          providers: oracle.providers.map((p: any) => ({
            provider: p.provider,
            price: p.price,
            last_updated: p.time,
          })),
          provider_count: oracle.providers.length,
        };
      } catch (err: any) {
        return { error: `Failed to get oracle price: ${err.message}` };
      }
    },
  });

  // ════════════════════════════════════════════════
  // WRITE TOOLS (require confirmation)
  // ════════════════════════════════════════════════

  // ── 7. xmd_mint ──
  api.registerTool({
    name: 'xmd_mint',
    description: 'Mint XMD by depositing a supported stablecoin (XUSDC, XPAX, XPYUSD, or MPD). Transfers the stablecoin to xmd.treasury with memo "mint". You receive XMD at the current oracle rate.',
    parameters: {
      type: 'object',
      required: ['collateral_symbol', 'amount', 'confirmed'],
      properties: {
        collateral_symbol: { type: 'string', description: 'Collateral token symbol: XUSDC, XPAX, XPYUSD, or MPD' },
        amount: { type: 'number', description: 'Amount of collateral to deposit (e.g. 100.0 for 100 XUSDC)' },
        confirmed: { type: 'boolean', description: 'Must be true to proceed' },
      },
    },
    handler: async ({ collateral_symbol, amount, confirmed }: {
      collateral_symbol: string; amount: number; confirmed?: boolean;
    }) => {
      if (!confirmed) {
        return {
          error: 'Confirmation required. Set confirmed=true to mint XMD.',
          collateral_symbol, amount,
        };
      }
      if (!collateral_symbol) return { error: 'collateral_symbol is required (XUSDC, XPAX, XPYUSD, or MPD)' };
      if (!amount || amount <= 0) return { error: 'amount must be positive' };

      const sym = collateral_symbol.toUpperCase();

      try {
        // Look up token config
        const tokens = await getTableRows(rpcEndpoint, {
          code: XMD_TREASURY, scope: XMD_TREASURY, table: 'tokens', limit: 50,
        });

        const token = tokens.find((t: any) => {
          const parsed = parseExtSym(t.symbol);
          return parsed?.symbol === sym;
        });

        if (!token) {
          const available = tokens.map((t: any) => parseExtSym(t.symbol)?.symbol).filter(Boolean);
          return { error: `Token "${sym}" not supported. Available: ${available.join(', ')}` };
        }

        if (!token.isMintEnabled) {
          return { error: `Minting with ${sym} is currently disabled` };
        }

        const parsed = parseExtSym(token.symbol);
        if (!parsed) return { error: 'Could not parse token symbol' };

        // Check treasury is not paused
        const globals = await getTableRows(rpcEndpoint, {
          code: XMD_TREASURY, scope: XMD_TREASURY, table: 'xmdglobals', limit: 1,
        });
        if (globals.length > 0 && globals[0].isPaused) {
          return { error: 'XMD treasury is currently paused' };
        }

        const quantity = formatAsset(amount, parsed.precision, parsed.symbol);

        const { api: eosApi, account, permission } = await getXmdSession();

        const result = await eosApi.transact({
          actions: [{
            account: parsed.contract,
            name: 'transfer',
            authorization: [{ actor: account, permission }],
            data: {
              from: account,
              to: XMD_TREASURY,
              quantity,
              memo: 'mint',
            },
          }],
        }, { blocksBehind: 3, expireSeconds: 30 });

        return {
          transaction_id: result.transaction_id || result.processed?.id,
          action: 'mint',
          deposited: quantity,
          deposited_contract: parsed.contract,
          account,
          note: `Deposited ${quantity} to mint XMD at oracle rate. XMD will be sent to your account.`,
        };
      } catch (err: any) {
        return { error: `Failed to mint XMD: ${err.message}` };
      }
    },
  });

  // ── 8. xmd_redeem ──
  api.registerTool({
    name: 'xmd_redeem',
    description: 'Redeem XMD for a supported stablecoin (XUSDC, XPAX, XPYUSD, or MPD). Transfers XMD to xmd.treasury with memo "redeem,SYMBOL". You receive the stablecoin at the current oracle rate.',
    parameters: {
      type: 'object',
      required: ['redeem_for', 'amount', 'confirmed'],
      properties: {
        redeem_for: { type: 'string', description: 'Which stablecoin to receive: XUSDC, XPAX, XPYUSD, or MPD' },
        amount: { type: 'number', description: 'Amount of XMD to redeem (e.g. 100.0)' },
        confirmed: { type: 'boolean', description: 'Must be true to proceed' },
      },
    },
    handler: async ({ redeem_for, amount, confirmed }: {
      redeem_for: string; amount: number; confirmed?: boolean;
    }) => {
      if (!confirmed) {
        return {
          error: 'Confirmation required. Set confirmed=true to redeem XMD.',
          redeem_for, amount,
        };
      }
      if (!redeem_for) return { error: 'redeem_for is required (XUSDC, XPAX, XPYUSD, or MPD)' };
      if (!amount || amount <= 0) return { error: 'amount must be positive' };

      const sym = redeem_for.toUpperCase();

      try {
        // Validate the target collateral exists and redeem is enabled
        const tokens = await getTableRows(rpcEndpoint, {
          code: XMD_TREASURY, scope: XMD_TREASURY, table: 'tokens', limit: 50,
        });

        const token = tokens.find((t: any) => {
          const parsed = parseExtSym(t.symbol);
          return parsed?.symbol === sym;
        });

        if (!token) {
          const available = tokens.map((t: any) => parseExtSym(t.symbol)?.symbol).filter(Boolean);
          return { error: `Token "${sym}" not supported. Available: ${available.join(', ')}` };
        }

        if (!token.isRedeemEnabled) {
          return { error: `Redeeming for ${sym} is currently disabled` };
        }

        // Check treasury is not paused
        const globals = await getTableRows(rpcEndpoint, {
          code: XMD_TREASURY, scope: XMD_TREASURY, table: 'xmdglobals', limit: 1,
        });
        if (globals.length > 0 && globals[0].isPaused) {
          return { error: 'XMD treasury is currently paused' };
        }

        const quantity = formatAsset(amount, XMD_PRECISION, XMD_SYMBOL);

        const { api: eosApi, account, permission } = await getXmdSession();

        const result = await eosApi.transact({
          actions: [{
            account: XMD_TOKEN,
            name: 'transfer',
            authorization: [{ actor: account, permission }],
            data: {
              from: account,
              to: XMD_TREASURY,
              quantity,
              memo: `redeem,${sym}`,
            },
          }],
        }, { blocksBehind: 3, expireSeconds: 30 });

        return {
          transaction_id: result.transaction_id || result.processed?.id,
          action: 'redeem',
          redeemed: quantity,
          redeem_for: sym,
          account,
          note: `Sent ${quantity} to treasury to redeem for ${sym} at oracle rate.`,
        };
      } catch (err: any) {
        return { error: `Failed to redeem XMD: ${err.message}` };
      }
    },
  });
}
