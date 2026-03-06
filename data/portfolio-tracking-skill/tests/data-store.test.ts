import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

// We'll use a temp directory to avoid touching real ~/.portfolio-tracker
let tmpDir: string;
let originalHome: string | undefined;

beforeEach(() => {
  tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'pt-test-'));
  originalHome = process.env.HOME;
  process.env.HOME = tmpDir;
});

afterEach(() => {
  process.env.HOME = originalHome;
  fs.rmSync(tmpDir, { recursive: true, force: true });
  // Clear module cache so data-store re-reads HOME
  vi.resetModules();
});

async function importDataStore() {
  return import('../scripts/data-store.js');
}

describe('loadData', () => {
  it('should create default data file when none exists', async () => {
    const { loadData } = await importDataStore();
    const data = loadData();

    expect(data.version).toBe(1);
    expect(data.displayCurrency).toBe('USD');
    expect(data.portfolios).toHaveLength(1);
    expect(data.portfolios[0].name).toBe('Main');
    expect(data.portfolios[0].assets).toEqual([]);
    expect(data.currentPortfolioId).toBe(data.portfolios[0].id);
    expect(data.lastPriceRefresh).toBeNull();

    // Verify file was written
    const filePath = path.join(tmpDir, '.portfolio-tracker', 'data.json');
    expect(fs.existsSync(filePath)).toBe(true);
  });

  it('should load existing data file', async () => {
    const dir = path.join(tmpDir, '.portfolio-tracker');
    fs.mkdirSync(dir, { recursive: true });
    const testData = {
      version: 1,
      currentPortfolioId: 'test-id',
      displayCurrency: 'CNY',
      exchangeRates: { USD: 1, CNY: 7.24, HKD: 7.8 },
      lastPriceRefresh: '2024-01-01',
      portfolios: [{ id: 'test-id', name: 'Test', assets: [] }],
    };
    fs.writeFileSync(path.join(dir, 'data.json'), JSON.stringify(testData));

    const { loadData } = await importDataStore();
    const data = loadData();

    expect(data.displayCurrency).toBe('CNY');
    expect(data.currentPortfolioId).toBe('test-id');
    expect(data.portfolios[0].name).toBe('Test');
  });
});

describe('saveData', () => {
  it('should write data to file', async () => {
    const { loadData, saveData } = await importDataStore();
    const data = loadData();
    data.displayCurrency = 'HKD';
    saveData(data);

    const filePath = path.join(tmpDir, '.portfolio-tracker', 'data.json');
    const raw = fs.readFileSync(filePath, 'utf-8');
    const parsed = JSON.parse(raw);
    expect(parsed.displayCurrency).toBe('HKD');
  });
});

describe('loadConfig', () => {
  it('should create default config when none exists', async () => {
    const { loadConfig } = await importDataStore();
    const config = loadConfig();

    expect(config.wallets).toEqual([]);
    expect(config.userProfile).toBeUndefined();
  });
});

describe('getCurrentPortfolio', () => {
  it('should return the current portfolio', async () => {
    const { loadData, getCurrentPortfolio } = await importDataStore();
    const data = loadData();
    const portfolio = getCurrentPortfolio(data);

    expect(portfolio.name).toBe('Main');
    expect(portfolio.id).toBe(data.currentPortfolioId);
  });

  it('should fallback to first portfolio if current ID is invalid', async () => {
    const { loadData, getCurrentPortfolio } = await importDataStore();
    const data = loadData();
    data.currentPortfolioId = 'nonexistent';
    const portfolio = getCurrentPortfolio(data);

    expect(portfolio.name).toBe('Main');
    expect(data.currentPortfolioId).toBe(data.portfolios[0].id);
  });
});

