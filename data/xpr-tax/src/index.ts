/**
 * Tax Skill — Crypto tax reporting for XPR Network
 *
 * All tools are read-only (query APIs + calculate).
 * Region system: pass `region` param (default "NZ") to any tool.
 * Adding a new region = adding an entry to REGIONS.
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

// ── Region Configuration ─────────────────────────

interface RegionConfig {
  name: string;
  code: string;
  currency: string;
  tax_year: { start_month: number; start_day: number };
  cost_basis_methods: string[];
  has_capital_gains: boolean;
  brackets: Array<{ limit: number; rate: number }>;
  disclaimer: string;
}

const REGIONS: Record<string, RegionConfig> = {
  NZ: {
    name: 'New Zealand',
    code: 'NZ',
    currency: 'NZD',
    tax_year: { start_month: 4, start_day: 1 },
    cost_basis_methods: ['fifo', 'average'],
    has_capital_gains: false,
    brackets: [
      { limit: 14000, rate: 0.105 },
      { limit: 48000, rate: 0.175 },
      { limit: 70000, rate: 0.30 },
      { limit: 180000, rate: 0.33 },
      { limit: Infinity, rate: 0.39 },
    ],
    disclaimer: 'Estimate only. Consult a NZ tax professional. IRD requires 7 years of records.',
  },
  US: {
    name: 'United States',
    code: 'US',
    currency: 'USD',
    tax_year: { start_month: 1, start_day: 1 },
    cost_basis_methods: ['fifo', 'average'],
    has_capital_gains: true,
    brackets: [
      { limit: 11600, rate: 0.10 },
      { limit: 47150, rate: 0.12 },
      { limit: 100525, rate: 0.22 },
      { limit: 191950, rate: 0.24 },
      { limit: 243725, rate: 0.32 },
      { limit: 609350, rate: 0.35 },
      { limit: Infinity, rate: 0.37 },
    ],
    disclaimer: 'Estimate only — uses 2024 Single filer federal brackets. Does not include state taxes, NIIT (3.8%), or long-term capital gains rates. Short-term gains (<1 year hold) are taxed as ordinary income. Consult a US CPA or tax professional. IRS requires records for 3+ years.',
  },
};

function getRegion(code?: string): RegionConfig {
  const key = (code || 'NZ').toUpperCase();
  const region = REGIONS[key];
  if (!region) {
    throw new Error(`Unsupported region "${key}". Supported: ${Object.keys(REGIONS).join(', ')}`);
  }
  return region;
}

// ── Tax Year Helpers ─────────────────────────────

function getTaxYearDates(taxYear: number, region: RegionConfig): { start: string; end: string } {
  const { start_month, start_day } = region.tax_year;
  // Tax year "2025" in NZ = Apr 1, 2024 – Mar 31, 2025
  const startYear = start_month > 1 ? taxYear - 1 : taxYear;
  const endYear = start_month > 1 ? taxYear : taxYear + 1;
  const endMonth = start_month - 1 || 12;
  const endDay = new Date(endYear, endMonth, 0).getDate(); // last day of end month

  const start = `${startYear}-${String(start_month).padStart(2, '0')}-${String(start_day).padStart(2, '0')}T00:00:00.000Z`;
  const end = `${endYear}-${String(endMonth).padStart(2, '0')}-${String(endDay).padStart(2, '0')}T23:59:59.999Z`;
  return { start, end };
}

// ── HTTP Helpers ─────────────────────────────────

const HTTP_TIMEOUT = 20000;

async function httpGet(url: string, headers?: Record<string, string>): Promise<any> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), HTTP_TIMEOUT);
  try {
    const resp = await fetch(url, { signal: controller.signal, headers });
    if (!resp.ok) {
      const text = await resp.text().catch(() => '');
      throw new Error(`HTTP GET ${url} failed (${resp.status}): ${text.slice(0, 200)}`);
    }
    return resp;
  } finally {
    clearTimeout(timer);
  }
}

async function httpGetJson(url: string, headers?: Record<string, string>): Promise<any> {
  const resp = await httpGet(url, headers);
  return resp.json();
}

async function httpGetText(url: string): Promise<string> {
  const resp = await httpGet(url);
  return resp.text();
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ── CoinGecko ────────────────────────────────────

// Auto-detect API key tier: Pro key starts with "CG-", Demo key otherwise
function getCoinGeckoConfig(): { baseUrl: string; headers: Record<string, string>; hasKey: boolean } {
  const apiKey = process.env.COINGECKO_API_KEY || '';
  if (!apiKey) {
    return { baseUrl: 'https://api.coingecko.com/api/v3', headers: {}, hasKey: false };
  }
  if (apiKey.startsWith('CG-')) {
    // Pro API key
    return {
      baseUrl: 'https://pro-api.coingecko.com/api/v3',
      headers: { 'x-cg-pro-api-key': apiKey },
      hasKey: true,
    };
  }
  // Demo API key (free tier with key)
  return {
    baseUrl: 'https://api.coingecko.com/api/v3',
    headers: { 'x-cg-demo-api-key': apiKey },
    hasKey: true,
  };
}

const COINGECKO_BASE = getCoinGeckoConfig().baseUrl;

const TOKEN_TO_COINGECKO: Record<string, string> = {
  XPR: 'proton',
  XBTC: 'bitcoin',
  XETH: 'ethereum',
  XDOGE: 'dogecoin',
  METAL: 'metal-blockchain',
  XUSDC: 'usd-coin',
  XMD: 'usd-coin',
  XXRP: 'ripple',
  XLTC: 'litecoin',
  XHBAR: 'hedera-hashgraph',
  LOAN: 'proton-loan',
  SLOAN: 'proton-loan',
};

const STABLECOINS = new Set(['XUSDC', 'XMD', 'USDT']);

// CoinGecko fetch with API key headers
async function cgFetch(path: string): Promise<any> {
  const cg = getCoinGeckoConfig();
  return httpGetJson(`${cg.baseUrl}${path}`, cg.headers);
}

// Persistent rate cache: "SYMBOL:YYYY-MM-DD" → rate
// Historical prices are immutable — once fetched they never change.
// Stored as JSON file so rates survive container restarts.
import * as fs from 'fs';
import * as path from 'path';

const RATE_CACHE_FILE = process.env.RATE_CACHE_PATH || path.join(process.cwd(), 'data', 'rate-cache.json');
const rateCache = new Map<string, number>();
let rateCacheDirty = false;

function loadRateCache(): void {
  try {
    if (fs.existsSync(RATE_CACHE_FILE)) {
      const data = JSON.parse(fs.readFileSync(RATE_CACHE_FILE, 'utf-8'));
      for (const [k, v] of Object.entries(data)) {
        if (typeof v === 'number' && v > 0) rateCache.set(k, v);
      }
      console.log(`[tax] Loaded ${rateCache.size} cached rates from ${RATE_CACHE_FILE}`);
    }
  } catch { /* start fresh */ }
}

function saveRateCache(): void {
  if (!rateCacheDirty) return;
  try {
    const dir = path.dirname(RATE_CACHE_FILE);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    const obj: Record<string, number> = {};
    for (const [k, v] of rateCache) obj[k] = v;
    fs.writeFileSync(RATE_CACHE_FILE, JSON.stringify(obj));
    rateCacheDirty = false;
  } catch (err) {
    console.error(`[tax] Failed to save rate cache:`, err);
  }
}

function cacheRate(key: string, rate: number): void {
  // Only cache historical date rates (not "current")
  if (key.includes(':current') || rate <= 0) return;
  rateCache.set(key, rate);
  rateCacheDirty = true;
}

// Load on startup
loadRateCache();

// ── CSV Parser ───────────────────────────────────

function parseCSV(csv: string): Array<Record<string, string>> {
  const lines = csv.trim().split('\n');
  if (lines.length < 2) return [];
  const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''));
  const rows: Array<Record<string, string>> = [];
  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',').map(v => v.trim().replace(/^"|"$/g, ''));
    const row: Record<string, string> = {};
    for (let j = 0; j < headers.length; j++) {
      row[headers[j]] = values[j] || '';
    }
    rows.push(row);
  }
  return rows;
}

// ── Transfer Categorization ──────────────────────

interface CategorizedTransfer {
  category: string;
  from: string;
  to: string;
  amount: number;
  symbol: string;
  memo: string;
  timestamp: string;
  tx_id: string;
  direction: 'incoming' | 'outgoing';
}

