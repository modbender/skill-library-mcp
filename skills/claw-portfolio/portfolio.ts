#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { z } from 'zod';
import { fetchDividendData, calculateDividendMetrics, getPortfolioDividendSummary, filterUpcomingDividends } from './src/lib/dividends.ts';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DATA_DIR = path.join(__dirname, 'data');
const PORTFOLIO_FILE = path.join(DATA_DIR, 'portfolio.json');

const isoDateSchema = z.string().regex(/^\d{4}-\d{2}-\d{2}$/);
const assetTypeSchema = z.enum(['stock', 'crypto']);

const soldLotSchema = z.object({
  holdingId: z.string().min(1),
  quantity: z.number().positive(),
  costBasis: z.number(),
  realizedPL: z.number(),
});

const sellRecordSchema = z.object({
  id: z.string().min(1),
  symbol: z.string().min(1),
  quantity: z.number().positive(),
  sellPrice: z.number().positive(),
  sellDate: isoDateSchema,
  lotsSold: z.array(soldLotSchema),
  totalRealizedPL: z.number(),
});

const holdingSchema = z.object({
  id: z.string().min(1),
  symbol: z.string().min(1),
  name: z.string().min(1),
  type: assetTypeSchema,
  quantity: z.number().positive(),
  purchasePrice: z.number().positive(),
  purchaseDate: isoDateSchema,
});

const portfolioSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  holdings: z.array(holdingSchema),
  sellHistory: z.array(sellRecordSchema).default([]),
  createdAt: z.string().min(1),
  lastUpdated: z.string().min(1),
});

const stateSchema = z.object({
  portfolios: z.array(portfolioSchema).min(1),
  activePortfolioId: z.string().nullable().default(null),
});

type AssetType = z.infer<typeof assetTypeSchema>;
type Holding = z.infer<typeof holdingSchema>;
type SoldLot = z.infer<typeof soldLotSchema>;
type SellRecord = z.infer<typeof sellRecordSchema>;
type Portfolio = z.infer<typeof portfolioSchema>;
type PortfolioState = z.infer<typeof stateSchema>;

type PriceResult = {
  price: number;
  change: number;
};

type DividendData = {
  trailingYield: number;
  forwardYield: number;
  annualDividendRate: number;
  exDividendDate: string | null;
  currency: string;
  lastUpdated: string;
};

type HoldingWithDividends = Holding & {
  dividendData?: DividendData;
  yoc?: number;
  projectedIncome?: number;
};

type DividendSummary = {
  totalProjectedIncome: number;
  weightedAvgYield: number;
  totalYOC: number;
  upcomingExDates: Array<{
    symbol: string;
    name: string;
    date: string;
    daysUntil: number;
  }>;
};

const symbolArgSchema = z.string().trim().min(1).transform((value) => value.toUpperCase());
const positiveNumberArgSchema = z.coerce.number().refine(
  (value) => Number.isFinite(value) && value > 0,
  'Value must be a positive number',
);
const nonEmptyArgSchema = z.string().trim().min(1);
const assetTypeArgSchema = z.preprocess(
  (value) => (typeof value === 'string' ? value.trim().toLowerCase() : value),
  assetTypeSchema,
);

function ensureDataDir(): void {
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }
}

function todayIsoDate(): string {
  return new Date().toISOString().split('T')[0];
}

function createDefaultPortfolio(name = 'Main Portfolio'): Portfolio {
  return {
    id: crypto.randomUUID(),
    name,
    holdings: [],
    sellHistory: [],
    createdAt: new Date().toISOString(),
    lastUpdated: new Date().toISOString(),
  };
}

function createDefaultState(): PortfolioState {
  const defaultPortfolio = createDefaultPortfolio();
  return {
    portfolios: [defaultPortfolio],
    activePortfolioId: defaultPortfolio.id,
  };
}

function saveState(state: PortfolioState): void {
  ensureDataDir();
  const validatedState = stateSchema.parse(state);
  fs.writeFileSync(PORTFOLIO_FILE, JSON.stringify(validatedState, null, 2));
}

