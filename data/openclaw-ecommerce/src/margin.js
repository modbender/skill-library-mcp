export function calculateMargin(cost, sell, feesPct = 0) {
  const fees = sell * (feesPct / 100);
  const profit = sell - cost - fees;
  const margin = (profit / sell) * 100;
  return {
    profit: profit,
    margin: margin,
    fees: fees
  };
}