function categorizeTransfer(
  account: string,
  from: string,
  to: string,
  amount: number,
  symbol: string,
  memo: string,
): string {
  const memoLower = (memo || '').toLowerCase();
  const isIncoming = to === account;
  const counterparty = isIncoming ? from : to;

  // Staking rewards (block production + community fund)
  if (isIncoming && (from === 'eosio' || from === 'eosio.vpay' || from === 'eosio.bpay' || from === 'cfund.proton')) {
    return 'staking_reward';
  }

  // Lending (lending.loan)
  if (counterparty === 'lending.loan') {
    if (isIncoming) {
      if (memoLower.includes('interest') || memoLower.includes('reward') || memoLower.includes('yield')) {
        return 'lending_interest';
      }
      return 'lending_withdrawal';
    }
    return 'lending_deposit';
  }

  // Swaps (proton.swaps)
  if (counterparty === 'proton.swaps') {
    return isIncoming ? 'swap_withdrawal' : 'swap_deposit';
  }

  // Long staking XPR (longstaking contract)
  if (counterparty === 'longstaking') {
    return isIncoming ? 'long_unstake' : 'long_stake';
  }

  // LOAN staking (lock.token + yield.farms)
  if (counterparty === 'lock.token' || counterparty === 'yield.farms') {
    return isIncoming ? 'loan_unstake' : 'loan_stake';
  }

  // DEX (Metal X)
  if (counterparty === 'dex' || counterparty === 'metalx') {
    return isIncoming ? 'dex_withdrawal' : 'dex_deposit';
  }

  // NFT marketplace
  if (counterparty === 'atomicmarket') {
    return isIncoming ? 'nft_sale' : 'nft_purchase';
  }

  // Agent escrow
  if (counterparty === 'agentescrow') {
    return 'escrow';
  }

  // Burned tokens — disposal at zero value = realized loss
  if (to === 'eosio.null') {
    return 'burn';
  }

  return 'transfer';
}

// ── Gains Calculation ────────────────────────────

interface TradeEvent {
  type: 'trade';
  date: string;
  buy_amount: number;
  buy_currency: string;
  sell_amount: number;
  sell_currency: string;
  fee?: number;
  fee_currency?: string;
  tx_id?: string;
}

interface TransferEvent {
  type: 'transfer';
  date: string;
  category: string;
  amount: number;
  symbol: string;
  direction: 'incoming' | 'outgoing';
  tx_id?: string;
}

interface Disposal {
  date: string;
  asset: string;
  amount: number;
  proceeds_local: number;
  cost_basis_local: number;
  gain_loss_local: number;
  method: string;
  tx_id?: string;
}

interface IncomeEvent {
  date: string;
  category: string;
  asset: string;
  amount: number;
  value_local: number;
  tx_id?: string;
}

interface GainsResult {
  disposals: Disposal[];
  income_events: IncomeEvent[];
  summary: {
    total_proceeds: number;
    total_cost_basis: number;
    total_gains: number;
    total_losses: number;
    net_gain_loss: number;
    total_income: number;
    grand_total_taxable: number;
  };
  remaining_lots: Record<string, Array<{ amount: number; cost_per_unit: number; date: string }>>;
  method: string;
  currency: string;
}

type RateMap = Record<string, number>; // "SYMBOL:YYYY-MM-DD" → local currency rate

function dateKey(date: string): string {
  return date.slice(0, 10); // YYYY-MM-DD
}

function getRate(rates: RateMap, symbol: string, date: string): number {
  const key = `${symbol}:${dateKey(date)}`;
  return rates[key] || rates[`${symbol}:current`] || 0;
}

// Income categories: these incoming transfers are taxable income
const INCOME_CATEGORIES = new Set([
  'staking_reward', 'lending_interest', 'nft_sale',
]);

// Long staking is special: only the EXCESS over what was staked is income.
// We track deposits and only count the surplus on unstake.
// Same for loan staking.
const LONG_STAKE_INCOME = new Set(['long_unstake', 'loan_unstake']);

// DeFi movements: not taxable events (moving between own wallets/protocols)
const DEFI_MOVE_CATEGORIES = new Set([
  'lending_deposit', 'lending_withdrawal',
  'swap_deposit', 'swap_withdrawal',
  'long_stake', 'long_unstake',
  'loan_stake', 'loan_unstake',
  'dex_deposit', 'dex_withdrawal',
  'escrow',
]);

function calculateGainsFIFO(
  trades: TradeEvent[],
  transfers: TransferEvent[],
  rates: RateMap,
  currency: string,
): GainsResult {
  // Lot queues: asset → [{ amount, cost_per_unit, date }]
  const lots: Record<string, Array<{ amount: number; cost_per_unit: number; date: string }>> = {};
  const disposals: Disposal[] = [];
  const incomeEvents: IncomeEvent[] = [];

  // Track long staking / loan staking deposits per symbol to compute excess on unstake
  const stakeDeposits: Record<string, number> = {}; // "long:SYMBOL" or "loan:SYMBOL" → total staked

  function addLot(asset: string, amount: number, costPerUnit: number, date: string): void {
    if (!lots[asset]) lots[asset] = [];
    lots[asset].push({ amount, cost_per_unit: costPerUnit, date });
  }

  function consumeLots(asset: string, amount: number): number {
    const queue = lots[asset] || [];
    let remaining = amount;
    let totalCost = 0;
    while (remaining > 0 && queue.length > 0) {
      const lot = queue[0];
      if (lot.amount <= remaining) {
        totalCost += lot.amount * lot.cost_per_unit;
        remaining -= lot.amount;
        queue.shift();
      } else {
        totalCost += remaining * lot.cost_per_unit;
        lot.amount -= remaining;
        remaining = 0;
      }
    }
    return totalCost;
  }

  // Merge and sort all events chronologically
  const events: Array<{ date: string; event: TradeEvent | TransferEvent }> = [
    ...trades.map(t => ({ date: t.date, event: t })),
    ...transfers.map(t => ({ date: t.date, event: t })),
  ];
  events.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

  let totalProceeds = 0;
  let totalCostBasis = 0;
  let totalGains = 0;
  let totalLosses = 0;
  let totalIncome = 0;

  for (const { event } of events) {
    if (event.type === 'trade') {
      const trade = event as TradeEvent;
      const buyRate = getRate(rates, trade.buy_currency, trade.date);
      const sellRate = getRate(rates, trade.sell_currency, trade.date);

      // Disposal of sell currency
      const proceeds = trade.sell_amount * sellRate;
      const costBasis = consumeLots(trade.sell_currency, trade.sell_amount);
      const gainLoss = proceeds - costBasis;

      disposals.push({
        date: trade.date,
        asset: trade.sell_currency,
        amount: trade.sell_amount,
        proceeds_local: proceeds,
        cost_basis_local: costBasis,
        gain_loss_local: gainLoss,
        method: 'fifo',
        tx_id: trade.tx_id,
      });

      totalProceeds += proceeds;
      totalCostBasis += costBasis;
      if (gainLoss > 0) totalGains += gainLoss;
      else totalLosses += Math.abs(gainLoss);

      // Acquisition of buy currency
      addLot(trade.buy_currency, trade.buy_amount, buyRate, trade.date);

    } else {
      const xfer = event as TransferEvent;
      const rate = getRate(rates, xfer.symbol, xfer.date);

      if (xfer.direction === 'incoming') {
        // Income categories: record as income + create cost basis lot
        if (INCOME_CATEGORIES.has(xfer.category)) {
          const value = xfer.amount * rate;
          incomeEvents.push({
            date: xfer.date,
            category: xfer.category,
            asset: xfer.symbol,
            amount: xfer.amount,
            value_local: value,
            tx_id: xfer.tx_id,
          });
          totalIncome += value;
          addLot(xfer.symbol, xfer.amount, rate, xfer.date);

        } else if (LONG_STAKE_INCOME.has(xfer.category)) {
          // Long staking / loan staking unstake — only the EXCESS over deposits is income
          // (e.g. stake 100 XPR, unstake 150 XPR → income of 50 XPR)
          const stakeKey = xfer.category === 'long_unstake' ? `long:${xfer.symbol}` : `loan:${xfer.symbol}`;
          const deposited = stakeDeposits[stakeKey] || 0;
          const excess = Math.max(0, xfer.amount - deposited);

          // Reduce tracked deposits by the principal portion returned
          stakeDeposits[stakeKey] = Math.max(0, deposited - (xfer.amount - excess));

          if (excess > 0) {
            const value = excess * rate;
            incomeEvents.push({
              date: xfer.date,
              category: xfer.category === 'long_unstake' ? 'long_staking_reward' : 'loan_staking_reward',
              asset: xfer.symbol,
              amount: excess,
              value_local: value,
              tx_id: xfer.tx_id,
            });
            totalIncome += value;
          }
          // Full amount returns as cost basis (principal at original cost, excess at current rate)
          addLot(xfer.symbol, xfer.amount, rate, xfer.date);

        } else if (!DEFI_MOVE_CATEGORIES.has(xfer.category)) {
          // Regular incoming transfer — cost basis acquisition
          addLot(xfer.symbol, xfer.amount, rate, xfer.date);
        }
        // DeFi moves (deposit/withdrawal) are not taxable events
      } else {
        // Outgoing transfer

        // Track long staking / loan staking deposits for excess calculation
        if (xfer.category === 'long_stake') {
          const key = `long:${xfer.symbol}`;
          stakeDeposits[key] = (stakeDeposits[key] || 0) + xfer.amount;
        } else if (xfer.category === 'loan_stake') {
          const key = `loan:${xfer.symbol}`;
          stakeDeposits[key] = (stakeDeposits[key] || 0) + xfer.amount;
        }

        // Burn = disposal at zero proceeds (realized loss)
        if (xfer.category === 'burn') {
          const costBasis = consumeLots(xfer.symbol, xfer.amount);
          disposals.push({
            date: xfer.date,
            asset: xfer.symbol,
            amount: xfer.amount,
            proceeds_local: 0,
            cost_basis_local: costBasis,
            gain_loss_local: -costBasis,
            method: 'fifo',
            tx_id: xfer.tx_id,
          });
          totalCostBasis += costBasis;
          totalLosses += costBasis;
        } else if (!DEFI_MOVE_CATEGORIES.has(xfer.category)) {
          // Disposal (sending to someone else)
          const proceeds = xfer.amount * rate;
          const costBasis = consumeLots(xfer.symbol, xfer.amount);
          const gainLoss = proceeds - costBasis;

          disposals.push({
            date: xfer.date,
            asset: xfer.symbol,
            amount: xfer.amount,
            proceeds_local: proceeds,
            cost_basis_local: costBasis,
            gain_loss_local: gainLoss,
            method: 'fifo',
            tx_id: xfer.tx_id,
          });

          totalProceeds += proceeds;
          totalCostBasis += costBasis;
          if (gainLoss > 0) totalGains += gainLoss;
          else totalLosses += Math.abs(gainLoss);
        }
      }
    }
  }

  return {
    disposals,
    income_events: incomeEvents,
    summary: {
      total_proceeds: round2(totalProceeds),
      total_cost_basis: round2(totalCostBasis),
      total_gains: round2(totalGains),
      total_losses: round2(totalLosses),
      net_gain_loss: round2(totalGains - totalLosses),
      total_income: round2(totalIncome),
      grand_total_taxable: round2(totalGains - totalLosses + totalIncome),
    },
    remaining_lots: lots,
    method: 'fifo',
    currency,
  };
}

