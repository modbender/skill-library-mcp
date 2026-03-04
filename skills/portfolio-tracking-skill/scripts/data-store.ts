import fs from 'node:fs';
import path from 'node:path';
import type { DataFile, ConfigFile, Portfolio, Asset, Currency, ExchangeRates } from './utils.js';
import { DEFAULT_FX_RATES, generateId } from './utils.js';

const DATA_DIR = path.join(process.env.HOME || '~', '.portfolio-tracker');
const DATA_FILE = path.join(DATA_DIR, 'data.json');
const CONFIG_FILE = path.join(DATA_DIR, 'config.json');

function ensureDir(): void {
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }
}

function createDefaultData(): DataFile {
  const defaultPortfolioId = generateId();
  return {
    version: 1,
    currentPortfolioId: defaultPortfolioId,
    displayCurrency: 'USD',
    exchangeRates: { ...DEFAULT_FX_RATES },
    lastPriceRefresh: null,
    portfolios: [
      { id: defaultPortfolioId, name: 'Main', assets: [] },
    ],
  };
}

function createDefaultConfig(): ConfigFile {
  return { wallets: [] };
}

// ─── Data File Operations ───────────────────────────────────────────

export function loadData(): DataFile {
  ensureDir();
  if (!fs.existsSync(DATA_FILE)) {
    const data = createDefaultData();
    saveData(data);
    return data;
  }
  const raw = fs.readFileSync(DATA_FILE, 'utf-8');
  return JSON.parse(raw) as DataFile;
}

export function saveData(data: DataFile): void {
  ensureDir();
  fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2), 'utf-8');
}

// ─── Config File Operations ─────────────────────────────────────────

export function loadConfig(): ConfigFile {
  ensureDir();
  if (!fs.existsSync(CONFIG_FILE)) {
    const config = createDefaultConfig();
    saveConfig(config);
    return config;
  }
  const raw = fs.readFileSync(CONFIG_FILE, 'utf-8');
  return JSON.parse(raw) as ConfigFile;
}

export function saveConfig(config: ConfigFile): void {
  ensureDir();
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2), 'utf-8');
}

// ─── Portfolio Helpers ──────────────────────────────────────────────

export function getCurrentPortfolio(data: DataFile): Portfolio {
  const p = data.portfolios.find(p => p.id === data.currentPortfolioId);
  if (!p) {
    if (data.portfolios.length > 0) {
      data.currentPortfolioId = data.portfolios[0].id;
      return data.portfolios[0];
    }
    throw new Error('No portfolios found');
  }
  return p;
}

export function addAsset(data: DataFile, asset: Asset): DataFile {
  const portfolio = getCurrentPortfolio(data);
  portfolio.assets.push(asset);
  return data;
}

export function removeAsset(data: DataFile, assetId: string): DataFile {
  const portfolio = getCurrentPortfolio(data);
  portfolio.assets = portfolio.assets.filter(a => a.id !== assetId);
  return data;
}

export function updateAsset(data: DataFile, assetId: string, updates: Partial<Asset>): DataFile {
  const portfolio = getCurrentPortfolio(data);
  const idx = portfolio.assets.findIndex(a => a.id === assetId);
  if (idx === -1) throw new Error(`Asset ${assetId} not found`);
  portfolio.assets[idx] = { ...portfolio.assets[idx], ...updates };
  return data;
}

export function setDisplayCurrency(data: DataFile, currency: Currency): DataFile {
  data.displayCurrency = currency;
  return data;
}

export function updateExchangeRates(data: DataFile, rates: ExchangeRates): DataFile {
  data.exchangeRates = rates;
  return data;
}

export function createPortfolio(data: DataFile, name: string): DataFile {
  const id = generateId();
  data.portfolios.push({ id, name, assets: [] });
  return data;
}

export function switchPortfolio(data: DataFile, portfolioId: string): DataFile {
  const p = data.portfolios.find(p => p.id === portfolioId);
  if (!p) throw new Error(`Portfolio ${portfolioId} not found`);
  data.currentPortfolioId = portfolioId;
  return data;
}

export function deletePortfolio(data: DataFile, portfolioId: string): DataFile {
  if (data.portfolios.length <= 1) throw new Error('Cannot delete the last portfolio');
  data.portfolios = data.portfolios.filter(p => p.id !== portfolioId);
  if (data.currentPortfolioId === portfolioId) {
    data.currentPortfolioId = data.portfolios[0].id;
  }
  return data;
}

// ─── CLI Entry Point ────────────────────────────────────────────────

const command = process.argv[2];

if (command) {
  try {
    let result: unknown;

    switch (command) {
      case 'load': {
        result = loadData();
        break;
      }
      case 'save': {
        const input = fs.readFileSync(0, 'utf-8'); // stdin
        const data = JSON.parse(input) as DataFile;
        saveData(data);
        result = { success: true };
        break;
      }
      case 'load-config': {
        result = loadConfig();
        break;
      }
      case 'save-config': {
        const input = fs.readFileSync(0, 'utf-8');
        const config = JSON.parse(input) as ConfigFile;
        saveConfig(config);
        result = { success: true };
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
