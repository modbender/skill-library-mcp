/**
 * Budget policy helper: percent of KRW balance, split equally across multiple BUYs.
 */
function floorTo(n, step) {
  if (!Number.isFinite(n)) return 0;
  if (!Number.isFinite(step) || step <= 1) return Math.floor(n);
  return Math.floor(n / step) * step;
}

/**
 * Decide how many BUY events to process and how much KRW per order.
 */
function computeSplitBudget(availableKRW, buyCount, policy) {
  const pct = Number(policy?.pct ?? 0.3);
  const reserveKRW = Number(policy?.reserveKRW ?? 0);
  const minOrderKRW = Number(policy?.minOrderKRW ?? 5000);
  const roundToKRW = Number(policy?.roundToKRW ?? 1000);

  const usable = Math.max(0, Math.floor(availableKRW) - reserveKRW);
  const totalBudget = Math.max(0, Math.floor(usable * pct));

  if (buyCount <= 0) {
    return { totalBudget, usableKRW: usable, perOrderKRW: 0, processCount: 0 };
  }

  const maxAffordable = minOrderKRW > 0 ? Math.floor(totalBudget / minOrderKRW) : buyCount;
  const processCount = Math.max(0, Math.min(buyCount, maxAffordable));

  if (processCount <= 0) {
    return { totalBudget, usableKRW: usable, perOrderKRW: 0, processCount: 0 };
  }

  const rawPer = totalBudget / processCount;
  const perOrder = floorTo(rawPer, roundToKRW);

  if (perOrder < minOrderKRW) {
    const fallbackCount = Math.floor(totalBudget / minOrderKRW);
    const finalCount = Math.max(0, Math.min(buyCount, fallbackCount));
    if (finalCount <= 0) return { totalBudget, usableKRW: usable, perOrderKRW: 0, processCount: 0 };
    return { totalBudget, usableKRW: usable, perOrderKRW: minOrderKRW, processCount: finalCount };
  }

  return { totalBudget, usableKRW: usable, perOrderKRW: perOrder, processCount };
}

module.exports = { computeSplitBudget };
