import { DividendData, Holding, HoldingWithDividends, DividendSummary, UpcomingDividend } from './types';

export async function fetchDividendData(symbol: string): Promise<DividendData | null> {
  try {
    // Use the quoteSummary endpoint for comprehensive dividend data
    const summaryResponse = await fetch(
      `https://query2.finance.yahoo.com/v10/finance/quoteSummary/${encodeURIComponent(symbol)}?modules=summaryDetail`,
    );
    
    if (!summaryResponse.ok) {
      return null;
    }

    const summaryData = (await summaryResponse.json()) as {
      quoteSummary?: {
        result?: Array<{
          summaryDetail?: {
            trailingAnnualDividendYield?: number;
            forwardAnnualDividendYield?: number;
            dividendRate?: number;
            dividendYield?: number;
            exDividendDate?: number;
            currency?: string;
          };
        }>;
      };
    };

    const summaryDetail = summaryData.quoteSummary?.result?.[0]?.summaryDetail;
    if (!summaryDetail) {
      return null;
    }

    // Calculate yields - Yahoo returns yields as decimals (e.g., 0.0056 for 0.56%)
    const trailingYield = (summaryDetail.trailingAnnualDividendYield ?? summaryDetail.dividendYield ?? 0) * 100;
    const forwardYield = (summaryDetail.forwardAnnualDividendYield ?? 0) * 100;
    const annualDividendRate = summaryDetail.dividendRate ?? 0;

    // Parse ex-dividend date
    let exDividendDate: string | null = null;
    if (summaryDetail.exDividendDate && summaryDetail.exDividendDate > 0) {
      exDividendDate = new Date(summaryDetail.exDividendDate * 1000).toISOString().split('T')[0];
    }

    return {
      trailingYield,
      forwardYield,
      annualDividendRate,
      exDividendDate,
      currency: summaryDetail.currency ?? 'USD',
      lastUpdated: new Date().toISOString(),
    };
  } catch (error) {
    console.error(`Error fetching dividend data for ${symbol}:`, error);
    return null;
  }
}

export function calculateDividendMetrics(
  holding: Holding,
  dividendData: DividendData,
  currentPrice: number
): HoldingWithDividends {
  const yoc = holding.purchasePrice > 0
    ? (dividendData.annualDividendRate / holding.purchasePrice) * 100
    : 0;

  const projectedIncome = holding.quantity * dividendData.annualDividendRate;

  return {
    ...holding,
    dividendData,
    yoc,
    projectedIncome,
  };
}

export function getPortfolioDividendSummary(
  holdings: HoldingWithDividends[],
  currentPrices: Map<string, number>
): DividendSummary {
  let totalProjectedIncome = 0;
  let totalWeightedYield = 0;
  let totalPortfolioValue = 0;
  let totalYOC = 0;
  let totalCost = 0;

  const upcomingExDates: UpcomingDividend[] = [];
  const today = new Date();

  for (const holding of holdings) {
    if (holding.dividendData && holding.projectedIncome !== undefined) {
      totalProjectedIncome += holding.projectedIncome;

      const currentPrice = currentPrices.get(holding.symbol) ?? holding.purchasePrice;
      const positionValue = holding.quantity * currentPrice;
      totalPortfolioValue += positionValue;
      totalWeightedYield += positionValue * (holding.dividendData.trailingYield / 100);

      const costBasis = holding.quantity * holding.purchasePrice;
      totalCost += costBasis;
      totalYOC += costBasis * ((holding.yoc ?? 0) / 100);

      if (holding.dividendData.exDividendDate) {
        const exDate = new Date(holding.dividendData.exDividendDate);
        const daysUntil = Math.ceil((exDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
        if (daysUntil >= 0) {
          upcomingExDates.push({
            symbol: holding.symbol,
            name: holding.name,
            date: holding.dividendData.exDividendDate,
            daysUntil,
          });
        }
      }
    }
  }

  upcomingExDates.sort((a, b) => a.daysUntil - b.daysUntil);

  return {
    totalProjectedIncome,
    weightedAvgYield: totalPortfolioValue > 0 ? (totalWeightedYield / totalPortfolioValue) * 100 : 0,
    totalYOC: totalCost > 0 ? (totalYOC / totalCost) * 100 : 0,
    upcomingExDates: upcomingExDates.slice(0, 10),
  };
}

export function filterUpcomingDividends(
  summary: DividendSummary,
  maxDays: number = 30
): UpcomingDividend[] {
  return summary.upcomingExDates.filter(d => d.daysUntil <= maxDays);
}
