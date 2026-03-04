import fs from 'fs';
import path from 'path';
import { PortfolioState, Portfolio, Holding, SellRecord } from './types';

const DATA_DIR = path.join(process.cwd(), 'data');
const PORTFOLIO_FILE = path.join(DATA_DIR, 'portfolio.json');

function ensureDataDir() {
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }
}

function createDefaultPortfolio(): Portfolio {
  return {
    id: crypto.randomUUID(),
    name: 'Main Portfolio',
    holdings: [],
    sellHistory: [],
    createdAt: new Date().toISOString(),
    lastUpdated: new Date().toISOString(),
  };
}

export function loadPortfolio(): PortfolioState {
  ensureDataDir();
  if (!fs.existsSync(PORTFOLIO_FILE)) {
    const defaultPortfolio = createDefaultPortfolio();
    const state: PortfolioState = {
      portfolios: [defaultPortfolio],
      activePortfolioId: defaultPortfolio.id,
    };
    savePortfolio(state);
    return state;
  }
  try {
    const data = fs.readFileSync(PORTFOLIO_FILE, 'utf-8');
    const state = JSON.parse(data);
    if (!state.portfolios || state.portfolios.length === 0) {
      const defaultPortfolio = createDefaultPortfolio();
      state.portfolios = [defaultPortfolio];
      state.activePortfolioId = defaultPortfolio.id;
      savePortfolio(state);
    }
    for (const portfolio of state.portfolios) {
      if (!portfolio.sellHistory) {
        portfolio.sellHistory = [];
      }
    }
    return state;
  } catch {
    const defaultPortfolio = createDefaultPortfolio();
    return { portfolios: [defaultPortfolio], activePortfolioId: defaultPortfolio.id };
  }
}

export function savePortfolio(state: PortfolioState): void {
  ensureDataDir();
  fs.writeFileSync(PORTFOLIO_FILE, JSON.stringify(state, null, 2));
}

export function getActivePortfolio(): Portfolio {
  const state = loadPortfolio();
  return state.portfolios.find(p => p.id === state.activePortfolioId) || state.portfolios[0];
}

export function setActivePortfolio(id: string): Portfolio | null {
  const state = loadPortfolio();
  const portfolio = state.portfolios.find(p => p.id === id);
  if (!portfolio) return null;
  state.activePortfolioId = id;
  savePortfolio(state);
  return portfolio;
}

export function createPortfolio(name: string): Portfolio {
  const state = loadPortfolio();
  const newPortfolio: Portfolio = {
    id: crypto.randomUUID(),
    name,
    holdings: [],
    sellHistory: [],
    createdAt: new Date().toISOString(),
    lastUpdated: new Date().toISOString(),
  };
  state.portfolios.push(newPortfolio);
  state.activePortfolioId = newPortfolio.id;
  savePortfolio(state);
  return newPortfolio;
}

export function deletePortfolio(id: string): boolean {
  const state = loadPortfolio();
  if (state.portfolios.length <= 1) return false;
  const index = state.portfolios.findIndex(p => p.id === id);
  if (index === -1) return false;
  state.portfolios.splice(index, 1);
  if (state.activePortfolioId === id) {
    state.activePortfolioId = state.portfolios[0].id;
  }
  savePortfolio(state);
  return true;
}

export function addHolding(holding: Omit<Holding, 'id'>): Holding {
  const state = loadPortfolio();
  const portfolio = state.portfolios.find(p => p.id === state.activePortfolioId) || state.portfolios[0];
  const newHolding: Holding = {
    ...holding,
    id: crypto.randomUUID(),
  };
  portfolio.holdings.push(newHolding);
  portfolio.lastUpdated = new Date().toISOString();
  savePortfolio(state);
  return newHolding;
}

export function updateHolding(id: string, updates: Partial<Holding>): Holding | null {
  const state = loadPortfolio();
  const portfolio = state.portfolios.find(p => p.id === state.activePortfolioId) || state.portfolios[0];
  const index = portfolio.holdings.findIndex(h => h.id === id);
  if (index === -1) return null;
  portfolio.holdings[index] = { ...portfolio.holdings[index], ...updates };
  portfolio.lastUpdated = new Date().toISOString();
  savePortfolio(state);
  return portfolio.holdings[index];
}

export function removeHolding(id: string): boolean {
  const state = loadPortfolio();
  const portfolio = state.portfolios.find(p => p.id === state.activePortfolioId) || state.portfolios[0];
  const index = portfolio.holdings.findIndex(h => h.id === id);
  if (index === -1) return false;
  portfolio.holdings.splice(index, 1);
  portfolio.lastUpdated = new Date().toISOString();
  savePortfolio(state);
  return true;
}

export function exportToCsv(): string {
  const portfolio = getActivePortfolio();
  const headers = ['Symbol', 'Name', 'Type', 'Quantity', 'Purchase Price', 'Purchase Date'];
  const rows = portfolio.holdings.map(h => [
    h.symbol,
    h.name,
    h.type,
    h.quantity.toString(),
    h.purchasePrice.toString(),
    h.purchaseDate,
  ]);
  return [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
}

export function getSellHistory(symbol?: string): SellRecord[] {
  const portfolio = getActivePortfolio();
  if (symbol) {
    return portfolio.sellHistory.filter(s => s.symbol === symbol.toUpperCase());
  }
  return portfolio.sellHistory;
}

export function addSellRecord(record: Omit<SellRecord, 'id'>): SellRecord {
  const state = loadPortfolio();
  const portfolio = state.portfolios.find(p => p.id === state.activePortfolioId) || state.portfolios[0];
  const newRecord: SellRecord = {
    ...record,
    id: crypto.randomUUID(),
  };
  portfolio.sellHistory.push(newRecord);
  portfolio.lastUpdated = new Date().toISOString();
  savePortfolio(state);
  return newRecord;
}
