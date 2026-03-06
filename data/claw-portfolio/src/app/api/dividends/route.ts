import { NextResponse } from 'next/server';
import { getActivePortfolio } from '@/lib/storage';
import { fetchDividendData, calculateDividendMetrics, getPortfolioDividendSummary, filterUpcomingDividends } from '@/lib/dividends';
import { fetchPrice } from '@/lib/prices';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const daysParam = searchParams.get('days');
    const maxDays = daysParam ? parseInt(daysParam) : 30;

    const portfolio = getActivePortfolio();
    const stockHoldings = portfolio.holdings.filter(h => h.type === 'stock');

    if (stockHoldings.length === 0) {
      return NextResponse.json({
        holdings: [],
        summary: {
          totalProjectedIncome: 0,
          weightedAvgYield: 0,
          totalYOC: 0,
          upcomingExDates: [],
        },
      });
    }

    const holdingsWithDividends = [];
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

    const summary = getPortfolioDividendSummary(holdingsWithDividends, currentPrices);
    const upcomingDates = filterUpcomingDividends(summary, maxDays);

    return NextResponse.json({
      holdings: holdingsWithDividends,
      summary: {
        ...summary,
        upcomingExDates: upcomingDates,
      },
    });
  } catch (error) {
    console.error('Error fetching dividend data:', error);
    return NextResponse.json(
      { error: 'Failed to fetch dividend data' },
      { status: 500 }
    );
  }
}
