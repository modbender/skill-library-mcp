#!/usr/bin/env node
// Hyperliquid Trader Analytics CLI
import { apiGet, apiPost, cli } from '../lib/aicoin-api.mjs';

cli({
  // hl_trader
  trader_stats: ({ address, period }) => {
    const p = {}; if (period) p.period = period;
    return apiGet(`/api/upgrade/v2/hl/traders/${address}/addr-stat`, p);
  },
  best_trades: ({ address, period, limit }) => {
    const p = { period }; if (limit) p.limit = limit;
    return apiGet(`/api/upgrade/v2/hl/traders/${address}/best-trades`, p);
  },
  performance: ({ address, period, limit }) => {
    const p = { period }; if (limit) p.limit = limit;
    return apiGet(`/api/upgrade/v2/hl/traders/${address}/performance-by-coin`, p);
  },
  completed_trades: ({ address, coin, limit }) => {
    const p = {}; if (coin) p.coin = coin; if (limit) p.limit = limit;
    return apiGet(`/api/upgrade/v2/hl/traders/${address}/completed-trades`, p);
  },
  accounts: ({ addresses }) => apiPost('/api/upgrade/v2/hl/traders/accounts', { addresses: JSON.parse(addresses) }),
  statistics: ({ addresses }) => apiPost('/api/upgrade/v2/hl/traders/statistics', { addresses: JSON.parse(addresses) }),
  // hl_fills
  fills: ({ address, coin, limit }) => {
    const p = {}; if (coin) p.coin = coin; if (limit) p.limit = limit;
    return apiGet(`/api/upgrade/v2/hl/fills/${address}`, p);
  },
  fills_by_oid: ({ oid }) => apiGet(`/api/upgrade/v2/hl/fills/oid/${oid}`),
  fills_by_twapid: ({ twapid }) => apiGet(`/api/upgrade/v2/hl/fills/twapid/${twapid}`),
  top_trades: ({ coin, interval, limit }) => {
    const p = { coin, interval }; if (limit) p.limit = limit;
    return apiGet('/api/upgrade/v2/hl/fills/top-trades', p);
  },
  // hl_orders
  orders_latest: ({ address, coin, limit }) => {
    const p = {}; if (coin) p.coin = coin; if (limit) p.limit = limit;
    return apiGet(`/api/upgrade/v2/hl/orders/${address}/latest`, p);
  },
  order_by_oid: ({ oid }) => apiGet(`/api/upgrade/v2/hl/orders/oid/${oid}`),
  filled_orders: ({ address, coin, limit }) => {
    const p = {}; if (coin) p.coin = coin; if (limit) p.limit = limit;
    return apiGet(`/api/upgrade/v2/hl/filled-orders/${address}/latest`, p);
  },
  filled_by_oid: ({ oid }) => apiGet(`/api/upgrade/v2/hl/filled-orders/oid/${oid}`),
  top_open: ({ coin, min_val, limit }) => {
    const p = {}; if (coin) p.coin = coin; if (min_val) p.min_val = min_val; if (limit) p.limit = limit;
    return apiGet('/api/upgrade/v2/hl/orders/top-open-orders', p);
  },
  active_stats: ({ coin, whale_threshold }) => {
    const p = {}; if (coin) p.coin = coin; if (whale_threshold) p.whale_threshold = whale_threshold;
    return apiGet('/api/upgrade/v2/hl/orders/active-stats', p);
  },
  twap_states: ({ address }) => apiGet(`/api/upgrade/v2/hl/twap-states/${address}/latest`),
  // hl_position
  current_pos_history: ({ address, coin }) => apiGet(`/api/upgrade/v2/hl/traders/${address}/current-position-history/${coin}`),
  completed_pos_history: ({ address, coin, startTime, endTime }) => {
    const p = {}; if (startTime) p.startTime = startTime; if (endTime) p.endTime = endTime;
    return apiGet(`/api/upgrade/v2/hl/traders/${address}/completed-position-history/${coin}`, p);
  },
  current_pnl: ({ address, coin, interval }) => apiGet(`/api/upgrade/v2/hl/traders/${address}/current-position-pnl/${coin}`, { interval }),
  completed_pnl: ({ address, coin, interval, startTime, endTime }) => {
    const p = { interval }; if (startTime) p.startTime = startTime; if (endTime) p.endTime = endTime;
    return apiGet(`/api/upgrade/v2/hl/traders/${address}/completed-position-pnl/${coin}`, p);
  },
  current_executions: ({ address, coin, interval }) => apiGet(`/api/upgrade/v2/hl/traders/${address}/current-position-executions/${coin}`, { interval }),
  completed_executions: ({ address, coin, interval, startTime, endTime }) => {
    const p = { interval }; if (startTime) p.startTime = startTime; if (endTime) p.endTime = endTime;
    return apiGet(`/api/upgrade/v2/hl/traders/${address}/completed-position-executions/${coin}`, p);
  },
  // hl_portfolio
  portfolio: ({ address, window }) => apiGet(`/api/upgrade/v2/hl/portfolio/${address}/${window}`),
  pnls: ({ address, period }) => {
    const p = {}; if (period) p.period = period;
    return apiGet(`/api/upgrade/v2/hl/pnls/${address}`, p);
  },
  max_drawdown: ({ address, days, scope = 'perp' }) => apiGet(`/api/upgrade/v2/hl/max-drawdown/${address}`, { days, scope }),
  net_flow: ({ address, days }) => apiGet(`/api/upgrade/v2/hl/ledger-updates/net-flow/${address}`, { days }),
  // hl_advanced
  info: ({ type, user, extra_params }) => {
    const body = { type }; if (user) body.user = user;
    if (extra_params) Object.assign(body, JSON.parse(extra_params));
    return apiPost('/api/upgrade/v2/hl/info', body);
  },
  smart_find: (params) => apiPost('/api/upgrade/v2/hl/smart/find', params || {}),
  discover: (params) => apiPost('/api/upgrade/v2/hl/traders/discover', params || {}),
});