function loadState(): PortfolioState {
  ensureDataDir();

  if (!fs.existsSync(PORTFOLIO_FILE)) {
    const initialState = createDefaultState();
    saveState(initialState);
    return initialState;
  }

  try {
    const content = fs.readFileSync(PORTFOLIO_FILE, 'utf-8');
    const parsedJson = JSON.parse(content) as unknown;
    const parsedState = stateSchema.parse(parsedJson);

    if (!parsedState.activePortfolioId || !parsedState.portfolios.some((p) => p.id === parsedState.activePortfolioId)) {
      parsedState.activePortfolioId = parsedState.portfolios[0].id;
      saveState(parsedState);
    }

    return parsedState;
  } catch (error) {
    const backupPath = `${PORTFOLIO_FILE}.invalid.${Date.now()}.bak`;
    try {
      fs.copyFileSync(PORTFOLIO_FILE, backupPath);
    } catch {
      // Best effort backup only.
    }

    const fallbackState = createDefaultState();
    saveState(fallbackState);

    const message = error instanceof Error ? error.message : 'Unknown validation error';
    console.error(`Portfolio data was invalid and has been reset. Backup: ${backupPath}`);
    console.error(`Validation error: ${message}`);
    return fallbackState;
  }
}

function getActivePortfolio(state: PortfolioState): Portfolio {
  return state.portfolios.find((portfolio) => portfolio.id === state.activePortfolioId) ?? state.portfolios[0];
}

function parseOrExit<T>(schema: z.ZodType<T>, value: unknown, usage: string[]): T {
  const parsed = schema.safeParse(value);
  if (parsed.success) {
    return parsed.data;
  }

  const message = parsed.error.issues[0]?.message ?? 'Invalid arguments';
  console.error(`Error: ${message}`);
  for (const line of usage) {
    console.error(line);
  }
  process.exit(1);
}

async function fetchPrice(symbol: string, type: AssetType): Promise<PriceResult | null> {
  try {
    if (type === 'crypto') {
      const coinId = symbol.toLowerCase().replace('-usdt', '').replace('-usd', '');
      const response = await fetch(
        `https://api.coingecko.com/api/v3/simple/price?ids=${encodeURIComponent(coinId)}&vs_currencies=usd&include_24hr_change=true`,
      );

      if (!response.ok) {
        return null;
      }

      const data = (await response.json()) as Record<string, { usd?: number; usd_24h_change?: number }>;
      const coinData = data[coinId];
      if (coinData && typeof coinData.usd === 'number') {
        return {
          price: coinData.usd,
          change: coinData.usd_24h_change ?? 0,
        };
      }
      return null;
    }

    const response = await fetch(
      `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(symbol)}?interval=1d&range=1d`,
    );
    if (!response.ok) {
      return null;
    }

    const data = (await response.json()) as {
      chart?: {
        result?: Array<{
          meta?: {
            regularMarketPrice?: number;
            chartPreviousClose?: number;
            previousClose?: number;
          };
        }>;
      };
    };

    const result = data.chart?.result?.[0];
    const price = result?.meta?.regularMarketPrice;
    if (typeof price !== 'number') {
      return null;
    }

    const previous = result?.meta?.chartPreviousClose ?? result?.meta?.previousClose;
    const change = typeof previous === 'number' && previous !== 0 ? ((price - previous) / previous) * 100 : 0;

    return { price, change };
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    console.error(`Error fetching ${symbol}: ${message}`);
    return null;
  }
}