function calculateGainsAverage(
  trades: TradeEvent[],
  transfers: TransferEvent[],
  rates: RateMap,
  currency: string,
): GainsResult {
  // Average cost per asset
  const holdings: Record<string, { total_amount: number; total_cost: number }> = {};
  const disposals: Disposal[] = [];
  const incomeEvents: IncomeEvent[] = [];

  // Track long staking / loan staking deposits per symbol to compute excess on unstake
  const stakeDeposits: Record<string, number> = {};

  function addHolding(asset: string, amount: number, cost: number): void {
    if (!holdings[asset]) holdings[asset] = { total_amount: 0, total_cost: 0 };
    holdings[asset].total_amount += amount;
    holdings[asset].total_cost += cost;
  }

  function avgCostPerUnit(asset: string): number {
    const h = holdings[asset];
    if (!h || h.total_amount <= 0) return 0;
    return h.total_cost / h.total_amount;
  }

  function consumeAvg(asset: string, amount: number): number {
    const h = holdings[asset];
    if (!h || h.total_amount <= 0) return 0;
    const costPerUnit = h.total_cost / h.total_amount;
    const consumed = Math.min(amount, h.total_amount);
    const cost = consumed * costPerUnit;
    h.total_amount -= consumed;
    h.total_cost -= cost;
    return cost;
  }

  const events: Array<{ date: string; event: TradeEvent | TransferEvent }> = [
    ...trades.map(t => ({ date: t.date, event: t })),
    ...transfers.map(t => ({ date: t.date, event: t })),
  ];
  events.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

  let totalProceeds = 0;
  let totalCostBasis = 0;
  let totalGains = 0;
  let totalLosses = 0;
  let totalIncome = 0;

  for (const { event } of events) {
    if (event.type === 'trade') {
      const trade = event as TradeEvent;
      const buyRate = getRate(rates, trade.buy_currency, trade.date);
      const sellRate = getRate(rates, trade.sell_currency, trade.date);

      const proceeds = trade.sell_amount * sellRate;
      const costBasis = consumeAvg(trade.sell_currency, trade.sell_amount);
      const gainLoss = proceeds - costBasis;

      disposals.push({
        date: trade.date,
        asset: trade.sell_currency,
        amount: trade.sell_amount,
        proceeds_local: proceeds,
        cost_basis_local: costBasis,
        gain_loss_local: gainLoss,
        method: 'average',
        tx_id: trade.tx_id,
      });

      totalProceeds += proceeds;
      totalCostBasis += costBasis;
      if (gainLoss > 0) totalGains += gainLoss;
      else totalLosses += Math.abs(gainLoss);

      addHolding(trade.buy_currency, trade.buy_amount, trade.buy_amount * buyRate);

    } else {
      const xfer = event as TransferEvent;
      const rate = getRate(rates, xfer.symbol, xfer.date);

      if (xfer.direction === 'incoming') {
        if (INCOME_CATEGORIES.has(xfer.category)) {
          const value = xfer.amount * rate;
          incomeEvents.push({
            date: xfer.date,
            category: xfer.category,
            asset: xfer.symbol,
            amount: xfer.amount,
            value_local: value,
            tx_id: xfer.tx_id,
          });
          totalIncome += value;
          addHolding(xfer.symbol, xfer.amount, value);

        } else if (LONG_STAKE_INCOME.has(xfer.category)) {
          // Long staking / loan staking unstake — only the EXCESS over deposits is income
          const stakeKey = xfer.category === 'long_unstake' ? `long:${xfer.symbol}` : `loan:${xfer.symbol}`;
          const deposited = stakeDeposits[stakeKey] || 0;
          const excess = Math.max(0, xfer.amount - deposited);
          stakeDeposits[stakeKey] = Math.max(0, deposited - (xfer.amount - excess));

          if (excess > 0) {
            const value = excess * rate;
            incomeEvents.push({
              date: xfer.date,
              category: xfer.category === 'long_unstake' ? 'long_staking_reward' : 'loan_staking_reward',
              asset: xfer.symbol,
              amount: excess,
              value_local: value,
              tx_id: xfer.tx_id,
            });
            totalIncome += value;
          }
          addHolding(xfer.symbol, xfer.amount, xfer.amount * rate);

        } else if (!DEFI_MOVE_CATEGORIES.has(xfer.category)) {
          addHolding(xfer.symbol, xfer.amount, xfer.amount * rate);
        }
      } else {
        // Track staking deposits
        if (xfer.category === 'long_stake') {
          stakeDeposits[`long:${xfer.symbol}`] = (stakeDeposits[`long:${xfer.symbol}`] || 0) + xfer.amount;
        } else if (xfer.category === 'loan_stake') {
          stakeDeposits[`loan:${xfer.symbol}`] = (stakeDeposits[`loan:${xfer.symbol}`] || 0) + xfer.amount;
        }

        // Burn = disposal at zero proceeds (realized loss)
        if (xfer.category === 'burn') {
          const costBasis = consumeAvg(xfer.symbol, xfer.amount);
          disposals.push({
            date: xfer.date,
            asset: xfer.symbol,
            amount: xfer.amount,
            proceeds_local: 0,
            cost_basis_local: costBasis,
            gain_loss_local: -costBasis,
            method: 'average',
            tx_id: xfer.tx_id,
          });
          totalCostBasis += costBasis;
          totalLosses += costBasis;
        } else if (!DEFI_MOVE_CATEGORIES.has(xfer.category)) {
          const proceeds = xfer.amount * rate;
          const costBasis = consumeAvg(xfer.symbol, xfer.amount);
          const gainLoss = proceeds - costBasis;

          disposals.push({
            date: xfer.date,
            asset: xfer.symbol,
            amount: xfer.amount,
            proceeds_local: proceeds,
            cost_basis_local: costBasis,
            gain_loss_local: gainLoss,
            method: 'average',
            tx_id: xfer.tx_id,
          });

          totalProceeds += proceeds;
          totalCostBasis += costBasis;
          if (gainLoss > 0) totalGains += gainLoss;
          else totalLosses += Math.abs(gainLoss);
        }
      }
    }
  }

  // Convert remaining holdings to lot-like format
  const remainingLots: Record<string, Array<{ amount: number; cost_per_unit: number; date: string }>> = {};
  for (const [asset, h] of Object.entries(holdings)) {
    if (h.total_amount > 0) {
      remainingLots[asset] = [{ amount: h.total_amount, cost_per_unit: avgCostPerUnit(asset), date: 'average' }];
    }
  }

  return {
    disposals,
    income_events: incomeEvents,
    summary: {
      total_proceeds: round2(totalProceeds),
      total_cost_basis: round2(totalCostBasis),
      total_gains: round2(totalGains),
      total_losses: round2(totalLosses),
      net_gain_loss: round2(totalGains - totalLosses),
      total_income: round2(totalIncome),
      grand_total_taxable: round2(totalGains - totalLosses + totalIncome),
    },
    remaining_lots: remainingLots,
    method: 'average',
    currency,
  };
}

function round2(n: number): number {
  return Math.round(n * 100) / 100;
}

// ── Tax Bracket Calculation ──────────────────────

