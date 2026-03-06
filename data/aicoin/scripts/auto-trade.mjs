#!/usr/bin/env node
// Automated Trading — config management + trade execution helper
// Strategy decisions are made by the AI agent, not this script.
import { cli } from '../lib/aicoin-api.mjs';
import { execSync } from 'node:child_process';
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dir = dirname(fileURLToPath(import.meta.url));
const WORKSPACE = resolve(process.env.HOME || '', '.openclaw', 'workspace');
const CONFIG_PATH = resolve(WORKSPACE, 'aicoin-trade-config.json');

const DEFAULT_CONFIG = {
  exchange: 'okx',
  symbol: 'BTC/USDT:USDT',
  market_type: 'swap',
  capital_pct: 0.5,
  leverage: 20,
  stop_loss_pct: 0.025,
  take_profit_pct: 0.05,
};

function loadConfig() {
  if (existsSync(CONFIG_PATH)) {
    try { return { ...DEFAULT_CONFIG, ...JSON.parse(readFileSync(CONFIG_PATH, 'utf-8')) }; } catch {}
  }
  return { ...DEFAULT_CONFIG };
}

function saveConfig(cfg) {
  writeFileSync(CONFIG_PATH, JSON.stringify(cfg, null, 2));
}

function ex(action, params) {
  const cmd = `node ${resolve(__dir, 'exchange.mjs')} ${action} '${JSON.stringify(params)}'`;
  return JSON.parse(execSync(cmd, { encoding: 'utf-8', cwd: resolve(__dir, '..'), timeout: 30000 }));
}

cli({
  // Save trading config
  setup: async (params) => {
    const cfg = { ...loadConfig(), ...params };
    saveConfig(cfg);
    return { saved: CONFIG_PATH, config: cfg };
  },

  // Show config + balance + positions
  status: async (params) => {
    const cfg = { ...loadConfig(), ...params };
    let balance, positions, openOrders;
    try { balance = ex('balance', { exchange: cfg.exchange, market_type: cfg.market_type }); } catch (e) { balance = { error: e.message }; }
    try { positions = ex('positions', { exchange: cfg.exchange, market_type: cfg.market_type }); } catch (e) { positions = { error: e.message }; }
    try { openOrders = ex('open_orders', { exchange: cfg.exchange, symbol: cfg.symbol, market_type: cfg.market_type }); } catch (e) { openOrders = { error: e.message }; }
    return { config: cfg, balance, positions, open_orders: openOrders };
  },

  // Execute a trade with risk management (agent decides direction)
  open: async (params) => {
    const cfg = { ...loadConfig(), ...params };
    const { direction } = params; // 'long' or 'short' — decided by agent
    if (!direction || !['long', 'short'].includes(direction)) {
      throw new Error('Missing "direction": must be "long" or "short"');
    }

    // 1. Check balance
    const bal = ex('balance', { exchange: cfg.exchange, market_type: cfg.market_type });
    const usdt = Number(bal.USDT?.free || 0);
    if (usdt < 1) throw new Error(`Insufficient balance: ${usdt} USDT`);

    // 2. Get current price
    const ticker = ex('ticker', { exchange: cfg.exchange, symbol: cfg.symbol, market_type: cfg.market_type });
    const price = ticker.last || ticker.close;

    // 3. Check market minimums & get contract size
    const base = cfg.symbol.split('/')[0];
    const mkts = ex('markets', { exchange: cfg.exchange, market_type: cfg.market_type, base });
    const mkt = mkts.find(m => m.symbol === cfg.symbol);
    const contractSize = mkt?.contractSize || 1; // e.g. OKX BTC = 0.01 BTC/contract
    const amountStep = mkt?.precision?.amount || 0.01; // exchange precision step
    const amountMin = mkt?.limits?.amount?.min || amountStep;

    // 4. Calculate position size (convert base amount to contracts for futures)
    const capital = usdt * cfg.capital_pct;
    const positionValue = capital * cfg.leverage;
    const amountInBase = positionValue / price;
    // For futures/swap, CCXT amount is in contracts; convert using contractSize
    const rawAmount = cfg.market_type !== 'spot' && contractSize
      ? amountInBase / contractSize
      : amountInBase;
    // Round down to exchange precision step & enforce minimum
    const amount = Math.max(Math.floor(rawAmount / amountStep) * amountStep, amountMin);
    if (amount * (contractSize || 1) * price < 1) throw new Error(`Position too small: ${amount} contracts ≈ ${(amount * contractSize).toFixed(6)} ${base}`);

    // 5. Set leverage
    try { ex('set_leverage', { exchange: cfg.exchange, symbol: cfg.symbol, leverage: cfg.leverage, market_type: cfg.market_type }); } catch {}

    // 6. Place market order
    const side = direction === 'long' ? 'buy' : 'sell';
    const order = ex('create_order', {
      exchange: cfg.exchange, symbol: cfg.symbol, type: 'market', side,
      amount, market_type: cfg.market_type,
    });

    // 7. Place stop-loss & take-profit
    const slPrice = direction === 'long' ? price * (1 - cfg.stop_loss_pct) : price * (1 + cfg.stop_loss_pct);
    const tpPrice = direction === 'long' ? price * (1 + cfg.take_profit_pct) : price * (1 - cfg.take_profit_pct);
    const closeSide = direction === 'long' ? 'sell' : 'buy';

    let sl, tp;
    try { sl = ex('create_order', { exchange: cfg.exchange, symbol: cfg.symbol, type: 'limit', side: closeSide, amount, price: Number(slPrice.toPrecision(6)), market_type: cfg.market_type }); } catch (e) { sl = { error: e.message }; }
    try { tp = ex('create_order', { exchange: cfg.exchange, symbol: cfg.symbol, type: 'limit', side: closeSide, amount, price: Number(tpPrice.toPrecision(6)), market_type: cfg.market_type }); } catch (e) { tp = { error: e.message }; }

    return {
      direction, amount,
      amount_base: `${Number((amount * contractSize).toPrecision(4))} ${base}`,
      contract_size: contractSize !== 1 ? `1 contract = ${contractSize} ${base}` : null,
      entry_price: price, stop_loss: Number(slPrice.toPrecision(6)), take_profit: Number(tpPrice.toPrecision(6)),
      order_id: order.id, sl_order: sl?.id || sl?.error, tp_order: tp?.id || tp?.error,
      capital_used: capital.toFixed(2), position_value: positionValue.toFixed(2),
    };
  },

  // Close current position
  close: async (params) => {
    const cfg = { ...loadConfig(), ...params };
    // Cancel open orders first
    try { ex('cancel_order', { exchange: cfg.exchange, symbol: cfg.symbol, market_type: cfg.market_type }); } catch {}
    // Get position
    const positions = ex('positions', { exchange: cfg.exchange, market_type: cfg.market_type });
    const pos = positions.find(p => p.symbol === cfg.symbol && Math.abs(Number(p.contracts || 0)) > 0);
    if (!pos) return { closed: false, reason: 'No open position' };

    const amount = Math.abs(Number(pos.contracts));
    const side = Number(pos.contracts) > 0 ? 'sell' : 'buy';
    const order = ex('create_order', {
      exchange: cfg.exchange, symbol: cfg.symbol, type: 'market', side, amount, market_type: cfg.market_type,
    });
    return { closed: true, side, amount, order_id: order.id };
  },
});
