#!/usr/bin/env node
// Hyperliquid Data CLI - Part 1: ticker, whale, liquidation, OI, taker
import { apiGet, apiPost, cli } from '../lib/aicoin-api.mjs';

cli({
  tickers: () => apiGet('/api/upgrade/v2/hl/tickers'),
  ticker: ({ coin }) => apiGet(`/api/upgrade/v2/hl/tickers/coin/${coin}`),
  whale_positions: ({ coin, min_usd } = {}) => {
    const p = {}; if (coin) p.coin = coin; if (min_usd) p.min_usd = min_usd;
    return apiGet('/api/upgrade/v2/hl/whales/open-positions', p);
  },
  whale_events: ({ coin } = {}) => {
    const p = {}; if (coin) p.coin = coin;
    return apiGet('/api/upgrade/v2/hl/whales/latest-events', p);
  },
  whale_directions: ({ coin } = {}) => {
    const p = {}; if (coin) p.coin = coin;
    return apiGet('/api/upgrade/v2/hl/whales/directions', p);
  },
  whale_history_ratio: ({ coin } = {}) => {
    const p = {}; if (coin) p.coin = coin;
    return apiGet('/api/upgrade/v2/hl/whales/history-long-ratio', p);
  },
  liq_history: ({ coin } = {}) => {
    const p = {}; if (coin) p.coin = coin;
    return apiGet('/api/upgrade/v2/hl/liquidations/history', p);
  },
  liq_stats: () => apiGet('/api/upgrade/v2/hl/liquidations/stat'),
  liq_stats_by_coin: ({ coin } = {}) => {
    const p = {}; if (coin) p.coin = coin;
    return apiGet('/api/upgrade/v2/hl/liquidations/stat-by-coin', p);
  },
  liq_top_positions: ({ coin, interval, limit }) => {
    const p = { coin, interval }; if (limit) p.limit = limit;
    return apiGet('/api/upgrade/v2/hl/liquidations/top-positions', p);
  },
  oi_summary: () => apiGet('/api/upgrade/v2/hl/open-interest/summary'),
  oi_top_coins: ({ limit } = {}) => {
    const p = {}; if (limit) p.limit = limit;
    return apiGet('/api/upgrade/v2/hl/open-interest/top-coins', p);
  },
  oi_history: ({ coin, interval }) => {
    const p = {}; if (interval) p.interval = interval;
    return apiGet(`/api/upgrade/v2/hl/open-interest/history/${coin}`, p);
  },
  taker_delta: ({ coin, interval }) => {
    const p = {}; if (interval) p.interval = interval;
    return apiGet(`/api/upgrade/v2/hl/accumulated-taker-delta/${coin}`, p);
  },
  taker_klines: ({ coin, interval = '4h' }) =>
    apiGet(`/api/upgrade/v2/hl/klines-with-taker-vol/${coin}/${interval}`),
});
