#!/usr/bin/env node
// AiCoin Market Data CLI
import { apiGet, apiPost, cli } from '../lib/aicoin-api.mjs';

cli({
  // market_info
  exchanges: () => apiGet('/api/v2/market'),
  ticker: ({ market_list }) => apiGet('/api/v2/market/ticker', { market_list }),
  hot_coins: ({ key, currency }) => {
    const p = { key };
    if (currency) p.currency = currency;
    return apiGet('/api/v2/market/hotTabCoins', p);
  },
  futures_interest: ({ lan, page, pageSize, currency } = {}) => {
    const p = {};
    if (lan) p.lan = lan;
    if (page) p.page = page;
    if (pageSize) p.pageSize = pageSize;
    if (currency) p.currency = currency;
    return apiGet('/api/v2/futures/interest', p);
  },
  // kline
  kline: ({ symbol, period, size = '100', since, open_time }) => {
    const p = { symbol, size };
    if (period) p.period = period;
    if (since) p.since = since;
    if (open_time) p.open_time = open_time;
    return apiGet('/api/v2/commonKline/dataRecords', p);
  },
  indicator_kline: ({ symbol, indicator_key, period, size = '100' }) => {
    const p = { symbol, indicator_key, size };
    if (period) p.period = period;
    return apiGet('/api/v2/indicatorKline/dataRecords', p);
  },
  indicator_pairs: ({ coinType, indicator_key } = {}) => {
    const p = {};
    if (coinType) p.coinType = coinType;
    if (indicator_key) p.indicator_key = indicator_key;
    return apiGet('/api/v2/indicatorKline/getTradingPair', p);
  },
  // index_data
  index_price: ({ key, currency }) => {
    const p = { key };
    if (currency) p.currency = currency;
    return apiGet('/api/v2/index/indexPrice', p);
  },
  index_info: ({ key, lan }) => {
    const p = { key };
    if (lan) p.lan = lan;
    return apiGet('/api/v2/index/indexInfo', p);
  },
  index_list: () => apiGet('/api/v2/index/getIndex'),
  // crypto_stock
  stock_quotes: ({ tickers } = {}) => {
    const p = {};
    if (tickers) p.tickers = tickers;
    return apiGet('/api/upgrade/v2/crypto_stock/quotes', p);
  },
  stock_top_gainer: ({ us_stock, hk_stock, limit = '30' } = {}) => {
    const p = { limit };
    if (us_stock != null) p.us_stock = us_stock;
    if (hk_stock != null) p.hk_stock = hk_stock;
    return apiGet('/api/upgrade/v2/crypto_stock/top-gainer', p);
  },
  stock_company: ({ symbol }) => apiGet(`/api/upgrade/v2/crypto_stock/company/${symbol}`),
  // coin_treasury
  treasury_entities: (body) => apiPost('/api/upgrade/v2/coin-treasuries/entities', body),
  treasury_history: (body) => apiPost('/api/upgrade/v2/coin-treasuries/history', body),
  treasury_accumulated: (body) => apiPost('/api/upgrade/v2/coin-treasuries/history/accumulated', body),
  treasury_latest_entities: ({ coin }) => apiGet('/api/upgrade/v2/coin-treasuries/latest/entities', { coin }),
  treasury_latest_history: ({ coin }) => apiGet('/api/upgrade/v2/coin-treasuries/latest/history', { coin }),
  treasury_summary: ({ coin }) => apiGet('/api/upgrade/v2/coin-treasuries/summary', { coin }),
  // depth
  depth_latest: ({ dbKey, size }) => {
    const p = { dbKey };
    if (size) p.size = size;
    return apiGet('/api/upgrade/v2/futures/latest-depth', p);
  },
  depth_full: ({ dbKey }) => apiGet('/api/upgrade/v2/futures/full-depth', { dbKey }),
  depth_grouped: ({ dbKey, groupSize }) => apiGet('/api/upgrade/v2/futures/full-depth/grouped', { dbKey, groupSize }),
});