function printHelp(): void {
  console.log(`
Portfolio Tracker CLI

Usage: portfolio <command> [options]

Commands:
  list, ls [--no-dividends]   List all holdings with values and dividend info
  add <sym> <qty> <price> <name> [date] [type]
                              Add a holding
  sell <sym> <qty> <price> [date]
                              Sell shares (FIFO)
  history, hist [symbol]      Show transaction history
  pnl                         Show realized + unrealized P/L
  dividends, div              Show detailed dividend information
  dividend-summary, divsum    Show portfolio dividend summary
  calendar, cal [days]        Show upcoming ex-dividend dates (default 30 days)
  remove, rm <symbol>         Remove a holding
  value, val                  Show portfolio total value
  portfolios, pf              List all portfolios
  switch <name>               Switch to another portfolio
  create <name>               Create a new portfolio
  help                        Show this help

Examples:
  portfolio add AAPL 10 150 "Apple Inc." 2025-01-15 stock
  portfolio add BTC 0.5 45000 "Bitcoin" crypto
  portfolio sell AAPL 5 180 2025-06-01
  portfolio history AAPL
  portfolio pnl
  portfolio dividends
  portfolio dividend-summary
  portfolio calendar 60
  portfolio remove AAPL
  portfolio switch "Crypto"
  portfolio create "My Portfolio"
`);
}

function formatSignedCurrency(value: number): string {
  return `${value >= 0 ? '+' : '-'}$${Math.abs(value).toFixed(2)}`;
}

function parseAddArgs(args: string[]): {
  symbol: string;
  quantity: number;
  price: number;
  name: string;
  purchaseDate: string;
  type: AssetType;
} {
  const usage = [
    'Usage: portfolio add <symbol> <quantity> <price> <name> [date] [type]',
    'Example: portfolio add AAPL 10 150 "Apple Inc." 2025-01-15 stock',
    '         portfolio add BTC 0.5 45000 "Bitcoin" crypto',
  ];

  const values = parseOrExit(z.array(z.string()).min(4).max(6), args, usage);
  const [symbolArg, quantityArg, priceArg, nameArg, arg4, arg5] = values;

  const symbol = parseOrExit(symbolArgSchema, symbolArg, usage);
  const quantity = parseOrExit(positiveNumberArgSchema, quantityArg, usage);
  const price = parseOrExit(positiveNumberArgSchema, priceArg, usage);
  const name = parseOrExit(nonEmptyArgSchema, nameArg, usage);

  let purchaseDate = todayIsoDate();
  let type: AssetType = 'stock';

  if (arg4) {
    const maybeDate = isoDateSchema.safeParse(arg4);
    if (maybeDate.success) {
      purchaseDate = maybeDate.data;
      if (arg5) {
        type = parseOrExit(assetTypeArgSchema, arg5, usage);
      }
    } else {
      type = parseOrExit(assetTypeArgSchema, arg4, usage);
    }
  }

  return { symbol, quantity, price, name, purchaseDate, type };
}

function parseSellArgs(args: string[]): {
  symbol: string;
  quantity: number;
  price: number;
  sellDate: string;
} {
  const usage = [
    'Usage: portfolio sell <symbol> <quantity> <price> [date]',
    'Example: portfolio sell AAPL 5 180 2025-06-01',
  ];

  const values = parseOrExit(z.array(z.string()).min(3).max(4), args, usage);
  const [symbolArg, quantityArg, priceArg, dateArg] = values;

  const symbol = parseOrExit(symbolArgSchema, symbolArg, usage);
  const quantity = parseOrExit(positiveNumberArgSchema, quantityArg, usage);
  const price = parseOrExit(positiveNumberArgSchema, priceArg, usage);
  const sellDate = dateArg ? parseOrExit(isoDateSchema, dateArg, usage) : todayIsoDate();

  return { symbol, quantity, price, sellDate };
}

