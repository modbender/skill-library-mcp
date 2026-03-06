export const DEGRADATION_STRATEGIES = {
  "HK:fundamentals": {
    action: "warn",
    message: "港股财务数据覆盖有限，部分字段可能为空",
    hideFields: ["revenue", "netProfit", "operatingCashflow"],
  },
  timeout: {
    action: "fallback",
    fallbackProvider: "next",
    maxRetries: 2,
  },
};

export function applyCapabilityDegradation(capability, market, parsed) {
  const key = `${market}:${capability}`;
  const strategy = DEGRADATION_STRATEGIES[key];
  if (!strategy || !parsed || typeof parsed !== "object") return { parsed, warnings: [] };
  if (strategy.action === "warn") {
    const next = { ...parsed };
    for (const field of strategy.hideFields || []) {
      if (field in next && next[field] == null) delete next[field];
    }
    return { parsed: next, warnings: [strategy.message] };
  }
  return { parsed, warnings: [] };
}

export function shouldRetryOnError(errorMessage) {
  const msg = String(errorMessage || "").toLowerCase();
  return msg.includes("timeout") || msg.includes("aborterror");
}
