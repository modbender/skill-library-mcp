import { NextResponse } from 'next/server';
import { 
  getActivePortfolio, 
  createPortfolio, 
  deletePortfolio, 
  setActivePortfolio, 
  loadPortfolio,
  addHolding, 
  updateHolding, 
  removeHolding,
  exportToCsv,
  getSellHistory,
  addSellRecord
} from '@/lib/storage';
import { Holding, Portfolio, SellRecord } from '@/lib/types';

export async function GET() {
  const portfolio = getActivePortfolio();
  const state = loadPortfolio();
  
  const sellHistory = getSellHistory();
  const realizedPL = sellHistory.reduce((sum, s) => sum + s.totalRealizedPL, 0);
  
  return NextResponse.json({
    portfolio,
    portfolios: state.portfolios,
    activePortfolioId: state.activePortfolioId,
    realizedPL,
    sellHistory,
  });
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    
    if (body.action === 'createPortfolio') {
      const portfolio = createPortfolio(body.name);
      return NextResponse.json(portfolio, { status: 201 });
    }
    
    if (body.action === 'setActive') {
      const portfolio = setActivePortfolio(body.id);
      if (!portfolio) {
        return NextResponse.json({ error: 'Portfolio not found' }, { status: 404 });
      }
      return NextResponse.json(portfolio);
    }
    
    if (body.action === 'deletePortfolio') {
      const success = deletePortfolio(body.id);
      if (!success) {
        return NextResponse.json({ error: 'Cannot delete last portfolio' }, { status: 400 });
      }
      return NextResponse.json({ success: true });
    }
    
    if (body.action === 'sell') {
      const portfolio = getActivePortfolio();
      const symbol = body.symbol.toUpperCase();
      const sellQty = parseFloat(body.quantity);
      const sellPrice = parseFloat(body.sellPrice);
      const sellDate = body.sellDate || new Date().toISOString().split('T')[0];
      
      const holdingsToSell = portfolio.holdings
        .filter(h => h.symbol === symbol)
        .sort((a, b) => new Date(a.purchaseDate).getTime() - new Date(b.purchaseDate).getTime());
      
      const totalAvailable = holdingsToSell.reduce((sum, h) => sum + h.quantity, 0);
      if (sellQty > totalAvailable) {
        return NextResponse.json({ error: `Not enough ${symbol} to sell. Available: ${totalAvailable}` }, { status: 400 });
      }
      
      const lotsSold = [];
      let remainingToSell = sellQty;
      let totalRealizedPL = 0;
      const state = loadPortfolio();
      const activePortfolio = state.portfolios.find(p => p.id === state.activePortfolioId);
      
      if (!activePortfolio) {
        return NextResponse.json({ error: 'Active portfolio not found' }, { status: 500 });
      }
      
      for (const holding of holdingsToSell) {
        if (remainingToSell <= 0) break;
        const qtyFromThisLot = Math.min(holding.quantity, remainingToSell);
        const costBasis = qtyFromThisLot * holding.purchasePrice;
        const proceeds = qtyFromThisLot * sellPrice;
        const realizedPL = proceeds - costBasis;
        totalRealizedPL += realizedPL;
        
        lotsSold.push({
          holdingId: holding.id,
          quantity: qtyFromThisLot,
          costBasis,
          realizedPL,
        });
        
        holding.quantity -= qtyFromThisLot;
        remainingToSell -= qtyFromThisLot;
        
        if (holding.quantity <= 0) {
          const idx = activePortfolio.holdings.findIndex(h => h.id === holding.id);
          if (idx !== -1) activePortfolio.holdings.splice(idx, 1);
        }
      }
      
      const sellRecord: Omit<SellRecord, 'id'> = {
        symbol,
        quantity: sellQty,
        sellPrice,
        sellDate,
        lotsSold,
        totalRealizedPL,
      };
      
      const savedRecord = addSellRecord(sellRecord);
      return NextResponse.json(savedRecord, { status: 201 });
    }
    
    const holding = addHolding({
      symbol: body.symbol,
      name: body.name,
      type: body.type,
      quantity: body.quantity,
      purchasePrice: body.purchasePrice,
      purchaseDate: body.purchaseDate || new Date().toISOString().split('T')[0],
    });
    return NextResponse.json(holding, { status: 201 });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to process request' }, { status: 500 });
  }
}

export async function PUT(request: Request) {
  try {
    const { id, updates } = await request.json();
    const holding = updateHolding(id, updates);
    if (!holding) {
      return NextResponse.json({ error: 'Holding not found' }, { status: 404 });
    }
    return NextResponse.json(holding);
  } catch (error) {
    return NextResponse.json({ error: 'Failed to update holding' }, { status: 500 });
  }
}

export async function DELETE(request: Request) {
  try {
    const { id } = await request.json();
    const success = removeHolding(id);
    if (!success) {
      return NextResponse.json({ error: 'Holding not found' }, { status: 404 });
    }
    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to remove holding' }, { status: 500 });
  }
}
