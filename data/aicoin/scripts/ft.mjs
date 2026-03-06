#!/usr/bin/env node
// Freqtrade Bot Control CLI
import { ftGet, ftPost, ftDelete, ftCli } from '../lib/freqtrade-api.mjs';

ftCli({
  ping: () => ftGet('ping'),
  start: () => ftPost('start'),
  stop: () => ftPost('stop'),
  reload: () => ftPost('reload_config'),
  config: () => ftGet('show_config'),
  version: () => ftGet('version'),
  sysinfo: () => ftGet('sysinfo'),
  health: () => ftGet('health'),
  logs: ({ limit } = {}) => ftGet('logs', { limit }),
  balance: () => ftGet('balance'),
  trades_open: () => ftGet('status'),
  trades_count: () => ftGet('count'),
  trade_by_id: ({ trade_id }) => ftGet(`trade/${trade_id}`),
  trades_history: ({ limit, offset } = {}) => ftGet('trades', { limit, offset }),
  force_enter: (p) => ftPost('forcebuy', p),
  force_exit: (p) => ftPost('forcesell', p),
  cancel_order: ({ trade_id }) => ftDelete(`trades/${trade_id}/open-order`),
  delete_trade: ({ trade_id }) => ftDelete(`trades/${trade_id}`),
  profit: () => ftGet('profit'),
  profit_per_pair: () => ftGet('performance'),
  daily: ({ count } = {}) => ftGet('daily', { timescale: count }),
  weekly: ({ count } = {}) => ftGet('weekly', { timescale: count }),
  monthly: ({ count } = {}) => ftGet('monthly', { timescale: count }),
  stats: () => ftGet('stats'),
});
