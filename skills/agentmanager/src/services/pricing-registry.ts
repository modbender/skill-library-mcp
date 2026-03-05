import type { ModelTier, TierPriceTable } from './model-tier.js';
import { defaultTierPricePerToken } from './model-tier.js';

export type PricingPolicy = {
  tierPricePerToken: TierPriceTable;
  maxTierCap: ModelTier;
};

export class PricingRegistry {
  private readonly policies = new Map<string, PricingPolicy>();

  constructor() {
    this.policies.set('anonymous', {
      tierPricePerToken: defaultTierPricePerToken,
      maxTierCap: 'premium'
    });
  }

  set(tokenOwner: string, policy: PricingPolicy): void {
    this.policies.set(tokenOwner, policy);
  }

  get(tokenOwner: string): PricingPolicy {
    return this.policies.get(tokenOwner) ?? this.policies.get('anonymous')!;
  }
}
