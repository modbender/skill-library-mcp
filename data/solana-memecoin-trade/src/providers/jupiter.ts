import { httpGetJson } from "./http.js";

export type JupQuote = any;

export async function getSolUsdPrice(jupBase: string, apiKey?: string): Promise<number | null> {
  const url = `${jupBase}/price/v3?ids=So11111111111111111111111111111111111111112`;
  const data = await httpGetJson<Record<string, { usdPrice: number }>>(url, apiKey ? { "x-api-key": apiKey } : undefined);
  const sol = data["So11111111111111111111111111111111111111112"];
  return sol?.usdPrice ?? null;
}

export async function getPriceDecimals(jupBase: string, mints: string[], apiKey?: string): Promise<Record<string, { usdPrice?: number; decimals?: number }>> {
  const url = `${jupBase}/price/v3?ids=${encodeURIComponent(mints.join(","))}`;
  return await httpGetJson<any>(url, apiKey ? { "x-api-key": apiKey } : undefined);
}

export async function getQuote(params: {
  jupBase: string;
  apiKey?: string;
  inputMint: string;
  outputMint: string;
  amount: string; // raw amount, before decimals
  slippageBps: number;
  restrictIntermediateTokens?: boolean;
  onlyDirectRoutes?: boolean;
  swapMode?: "ExactIn" | "ExactOut";
}): Promise<JupQuote> {
  const qs = new URLSearchParams();
  qs.set("inputMint", params.inputMint);
  qs.set("outputMint", params.outputMint);
  qs.set("amount", params.amount);
  qs.set("slippageBps", String(params.slippageBps));
  qs.set("swapMode", params.swapMode ?? "ExactIn");
  if (params.restrictIntermediateTokens !== undefined) qs.set("restrictIntermediateTokens", String(params.restrictIntermediateTokens));
  if (params.onlyDirectRoutes !== undefined) qs.set("onlyDirectRoutes", String(params.onlyDirectRoutes));
  const url = `${params.jupBase}/swap/v1/quote?${qs.toString()}`;
  return await httpGetJson<any>(url, params.apiKey ? { "x-api-key": params.apiKey } : undefined);
}

export async function buildSwapTx(params: {
  jupBase: string;
  apiKey?: string;
  quoteResponse: any;
  userPublicKey: string;
  wrapAndUnwrapSol?: boolean;
  dynamicComputeUnitLimit?: boolean;
  dynamicSlippage?: boolean;
  prioritizationFeeLamports?: any;
}): Promise<any> {
  const url = `${params.jupBase}/swap/v1/swap`;
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(params.apiKey ? { "x-api-key": params.apiKey } : {}),
    },
    body: JSON.stringify({
      quoteResponse: params.quoteResponse,
      userPublicKey: params.userPublicKey,
      wrapAndUnwrapSol: params.wrapAndUnwrapSol ?? true,
      dynamicComputeUnitLimit: params.dynamicComputeUnitLimit ?? true,
      dynamicSlippage: params.dynamicSlippage ?? true,
      prioritizationFeeLamports: params.prioritizationFeeLamports,
    }),
  });
  if (!res.ok) throw new Error(`Jupiter swap build failed: HTTP ${res.status}`);
  return await res.json();
}
