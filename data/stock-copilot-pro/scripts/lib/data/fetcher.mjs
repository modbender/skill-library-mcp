import { ThsIfindProvider } from "./providers/ths-ifind.mjs";
import { applyCapabilityDegradation, shouldRetryOnError } from "./fallback.mjs";

function isCapabilityUsable(parsed) {
  if (!parsed || typeof parsed !== "object") return false;
  return Object.values(parsed).some((v) => v != null && v !== "");
}

export function getProvidersForMarket(market) {
  const providers = [];
  if (market === "CN" || market === "HK") providers.push(new ThsIfindProvider());
  return providers;
}

async function fetchWithFallback(capability, symbol, market, providers, options = {}) {
  const errors = [];
  for (const provider of providers) {
    if (!provider.supportsMarket(market)) continue;
    if (!provider.capabilities.includes(capability)) continue;
    const maxRetries = Math.max(1, Number(options.maxRetries || 1));
    for (let retry = 0; retry < maxRetries; retry++) {
      try {
        const result = await provider.fetch(capability, symbol, options);
        if (result?.success && isCapabilityUsable(result.parsed)) {
          const degraded = applyCapabilityDegradation(capability, market, result.parsed);
          return {
            success: true,
            provider: provider.name,
            toolId: result.toolId,
            parsed: degraded.parsed,
            warnings: degraded.warnings,
            raw: result.raw,
          };
        }
      } catch (error) {
        const msg = error?.message || String(error);
        errors.push({ provider: provider.name, error: msg });
        if (!shouldRetryOnError(msg)) break;
      }
    }
  }
  return { success: false, errors };
}

export async function fetchCapabilities(symbol, market, capabilities, options = {}) {
  const providers = options.providers || getProvidersForMarket(market);
  const results = {};
  await Promise.allSettled(
    (capabilities || []).map(async (capability) => {
      results[capability] = await fetchWithFallback(capability, symbol, market, providers, options);
    }),
  );
  return results;
}
