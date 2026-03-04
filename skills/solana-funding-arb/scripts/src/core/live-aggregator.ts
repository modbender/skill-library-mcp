/**
 * Live Aggregator
 * 
 * Aggregates funding rates from all live protocol integrations
 */

import { DriftLive } from '../protocols/drift-live';
import { MangoLive } from '../protocols/mango-live';
import { ZetaLive } from '../protocols/zeta-live';
import { JupiterLive } from '../protocols/jupiter-live';
import { logger } from '../utils/logger';

export interface UnifiedLiveRate {
  protocol: string;
  market: string;
  fundingRate: number;
  fundingRateApy: number;
  longPayShort: boolean;
  price: number;
  openInterest: number;
}

export class LiveAggregator {
  private drift: DriftLive;
  private mango: MangoLive;
  private zeta: ZetaLive;
  private jupiter: JupiterLive;
  private initialized = false;

  constructor(rpcUrl: string) {
    this.drift = new DriftLive(rpcUrl);
    this.mango = new MangoLive(rpcUrl);
    this.zeta = new ZetaLive(rpcUrl);
    this.jupiter = new JupiterLive(rpcUrl);
  }

  async initialize(): Promise<void> {
    if (this.initialized) return;

    logger.info('Initializing live aggregator...');
    
    // Initialize all protocols in parallel
    const results = await Promise.allSettled([
      this.drift.initialize(),
      this.mango.initialize(),
      this.zeta.initialize(),
    ]);

    results.forEach((result, i) => {
      const name = ['Drift', 'Mango', 'Zeta'][i];
      if (result.status === 'rejected') {
        logger.warn(`${name} initialization failed: ${result.reason}`);
      }
    });

    this.initialized = true;
    logger.info('Live aggregator ready');
  }

  async getAllFundingRates(): Promise<UnifiedLiveRate[]> {
    if (!this.initialized) {
      await this.initialize();
    }

    // Fetch from all protocols in parallel
    const [driftRates, mangoRates, zetaRates, jupiterRates] = await Promise.all([
      this.drift.getFundingRates().catch(() => []),
      this.mango.getFundingRates().catch(() => []),
      this.zeta.getFundingRates().catch(() => []),
      this.jupiter.getFundingRates().catch(() => []),
    ]);

    const allRates: UnifiedLiveRate[] = [
      ...driftRates.map(r => ({
        protocol: 'Drift',
        market: `DRIFT:${r.market}`,
        fundingRate: r.fundingRate,
        fundingRateApy: r.fundingRateApy,
        longPayShort: r.longPayShort,
        price: r.oraclePrice,
        openInterest: r.openInterest
      })),
      ...mangoRates.map(r => ({
        protocol: 'Mango',
        ...r
      })),
      ...zetaRates.map(r => ({
        protocol: 'Zeta',
        ...r
      })),
      ...jupiterRates.map(r => ({
        protocol: 'Jupiter',
        ...r
      })),
    ];

    // Sort by absolute APY (highest opportunities first)
    allRates.sort((a, b) => Math.abs(b.fundingRateApy) - Math.abs(a.fundingRateApy));

    return allRates;
  }

  async disconnect(): Promise<void> {
    await this.drift.disconnect();
    await this.zeta.disconnect();
    this.initialized = false;
  }
}