async function run(): Promise<void> {
  const command = process.argv[2] ?? 'help';
  const args = process.argv.slice(3);

  const state = loadState();
  const portfolio = getActivePortfolio(state);

  switch (command) {
    case 'list':
    case 'ls': {
      const skipDividends = args.includes('--no-dividends');
      console.log(`\n${portfolio.name}\n`);
      if (portfolio.holdings.length === 0) {
        console.log('  No holdings yet.\n');
        return;
      }

      if (skipDividends) {
        console.log('  Symbol    Type      Qty     Cost      Value     P&L');
        console.log(`  ${'-'.repeat(60)}`);
      } else {
        console.log('  Symbol    Type      Qty     Cost      Value     P&L        Yield%   YOC%   Income/Yr');
        console.log(`  ${'-'.repeat(85)}`);
      }

      let totalCost = 0;
      let totalValue = 0;
      const holdingsWithDividends: HoldingWithDividends[] = [];
      const currentPrices = new Map<string, number>();

      for (const holding of portfolio.holdings) {
        const priceData = await fetchPrice(holding.symbol, holding.type);
        const livePrice = priceData?.price ?? holding.purchasePrice;
        const value = livePrice * holding.quantity;
        const cost = holding.purchasePrice * holding.quantity;
        const pnl = value - cost;

        totalCost += cost;
        totalValue += value;
        currentPrices.set(holding.symbol, livePrice);

        let holdingWithDividends: HoldingWithDividends = { ...holding };

        if (!skipDividends && holding.type === 'stock') {
          const dividendData = await fetchDividendData(holding.symbol);
          if (dividendData) {
            holdingWithDividends = calculateDividendMetrics(holding, dividendData, livePrice);
          }
        }

        holdingsWithDividends.push(holdingWithDividends);

        const pnlString = pnl >= 0 ? `+$${pnl.toFixed(2)}` : `-$${Math.abs(pnl).toFixed(2)}`;

        if (skipDividends) {
          console.log(
            `  ${holding.symbol.padEnd(8)} ${holding.type.padEnd(8)} ${holding.quantity
              .toString()
              .padEnd(7)} $${cost.toFixed(2).padStart(8)} $${value.toFixed(2).padStart(9)} ${pnlString.padStart(10)}`,
          );
        } else {
          const yieldStr = holdingWithDividends.dividendData
            ? `${holdingWithDividends.dividendData.trailingYield.toFixed(2)}%`
            : 'N/A';
          const yocStr = holdingWithDividends.yoc !== undefined
            ? `${holdingWithDividends.yoc.toFixed(2)}%`
            : 'N/A';
          const incomeStr = holdingWithDividends.projectedIncome !== undefined
            ? `$${holdingWithDividends.projectedIncome.toFixed(2)}`
            : 'N/A';

          console.log(
            `  ${holding.symbol.padEnd(8)} ${holding.type.padEnd(8)} ${holding.quantity
              .toString()
              .padEnd(7)} $${cost.toFixed(2).padStart(8)} $${value.toFixed(2).padStart(9)} ${pnlString.padStart(10)} ${yieldStr.padStart(8)} ${yocStr.padStart(6)} ${incomeStr.padStart(11)}`,
          );
        }
      }

      if (skipDividends) {
        console.log(`  ${'-'.repeat(60)}`);
      } else {
        console.log(`  ${'-'.repeat(85)}`);
      }

      const totalPnl = totalValue - totalCost;
      console.log(`\n  Total Cost:  $${totalCost.toFixed(2)}`);
      console.log(`  Total Value: $${totalValue.toFixed(2)}`);
      console.log(`  Total P&L:   ${totalPnl >= 0 ? '+' : ''}$${totalPnl.toFixed(2)}`);

      if (!skipDividends) {
        const dividendSummary = getPortfolioDividendSummary(holdingsWithDividends, currentPrices);
        console.log(`\n  Dividend Summary:`);
        console.log(`    Total Projected Income: $${dividendSummary.totalProjectedIncome.toFixed(2)}/year`);
        console.log(`    Weighted Avg Yield:     ${dividendSummary.weightedAvgYield.toFixed(2)}%`);
        console.log(`    Portfolio YOC:          ${dividendSummary.totalYOC.toFixed(2)}%`);
      }

      console.log('');
      return;
    }

    case 'add': {
      const parsed = parseAddArgs(args);
      const newHolding: Holding = {
        id: crypto.randomUUID(),
        symbol: parsed.symbol,
        name: parsed.name,
        type: parsed.type,
        quantity: parsed.quantity,
        purchasePrice: parsed.price,
        purchaseDate: parsed.purchaseDate,
      };

      portfolio.holdings.push(newHolding);
      portfolio.lastUpdated = new Date().toISOString();
      saveState(state);

      console.log(`Added ${parsed.quantity} ${parsed.symbol} to ${portfolio.name} (${parsed.purchaseDate})`);
      return;
    }

    case 'remove':
    case 'rm': {
      const usage = ['Usage: portfolio remove <symbol>'];
      const [symbolArg] = parseOrExit(z.array(z.string()).length(1), args, usage);
      const symbol = parseOrExit(symbolArgSchema, symbolArg, usage);

      const index = portfolio.holdings.findIndex((holding) => holding.symbol === symbol);
      if (index === -1) {
        console.error(`${symbol} not found in portfolio`);
        process.exit(1);
      }

      portfolio.holdings.splice(index, 1);
      portfolio.lastUpdated = new Date().toISOString();
      saveState(state);

      console.log(`Removed ${symbol} from ${portfolio.name}`);
      return;
    }

    case 'portfolios':
    case 'pf': {
      parseOrExit(z.array(z.string()).max(0), args, ['Usage: portfolio portfolios']);
      console.log('\nPortfolios:\n');
      for (const item of state.portfolios) {
        const activeSuffix = item.id === state.activePortfolioId ? ' (active)' : '';
        console.log(`  - ${item.name}${activeSuffix} (${item.holdings.length} holdings)`);
      }
      console.log('');
      return;
    }

    case 'switch': {
      const usage = ['Usage: portfolio switch <portfolio-name>'];
      const values = parseOrExit(z.array(z.string()).min(1), args, usage);
      const name = parseOrExit(nonEmptyArgSchema, values.join(' '), usage);

      const nextPortfolio = state.portfolios.find(
        (candidate) => candidate.name.toLowerCase() === name.toLowerCase(),
      );

      if (!nextPortfolio) {
        console.error(`Portfolio "${name}" not found`);
        process.exit(1);
      }

      state.activePortfolioId = nextPortfolio.id;
      saveState(state);

      console.log(`Switched to "${nextPortfolio.name}"`);
      return;
    }

    case 'create': {
      const usage = ['Usage: portfolio create <name>'];
      const values = parseOrExit(z.array(z.string()).min(1), args, usage);
      const name = parseOrExit(nonEmptyArgSchema, values.join(' '), usage);

      const newPortfolio = createDefaultPortfolio(name);
      state.portfolios.push(newPortfolio);
      state.activePortfolioId = newPortfolio.id;
      saveState(state);

      console.log(`Created and switched to "${name}"`);
      return;
    }

    case 'value':
    case 'val': {
      parseOrExit(z.array(z.string()).max(0), args, ['Usage: portfolio value']);
      let totalValue = 0;
      let totalCost = 0;

      for (const holding of portfolio.holdings) {
        const priceData = await fetchPrice(holding.symbol, holding.type);
        const livePrice = priceData?.price ?? holding.purchasePrice;
        totalValue += livePrice * holding.quantity;
        totalCost += holding.purchasePrice * holding.quantity;
      }

      const pnl = totalValue - totalCost;
      const pnlPercent = totalCost === 0 ? 0 : (pnl / totalCost) * 100;

      console.log(`\n${portfolio.name}`);
      console.log(`   Value: $${totalValue.toFixed(2)}`);
      console.log(`   Cost:  $${totalCost.toFixed(2)}`);
      console.log(`   P&L:   ${pnl >= 0 ? '+' : ''}$${pnl.toFixed(2)} (${pnlPercent.toFixed(2)}%)\n`);
      return;
    }

    case 'sell': {
      const parsed = parseSellArgs(args);
      const holdingsToSell = portfolio.holdings
        .filter((holding) => holding.symbol === parsed.symbol)
        .sort((a, b) => new Date(a.purchaseDate).getTime() - new Date(b.purchaseDate).getTime());

      const totalAvailable = holdingsToSell.reduce((sum, holding) => sum + holding.quantity, 0);
      if (parsed.quantity > totalAvailable) {
        console.error(`Not enough ${parsed.symbol} to sell. Available: ${totalAvailable}`);
        process.exit(1);
      }

      const lotsSold: SoldLot[] = [];
      let remainingToSell = parsed.quantity;
      let totalRealizedPL = 0;

      for (const holding of holdingsToSell) {
        if (remainingToSell <= 0) {
          break;
        }

        const quantityFromLot = Math.min(holding.quantity, remainingToSell);
        const costBasis = quantityFromLot * holding.purchasePrice;
        const proceeds = quantityFromLot * parsed.price;
        const realizedPL = proceeds - costBasis;

        totalRealizedPL += realizedPL;
        lotsSold.push({
          holdingId: holding.id,
          quantity: quantityFromLot,
          costBasis,
          realizedPL,
        });

        holding.quantity -= quantityFromLot;
        remainingToSell -= quantityFromLot;

        if (holding.quantity <= 0) {
          const index = portfolio.holdings.findIndex((candidate) => candidate.id === holding.id);
          if (index !== -1) {
            portfolio.holdings.splice(index, 1);
          }
        }
      }

      const sellRecord: SellRecord = {
        id: crypto.randomUUID(),
        symbol: parsed.symbol,
        quantity: parsed.quantity,
        sellPrice: parsed.price,
        sellDate: parsed.sellDate,
        lotsSold,
        totalRealizedPL,
      };

      portfolio.sellHistory.push(sellRecord);
      portfolio.lastUpdated = new Date().toISOString();
      saveState(state);

      console.log(`Sold ${parsed.quantity} ${parsed.symbol} @ $${parsed.price} (${parsed.sellDate})`);
      console.log(`   Realized P/L: ${formatSignedCurrency(totalRealizedPL)}`);
      return;
    }

    case 'history':
    case 'hist': {
      const usage = ['Usage: portfolio history [symbol]'];
      const values = parseOrExit(z.array(z.string()).max(1), args, usage);
      const filterSymbol = values[0] ? parseOrExit(symbolArgSchema, values[0], usage) : null;

      const records = filterSymbol
        ? portfolio.sellHistory.filter((record) => record.symbol === filterSymbol)
        : portfolio.sellHistory;

      console.log(`\nTransaction History${filterSymbol ? ` (${filterSymbol})` : ''}\n`);
      if (records.length === 0) {
        console.log('  No transactions yet.\n');
        return;
      }

      console.log('  Date       Symbol    Qty     Price    P/L');
      console.log(`  ${'-'.repeat(50)}`);

      let totalRealized = 0;
      for (const record of records) {
        totalRealized += record.totalRealizedPL;
        const pnlString = record.totalRealizedPL >= 0
          ? `+$${record.totalRealizedPL.toFixed(2)}`
          : `-$${Math.abs(record.totalRealizedPL).toFixed(2)}`;

        console.log(
          `  ${record.sellDate}  ${record.symbol.padEnd(8)} ${record.quantity
            .toString()
            .padEnd(7)} $${record.sellPrice.toFixed(2).padStart(7)} ${pnlString.padStart(10)}`,
        );
      }

      console.log(`  ${'-'.repeat(50)}`);
      console.log(`\n  Total Realized P/L: ${formatSignedCurrency(totalRealized)}\n`);
      return;
    }

    case 'pnl': {
      parseOrExit(z.array(z.string()).max(0), args, ['Usage: portfolio pnl']);
      let unrealizedValue = 0;
      let unrealizedCost = 0;

      for (const holding of portfolio.holdings) {
        const priceData = await fetchPrice(holding.symbol, holding.type);
        const livePrice = priceData?.price ?? holding.purchasePrice;
        unrealizedValue += livePrice * holding.quantity;
        unrealizedCost += holding.purchasePrice * holding.quantity;
      }

      const unrealizedPL = unrealizedValue - unrealizedCost;
      const realizedPL = portfolio.sellHistory.reduce((sum, record) => sum + record.totalRealizedPL, 0);
      const totalPL = unrealizedPL + realizedPL;

      console.log(`\nP/L Summary - ${portfolio.name}\n`);
      console.log(`  Unrealized P/L: ${formatSignedCurrency(unrealizedPL)}`);
      console.log(`  Realized P/L:   ${formatSignedCurrency(realizedPL)}`);
      console.log(`  ${'-'.repeat(30)}`);
      console.log(`  Total P/L:      ${formatSignedCurrency(totalPL)}\n`);
      return;
    }

    case 'dividends':
    case 'div': {
      parseOrExit(z.array(z.string()).max(0), args, ['Usage: portfolio dividends']);
      console.log(`\nDividend Details - ${portfolio.name}\n`);

      if (portfolio.holdings.length === 0) {
        console.log('  No holdings yet.\n');
        return;
      }

      const stockHoldings = portfolio.holdings.filter(h => h.type === 'stock');
      if (stockHoldings.length === 0) {
        console.log('  No stock holdings.\n');
        return;
      }

      console.log('  Symbol    Name                    Yield%   Fwd%   YOC%    Income/Yr   Ex-Date');
      console.log(`  ${'-'.repeat(80)}`);

      const holdingsWithDividends: HoldingWithDividends[] = [];
      const currentPrices = new Map<string, number>();

      for (const holding of stockHoldings) {
        const priceData = await fetchPrice(holding.symbol, holding.type);
        const livePrice = priceData?.price ?? holding.purchasePrice;
        currentPrices.set(holding.symbol, livePrice);

        const dividendData = await fetchDividendData(holding.symbol);
        const holdingWithDividends = dividendData
          ? calculateDividendMetrics(holding, dividendData, livePrice)
          : { ...holding };

        holdingsWithDividends.push(holdingWithDividends);

        const name = holding.name.length > 20 ? holding.name.substring(0, 17) + '...' : holding.name;
        const yieldStr = holdingWithDividends.dividendData
          ? `${holdingWithDividends.dividendData.trailingYield.toFixed(2)}%`
          : 'N/A';
        const fwdStr = holdingWithDividends.dividendData
          ? `${holdingWithDividends.dividendData.forwardYield.toFixed(2)}%`
          : 'N/A';
        const yocStr = holdingWithDividends.yoc !== undefined
          ? `${holdingWithDividends.yoc.toFixed(2)}%`
          : 'N/A';
        const incomeStr = holdingWithDividends.projectedIncome !== undefined
          ? `$${holdingWithDividends.projectedIncome.toFixed(2)}`
          : 'N/A';
        const exDateStr = holdingWithDividends.dividendData?.exDividendDate
          ? holdingWithDividends.dividendData.exDividendDate
          : 'N/A';

        console.log(
          `  ${holding.symbol.padEnd(8)} ${name.padEnd(22)} ${yieldStr.padStart(6)} ${fwdStr.padStart(6)} ${yocStr.padStart(6)} ${incomeStr.padStart(11)}  ${exDateStr}`,
        );
      }

      console.log(`  ${'-'.repeat(80)}`);

      const dividendSummary = getPortfolioDividendSummary(holdingsWithDividends, currentPrices);
      console.log(`\n  Portfolio Totals:`);
      console.log(`    Total Projected Income: $${dividendSummary.totalProjectedIncome.toFixed(2)}/year`);
      console.log(`    Monthly Estimate:       $${(dividendSummary.totalProjectedIncome / 12).toFixed(2)}`);
      console.log(`    Weighted Avg Yield:     ${dividendSummary.weightedAvgYield.toFixed(2)}%`);
      console.log(`    Portfolio YOC:          ${dividendSummary.totalYOC.toFixed(2)}%\n`);
      return;
    }

    case 'dividend-summary':
    case 'divsum': {
      parseOrExit(z.array(z.string()).max(0), args, ['Usage: portfolio dividend-summary']);
      console.log(`\nDividend Summary - ${portfolio.name}\n`);

      if (portfolio.holdings.length === 0) {
        console.log('  No holdings yet.\n');
        return;
      }

      const stockHoldings = portfolio.holdings.filter(h => h.type === 'stock');
      if (stockHoldings.length === 0) {
        console.log('  No stock holdings.\n');
        return;
      }

      const holdingsWithDividends: HoldingWithDividends[] = [];
      const currentPrices = new Map<string, number>();

      for (const holding of stockHoldings) {
        const priceData = await fetchPrice(holding.symbol, holding.type);
        const livePrice = priceData?.price ?? holding.purchasePrice;
        currentPrices.set(holding.symbol, livePrice);

        const dividendData = await fetchDividendData(holding.symbol);
        const holdingWithDividends = dividendData
          ? calculateDividendMetrics(holding, dividendData, livePrice)
          : { ...holding };

        holdingsWithDividends.push(holdingWithDividends);
      }

      const dividendSummary = getPortfolioDividendSummary(holdingsWithDividends, currentPrices);

      console.log('  Portfolio Dividend Metrics\n');
      console.log(`    Total Projected Income:   $${dividendSummary.totalProjectedIncome.toFixed(2)}/year`);
      console.log(`    Monthly Estimate:         $${(dividendSummary.totalProjectedIncome / 12).toFixed(2)}`);
      console.log(`    Quarterly Estimate:       $${(dividendSummary.totalProjectedIncome / 4).toFixed(2)}`);
      console.log(`    Weighted Average Yield:   ${dividendSummary.weightedAvgYield.toFixed(2)}%`);
      console.log(`    Portfolio Yield on Cost:  ${dividendSummary.totalYOC.toFixed(2)}%`);
      console.log(`    Dividend-Paying Stocks:   ${holdingsWithDividends.filter(h => h.dividendData && h.dividendData.trailingYield > 0).length}/${stockHoldings.length}\n`);
      return;
    }

    case 'calendar':
    case 'cal': {
      const daysArg = args[0] ? parseInt(args[0]) : 30;
      const maxDays = isNaN(daysArg) || daysArg <= 0 ? 30 : daysArg;

      console.log(`\nDividend Calendar - Next ${maxDays} Days - ${portfolio.name}\n`);

      if (portfolio.holdings.length === 0) {
        console.log('  No holdings yet.\n');
        return;
      }

      const stockHoldings = portfolio.holdings.filter(h => h.type === 'stock');
      if (stockHoldings.length === 0) {
        console.log('  No stock holdings.\n');
        return;
      }

      const holdingsWithDividends: HoldingWithDividends[] = [];
      const currentPrices = new Map<string, number>();

      for (const holding of stockHoldings) {
        const priceData = await fetchPrice(holding.symbol, holding.type);
        const livePrice = priceData?.price ?? holding.purchasePrice;
        currentPrices.set(holding.symbol, livePrice);

        const dividendData = await fetchDividendData(holding.symbol);
        const holdingWithDividends = dividendData
          ? calculateDividendMetrics(holding, dividendData, livePrice)
          : { ...holding };

        holdingsWithDividends.push(holdingWithDividends);
      }

      const dividendSummary = getPortfolioDividendSummary(holdingsWithDividends, currentPrices);
      const upcoming = filterUpcomingDividends(dividendSummary, maxDays);

      if (upcoming.length === 0) {
        console.log('  No upcoming ex-dividend dates in the specified period.\n');
        return;
      }

      console.log('  Date       Symbol    Name                    Days Until');
      console.log(`  ${'-'.repeat(60)}`);

      for (const item of upcoming) {
        const name = item.name.length > 20 ? item.name.substring(0, 17) + '...' : item.name;
        const daysLabel = item.daysUntil === 0 ? 'TODAY' : item.daysUntil === 1 ? 'tomorrow' : `${item.daysUntil} days`;
        console.log(`  ${item.date}  ${item.symbol.padEnd(8)} ${name.padEnd(22)} ${daysLabel}`);
      }

      console.log(`  ${'-'.repeat(60)}\n`);
      return;
    }

    case 'help':
    default:
      printHelp();
      return;
  }
}

run().catch((error) => {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`Unexpected error: ${message}`);
  process.exit(1);
});
