/**
 * Lending Skill — LOAN Protocol (lending.loan) on XPR Network
 *
 * Read-only tools use fetch-based RPC helpers (no signing).
 * Write tools create a session from env vars for signing transactions.
 *
 * IMPORTANT: LOAN Protocol is mainnet only.
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

const LENDING_CONTRACT = 'lending.loan';
const LOAN_TOKEN_CONTRACT = 'loan.token';
const LOAN_TOKEN_SYMBOL = 'LOAN';

// Mainnet RPC endpoints (LOAN Protocol is mainnet only)
const MAINNET_RPC = 'https://xpr-mainnet-rpc.saltant.io';

// Metal X API for APY/TVL stats
const METALX_LOAN_API = 'https://identity.api.prod.metalx.com/v1/loan/stats';
const VALID_DAYS = [7, 30, 90];

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
  limit?: number; key_type?: string; index_position?: string;
  json?: boolean;
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
  });
  return result.rows || [];
}

// ── Metal X API Helper ───────────────────────────

async function metalXLoanGet(path: string): Promise<any> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), RPC_TIMEOUT);
  try {
    const resp = await fetch(`${METALX_LOAN_API}${path}`, {
      signal: controller.signal,
      headers: { 'Accept': 'application/json' },
    });
    if (!resp.ok) {
      const text = await resp.text().catch(() => '');
      throw new Error(`Metal X loan API failed (${resp.status}): ${text.slice(0, 200)}`);
    }
    return await resp.json();
  } finally {
    clearTimeout(timer);
  }
}

// ── Session Factory ──────────────────────────────

let cachedSession: { api: any; account: string; permission: string } | null = null;

async function getLendingSession(): Promise<{ api: any; account: string; permission: string }> {
  if (cachedSession) return cachedSession;

  const privateKey = process.env.XPR_PRIVATE_KEY;
  const account = process.env.XPR_ACCOUNT;
  const permission = process.env.XPR_PERMISSION || 'active';

  if (!privateKey) throw new Error('XPR_PRIVATE_KEY is required for lending write operations');
  if (!account) throw new Error('XPR_ACCOUNT is required for lending write operations');

  const { Api, JsonRpc, JsSignatureProvider } = await import('@proton/js');
  const rpc = new JsonRpc(MAINNET_RPC);
  const signatureProvider = new JsSignatureProvider([privateKey]);
  const api = new Api({ rpc, signatureProvider });

  cachedSession = { api, account, permission };
  return cachedSession;
}

// ── Helper: Parse extended_symbol ────────────────

function parseExtSym(sym: any): { precision: number; symbol: string; contract: string } | null {
  if (!sym) return null;
  // Format from chain: { sym: "8,LBTC", contract: "shares.loan" }
  const symStr = sym.sym || sym.symbol || '';
  const parts = symStr.split(',');
  if (parts.length !== 2) return null;
  return {
    precision: parseInt(parts[0]) || 0,
    symbol: parts[1].trim(),
    contract: sym.contract || '',
  };
}

// ── Helper: Format asset ─────────────────────────

function formatAsset(amount: number | string, precision: number, symbol: string): string {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;
  return `${num.toFixed(precision)} ${symbol}`;
}

// ── Helper: Parse quantity string ────────────────

function parseQuantity(qty: string): { amount: number; symbol: string } | null {
  const parts = qty.trim().split(' ');
  if (parts.length !== 2) return null;
  return { amount: parseFloat(parts[0]), symbol: parts[1] };
}

// ── Skill Entry Point ────────────────────────────

export default function lendingSkill(api: SkillApi): void {
  const config = api.getConfig();
  // LOAN Protocol is mainnet only — always use mainnet RPC
  const rpcEndpoint = MAINNET_RPC;

  // ════════════════════════════════════════════════
  // READ-ONLY TOOLS
  // ════════════════════════════════════════════════

  // ── 1. loan_list_markets ──
  api.registerTool({
    name: 'loan_list_markets',
    description: 'List all LOAN Protocol lending markets with interest models, collateral factors, utilization, and reserves. Mainnet only.',
    parameters: {
      type: 'object',
      properties: {},
    },
    handler: async () => {
      try {
        const markets = await getTableRows(rpcEndpoint, {
          code: LENDING_CONTRACT, scope: LENDING_CONTRACT, table: 'markets', limit: 50,
        });

        return {
          markets: markets.map((m: any) => {
            const share = parseExtSym(m.share_symbol);
            const underlying = parseExtSym(m.underlying_symbol);

            // Calculate utilization from borrows and cash
            const totalVarBorrows = m.total_variable_borrows
              ? parseFloat((m.total_variable_borrows.quantity || '0').split(' ')[0])
              : 0;
            const totalStableBorrows = m.total_stable_borrows
              ? parseFloat((m.total_stable_borrows.quantity || '0').split(' ')[0])
              : 0;
            const totalReserves = m.total_reserves
              ? parseFloat((m.total_reserves.quantity || '0').split(' ')[0])
              : 0;

            return {
              market_symbol: share?.symbol || 'unknown',
              underlying_symbol: underlying?.symbol || 'unknown',
              share_contract: share?.contract || '',
              underlying_contract: underlying?.contract || '',
              precision: underlying?.precision || 0,
              collateral_factor: m.collateral_factor,
              reserve_factor: m.reserve_factor,
              borrow_index: m.borrow_index,
              stable_loans_enabled: m.stable_loans_enabled,
              total_variable_borrows: m.total_variable_borrows?.quantity || '0',
              total_stable_borrows: m.total_stable_borrows?.quantity || '0',
              total_reserves: m.total_reserves?.quantity || '0',
              average_stable_rate: m.average_stable_rate,
              variable_interest_model: m.variable_interest_model,
              oracle_feed_index: m.oracle_feed_index,
            };
          }),
          total: markets.length,
          note: 'LOAN Protocol is mainnet only. Collateral factors indicate max borrow percentage of collateral value.',
        };
      } catch (err: any) {
        return { error: `Failed to list markets: ${err.message}` };
      }
    },
  });

  // ── 2. loan_get_market ──
  api.registerTool({
    name: 'loan_get_market',
    description: 'Get detailed info for a specific LOAN Protocol lending market by L-token symbol (e.g. "LBTC", "LUSDC"). Returns interest model, collateral factor, reserves, and utilization.',
    parameters: {
      type: 'object',
      required: ['market_symbol'],
      properties: {
        market_symbol: { type: 'string', description: 'L-token symbol e.g. "LBTC", "LUSDC", "LXPR"' },
      },
    },
    handler: async ({ market_symbol }: { market_symbol: string }) => {
      if (!market_symbol) return { error: 'market_symbol is required (e.g. "LBTC")' };
      const sym = market_symbol.toUpperCase();

      try {
        const markets = await getTableRows(rpcEndpoint, {
          code: LENDING_CONTRACT, scope: LENDING_CONTRACT, table: 'markets', limit: 50,
        });

        const market = markets.find((m: any) => {
          const share = parseExtSym(m.share_symbol);
          return share?.symbol === sym;
        });

        if (!market) {
          const available = markets.map((m: any) => parseExtSym(m.share_symbol)?.symbol).filter(Boolean);
          return { error: `Market "${sym}" not found. Available: ${available.join(', ')}` };
        }

        const share = parseExtSym(market.share_symbol);
        const underlying = parseExtSym(market.underlying_symbol);

        // Also fetch reward config for this market
        let rewardConfig: any = null;
        try {
          const rewardsCfg = await getTableRows(rpcEndpoint, {
            code: LENDING_CONTRACT, scope: LENDING_CONTRACT, table: 'rewards.cfg', limit: 50,
          });
          rewardConfig = rewardsCfg.find((r: any) => r.market_symbol === sym);
        } catch { /* rewards.cfg table may not exist */ }

        return {
          market_symbol: share?.symbol,
          underlying_symbol: underlying?.symbol,
          share_contract: share?.contract,
          underlying_contract: underlying?.contract,
          precision: underlying?.precision,
          collateral_factor: market.collateral_factor,
          collateral_factor_pct: `${((market.collateral_factor || 0) * 100).toFixed(0)}%`,
          reserve_factor: market.reserve_factor,
          reserve_factor_pct: `${((market.reserve_factor || 0) * 100).toFixed(0)}%`,
          borrow_index: market.borrow_index,
          stable_loans_enabled: market.stable_loans_enabled,
          max_stable_borrow_percentage: market.max_stable_borrow_percentage,
          total_variable_borrows: market.total_variable_borrows?.quantity || '0',
          total_stable_borrows: market.total_stable_borrows?.quantity || '0',
          total_reserves: market.total_reserves?.quantity || '0',
          average_stable_rate: market.average_stable_rate,
          variable_interest_model: market.variable_interest_model,
          stable_interest_model: market.stable_interest_model,
          oracle_feed_index: market.oracle_feed_index,
          variable_accrual_time: market.variable_accrual_time,
          stable_accrual_time: market.stable_accrual_time,
          rewards: rewardConfig ? {
            supplier_rewards_per_half_second: rewardConfig.supplier_rewards_per_half_second,
            borrower_rewards_per_half_second: rewardConfig.borrower_rewards_per_half_second,
            supply_index: rewardConfig.supply_index,
            borrow_index: rewardConfig.borrow_index,
          } : null,
        };
      } catch (err: any) {
        return { error: `Failed to get market: ${err.message}` };
      }
    },
  });

  // ── 3. loan_get_user_positions ──
  api.registerTool({
    name: 'loan_get_user_positions',
    description: 'Get a user\'s supply (L-token shares) and borrow positions across all LOAN Protocol markets.',
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
        // All lending tables are scoped by lending.loan, keyed by account name
        const shares = await getTableRows(rpcEndpoint, {
          code: LENDING_CONTRACT, scope: LENDING_CONTRACT, table: 'shares',
          lower_bound: account, upper_bound: account, limit: 1, key_type: 'name',
        });

        const borrows = await getTableRows(rpcEndpoint, {
          code: LENDING_CONTRACT, scope: LENDING_CONTRACT, table: 'borrows',
          lower_bound: account, upper_bound: account, limit: 1, key_type: 'name',
        });

        // Parse share positions
        const supplyPositions = shares.flatMap((row: any) => {
          if (!row.tokens || !Array.isArray(row.tokens)) return [];
          return row.tokens.map((t: any) => {
            const sym = parseExtSym(t.key);
            return {
              market_symbol: sym?.symbol || 'unknown',
              contract: sym?.contract || '',
              balance_raw: t.value,
              balance: sym ? formatAsset(t.value / Math.pow(10, sym.precision), sym.precision, sym.symbol) : String(t.value),
            };
          });
        });

        // Parse borrow positions
        const borrowPositions = borrows.flatMap((row: any) => {
          if (!row.tokens || !Array.isArray(row.tokens)) return [];
          return row.tokens.map((t: any) => {
            const sym = parseExtSym(t.key);
            const snapshot = t.value || {};
            return {
              underlying_symbol: sym?.symbol || 'unknown',
              contract: sym?.contract || '',
              variable_principal_raw: snapshot.variable_principal || 0,
              variable_principal: sym
                ? formatAsset((snapshot.variable_principal || 0) / Math.pow(10, sym.precision), sym.precision, sym.symbol)
                : String(snapshot.variable_principal || 0),
              stable_principal_raw: snapshot.stable_principal || 0,
              stable_principal: sym
                ? formatAsset((snapshot.stable_principal || 0) / Math.pow(10, sym.precision), sym.precision, sym.symbol)
                : String(snapshot.stable_principal || 0),
              stable_rate: snapshot.stable_rate,
              last_stable_update: snapshot.last_stable_update,
              variable_interest_index: snapshot.variable_interest_index,
            };
          });
        });

        return {
          account,
          supply_positions: supplyPositions,
          borrow_positions: borrowPositions,
          has_supply: supplyPositions.length > 0,
          has_borrows: borrowPositions.length > 0,
        };
      } catch (err: any) {
        return { error: `Failed to get user positions: ${err.message}` };
      }
    },
  });

  // ── 4. loan_get_user_rewards ──
  api.registerTool({
    name: 'loan_get_user_rewards',
    description: 'Get a user\'s unclaimed LOAN token rewards per market. Call loan_claim_rewards to claim them.',
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
        // User rewards — scoped by lending.loan, keyed by account name
        const rewards = await getTableRows(rpcEndpoint, {
          code: LENDING_CONTRACT, scope: LENDING_CONTRACT, table: 'rewards',
          lower_bound: account, upper_bound: account, limit: 1, key_type: 'name',
        });

        // Global reward config per market
        const globalRewards = await getTableRows(rpcEndpoint, {
          code: LENDING_CONTRACT, scope: LENDING_CONTRACT, table: 'rewards.cfg', limit: 50,
        });

        const rewardPositions = rewards.flatMap((row: any) => {
          if (!row.markets || !Array.isArray(row.markets)) return [];
          return row.markets.map((m: any) => {
            const snapshot = m.value || {};
            // LOAN token has precision 4
            const accruedFormatted = formatAsset((snapshot.accrued_amount || 0) / 10000, 4, LOAN_TOKEN_SYMBOL);
            return {
              market_symbol: m.key,
              accrued_amount_raw: snapshot.accrued_amount || 0,
              accrued_amount: accruedFormatted,
              borrower_index: snapshot.borrower_index,
              supplier_index: snapshot.supplier_index,
            };
          });
        });

        const totalAccrued = rewardPositions.reduce(
          (sum: number, p: any) => sum + (p.accrued_amount_raw || 0),
          0,
        );

        return {
          account,
          rewards: rewardPositions,
          total_unclaimed: formatAsset(totalAccrued / 10000, 4, LOAN_TOKEN_SYMBOL),
          total_unclaimed_raw: totalAccrued,
          note: 'Call loan_claim_rewards to claim. Combine with update.user action for up-to-date amounts.',
        };
      } catch (err: any) {
        return { error: `Failed to get user rewards: ${err.message}` };
      }
    },
  });

  // ── 5. loan_get_config ──
  api.registerTool({
    name: 'loan_get_config',
    description: 'Get global LOAN Protocol lending configuration (oracle contract, close factor for liquidations, liquidation incentive, reward token).',
    parameters: {
      type: 'object',
      properties: {},
    },
    handler: async () => {
      try {
        const globals = await getTableRows(rpcEndpoint, {
          code: LENDING_CONTRACT, scope: LENDING_CONTRACT, table: 'globals.cfg', limit: 1,
        });

        if (globals.length === 0) {
          return { error: 'Global config not found' };
        }

        const cfg = globals[0];
        return {
          oracle_contract: cfg.oracle_contract,
          close_factor: cfg.close_factor,
          close_factor_pct: `${((cfg.close_factor || 0) * 100).toFixed(1)}%`,
          liquidation_incentive: cfg.liquidation_incentive,
          liquidation_incentive_pct: `${((cfg.liquidation_incentive || 0) * 100).toFixed(1)}%`,
          reward_symbol: cfg.reward_symbol,
          note: `Close factor = max % of debt repayable per liquidation. Liquidation incentive = discount liquidators get on seized collateral.`,
        };
      } catch (err: any) {
        return { error: `Failed to get config: ${err.message}` };
      }
    },
  });

  // ── 6. loan_get_market_apy ──
  api.registerTool({
    name: 'loan_get_market_apy',
    description: 'Get historical APY (annual percentage yield) for a lending market. Returns deposit and borrow APYs including LOAN token rewards. Data from Metal X API.',
    parameters: {
      type: 'object',
      required: ['underlying_symbol'],
      properties: {
        underlying_symbol: { type: 'string', description: 'Underlying token symbol e.g. "XBTC", "XUSDC", "XPR"' },
        days: { type: 'number', description: 'Time period: 7, 30, or 90 days (default 7)' },
      },
    },
    handler: async ({ underlying_symbol, days }: { underlying_symbol: string; days?: number }) => {
      if (!underlying_symbol) return { error: 'underlying_symbol is required (e.g. "XBTC")' };
      const d = VALID_DAYS.includes(days || 0) ? days! : 7;

      try {
        const data = await metalXLoanGet(`/apy?token_symbol=${encodeURIComponent(underlying_symbol.toUpperCase())}&days=${d}`);

        return {
          token: data.tokenSymbol || underlying_symbol.toUpperCase(),
          days: data.days || d,
          avg_deposit_apy_pct: `${((data.avgDepositApy || 0) * 100).toFixed(2)}%`,
          avg_deposit_with_loan_apy_pct: `${((data.avgDepositLoanApy || 0) * 100).toFixed(2)}%`,
          avg_borrow_apy_pct: `${((data.avgBorrowApy || 0) * 100).toFixed(2)}%`,
          avg_borrow_with_loan_apy_pct: `${((data.avgBorrowLoanApy || 0) * 100).toFixed(2)}%`,
          net_borrow_apy_pct: `${(((data.avgBorrowLoanApy || 0) - (data.avgBorrowApy || 0)) * 100).toFixed(2)}%`,
          chart_data: (data.chartData || []).slice(-7).map((p: any) => ({
            date: p.date,
            deposit_apy_pct: `${((p.depositApy || 0) * 100).toFixed(2)}%`,
            borrow_apy_pct: `${((p.borrowApy || 0) * 100).toFixed(2)}%`,
          })),
          note: 'APY includes interest. "with_loan" APYs include LOAN token rewards. Net borrow APY = LOAN rewards - interest cost (positive = earning while borrowing).',
        };
      } catch (err: any) {
        return { error: `Failed to get APY: ${err.message}` };
      }
    },
  });

  // ── 7. loan_get_market_tvl ──
  api.registerTool({
    name: 'loan_get_market_tvl',
    description: 'Get historical TVL (total value locked) for a lending market in USD. Returns deposit and borrow TVL. Data from Metal X API.',
    parameters: {
      type: 'object',
      required: ['underlying_symbol'],
      properties: {
        underlying_symbol: { type: 'string', description: 'Underlying token symbol e.g. "XBTC", "XUSDC", "XPR"' },
        days: { type: 'number', description: 'Time period: 7, 30, or 90 days (default 7)' },
      },
    },
    handler: async ({ underlying_symbol, days }: { underlying_symbol: string; days?: number }) => {
      if (!underlying_symbol) return { error: 'underlying_symbol is required (e.g. "XBTC")' };
      const d = VALID_DAYS.includes(days || 0) ? days! : 7;

      try {
        const data = await metalXLoanGet(`/tvl?token_symbol=${encodeURIComponent(underlying_symbol.toUpperCase())}&days=${d}`);

        return {
          token: data.tokenSymbol || underlying_symbol.toUpperCase(),
          days: data.days || d,
          avg_deposit_tvl_usd: `$${((data.avgDepositTvl || 0)).toLocaleString('en-US', { maximumFractionDigits: 0 })}`,
          avg_borrow_tvl_usd: `$${((data.avgBorrowTvl || 0)).toLocaleString('en-US', { maximumFractionDigits: 0 })}`,
          utilization_pct: data.avgDepositTvl > 0
            ? `${((data.avgBorrowTvl / data.avgDepositTvl) * 100).toFixed(1)}%`
            : '0%',
          chart_data: (data.chartData || []).slice(-7).map((p: any) => ({
            date: p.date,
            deposit_tvl_usd: Math.round(p.depositTvl || 0),
            borrow_tvl_usd: Math.round(p.borrowTvl || 0),
          })),
        };
      } catch (err: any) {
        return { error: `Failed to get TVL: ${err.message}` };
      }
    },
  });

  // ════════════════════════════════════════════════
  // WRITE TOOLS (require confirmation)
  // ════════════════════════════════════════════════

  // ── 8. loan_enter_markets ──
  api.registerTool({
    name: 'loan_enter_markets',
    description: 'Enter lending markets to enable supply/borrow. Must enter a market before interacting with it. No-op if already entered.',
    parameters: {
      type: 'object',
      required: ['markets', 'confirmed'],
      properties: {
        markets: {
          type: 'array',
          description: 'Array of L-token market symbols to enter, e.g. ["LBTC", "LUSDC"]',
        },
        confirmed: { type: 'boolean', description: 'Must be true to proceed' },
      },
    },
    handler: async ({ markets, confirmed }: { markets: string[]; confirmed?: boolean }) => {
      if (!confirmed) {
        return { error: 'Confirmation required. Set confirmed=true to enter these markets.', markets };
      }
      if (!Array.isArray(markets) || markets.length === 0) {
        return { error: 'markets must be a non-empty array of market symbols (e.g. ["LBTC"])' };
      }

      try {
        const { api: eosApi, account, permission } = await getLendingSession();

        const result = await eosApi.transact({
          actions: [{
            account: LENDING_CONTRACT,
            name: 'entermarkets',
            authorization: [{ actor: account, permission }],
            data: {
              payer: account,
              user: account,
              markets: markets.map(m => m.toUpperCase()),
            },
          }],
        }, { blocksBehind: 3, expireSeconds: 30 });

        return {
          transaction_id: result.transaction_id || result.processed?.id,
          entered_markets: markets.map(m => m.toUpperCase()),
          account,
        };
      } catch (err: any) {
        return { error: `Failed to enter markets: ${err.message}` };
      }
    },
  });

  // ── 7. loan_exit_markets ──
  api.registerTool({
    name: 'loan_exit_markets',
    description: 'Exit lending markets. User must not have outstanding rewards, collateral, or borrows in these markets.',
    parameters: {
      type: 'object',
      required: ['markets', 'confirmed'],
      properties: {
        markets: {
          type: 'array',
          description: 'Array of L-token market symbols to exit, e.g. ["LBTC"]',
        },
        confirmed: { type: 'boolean', description: 'Must be true to proceed' },
      },
    },
    handler: async ({ markets, confirmed }: { markets: string[]; confirmed?: boolean }) => {
      if (!confirmed) {
        return { error: 'Confirmation required. Set confirmed=true to exit these markets.', markets };
      }
      if (!Array.isArray(markets) || markets.length === 0) {
        return { error: 'markets must be a non-empty array of market symbols' };
      }

      try {
        const { api: eosApi, account, permission } = await getLendingSession();

        const result = await eosApi.transact({
          actions: [{
            account: LENDING_CONTRACT,
            name: 'exitmarkets',
            authorization: [{ actor: account, permission }],
            data: {
              user: account,
              markets: markets.map(m => m.toUpperCase()),
            },
          }],
        }, { blocksBehind: 3, expireSeconds: 30 });

        return {
          transaction_id: result.transaction_id || result.processed?.id,
          exited_markets: markets.map(m => m.toUpperCase()),
          account,
        };
      } catch (err: any) {
        return { error: `Failed to exit markets: ${err.message}` };
      }
    },
  });

  // ── 8. loan_supply ──
  api.registerTool({
    name: 'loan_supply',
    description: 'Supply underlying tokens to LOAN Protocol to earn interest. Transfers tokens to lending.loan with "mint" memo, which mints L-tokens and deposits them as collateral. You must enter the market first.',
    parameters: {
      type: 'object',
      required: ['market_symbol', 'amount', 'confirmed'],
      properties: {
        market_symbol: { type: 'string', description: 'L-token market symbol, e.g. "LBTC"' },
        amount: { type: 'number', description: 'Amount of underlying tokens to supply' },
        confirmed: { type: 'boolean', description: 'Must be true to proceed' },
      },
    },
    handler: async ({ market_symbol, amount, confirmed }: {
      market_symbol: string; amount: number; confirmed?: boolean;
    }) => {
      if (!confirmed) {
        return {
          error: 'Confirmation required. Set confirmed=true to supply tokens.',
          market_symbol, amount,
        };
      }
      if (!market_symbol) return { error: 'market_symbol is required (e.g. "LBTC")' };
      if (!amount || amount <= 0) return { error: 'amount must be positive' };

      try {
        // Look up market to find underlying token contract and precision
        const markets = await getTableRows(rpcEndpoint, {
          code: LENDING_CONTRACT, scope: LENDING_CONTRACT, table: 'markets', limit: 50,
        });

        const market = markets.find((m: any) => {
          const share = parseExtSym(m.share_symbol);
          return share?.symbol === market_symbol.toUpperCase();
        });

        if (!market) {
          const available = markets.map((m: any) => parseExtSym(m.share_symbol)?.symbol).filter(Boolean);
          return { error: `Market "${market_symbol}" not found. Available: ${available.join(', ')}` };
        }

        const underlying = parseExtSym(market.underlying_symbol);
        if (!underlying) return { error: 'Could not parse underlying token info from market' };

        const quantity = formatAsset(amount, underlying.precision, underlying.symbol);

        const { api: eosApi, account, permission } = await getLendingSession();

        const result = await eosApi.transact({
          actions: [{
            account: underlying.contract,
            name: 'transfer',
            authorization: [{ actor: account, permission }],
            data: {
              from: account,
              to: LENDING_CONTRACT,
              quantity,
              memo: 'mint',
            },
          }],
        }, { blocksBehind: 3, expireSeconds: 30 });

        return {
          transaction_id: result.transaction_id || result.processed?.id,
          action: 'supply (mint)',
          market: market_symbol.toUpperCase(),
          quantity,
          underlying_contract: underlying.contract,
          account,
          note: 'L-tokens minted and deposited as collateral automatically.',
        };
      } catch (err: any) {
        return { error: `Failed to supply: ${err.message}` };
      }
    },
  });

  // ── 9. loan_borrow ──
  api.registerTool({
    name: 'loan_borrow',
    description: 'Borrow underlying tokens from LOAN Protocol against deposited collateral. Ensure your collateral value covers the new borrow — borrowing at the limit risks liquidation.',
    parameters: {
      type: 'object',
      required: ['market_symbol', 'amount', 'confirmed'],
      properties: {
        market_symbol: { type: 'string', description: 'L-token market symbol to borrow from, e.g. "LUSDC"' },
        amount: { type: 'number', description: 'Amount of underlying tokens to borrow' },
        use_stable_rate: { type: 'boolean', description: 'Use stable (fixed) rate loan. Default false (variable rate).' },
        confirmed: { type: 'boolean', description: 'Must be true to proceed' },
      },
    },
    handler: async ({ market_symbol, amount, use_stable_rate, confirmed }: {
      market_symbol: string; amount: number; use_stable_rate?: boolean; confirmed?: boolean;
    }) => {
      if (!confirmed) {
        return {
          error: 'Confirmation required. Set confirmed=true to borrow. WARNING: Borrowing close to the collateral factor risks liquidation.',
          market_symbol, amount, use_stable_rate: use_stable_rate || false,
        };
      }
      if (!market_symbol) return { error: 'market_symbol is required (e.g. "LUSDC")' };
      if (!amount || amount <= 0) return { error: 'amount must be positive' };

      try {
        const markets = await getTableRows(rpcEndpoint, {
          code: LENDING_CONTRACT, scope: LENDING_CONTRACT, table: 'markets', limit: 50,
        });

        const market = markets.find((m: any) => {
          const share = parseExtSym(m.share_symbol);
          return share?.symbol === market_symbol.toUpperCase();
        });

        if (!market) {
          const available = markets.map((m: any) => parseExtSym(m.share_symbol)?.symbol).filter(Boolean);
          return { error: `Market "${market_symbol}" not found. Available: ${available.join(', ')}` };
        }

        const underlying = parseExtSym(market.underlying_symbol);
        if (!underlying) return { error: 'Could not parse underlying token info' };

        if (use_stable_rate && !market.stable_loans_enabled) {
          return { error: `Stable loans are not enabled for market ${market_symbol}. Use variable rate.` };
        }

        const quantity = formatAsset(amount, underlying.precision, underlying.symbol);

        const { api: eosApi, account, permission } = await getLendingSession();

        const result = await eosApi.transact({
          actions: [{
            account: LENDING_CONTRACT,
            name: 'borrow',
            authorization: [{ actor: account, permission }],
            data: {
              borrower: account,
              underlying: {
                quantity,
                contract: underlying.contract,
              },
              use_stable_rate: use_stable_rate || false,
            },
          }],
        }, { blocksBehind: 3, expireSeconds: 30 });

        return {
          transaction_id: result.transaction_id || result.processed?.id,
          action: 'borrow',
          market: market_symbol.toUpperCase(),
          quantity,
          rate_type: use_stable_rate ? 'stable' : 'variable',
          account,
          warning: 'Monitor your collateral ratio. If it drops below the collateral factor, you may be liquidated.',
        };
      } catch (err: any) {
        return { error: `Failed to borrow: ${err.message}` };
      }
    },
  });

  // ── 10. loan_repay ──
  api.registerTool({
    name: 'loan_repay',
    description: 'Repay borrowed tokens on LOAN Protocol. Transfers underlying tokens to lending.loan with "repay" memo. Can optionally repay on behalf of another borrower.',
    parameters: {
      type: 'object',
      required: ['market_symbol', 'amount', 'rate_type', 'confirmed'],
      properties: {
        market_symbol: { type: 'string', description: 'L-token market symbol, e.g. "LUSDC"' },
        amount: { type: 'number', description: 'Amount of underlying tokens to repay. Overpayment is refunded.' },
        rate_type: { type: 'string', description: '"variable" or "stable" — which borrow to repay' },
        borrower: { type: 'string', description: 'Optional: repay on behalf of another account' },
        confirmed: { type: 'boolean', description: 'Must be true to proceed' },
      },
    },
    handler: async ({ market_symbol, amount, rate_type, borrower, confirmed }: {
      market_symbol: string; amount: number; rate_type: string; borrower?: string; confirmed?: boolean;
    }) => {
      if (!confirmed) {
        return {
          error: 'Confirmation required. Set confirmed=true to repay.',
          market_symbol, amount, rate_type, borrower,
        };
      }
      if (!market_symbol) return { error: 'market_symbol is required' };
      if (!amount || amount <= 0) return { error: 'amount must be positive' };
      if (rate_type !== 'variable' && rate_type !== 'stable') {
        return { error: 'rate_type must be "variable" or "stable"' };
      }

      try {
        const markets = await getTableRows(rpcEndpoint, {
          code: LENDING_CONTRACT, scope: LENDING_CONTRACT, table: 'markets', limit: 50,
        });

        const market = markets.find((m: any) => {
          const share = parseExtSym(m.share_symbol);
          return share?.symbol === market_symbol.toUpperCase();
        });

        if (!market) {
          const available = markets.map((m: any) => parseExtSym(m.share_symbol)?.symbol).filter(Boolean);
          return { error: `Market "${market_symbol}" not found. Available: ${available.join(', ')}` };
        }

        const underlying = parseExtSym(market.underlying_symbol);
        if (!underlying) return { error: 'Could not parse underlying token info' };

        const quantity = formatAsset(amount, underlying.precision, underlying.symbol);
        let memo = `repay,${rate_type}`;
        if (borrower) memo += `,${borrower}`;

        const { api: eosApi, account, permission } = await getLendingSession();

        const result = await eosApi.transact({
          actions: [{
            account: underlying.contract,
            name: 'transfer',
            authorization: [{ actor: account, permission }],
            data: {
              from: account,
              to: LENDING_CONTRACT,
              quantity,
              memo,
            },
          }],
        }, { blocksBehind: 3, expireSeconds: 30 });

        return {
          transaction_id: result.transaction_id || result.processed?.id,
          action: 'repay',
          market: market_symbol.toUpperCase(),
          quantity,
          rate_type,
          borrower: borrower || account,
          account,
          note: 'Any overpayment is automatically refunded.',
        };
      } catch (err: any) {
        return { error: `Failed to repay: ${err.message}` };
      }
    },
  });

  // ── 11. loan_redeem ──
  api.registerTool({
    name: 'loan_redeem',
    description: 'Redeem deposited L-tokens for underlying tokens. Burns L-tokens and returns the equivalent underlying amount at the current exchange rate. Collateral must still cover outstanding borrows after redemption.',
    parameters: {
      type: 'object',
      required: ['market_symbol', 'amount', 'confirmed'],
      properties: {
        market_symbol: { type: 'string', description: 'L-token market symbol, e.g. "LBTC"' },
        amount: { type: 'number', description: 'Amount of L-tokens to redeem' },
        confirmed: { type: 'boolean', description: 'Must be true to proceed' },
      },
    },
    handler: async ({ market_symbol, amount, confirmed }: {
      market_symbol: string; amount: number; confirmed?: boolean;
    }) => {
      if (!confirmed) {
        return {
          error: 'Confirmation required. Set confirmed=true to redeem L-tokens.',
          market_symbol, amount,
        };
      }
      if (!market_symbol) return { error: 'market_symbol is required' };
      if (!amount || amount <= 0) return { error: 'amount must be positive' };

      try {
        const markets = await getTableRows(rpcEndpoint, {
          code: LENDING_CONTRACT, scope: LENDING_CONTRACT, table: 'markets', limit: 50,
        });

        const market = markets.find((m: any) => {
          const share = parseExtSym(m.share_symbol);
          return share?.symbol === market_symbol.toUpperCase();
        });

        if (!market) {
          const available = markets.map((m: any) => parseExtSym(m.share_symbol)?.symbol).filter(Boolean);
          return { error: `Market "${market_symbol}" not found. Available: ${available.join(', ')}` };
        }

        const share = parseExtSym(market.share_symbol);
        if (!share) return { error: 'Could not parse share token info' };

        const quantity = formatAsset(amount, share.precision, share.symbol);

        const { api: eosApi, account, permission } = await getLendingSession();

        const result = await eosApi.transact({
          actions: [{
            account: LENDING_CONTRACT,
            name: 'redeem',
            authorization: [{ actor: account, permission }],
            data: {
              redeemer: account,
              token: {
                quantity,
                contract: share.contract,
              },
            },
          }],
        }, { blocksBehind: 3, expireSeconds: 30 });

        return {
          transaction_id: result.transaction_id || result.processed?.id,
          action: 'redeem',
          market: market_symbol.toUpperCase(),
          quantity_redeemed: quantity,
          account,
          note: 'Underlying tokens returned at current exchange rate. Interest earned is included.',
        };
      } catch (err: any) {
        return { error: `Failed to redeem: ${err.message}` };
      }
    },
  });

  // ── 12. loan_withdraw_collateral ──
  api.registerTool({
    name: 'loan_withdraw_collateral',
    description: 'Withdraw L-tokens from collateral without burning them. Reduces borrowing capacity. Collateral must still cover outstanding borrows after withdrawal.',
    parameters: {
      type: 'object',
      required: ['market_symbol', 'amount', 'confirmed'],
      properties: {
        market_symbol: { type: 'string', description: 'L-token market symbol, e.g. "LBTC"' },
        amount: { type: 'number', description: 'Amount of L-tokens to withdraw from collateral' },
        confirmed: { type: 'boolean', description: 'Must be true to proceed' },
      },
    },
    handler: async ({ market_symbol, amount, confirmed }: {
      market_symbol: string; amount: number; confirmed?: boolean;
    }) => {
      if (!confirmed) {
        return {
          error: 'Confirmation required. Set confirmed=true to withdraw collateral.',
          market_symbol, amount,
        };
      }
      if (!market_symbol) return { error: 'market_symbol is required' };
      if (!amount || amount <= 0) return { error: 'amount must be positive' };

      try {
        const markets = await getTableRows(rpcEndpoint, {
          code: LENDING_CONTRACT, scope: LENDING_CONTRACT, table: 'markets', limit: 50,
        });

        const market = markets.find((m: any) => {
          const share = parseExtSym(m.share_symbol);
          return share?.symbol === market_symbol.toUpperCase();
        });

        if (!market) {
          const available = markets.map((m: any) => parseExtSym(m.share_symbol)?.symbol).filter(Boolean);
          return { error: `Market "${market_symbol}" not found. Available: ${available.join(', ')}` };
        }

        const share = parseExtSym(market.share_symbol);
        if (!share) return { error: 'Could not parse share token info' };

        const quantity = formatAsset(amount, share.precision, share.symbol);

        const { api: eosApi, account, permission } = await getLendingSession();

        const result = await eosApi.transact({
          actions: [{
            account: LENDING_CONTRACT,
            name: 'withdraw',
            authorization: [{ actor: account, permission }],
            data: {
              withdrawer: account,
              token: {
                quantity,
                contract: share.contract,
              },
            },
          }],
        }, { blocksBehind: 3, expireSeconds: 30 });

        return {
          transaction_id: result.transaction_id || result.processed?.id,
          action: 'withdraw_collateral',
          market: market_symbol.toUpperCase(),
          quantity_withdrawn: quantity,
          account,
          note: 'L-tokens withdrawn from collateral to your wallet. Use redeem to convert to underlying.',
        };
      } catch (err: any) {
        return { error: `Failed to withdraw collateral: ${err.message}` };
      }
    },
  });

  // ── 13. loan_claim_rewards ──
  api.registerTool({
    name: 'loan_claim_rewards',
    description: 'Claim accrued LOAN token rewards from LOAN Protocol lending markets. Combines update.user (to accrue latest rewards) with claim action.',
    parameters: {
      type: 'object',
      required: ['markets', 'confirmed'],
      properties: {
        markets: {
          type: 'array',
          description: 'Array of L-token market symbols to claim from, e.g. ["LBTC", "LUSDC"]',
        },
        confirmed: { type: 'boolean', description: 'Must be true to proceed' },
      },
    },
    handler: async ({ markets, confirmed }: { markets: string[]; confirmed?: boolean }) => {
      if (!confirmed) {
        return { error: 'Confirmation required. Set confirmed=true to claim rewards.', markets };
      }
      if (!Array.isArray(markets) || markets.length === 0) {
        return { error: 'markets must be a non-empty array of market symbols' };
      }

      try {
        const { api: eosApi, account, permission } = await getLendingSession();
        const marketSymbols = markets.map(m => m.toUpperCase());

        // Combine update.user + claim in one transaction for up-to-date rewards
        const result = await eosApi.transact({
          actions: [
            {
              account: LENDING_CONTRACT,
              name: 'update.user',
              authorization: [{ actor: account, permission }],
              data: { user: account },
            },
            {
              account: LENDING_CONTRACT,
              name: 'claim',
              authorization: [{ actor: account, permission }],
              data: {
                user: account,
                markets: marketSymbols,
              },
            },
          ],
        }, { blocksBehind: 3, expireSeconds: 30 });

        return {
          transaction_id: result.transaction_id || result.processed?.id,
          action: 'claim_rewards',
          markets_claimed: marketSymbols,
          account,
          note: 'LOAN rewards sent to your account. User state updated before claiming for accurate amounts.',
        };
      } catch (err: any) {
        return { error: `Failed to claim rewards: ${err.message}` };
      }
    },
  });
}
