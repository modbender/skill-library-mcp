export function halted(state: {
  dailyPnlPct: number;
  tradesToday: number;
  openPositions: number;
}, cfg: any): { stop: boolean; reason?: string } {
  const p = cfg.portfolio;
  if (state.dailyPnlPct <= -p.daily_loss_limit_pct) return { stop: true, reason: "dailyLossLimit" };
  if (state.tradesToday >= p.max_trades_per_day) return { stop: true, reason: "maxTradesPerDay" };
  if (state.openPositions >= p.max_open_positions) return { stop: true, reason: "maxOpenPositions" };
  return { stop: false };
}
