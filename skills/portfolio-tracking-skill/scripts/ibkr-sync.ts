import { XMLParser } from 'fast-xml-parser';

const FLEX_BASE_URL = 'https://gdcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService';

// ─── Types ──────────────────────────────────────────────────────────

export interface IbkrPosition {
  symbol: string;
  name: string;
  quantity: number;
  avgPrice: number;
  currentPrice: number;
  type: 'USSTOCK' | 'HKSTOCK';
  currency: 'USD' | 'HKD';
}

export interface IbkrCashBalance {
  currency: string;
  amount: number;
}

export interface IbkrTrade {
  symbol: string;
  name: string;
  dateTime: string; // ISO string for JSON serialization
  quantity: number;
  tradePrice: number;
  currency: string;
  buySell: 'BUY' | 'SELL';
  type: 'USSTOCK' | 'HKSTOCK';
}

export interface FlexResponse {
  status: string;
  referenceCode?: string;
  errorCode?: string;
  errorMessage?: string;
}

export interface ImportableAsset {
  symbol: string;
  name: string;
  quantity: number;
  type: 'USSTOCK' | 'HKSTOCK' | 'CASH';
  currency: 'USD' | 'HKD';
  avgPrice?: number;
  currentPrice?: number;
}

// ─── Symbol & Type Mapping ──────────────────────────────────────────

export function mapIbkrSymbol(symbol: string, exchange: string): string {
  if (exchange === 'SEHK') {
    return `${symbol.padStart(4, '0')}.HK`;
  }
  return symbol;
}

export function mapIbkrAssetType(exchange: string): 'USSTOCK' | 'HKSTOCK' {
  return exchange === 'SEHK' ? 'HKSTOCK' : 'USSTOCK';
}

function mapCurrency(exchange: string): 'USD' | 'HKD' {
  return exchange === 'SEHK' ? 'HKD' : 'USD';
}

// ─── XML Parsing ────────────────────────────────────────────────────

const parser = new XMLParser({
  ignoreAttributes: false,
  attributeNamePrefix: '',
  parseAttributeValue: false,
});

function ensureArray<T>(val: T | T[] | undefined | null): T[] {
  if (!val) return [];
  return Array.isArray(val) ? val : [val];
}

function getFlexStatement(parsed: any): any {
  return parsed?.FlexQueryResponse?.FlexStatements?.FlexStatement;
}

export function parseOpenPositions(xml: string): IbkrPosition[] {
  const parsed = parser.parse(xml);
  const statement = getFlexStatement(parsed);
  if (!statement) return [];

  const rawPositions = ensureArray(statement.OpenPositions?.OpenPosition);
  if (rawPositions.length === 0) return [];

  const aggregated = new Map<string, {
    symbol: string;
    name: string;
    totalQuantity: number;
    totalCost: number;
    markPrice: number;
    type: 'USSTOCK' | 'HKSTOCK';
    currency: 'USD' | 'HKD';
  }>();

  for (const pos of rawPositions) {
    const quantity = parseFloat(pos.position ?? pos.quantity);
    if (quantity === 0 || isNaN(quantity)) continue;

    const exchange = pos.listingExchange;
    const symbol = mapIbkrSymbol(pos.symbol, exchange);
    const costBasis = parseFloat(pos.costBasisPrice);
    const markPrice = parseFloat(pos.markPrice);

    const existing = aggregated.get(symbol);
    if (existing) {
      existing.totalCost += quantity * costBasis;
      existing.totalQuantity += quantity;
      existing.markPrice = markPrice;
    } else {
      aggregated.set(symbol, {
        symbol,
        name: pos.description,
        totalQuantity: quantity,
        totalCost: quantity * costBasis,
        markPrice,
        type: mapIbkrAssetType(exchange),
        currency: mapCurrency(exchange),
      });
    }
  }

  return Array.from(aggregated.values()).map(p => ({
    symbol: p.symbol,
    name: p.name,
    quantity: p.totalQuantity,
    avgPrice: p.totalQuantity > 0 ? p.totalCost / p.totalQuantity : 0,
    currentPrice: p.markPrice,
    type: p.type,
    currency: p.currency,
  }));
}

export function parseCashReport(xml: string): IbkrCashBalance[] {
  const parsed = parser.parse(xml);
  const statement = getFlexStatement(parsed);
  if (!statement) return [];

  const rawCash = ensureArray(statement.CashReport?.CashReportCurrency);
  if (rawCash.length === 0) return [];

  const EXCLUDED = new Set(['BASE_SUMMARY', 'TOTAL']);
  return rawCash
    .filter((c: any) => !EXCLUDED.has(c.currency) && parseFloat(c.endingCash) > 0)
    .map((c: any) => ({ currency: c.currency, amount: parseFloat(c.endingCash) }));
}