function calculateTax(taxableIncome: number, region: RegionConfig): Array<{ bracket: string; income: number; rate: number; tax: number }> {
  const result: Array<{ bracket: string; income: number; rate: number; tax: number }> = [];
  let remaining = taxableIncome;
  let prevLimit = 0;

  for (const { limit, rate } of region.brackets) {
    if (remaining <= 0) break;
    const bracketSize = limit === Infinity ? remaining : Math.min(remaining, limit - prevLimit);
    if (bracketSize <= 0) {
      prevLimit = limit;
      continue;
    }
    const tax = bracketSize * rate;
    const bracketLabel = limit === Infinity
      ? `$${prevLimit.toLocaleString()}+`
      : `$${prevLimit.toLocaleString()} – $${limit.toLocaleString()}`;
    result.push({ bracket: bracketLabel, income: round2(bracketSize), rate, tax: round2(tax) });
    remaining -= bracketSize;
    prevLimit = limit;
  }

  return result;
}

// ── Balance Markdown Formatter ───────────────────

function formatBalancesMarkdown(balances: any): string {
  if (!balances || balances.error) {
    return `*Data unavailable${balances?.error ? `: ${balances.error}` : ''}*`;
  }

  // Handle both grouped format { liquid: [], staked: [] } and flat API response { balances: [] }
  let grouped: Record<string, any[]>;
  if (balances.liquid || balances.staked || balances.lending || balances.yield_farm) {
    grouped = balances;
  } else if (Array.isArray(balances.balances)) {
    grouped = { liquid: [], staked: [], lending: [], yield_farm: [] };
    for (const item of balances.balances) {
      const t = (item.type || 'liquid').toLowerCase().replace(/ /g, '_');
      const bucket = grouped[t] || (grouped[t] = []);
      bucket.push(item);
    }
  } else {
    return '*No balances found*';
  }

  const lines: string[] = [];

  const formatGroup = (name: string, items: any[]) => {
    if (!Array.isArray(items) || items.length === 0) return;
    lines.push(`**${name}:**`);
    lines.push('');
    lines.push('| Token | Amount |');
    lines.push('|-------|-------:|');
    for (const item of items) {
      if (typeof item === 'string') {
        lines.push(`| ${item.split(' ')[1] || '?'} | ${item} |`);
      } else {
        const sym = item.currency || item.symbol || '?';
        const display = item.display || item.amount || item.quantity || item.balance || '?';
        lines.push(`| ${sym} | ${display} |`);
      }
    }
    lines.push('');
  };

  formatGroup('Liquid', grouped.liquid);
  formatGroup('Staked', grouped.staked);
  formatGroup('Lending', grouped.lending);
  formatGroup('Yield Farm', grouped.yield_farm);

  return lines.length > 0 ? lines.join('\n') : '*No balances found*';
}

// ── Skill Entry Point ────────────────────────────