describe('addAsset / removeAsset / updateAsset', () => {
  it('should add an asset to current portfolio', async () => {
    const { loadData, addAsset, getCurrentPortfolio } = await importDataStore();
    const data = loadData();

    const asset = {
      id: 'test-asset-1',
      type: 'CRYPTO' as const,
      symbol: 'BTC',
      name: 'Bitcoin',
      quantity: 1.5,
      avgPrice: 40000,
      currentPrice: 50000,
      currency: 'USD' as const,
      transactions: [],
    };

    addAsset(data, asset);
    const portfolio = getCurrentPortfolio(data);
    expect(portfolio.assets).toHaveLength(1);
    expect(portfolio.assets[0].symbol).toBe('BTC');
  });

  it('should remove an asset', async () => {
    const { loadData, addAsset, removeAsset, getCurrentPortfolio } = await importDataStore();
    const data = loadData();

    addAsset(data, {
      id: 'rm-1', type: 'CRYPTO', symbol: 'ETH', name: 'Ethereum',
      quantity: 10, avgPrice: 3000, currentPrice: 3500, currency: 'USD', transactions: [],
    });

    removeAsset(data, 'rm-1');
    expect(getCurrentPortfolio(data).assets).toHaveLength(0);
  });

  it('should update an asset', async () => {
    const { loadData, addAsset, updateAsset, getCurrentPortfolio } = await importDataStore();
    const data = loadData();

    addAsset(data, {
      id: 'upd-1', type: 'USSTOCK', symbol: 'AAPL', name: 'Apple',
      quantity: 100, avgPrice: 150, currentPrice: 175, currency: 'USD', transactions: [],
    });

    updateAsset(data, 'upd-1', { currentPrice: 180, quantity: 110 });
    const asset = getCurrentPortfolio(data).assets[0];
    expect(asset.currentPrice).toBe(180);
    expect(asset.quantity).toBe(110);
  });

  it('should throw when updating non-existent asset', async () => {
    const { loadData, updateAsset } = await importDataStore();
    const data = loadData();
    expect(() => updateAsset(data, 'nope', { quantity: 1 })).toThrow('Asset nope not found');
  });
});

describe('portfolio management', () => {
  it('should create a new portfolio', async () => {
    const { loadData, createPortfolio } = await importDataStore();
    const data = loadData();
    createPortfolio(data, 'Second');
    expect(data.portfolios).toHaveLength(2);
    expect(data.portfolios[1].name).toBe('Second');
  });

  it('should switch portfolio', async () => {
    const { loadData, createPortfolio, switchPortfolio } = await importDataStore();
    const data = loadData();
    createPortfolio(data, 'Other');
    const otherId = data.portfolios[1].id;

    switchPortfolio(data, otherId);
    expect(data.currentPortfolioId).toBe(otherId);
  });

  it('should throw when switching to non-existent portfolio', async () => {
    const { loadData, switchPortfolio } = await importDataStore();
    const data = loadData();
    expect(() => switchPortfolio(data, 'bad-id')).toThrow('Portfolio bad-id not found');
  });

  it('should delete a portfolio', async () => {
    const { loadData, createPortfolio, deletePortfolio } = await importDataStore();
    const data = loadData();
    createPortfolio(data, 'ToDelete');
    const deleteId = data.portfolios[1].id;

    deletePortfolio(data, deleteId);
    expect(data.portfolios).toHaveLength(1);
  });

  it('should not delete the last portfolio', async () => {
    const { loadData, deletePortfolio } = await importDataStore();
    const data = loadData();
    expect(() => deletePortfolio(data, data.portfolios[0].id)).toThrow('Cannot delete the last portfolio');
  });

  it('should update currentPortfolioId when deleting current portfolio', async () => {
    const { loadData, createPortfolio, switchPortfolio, deletePortfolio } = await importDataStore();
    const data = loadData();
    const firstId = data.portfolios[0].id;
    createPortfolio(data, 'Second');
    const secondId = data.portfolios[1].id;

    switchPortfolio(data, secondId);
    deletePortfolio(data, secondId);
    expect(data.currentPortfolioId).toBe(firstId);
  });
});

describe('setDisplayCurrency / updateExchangeRates', () => {
  it('should set display currency', async () => {
    const { loadData, setDisplayCurrency } = await importDataStore();
    const data = loadData();
    setDisplayCurrency(data, 'CNY');
    expect(data.displayCurrency).toBe('CNY');
  });

  it('should update exchange rates', async () => {
    const { loadData, updateExchangeRates } = await importDataStore();
    const data = loadData();
    updateExchangeRates(data, { USD: 1, CNY: 7.3, HKD: 7.85 });
    expect(data.exchangeRates.CNY).toBe(7.3);
    expect(data.exchangeRates.HKD).toBe(7.85);
  });
});