export function parseTrades(xml: string): IbkrTrade[] {
  const parsed = parser.parse(xml);
  const statement = getFlexStatement(parsed);
  if (!statement) return [];

  const rawTrades = ensureArray(statement.Trades?.Trade);
  if (rawTrades.length === 0) return [];

  return rawTrades.map((t: any) => {
    const exchange = t.listingExchange;
    const [datePart, timePart] = (t.dateTime as string).split(';');
    const dateStr = timePart
      ? `${datePart}T${timePart.slice(0, 2)}:${timePart.slice(2, 4)}:${timePart.slice(4, 6)}`
      : datePart;

    return {
      symbol: mapIbkrSymbol(t.symbol, exchange),
      name: t.description,
      dateTime: new Date(dateStr).toISOString(),
      quantity: Math.abs(parseFloat(t.quantity)),
      tradePrice: parseFloat(t.tradePrice),
      currency: t.currency,
      buySell: t.buySell as 'BUY' | 'SELL',
      type: mapIbkrAssetType(exchange),
    };
  });
}

export function parseFlexResponse(xml: string): FlexResponse {
  const parsed = parser.parse(xml);
  const resp = parsed.FlexStatementResponse;
  return {
    status: resp.Status,
    referenceCode: resp.ReferenceCode?.toString(),
    errorCode: resp.ErrorCode?.toString(),
    errorMessage: resp.ErrorMessage,
  };
}

// ─── API Calls ──────────────────────────────────────────────────────

async function requestFlexStatement(token: string, queryId: string): Promise<string> {
  const url = `${FLEX_BASE_URL}.SendRequest?t=${token}&q=${queryId}&v=3`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`IBKR SendRequest failed: HTTP ${res.status}`);

  const xml = await res.text();
  const parsed = parseFlexResponse(xml);

  if (parsed.status === 'Success' && parsed.referenceCode) return parsed.referenceCode;
  throw new Error(`IBKR SendRequest error: [${parsed.errorCode}] ${parsed.errorMessage}`);
}

async function fetchFlexStatement(token: string, referenceCode: string): Promise<string> {
  const MAX_RETRIES = 10;
  const RETRY_DELAY_MS = 3000;

  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    const url = `${FLEX_BASE_URL}.GetStatement?t=${token}&q=${referenceCode}&v=3`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`IBKR GetStatement failed: HTTP ${res.status}`);

    const text = await res.text();

    if (text.includes('<FlexStatementResponse') || text.includes('<ErrorCode>')) {
      const parsed = parseFlexResponse(text);
      if (parsed.errorCode === '1019') {
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY_MS));
        continue;
      }
      throw new Error(`IBKR GetStatement error: [${parsed.errorCode}] ${parsed.errorMessage}`);
    }

    return text;
  }

  throw new Error('IBKR statement generation timed out after maximum retries');
}

// ─── Public API ─────────────────────────────────────────────────────

export async function fetchIbkrPositions(token: string, queryId: string): Promise<{
  assets: ImportableAsset[];
  trades: IbkrTrade[];
}> {
  const referenceCode = await requestFlexStatement(token, queryId);
  const xml = await fetchFlexStatement(token, referenceCode);

  const positions = parseOpenPositions(xml);
  const cashBalances = parseCashReport(xml);
  const trades = parseTrades(xml);

  const assets: ImportableAsset[] = positions.map(p => ({
    symbol: p.symbol,
    name: p.name,
    quantity: p.quantity,
    type: p.type,
    currency: p.currency,
    avgPrice: p.avgPrice,
    currentPrice: p.currentPrice,
  }));

  for (const cash of cashBalances) {
    if (cash.currency === 'USD' || cash.currency === 'HKD') {
      assets.push({
        symbol: cash.currency,
        name: `${cash.currency} Cash`,
        quantity: cash.amount,
        type: 'CASH',
        currency: cash.currency as 'USD' | 'HKD',
        avgPrice: 1,
        currentPrice: 1,
      });
    }
  }

  return { assets, trades };
}

export async function validateIbkrCredentials(token: string, queryId: string): Promise<{ valid: boolean; error?: string }> {
  try {
    const referenceCode = await requestFlexStatement(token, queryId);
    return { valid: !!referenceCode };
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
        const token = process.argv[3];
        const queryId = process.argv[4];
        if (!token || !queryId) throw new Error('Usage: sync <token> <queryId>');
        result = await fetchIbkrPositions(token, queryId);
        break;
      }
      case 'validate': {
        const token = process.argv[3];
        const queryId = process.argv[4];
        if (!token || !queryId) throw new Error('Usage: validate <token> <queryId>');
        result = await validateIbkrCredentials(token, queryId);
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
