export { DriftProtocol } from './drift';
export type { FundingRate, DriftPosition, DriftMarket } from './drift';

export { JupiterPerps } from './jupiter-perps';
export type { JupiterFundingRate } from './jupiter-perps';

export { ZetaMarkets } from './zeta';
export type { ZetaFundingRate } from './zeta';

export { FlashTrade } from './flash';
export type { FlashFundingRate } from './flash';

export { MangoMarkets } from './mango';
export type { MangoFundingRate } from './mango';

export { GooseFX } from './goosefx';
export type { GooseFundingRate } from './goosefx';

export { ParclProtocol } from './parcl';
export type { ParclFundingRate } from './parcl';

// Unified funding rate type
export interface UnifiedFundingRate {
  protocol: string;
  market: string;
  fundingRate: number;
  fundingRateApy: number;
  longPayShort: boolean;
  price: number;
  openInterest: number;
}
