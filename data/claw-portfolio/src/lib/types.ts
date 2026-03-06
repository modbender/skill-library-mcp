export type AssetType = 'stock' | 'crypto';

export interface DividendData {
  trailingYield: number;
  forwardYield: number;
  annualDividendRate: number;
  exDividendDate: string | null;
  currency: string;
  lastUpdated: string;
}

export interface Holding {
  id: string;
  symbol: string;
  name: string;
  type: AssetType;
  quantity: number;
  purchasePrice: number;
  purchaseDate: string;
}

export interface HoldingWithDividends extends Holding {
  dividendData?: DividendData;
  yoc?: number;
  projectedIncome?: number;
}

export interface SoldLot {
  holdingId: string;
  quantity: number;
  costBasis: number;
  realizedPL: number;
}

export interface SellRecord {
  id: string;
  symbol: string;
  quantity: number;
  sellPrice: number;
  sellDate: string;
  lotsSold: SoldLot[];
  totalRealizedPL: number;
}

export interface PriceData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  lastUpdated: string;
}

export interface PortfolioSummary {
  totalValue: number;
  totalCost: number;
  totalGain: number;
  totalGainPercent: number;
}

export interface DividendSummary {
  totalProjectedIncome: number;
  weightedAvgYield: number;
  totalYOC: number;
  upcomingExDates: Array<{
    symbol: string;
    name: string;
    date: string;
    daysUntil: number;
  }>;
}

export interface UpcomingDividend {
  symbol: string;
  name: string;
  date: string;
  daysUntil: number;
}

export interface Portfolio {
  id: string;
  name: string;
  holdings: Holding[];
  sellHistory: SellRecord[];
  createdAt: string;
  lastUpdated: string;
}

export interface PortfolioState {
  portfolios: Portfolio[];
  activePortfolioId: string | null;
}
