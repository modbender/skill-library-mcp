export type EngineTag = "COPY" | "AI";

export type BudgetState = {
  // pnl in percentage of bankroll (negative means loss)
  pnlCopyPct: number;
  pnlAiPct: number;
};

export function budgetLimits(cfg: any): { copyMaxLossPct: number; aiMaxLossPct: number } {
  const daily = cfg.portfolio.daily_loss_limit_pct as number;
  const split = cfg.risk_budget_split;
  const copyMaxLossPct = daily * (split.copy_trade_pct / 100);
  const aiMaxLossPct = daily * (split.ai_trade_pct / 100);
  return { copyMaxLossPct, aiMaxLossPct };
}

export function engineHalted(tag: EngineTag, b: BudgetState, cfg: any): { stop: boolean; reason?: string } {
  const lim = budgetLimits(cfg);
  if (tag === "COPY" && b.pnlCopyPct <= -lim.copyMaxLossPct) return { stop: true, reason: "copyBudgetExceeded" };
  if (tag === "AI" && b.pnlAiPct <= -lim.aiMaxLossPct) return { stop: true, reason: "aiBudgetExceeded" };
  return { stop: false };
}
