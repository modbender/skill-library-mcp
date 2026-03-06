#!/usr/bin/env node
// AiCoin Features & Signals CLI
import { apiGet, cli } from '../lib/aicoin-api.mjs';

cli({
  // market_overview
  nav: ({ lan } = {}) => { const p = {}; if (lan) p.lan = lan; return apiGet('/api/v2/mix/nav', p); },
  ls_ratio: () => apiGet('/api/v2/mix/ls-ratio'),
  liquidation: ({ currency, type, coinKey, marketKey } = {}) => {
    const p = {};
    if (currency) p.currency = currency;
    if (type) p.type = type;
    if (coinKey) p.coinKey = coinKey;
    if (marketKey) p.marketKey = marketKey;
    return apiGet('/api/v2/mix/liq', p);
  },
  grayscale_trust: () => apiGet('/api/v2/mix/grayscale-trust'),
  gray_scale: ({ coins }) => apiGet('/api/v2/mix/gray-scale', { coins }),
  stock_market: () => apiGet('/api/v2/mix/stock-market'),
  // order_flow
  big_orders: ({ symbol }) => apiGet('/api/v2/order/bigOrder', { symbol }),
  agg_trades: ({ symbol }) => apiGet('/api/v2/order/aggTrade', { symbol }),
  // trading_pair
  pair_ticker: ({ key_list }) => apiGet('/api/v2/trading-pair/ticker', { key_list }),
  pair_by_market: ({ market }) => apiGet('/api/v2/trading-pair/getTradingPair', { market }),
  pair_list: ({ market, currency, show }) => {
    const p = { market };
    if (currency) p.currency = currency;
    if (show) p.show = show;
    return apiGet('/api/v2/trading-pair', p);
  },
  // signal_data
  strategy_signal: ({ coin_type, signal_key, latest_time } = {}) => {
    const p = {};
    if (coin_type) p.coin_type = coin_type;
    if (signal_key) p.signal_key = signal_key;
    if (latest_time) p.latest_time = latest_time;
    return apiGet('/api/v2/signal/strategySignal', p);
  },
  signal_alert: () => apiGet('/api/v2/signal/signalAlert'),
  signal_config: ({ lan } = {}) => { const p = {}; if (lan) p.lan = lan; return apiGet('/api/v2/signal/signalAlertConf', p); },
  signal_alert_list: () => apiGet('/api/v2/signal/getSignalAlertSetList'),
  change_signal: ({ type, currency } = {}) => {
    const p = {};
    if (type) p.type = type;
    if (currency) p.currency = currency;
    return apiGet('/api/v2/signal/changeSignal', p);
  },
  delete_signal: ({ id }) => apiGet('/api/v2/signal/delSignalAlert', { id }),
});