export default function taxSkill(api: SkillApi): void {
  const SALTANT_BASE = 'https://api-xprnetwork-main.saltant.io';
  const METALX_TAX_BASE = 'https://dex.api.mainnet.metalx.com';

  // ════════════════════════════════════════════════
  // 1. tax_get_balances
  // ════════════════════════════════════════════════

  api.registerTool({
    name: 'tax_get_balances',
    description: 'Get token balances at a specific date (or now). Returns liquid, staked, lending (with underlying), and yield farm balances. Uses mainnet Saltant historical balance API.',
    parameters: {
      type: 'object',
      required: ['account'],
      properties: {
        account: { type: 'string', description: 'XPR Network account name' },
        date: { type: 'string', description: 'ISO 8601 date for historical snapshot (default: now). E.g. "2025-03-31T23:59:59Z"' },
      },
    },
    handler: async ({ account, date }: { account: string; date?: string }) => {
      if (!account || typeof account !== 'string') {
        return { error: 'account parameter is required' };
      }

      try {
        let url = `${SALTANT_BASE}/v2/state/get_balance?account=${encodeURIComponent(account)}`;
        if (date) {
          url += `&datetime=${encodeURIComponent(date)}`;
        }

        const data = await httpGetJson(url);

        // API returns { balances: [{ type, symbol, amount, ... }] } — group by type
        const rawBalances: any[] = data.balances || data.liquid || [];
        const balances: Record<string, any[]> = {
          liquid: [],
          staked: [],
          lending: [],
          yield_farm: [],
        };

        const tokenSet = new Set<string>();
        for (const item of rawBalances) {
          const balType = (item.type || 'liquid').toLowerCase().replace(/ /g, '_');
          const sym = item.currency || item.symbol || '';
          if (sym) tokenSet.add(sym);
          const bucket = balances[balType] || (balances[balType] = []);
          bucket.push(item);
        }

        return {
          account,
          date: date || new Date().toISOString(),
          balances,
          tokens_found: tokenSet.size,
          token_list: [...tokenSet].sort(),
        };
      } catch (err: any) {
        return { error: `Failed to fetch balances: ${err.message}` };
      }
    },
  });

  // ════════════════════════════════════════════════
  // 2. tax_get_dex_trades
  // ════════════════════════════════════════════════

  api.registerTool({
    name: 'tax_get_dex_trades',
    description: 'Get Metal X DEX trading history for an account. Returns all trades with buy/sell amounts, currencies, fees, and dates. Date filtering is client-side on the full export.',
    parameters: {
      type: 'object',
      required: ['account'],
      properties: {
        account: { type: 'string', description: 'XPR Network account name' },
        start_date: { type: 'string', description: 'Filter trades after this ISO date (inclusive)' },
        end_date: { type: 'string', description: 'Filter trades before this ISO date (inclusive)' },
      },
    },
    handler: async ({ account, start_date, end_date }: {
      account: string; start_date?: string; end_date?: string;
    }) => {
      if (!account || typeof account !== 'string') {
        return { error: 'account parameter is required' };
      }

      try {
        const url = `${METALX_TAX_BASE}/dex/v1/tax/user?account=${encodeURIComponent(account)}`;
        const csvText = await httpGetText(url);

        if (!csvText || csvText.trim().length === 0) {
          return { trades: [], total: 0, note: 'No trading history found' };
        }

        const rows = parseCSV(csvText);
        if (rows.length === 0) {
          return { trades: [], total: 0, note: 'CSV parsed but no data rows found' };
        }

        // Map CSV columns to trade objects
        // Expected columns: Type, Buy Amount, Buy Currency, Sell Amount, Sell Currency, Fee, Fee Currency, Date, Tx-ID
        // Filter to only "Trade" rows — Withdrawal/Income/Deposit are handled by tax_get_transfers
        let trades = rows
          .filter(row => (row['Type'] || row['type'] || '').toLowerCase() === 'trade')
          .map(row => ({
            type: row['Type'] || row['type'] || '',
            buy_amount: parseFloat(row['Buy Amount'] || row['buy_amount'] || '0'),
            buy_currency: row['Buy Currency'] || row['buy_currency'] || '',
            sell_amount: parseFloat(row['Sell Amount'] || row['sell_amount'] || '0'),
            sell_currency: row['Sell Currency'] || row['sell_currency'] || '',
            fee: parseFloat(row['Fee'] || row['fee'] || '0'),
            fee_currency: row['Fee Currency'] || row['fee_currency'] || '',
            date: row['Date'] || row['date'] || '',
            tx_id: row['Tx-ID'] || row['TxId'] || row['txid'] || row['tx_id'] || '',
          }));

        // Client-side date filtering
        if (start_date) {
          const startMs = new Date(start_date).getTime();
          trades = trades.filter(t => new Date(t.date).getTime() >= startMs);
        }
        if (end_date) {
          const endMs = new Date(end_date).getTime();
          trades = trades.filter(t => new Date(t.date).getTime() <= endMs);
        }

        // Volume summary
        const volumeByCurrency: Record<string, number> = {};
        for (const t of trades) {
          if (t.sell_currency) {
            volumeByCurrency[t.sell_currency] = (volumeByCurrency[t.sell_currency] || 0) + t.sell_amount;
          }
        }

        return {
          trades,
          total: trades.length,
          volume_by_currency: volumeByCurrency,
          date_range: trades.length > 0
            ? { earliest: trades[0].date, latest: trades[trades.length - 1].date }
            : null,
        };
      } catch (err: any) {
        return { error: `Failed to fetch DEX trades: ${err.message}` };
      }
    },
  });

  // ════════════════════════════════════════════════
  // 3. tax_get_transfers
  // ════════════════════════════════════════════════

  api.registerTool({
    name: 'tax_get_transfers',
    description: 'Get on-chain transfer history with automatic categorization. Categories: staking_reward, lending_deposit/withdrawal/interest, swap_deposit/withdrawal, long_stake/unstake, loan_stake/unstake, dex_deposit/withdrawal, nft_sale/purchase, burn, escrow, transfer. Paginated from Hyperion.',
    parameters: {
      type: 'object',
      required: ['account'],
      properties: {
        account: { type: 'string', description: 'XPR Network account name' },
        start_date: { type: 'string', description: 'Filter after this ISO date' },
        end_date: { type: 'string', description: 'Filter before this ISO date' },
        max_results: { type: 'number', description: 'Max transfers to return (default 1000, max 5000)' },
      },
    },
    handler: async ({ account, start_date, end_date, max_results }: {
      account: string; start_date?: string; end_date?: string; max_results?: number;
    }) => {
      if (!account || typeof account !== 'string') {
        return { error: 'account parameter is required' };
      }

      const limit = Math.min(max_results || 1000, 5000);
      const pageSize = 100;
      const allTransfers: CategorizedTransfer[] = [];

      try {
        let skip = 0;
        let hasMore = true;

        while (hasMore && allTransfers.length < limit) {
          let url = `${SALTANT_BASE}/v2/history/get_actions?account=${encodeURIComponent(account)}&act.name=transfer&limit=100&sort=asc&skip=${skip}`;
          if (start_date) url += `&after=${encodeURIComponent(start_date)}`;
          if (end_date) url += `&before=${encodeURIComponent(end_date)}`;

          const data = await httpGetJson(url);
          const actions: any[] = data.actions || [];

          if (actions.length === 0) {
            hasMore = false;
            break;
          }

          for (const action of actions) {
            if (allTransfers.length >= limit) break;

            const act = action.act?.data || {};
            const from = act.from || '';
            const to = act.to || '';
            const memo = act.memo || '';

            // Parse amount: "100.0000 XPR" → { amount: 100, symbol: "XPR" }
            const quantityStr = act.quantity || '0 UNKNOWN';
            const parts = quantityStr.split(' ');
            const amount = parseFloat(parts[0]) || 0;
            const symbol = parts[1] || 'UNKNOWN';

            if (amount === 0) continue;

            const category = categorizeTransfer(account, from, to, amount, symbol, memo);
            const direction: 'incoming' | 'outgoing' = to === account ? 'incoming' : 'outgoing';
            const timestamp = action['@timestamp'] || action.timestamp || '';

            allTransfers.push({
              category,
              from,
              to,
              amount,
              symbol,
              memo,
              timestamp,
              tx_id: action.trx_id || '',
              direction,
            });
          }

          skip += actions.length;
          if (actions.length < pageSize) hasMore = false;
        }

        // Summary by category
        const byCategory: Record<string, number> = {};
        const bySymbol: Record<string, { incoming: number; outgoing: number }> = {};
        for (const t of allTransfers) {
          byCategory[t.category] = (byCategory[t.category] || 0) + 1;
          if (!bySymbol[t.symbol]) bySymbol[t.symbol] = { incoming: 0, outgoing: 0 };
          bySymbol[t.symbol][t.direction] += t.amount;
        }

        return {
          transfers: allTransfers,
          total: allTransfers.length,
          summary_by_category: byCategory,
          summary_by_symbol: bySymbol,
          truncated: allTransfers.length >= limit,
        };
      } catch (err: any) {
        return { error: `Failed to fetch transfers: ${err.message}` };
      }
    },
  });

  // ════════════════════════════════════════════════
  // 4. tax_get_rates
  // ════════════════════════════════════════════════

  api.registerTool({
    name: 'tax_get_rates',
    description: 'Get local currency conversion rates for crypto tokens. Uses CoinGecko for major tokens, forex for stablecoins. Supports current and historical rates. Returns a map of "SYMBOL:date" → rate.',
    parameters: {
      type: 'object',
      required: ['symbols'],
      properties: {
        symbols: {
          type: 'array',
          description: 'Array of token symbols to get rates for, e.g. ["XPR", "XUSDC", "XBTC"]',
        },
        date: { type: 'string', description: 'ISO date for historical rate (default: current). E.g. "2025-03-31"' },
        region: { type: 'string', description: 'Region code: "NZ" (default, NZD) or "US" (USD)' },
      },
    },
    handler: async ({ symbols, date, region }: {
      symbols: string[]; date?: string; region?: string;
    }) => {
      if (!Array.isArray(symbols) || symbols.length === 0) {
        return { error: 'symbols must be a non-empty array of token symbols' };
      }

      const regionConfig = getRegion(region);
      const currency = regionConfig.currency.toLowerCase();
      const rates: Record<string, number> = {};
      const errors: string[] = [];

      // Separate stablecoins from others
      const stableSymbols = symbols.filter(s => STABLECOINS.has(s.toUpperCase()));
      const cryptoSymbols = symbols.filter(s => !STABLECOINS.has(s.toUpperCase()));

      // Get USD → local forex rate upfront (needed for stablecoins AND USD fallback)
      let forexRate = 1;
      if (currency !== 'usd') {
        try {
          const forexData = await cgFetch(`/simple/price?ids=usd-coin&vs_currencies=${currency}`);
          forexRate = forexData['usd-coin']?.[currency] || 1;
        } catch (err: any) {
          errors.push(`Forex rate error: ${err.message}`);
        }
      }

      // 1. Handle stablecoins via forex rate (USD → local)
      if (stableSymbols.length > 0) {
        const dk = date ? dateKey(date) : 'current';
        for (const sym of stableSymbols) {
          const key = `${sym.toUpperCase()}:${dk}`;
          rates[key] = forexRate;
        }
      }

      // 2. Handle crypto tokens via CoinGecko
      if (cryptoSymbols.length > 0) {
        if (date) {
          // Historical: one request per token (CoinGecko /coins/{id}/history)
          const d = new Date(date);
          const ddMmYyyy = `${String(d.getUTCDate()).padStart(2, '0')}-${String(d.getUTCMonth() + 1).padStart(2, '0')}-${d.getUTCFullYear()}`;

          for (const sym of cryptoSymbols) {
            const upper = sym.toUpperCase();
            const cacheKey = `${upper}:${dateKey(date)}`;

            if (rateCache.has(cacheKey)) {
              rates[cacheKey] = rateCache.get(cacheKey)!;
              continue;
            }

            const cgId = TOKEN_TO_COINGECKO[upper];
            if (!cgId) {
              errors.push(`No CoinGecko mapping for ${upper}`);
              continue;
            }

            try {
              const histData = await cgFetch(`/coins/${cgId}/history?date=${ddMmYyyy}`);
              // Prefer local currency price; if unavailable, use USD × forex rate
              let price = histData?.market_data?.current_price?.[currency] || 0;
              if (!price) {
                const usdPrice = histData?.market_data?.current_price?.usd || 0;
                price = usdPrice * forexRate;
              }
              rates[cacheKey] = price;
              cacheRate(cacheKey, price);
            } catch (err: any) {
              errors.push(`CoinGecko history error for ${upper}: ${err.message}`);
            }

            await sleep(getCoinGeckoConfig().hasKey ? 100 : 200); // Rate limit (faster with key)
          }
        } else {
          // Current: batch request
          const cgIds = cryptoSymbols
            .map(s => TOKEN_TO_COINGECKO[s.toUpperCase()])
            .filter(Boolean);

          if (cgIds.length > 0) {
            try {
              const batchData = await cgFetch(`/simple/price?ids=${cgIds.join(',')}&vs_currencies=${currency},usd`);

              for (const sym of cryptoSymbols) {
                const upper = sym.toUpperCase();
                const cgId = TOKEN_TO_COINGECKO[upper];
                if (!cgId) continue;
                // Prefer local currency; if unavailable, use USD × forex rate
                let price = batchData[cgId]?.[currency] || 0;
                if (!price) {
                  price = (batchData[cgId]?.usd || 0) * forexRate;
                }
                rates[`${upper}:current`] = price;
              }
            } catch (err: any) {
              errors.push(`CoinGecko batch error: ${err.message}`);
            }
          }

          // Map symbols without CoinGecko IDs
          for (const sym of cryptoSymbols) {
            const upper = sym.toUpperCase();
            if (!TOKEN_TO_COINGECKO[upper] && !rates[`${upper}:current`]) {
              errors.push(`No CoinGecko mapping for ${upper} — price unavailable`);
            }
          }
        }
      }

      saveRateCache();

      return {
        rates,
        currency: regionConfig.currency,
        date: date || 'current',
        errors: errors.length > 0 ? errors : undefined,
      };
    },
  });

  // ════════════════════════════════════════════════
  // 5. tax_calculate_gains
  // ════════════════════════════════════════════════

  api.registerTool({
    name: 'tax_calculate_gains',
    description: 'Calculate taxable gains/losses using FIFO or Average Cost method. Takes pre-fetched trades, transfers, and rates. Returns disposals, income events, and summary with total taxable income.',
    parameters: {
      type: 'object',
      required: ['trades', 'transfers', 'rates'],
      properties: {
        trades: {
          type: 'array',
          description: 'Array of DEX trades from tax_get_dex_trades',
        },
        transfers: {
          type: 'array',
          description: 'Array of categorized transfers from tax_get_transfers',
        },
        rates: {
          type: 'object',
          description: 'Rate map from tax_get_rates: {"SYMBOL:YYYY-MM-DD": rate}',
        },
        method: { type: 'string', description: '"fifo" (default) or "average"' },
        region: { type: 'string', description: 'Region code: "NZ" (default) or "US"' },
      },
    },
    handler: async ({ trades, transfers, rates, method, region }: {
      trades: any[]; transfers: any[]; rates: Record<string, number>;
      method?: string; region?: string;
    }) => {
      const regionConfig = getRegion(region);
      const costMethod = (method || 'fifo').toLowerCase();

      if (!regionConfig.cost_basis_methods.includes(costMethod)) {
        return { error: `Method "${costMethod}" not supported for ${regionConfig.code}. Supported: ${regionConfig.cost_basis_methods.join(', ')}` };
      }

      // Normalize trade objects
      const tradeEvents: TradeEvent[] = (trades || []).map((t: any) => ({
        type: 'trade' as const,
        date: t.date || '',
        buy_amount: parseFloat(t.buy_amount) || 0,
        buy_currency: t.buy_currency || '',
        sell_amount: parseFloat(t.sell_amount) || 0,
        sell_currency: t.sell_currency || '',
        fee: parseFloat(t.fee) || 0,
        fee_currency: t.fee_currency || '',
        tx_id: t.tx_id || '',
      }));

      // Normalize transfer objects
      const transferEvents: TransferEvent[] = (transfers || []).map((t: any) => ({
        type: 'transfer' as const,
        date: t.timestamp || t.date || '',
        category: t.category || 'transfer',
        amount: parseFloat(t.amount) || 0,
        symbol: t.symbol || '',
        direction: t.direction || 'incoming',
        tx_id: t.tx_id || '',
      }));

      const result = costMethod === 'average'
        ? calculateGainsAverage(tradeEvents, transferEvents, rates, regionConfig.currency)
        : calculateGainsFIFO(tradeEvents, transferEvents, rates, regionConfig.currency);

      return result;
    },
  });

  // ════════════════════════════════════════════════
  // 6. tax_generate_report
  // ════════════════════════════════════════════════

  api.registerTool({
    name: 'tax_generate_report',
    description: 'Generate a full crypto tax report. Orchestrates all tax tools: fetches balances, trades, transfers, rates, calculates gains, and estimates tax by bracket. Can accept pre-computed data to skip API calls.',
    parameters: {
      type: 'object',
      required: ['account', 'tax_year'],
      properties: {
        account: { type: 'string', description: 'XPR Network account name' },
        tax_year: { type: 'number', description: 'Tax year number. NZ: 2025 = Apr 2024–Mar 2025. US: 2024 = Jan 2024–Dec 2024' },
        method: { type: 'string', description: '"fifo" (default) or "average"' },
        region: { type: 'string', description: 'Region code: "NZ" (default) or "US"' },
        balances_opening: { type: 'object', description: 'Pre-computed opening balances (skip API call)' },
        balances_closing: { type: 'object', description: 'Pre-computed closing balances (skip API call)' },
        trades: { type: 'array', description: 'Pre-computed trades array (skip API call)' },
        transfers: { type: 'array', description: 'Pre-computed transfers array (skip API call)' },
      },
    },
    handler: async ({ account, tax_year, method, region, balances_opening, balances_closing, trades, transfers }: {
      account: string;
      tax_year: number;
      method?: string;
      region?: string;
      balances_opening?: any;
      balances_closing?: any;
      trades?: any[];
      transfers?: any[];
    }) => {
      if (!account || typeof account !== 'string') {
        return { error: 'account parameter is required' };
      }
      if (!tax_year || typeof tax_year !== 'number') {
        return { error: 'tax_year parameter is required (e.g. 2025)' };
      }

      const regionConfig = getRegion(region);
      const costMethod = (method || 'fifo').toLowerCase();
      const { start, end } = getTaxYearDates(tax_year, regionConfig);
      const currency = regionConfig.currency.toLowerCase();
      const steps: string[] = [];

      try {
        // Step 1: Fetch opening balances
        let openingBalances = balances_opening;
        if (!openingBalances) {
          steps.push('Fetching opening balances...');
          try {
            let url = `${SALTANT_BASE}/v2/state/get_balance?account=${encodeURIComponent(account)}&datetime=${encodeURIComponent(start)}`;
            openingBalances = await httpGetJson(url);
          } catch (err: any) {
            openingBalances = { error: err.message };
          }
        }

        // Step 2: Fetch closing balances
        let closingBalances = balances_closing;
        if (!closingBalances) {
          steps.push('Fetching closing balances...');
          try {
            let url = `${SALTANT_BASE}/v2/state/get_balance?account=${encodeURIComponent(account)}&datetime=${encodeURIComponent(end)}`;
            closingBalances = await httpGetJson(url);
          } catch (err: any) {
            closingBalances = { error: err.message };
          }
        }

        // Step 3: Fetch DEX trades
        let tradeData = trades;
        if (!tradeData) {
          steps.push('Fetching DEX trades...');
          try {
            const url = `${METALX_TAX_BASE}/dex/v1/tax/user?account=${encodeURIComponent(account)}`;
            const csvText = await httpGetText(url);
            const rows = parseCSV(csvText);

            tradeData = rows
              .filter(row => (row['Type'] || row['type'] || '').toLowerCase() === 'trade')
              .map(row => ({
                type: row['Type'] || row['type'] || '',
                buy_amount: parseFloat(row['Buy Amount'] || row['buy_amount'] || '0'),
                buy_currency: row['Buy Currency'] || row['buy_currency'] || '',
                sell_amount: parseFloat(row['Sell Amount'] || row['sell_amount'] || '0'),
                sell_currency: row['Sell Currency'] || row['sell_currency'] || '',
                fee: parseFloat(row['Fee'] || row['fee'] || '0'),
                fee_currency: row['Fee Currency'] || row['fee_currency'] || '',
                date: row['Date'] || row['date'] || '',
                tx_id: row['Tx-ID'] || row['TxId'] || row['txid'] || row['tx_id'] || '',
              }));

            // Filter to tax year
            const startMs = new Date(start).getTime();
            const endMs = new Date(end).getTime();
            tradeData = tradeData.filter(t => {
              const ms = new Date(t.date).getTime();
              return ms >= startMs && ms <= endMs;
            });
          } catch (err: any) {
            tradeData = [];
            steps.push(`DEX trades error: ${err.message}`);
          }
        }

        // Step 4: Fetch transfers
        let transferData = transfers;
        if (!transferData) {
          steps.push('Fetching transfers...');
          try {
            const allTransfers: CategorizedTransfer[] = [];
            let skip = 0;
            let hasMore = true;
            const maxTransfers = 5000;
            const pageSize = 100;

            while (hasMore && allTransfers.length < maxTransfers) {
              let url = `${SALTANT_BASE}/v2/history/get_actions?account=${encodeURIComponent(account)}&act.name=transfer&limit=100&sort=asc&skip=${skip}`;
              url += `&after=${encodeURIComponent(start)}&before=${encodeURIComponent(end)}`;

              const data = await httpGetJson(url);
              const actions: any[] = data.actions || [];

              if (actions.length === 0) { hasMore = false; break; }

              for (const action of actions) {
                if (allTransfers.length >= maxTransfers) break;
                const act = action.act?.data || {};
                const from = act.from || '';
                const to = act.to || '';
                const memo = act.memo || '';
                const quantityStr = act.quantity || '0 UNKNOWN';
                const parts = quantityStr.split(' ');
                const amount = parseFloat(parts[0]) || 0;
                const symbol = parts[1] || 'UNKNOWN';
                if (amount === 0) continue;

                const category = categorizeTransfer(account, from, to, amount, symbol, memo);
                const direction: 'incoming' | 'outgoing' = to === account ? 'incoming' : 'outgoing';

                allTransfers.push({
                  category, from, to, amount, symbol, memo,
                  timestamp: action['@timestamp'] || action.timestamp || '',
                  tx_id: action.trx_id || '',
                  direction,
                });
              }

              skip += actions.length;
              if (actions.length < pageSize) hasMore = false;
            }

            transferData = allTransfers;
          } catch (err: any) {
            transferData = [];
            steps.push(`Transfers error: ${err.message}`);
          }
        }

        // Step 5: Build conversion rates
        // Strategy: DEX trades give us direct price ratios (primary source),
        // stablecoins use forex rate, CoinGecko as fallback for recent dates only
        steps.push('Building conversion rates...');
        const rates: Record<string, number> = {};
        const allSymbols = new Set<string>();
        const uniqueDates = new Set<string>();

        for (const t of (tradeData || [])) {
          if (t.buy_currency) { allSymbols.add(t.buy_currency); uniqueDates.add(dateKey(t.date)); }
          if (t.sell_currency) { allSymbols.add(t.sell_currency); uniqueDates.add(dateKey(t.date)); }
        }
        for (const t of (transferData || []) as CategorizedTransfer[]) {
          if (t.symbol) { allSymbols.add(t.symbol); uniqueDates.add(dateKey(t.timestamp)); }
        }

        // Pre-populate rates from persistent cache (historical prices are immutable)
        let cacheHits = 0;
        for (const sym of allSymbols) {
          const upper = sym.toUpperCase();
          for (const d of uniqueDates) {
            const key = `${upper}:${d}`;
            const cached = rateCache.get(key);
            if (cached && cached > 0) {
              rates[key] = cached;
              cacheHits++;
            }
          }
        }
        if (cacheHits > 0) steps.push(`Loaded ${cacheHits} rates from cache`);

        // Get USD→local forex rate (stablecoins and XMD are pegged to USD)
        let forexRate = 1;
        if (currency !== 'usd') {
          try {
            const forexData = await cgFetch(`/simple/price?ids=usd-coin&vs_currencies=${currency}`);
            forexRate = forexData['usd-coin']?.[currency] || 1;
          } catch { /* use 1 */ }
        }

        // Set stablecoin/XMD rates for all dates (they're pegged to USD)
        for (const sym of allSymbols) {
          const upper = sym.toUpperCase();
          if (STABLECOINS.has(upper) || upper === 'XMD') {
            for (const d of uniqueDates) {
              rates[`${upper}:${d}`] = forexRate;
            }
            rates[`${upper}:current`] = forexRate;
          }
        }

        // Derive token rates from DEX trades (primary source — no API limits)
        // Most trades are TOKEN→XMD, so rate = buy_xmd / sell_token * forexRate
        const dexRatesByDate: Record<string, number> = {}; // "SYMBOL:date" → local rate
        for (const t of (tradeData || [])) {
          if (!t.date || !t.sell_currency || !t.buy_currency) continue;
          const d = dateKey(t.date);

          // TOKEN → XMD: sell token, buy XMD → token price = (buy_xmd / sell_token) * forex
          if ((t.buy_currency === 'XMD' || STABLECOINS.has(t.buy_currency.toUpperCase())) && t.sell_amount > 0 && t.buy_amount > 0) {
            const tokenRate = (t.buy_amount / t.sell_amount) * forexRate;
            const key = `${t.sell_currency.toUpperCase()}:${d}`;
            // Use last trade of the day (overwrites earlier)
            dexRatesByDate[key] = tokenRate;
          }
          // XMD → TOKEN: sell XMD, buy token → token price = (sell_xmd / buy_token) * forex
          if ((t.sell_currency === 'XMD' || STABLECOINS.has(t.sell_currency.toUpperCase())) && t.buy_amount > 0 && t.sell_amount > 0) {
            const tokenRate = (t.sell_amount / t.buy_amount) * forexRate;
            const key = `${t.buy_currency.toUpperCase()}:${d}`;
            dexRatesByDate[key] = tokenRate;
          }
        }

        // Apply DEX-derived rates
        for (const [key, rate] of Object.entries(dexRatesByDate)) {
          if (!rates[key]) {
            rates[key] = rate;
            cacheRate(key, rate);
          }
        }

        // Fill gaps: for dates without a DEX trade, use nearest available DEX rate
        const symbolsNeedingRates = [...allSymbols].filter(s => {
          const upper = s.toUpperCase();
          return !STABLECOINS.has(upper) && upper !== 'XMD';
        });
        const sortedDates = [...uniqueDates].sort();

        for (const sym of symbolsNeedingRates) {
          const upper = sym.toUpperCase();
          let lastKnownRate = 0;

          for (const d of sortedDates) {
            const key = `${upper}:${d}`;
            if (rates[key] && rates[key] > 0) {
              lastKnownRate = rates[key];
            } else if (lastKnownRate > 0) {
              // Forward-fill from last known rate
              rates[key] = lastKnownRate;
            }
          }
        }

        // Fallback: CoinGecko for dates where we still have no rate
        // With API key: no date limit, higher rate limits, more fetches allowed
        // Without key: limited to 365 days, max 30 fetches
        const cgConfig = getCoinGeckoConfig();
        const now = Date.now();
        const oneYearMs = 365 * 24 * 60 * 60 * 1000;
        let cgFetches = 0;
        const MAX_CG_FETCHES = cgConfig.hasKey ? 2000 : 30;
        const CG_DELAY = cgConfig.hasKey ? 100 : 200;

        for (const d of sortedDates) {
          const dateMs = new Date(d + 'T00:00:00Z').getTime();
          if (isNaN(dateMs)) continue;
          // Without API key, skip dates beyond 365 days (CoinGecko free limit)
          if (!cgConfig.hasKey && (now - dateMs) > oneYearMs) continue;

          for (const sym of symbolsNeedingRates) {
            const upper = sym.toUpperCase();
            const key = `${upper}:${d}`;
            if (rates[key] && rates[key] > 0) continue;
            if (cgFetches >= MAX_CG_FETCHES) continue;

            const cgId = TOKEN_TO_COINGECKO[upper];
            if (!cgId) continue;

            const dateObj = new Date(d + 'T00:00:00Z');
            const ddMmYyyy = `${String(dateObj.getUTCDate()).padStart(2, '0')}-${String(dateObj.getUTCMonth() + 1).padStart(2, '0')}-${dateObj.getUTCFullYear()}`;

            try {
              const histData = await cgFetch(`/coins/${cgId}/history?date=${ddMmYyyy}`);
              // Prefer local currency; if unavailable, use USD × forex rate
              let price = histData?.market_data?.current_price?.[currency] || 0;
              if (!price) {
                const usdPrice = histData?.market_data?.current_price?.usd || 0;
                price = usdPrice * forexRate;
              }
              if (price > 0) {
                rates[key] = price;
                cacheRate(key, price);
              }
              cgFetches++;
            } catch { /* skip */ }

            await sleep(CG_DELAY);
          }
        }

        // Forward-fill again after CoinGecko to cover remaining gaps
        for (const sym of symbolsNeedingRates) {
          const upper = sym.toUpperCase();
          let lastKnownRate = 0;
          for (const d of sortedDates) {
            const key = `${upper}:${d}`;
            if (rates[key] && rates[key] > 0) {
              lastKnownRate = rates[key];
            } else if (lastKnownRate > 0) {
              rates[key] = lastKnownRate;
            }
          }
          // Also backward-fill: if the first few dates had no rate but later ones do
          let firstKnownRate = 0;
          for (let i = sortedDates.length - 1; i >= 0; i--) {
            const d = sortedDates[i];
            const key = `${upper}:${d}`;
            if (rates[key] && rates[key] > 0) {
              firstKnownRate = rates[key];
            } else if (firstKnownRate > 0) {
              rates[key] = firstKnownRate;
            }
          }
        }

        // Final fallback: fetch current rate for any symbols still missing
        const missingSymbols = symbolsNeedingRates.filter(sym => {
          const upper = sym.toUpperCase();
          return sortedDates.some(d => !rates[`${upper}:${d}`] || rates[`${upper}:${d}`] === 0);
        });
        if (missingSymbols.length > 0) {
          const cgIds = missingSymbols.map(s => TOKEN_TO_COINGECKO[s.toUpperCase()]).filter(Boolean);
          if (cgIds.length > 0) {
            try {
              const currentData = await cgFetch(`/simple/price?ids=${cgIds.join(',')}&vs_currencies=${currency},usd`);
              for (const sym of missingSymbols) {
                const upper = sym.toUpperCase();
                const cgId = TOKEN_TO_COINGECKO[upper];
                if (!cgId || !currentData[cgId]) continue;
                let price = currentData[cgId][currency] || 0;
                if (!price) {
                  price = (currentData[cgId].usd || 0) * forexRate;
                }
                if (price > 0) {
                  // Apply to all dates that still have no rate
                  for (const d of sortedDates) {
                    const key = `${upper}:${d}`;
                    if (!rates[key] || rates[key] === 0) {
                      rates[key] = price;
                    }
                  }
                  rates[`${upper}:current`] = price;
                }
              }
            } catch { /* skip */ }
          }
        }

        // Persist rate cache to disk
        saveRateCache();

        // Step 6: Calculate gains
        steps.push('Calculating gains...');
        const tradeEvents: TradeEvent[] = (tradeData || []).map((t: any) => ({
          type: 'trade' as const,
          date: t.date || '',
          buy_amount: parseFloat(t.buy_amount) || 0,
          buy_currency: t.buy_currency || '',
          sell_amount: parseFloat(t.sell_amount) || 0,
          sell_currency: t.sell_currency || '',
          fee: parseFloat(t.fee) || 0,
          fee_currency: t.fee_currency || '',
          tx_id: t.tx_id || '',
        }));

        const transferEvents: TransferEvent[] = (transferData || []).map((t: any) => ({
          type: 'transfer' as const,
          date: t.timestamp || t.date || '',
          category: t.category || 'transfer',
          amount: parseFloat(t.amount) || 0,
          symbol: t.symbol || '',
          direction: t.direction || 'incoming',
          tx_id: t.tx_id || '',
        }));

        const gains = costMethod === 'average'
          ? calculateGainsAverage(tradeEvents, transferEvents, rates, regionConfig.currency)
          : calculateGainsFIFO(tradeEvents, transferEvents, rates, regionConfig.currency);

        // Step 7: Estimate tax
        const taxableIncome = gains.summary.grand_total_taxable;
        const taxBrackets = calculateTax(Math.max(0, taxableIncome), regionConfig);
        const estimatedTax = taxBrackets.reduce((sum, b) => sum + b.tax, 0);

        // Build CSV exports
        const disposalCsv = [
          'Date,Asset,Amount,Proceeds,Cost Basis,Gain/Loss,Method,TX ID',
          ...gains.disposals.map(d =>
            `${d.date},${d.asset},${d.amount},${d.proceeds_local.toFixed(2)},${d.cost_basis_local.toFixed(2)},${d.gain_loss_local.toFixed(2)},${d.method},${d.tx_id || ''}`
          ),
        ].join('\n');

        const incomeCsv = [
          'Date,Category,Asset,Amount,Value,TX ID',
          ...gains.income_events.map(e =>
            `${e.date},${e.category},${e.asset},${e.amount},${e.value_local.toFixed(2)},${e.tx_id || ''}`
          ),
        ].join('\n');

        // Transfer summary by category
        const transferSummary: Record<string, number> = {};
        for (const t of (transferData || []) as CategorizedTransfer[]) {
          transferSummary[t.category] = (transferSummary[t.category] || 0) + 1;
        }

        // Income by category
        const incomeByCategory = gains.income_events.reduce((acc: Record<string, number>, e) => {
          acc[e.category] = (acc[e.category] || 0) + e.value_local;
          return acc;
        }, {});

        const effectiveRate = taxableIncome > 0
          ? `${((estimatedTax / taxableIncome) * 100).toFixed(2)}%`
          : '0%';

        // ── Build formatted markdown report ──
        const CUR = regionConfig.currency;
        const fmt = (n: number) => `$${n.toLocaleString('en-NZ', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        const startLabel = start.slice(0, 10);
        const endLabel = end.slice(0, 10);

        const md: string[] = [];
        md.push(`# Crypto Tax Report — ${regionConfig.name}`);
        md.push('');
        md.push(`**Account:** \`${account}\``);
        md.push(`**Tax Year:** ${tax_year} (${startLabel} to ${endLabel})`);
        md.push(`**Currency:** ${CUR}`);
        md.push(`**Cost Basis Method:** ${costMethod.toUpperCase()}`);
        md.push(`**Generated:** ${new Date().toISOString().slice(0, 10)}`);
        md.push('');

        // Balance sheets
        md.push('---');
        md.push('');
        md.push('## Balance Snapshots');
        md.push('');
        md.push(`### Opening Balances (${startLabel})`);
        md.push('');
        md.push(formatBalancesMarkdown(openingBalances));
        md.push('');
        md.push(`### Closing Balances (${endLabel})`);
        md.push('');
        md.push(formatBalancesMarkdown(closingBalances));
        md.push('');

        // Activity summary
        md.push('---');
        md.push('');
        md.push('## Activity Summary');
        md.push('');
        md.push(`| Metric | Count |`);
        md.push(`|--------|-------|`);
        md.push(`| DEX Trades | ${(tradeData || []).length} |`);
        md.push(`| On-chain Transfers | ${(transferData || []).length} |`);
        md.push('');

        if (Object.keys(transferSummary).length > 0) {
          md.push('**Transfers by Category:**');
          md.push('');
          md.push('| Category | Count |');
          md.push('|----------|-------|');
          for (const [cat, count] of Object.entries(transferSummary).sort((a, b) => (b[1] as number) - (a[1] as number))) {
            md.push(`| ${cat} | ${count} |`);
          }
          md.push('');
        }

        // Trading summary
        md.push('---');
        md.push('');
        md.push('## Trading Summary');
        md.push('');
        md.push(`| | ${CUR} |`);
        md.push(`|---|---:|`);
        md.push(`| Total Proceeds | ${fmt(gains.summary.total_proceeds)} |`);
        md.push(`| Total Cost Basis | ${fmt(gains.summary.total_cost_basis)} |`);
        md.push(`| **Net Gain/Loss** | **${fmt(gains.summary.net_gain_loss)}** |`);
        md.push(`| Disposals | ${gains.disposals.length} |`);
        md.push('');

        // Top disposals (max 20)
        if (gains.disposals.length > 0) {
          md.push('### Disposals');
          md.push('');
          md.push('| Date | Asset | Amount | Proceeds | Cost Basis | Gain/Loss |');
          md.push('|------|-------|-------:|--------:|---------:|----------:|');
          const topDisposals = gains.disposals.slice(0, 20);
          for (const d of topDisposals) {
            md.push(`| ${d.date.slice(0, 10)} | ${d.asset} | ${d.amount} | ${fmt(d.proceeds_local)} | ${fmt(d.cost_basis_local)} | ${fmt(d.gain_loss_local)} |`);
          }
          if (gains.disposals.length > 20) {
            md.push(`| ... | *${gains.disposals.length - 20} more* | | | | |`);
          }
          md.push('');
        }

        // Income summary
        md.push('---');
        md.push('');
        md.push('## Income Summary');
        md.push('');
        md.push(`| Category | ${CUR} |`);
        md.push(`|----------|---:|`);
        for (const [cat, val] of Object.entries(incomeByCategory).sort((a, b) => (b[1] as number) - (a[1] as number))) {
          md.push(`| ${cat} | ${fmt(val as number)} |`);
        }
        md.push(`| **Total Income** | **${fmt(gains.summary.total_income)}** |`);
        md.push('');

        // Top income events (max 20)
        if (gains.income_events.length > 0) {
          md.push('### Income Events');
          md.push('');
          md.push('| Date | Category | Asset | Amount | Value |');
          md.push('|------|----------|-------|-------:|------:|');
          const topIncome = gains.income_events.slice(0, 20);
          for (const e of topIncome) {
            md.push(`| ${e.date.slice(0, 10)} | ${e.category} | ${e.asset} | ${e.amount} | ${fmt(e.value_local)} |`);
          }
          if (gains.income_events.length > 20) {
            md.push(`| ... | *${gains.income_events.length - 20} more* | | | |`);
          }
          md.push('');
        }

        // Tax estimate
        md.push('---');
        md.push('');
        md.push('## Estimated Tax');
        md.push('');
        md.push(`| | ${CUR} |`);
        md.push(`|---|---:|`);
        md.push(`| Net Trading Gain/Loss | ${fmt(gains.summary.net_gain_loss)} |`);
        md.push(`| Total Income | ${fmt(gains.summary.total_income)} |`);
        md.push(`| **Total Taxable** | **${fmt(gains.summary.grand_total_taxable)}** |`);
        md.push('');

        if (taxBrackets.length > 0) {
          md.push('**Tax Brackets:**');
          md.push('');
          md.push('| Bracket | Income | Rate | Tax |');
          md.push('|---------|-------:|-----:|----:|');
          for (const b of taxBrackets) {
            md.push(`| ${b.bracket} | ${fmt(b.income)} | ${(b.rate * 100).toFixed(1)}% | ${fmt(b.tax)} |`);
          }
          md.push(`| **Total** | | | **${fmt(round2(estimatedTax))}** |`);
          md.push(`| **Effective Rate** | | **${effectiveRate}** | |`);
          md.push('');
        }

        if (!regionConfig.has_capital_gains) {
          md.push('> No separate capital gains tax in ' + regionConfig.name + ' — all crypto gains are treated as income.');
          md.push('');
        }

        // Disclaimer
        md.push('---');
        md.push('');
        md.push(`**Disclaimer:** ${regionConfig.disclaimer}`);
        md.push('');

        const reportMarkdown = md.join('\n');

        return {
          report: {
            account,
            tax_year: tax_year,
            region: regionConfig.code,
            currency: regionConfig.currency,
            period: { start, end },
            method: costMethod,
          },
          opening_balances: openingBalances,
          closing_balances: closingBalances,
          activity: {
            dex_trades: (tradeData || []).length,
            transfers: (transferData || []).length,
            transfer_categories: transferSummary,
          },
          trading_summary: {
            total_proceeds: gains.summary.total_proceeds,
            total_cost_basis: gains.summary.total_cost_basis,
            net_gain_loss: gains.summary.net_gain_loss,
            total_disposals: gains.disposals.length,
          },
          income_summary: {
            total_income: gains.summary.total_income,
            by_category: incomeByCategory,
            total_events: gains.income_events.length,
          },
          tax_estimate: {
            total_taxable_income: gains.summary.grand_total_taxable,
            brackets: taxBrackets,
            estimated_tax: round2(estimatedTax),
            effective_rate: effectiveRate,
            note: regionConfig.has_capital_gains
              ? 'Capital gains tax applies in this region'
              : 'No separate capital gains tax — all gains treated as income',
          },
          report_markdown: reportMarkdown,
          csv_exports: {
            disposals: disposalCsv,
            income: incomeCsv,
          },
          remaining_cost_basis: gains.remaining_lots,
          steps_completed: steps,
          disclaimer: regionConfig.disclaimer,
        };
      } catch (err: any) {
        return { error: `Report generation failed: ${err.message}`, steps_completed: steps };
      }
    },
  });
}
