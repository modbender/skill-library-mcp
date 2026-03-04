export type Mode = "paper" | "live";

export type Candidate = {
  mint: string;
  sourceTags: string[];
};

export type DexMetrics = {
  mint: string;
  pairAddress?: string;
  liqUsd: number;
  vol5mUsd: number;
  tx5m: number;
  priceChange5mPct: number;
  pairAgeMin: number;
  priceImpactPct?: number;
  currentPriceUsd?: number;
};

export type TokenMeta = {
  mint: string;
  mintAuthorityActive: boolean | null;
  freezeAuthorityActive: boolean | null;
  singleHolderPct: number | null;
  top10HoldersPct: number | null;
};

export type WalletEvent = {
  wallet: string;
  side: "BUY" | "SELL";
  mint: string;
  ts: number;
  priceRefUsd?: number;
};

export type PositionTag = "COPY" | "AI";

export type Position = {
  mint: string;
  tag: PositionTag;
  entryPriceUsd: number;
  sizeUsd: number;
  openTs: number;
  stopLossUsd: number;
  tp1Usd: number;
  tp2Usd: number;
  trailingStopPct: number;
  remainingPct: number; // 0..100
  peakPriceUsd: number;
  tokenAmountRaw?: string; // raw units as string
  tokenDecimals?: number;
};

export type Decision = {
  action: "BUY" | "SELL" | "SKIP";
  reason: string;
  mint: string;
  tag?: PositionTag;
  sizeUsd?: number;
};
