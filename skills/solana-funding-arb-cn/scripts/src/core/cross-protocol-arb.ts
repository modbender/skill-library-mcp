/**
 * Cross-Protocol Arbitrage Detector
 * 
 * Finds funding rate arbitrage opportunities across different protocols.
 * Example: SOL-PERP has +0.05%/hr on Drift but -0.02%/hr on Jupiter
 * → Long on Jupiter, Short on Drift = collect both funding rates
 */

export interface ArbOpportunity {
  asset: string;
  longProtocol: string;
  longMarket: string;
  longRate: number;
  shortProtocol: string;
  shortMarket: string;
  shortRate: number;
  netApy: number;  // Combined APY from both sides
  spreadApy: number;  // Difference in APY
  riskLevel: 'low' | 'medium' | 'high';
}

export interface UnifiedRate {
  protocol: string;
  market: string;
  fundingRate: number;
  fundingRateApy: number;
  longPayShort: boolean;
  price: number;
}

/**
 * Find cross-protocol arbitrage opportunities
 */
export function findArbOpportunities(rates: UnifiedRate[]): ArbOpportunity[] {
  const opportunities: ArbOpportunity[] = [];
  
  // Group rates by base asset
  const assetGroups = groupByAsset(rates);
  
  for (const [asset, protocols] of Object.entries(assetGroups)) {
    if (protocols.length < 2) continue;
    
    // Sort by funding rate (highest to lowest)
    protocols.sort((a, b) => b.fundingRate - a.fundingRate);
    
    // Find opportunities: short where funding is highest, long where lowest
    const highest = protocols[0];
    const lowest = protocols[protocols.length - 1];
    
    // Only consider if there's a meaningful spread
    const spreadApy = Math.abs(highest.fundingRateApy - lowest.fundingRateApy);
    if (spreadApy < 50) continue; // Min 50% APY spread
    
    // Calculate net APY
    // If highest is positive (longs pay), we short there and collect
    // If lowest is negative (shorts pay), we long there and collect
    let netApy = 0;
    
    if (highest.longPayShort) {
      // Longs pay shorts on highest protocol → we SHORT and collect
      netApy += Math.abs(highest.fundingRateApy);
    } else {
      // Shorts pay longs → we SHORT and pay (reduce profit)
      netApy -= Math.abs(highest.fundingRateApy);
    }
    
    if (!lowest.longPayShort) {
      // Shorts pay longs on lowest protocol → we LONG and collect
      netApy += Math.abs(lowest.fundingRateApy);
    } else {
      // Longs pay shorts → we LONG and pay (reduce profit)
      netApy -= Math.abs(lowest.fundingRateApy);
    }
    
    // Only add if net APY is positive
    if (netApy > 0) {
      opportunities.push({
        asset,
        longProtocol: lowest.protocol,
        longMarket: lowest.market,
        longRate: lowest.fundingRate,
        shortProtocol: highest.protocol,
        shortMarket: highest.market,
        shortRate: highest.fundingRate,
        netApy,
        spreadApy,
        riskLevel: getRiskLevel(highest, lowest)
      });
    }
  }
  
  // Sort by net APY (highest first)
  opportunities.sort((a, b) => b.netApy - a.netApy);
  
  return opportunities;
}

/**
 * Group rates by base asset
 */
function groupByAsset(rates: UnifiedRate[]): Record<string, UnifiedRate[]> {
  const groups: Record<string, UnifiedRate[]> = {};
  
  for (const rate of rates) {
    // Extract base asset from market name
    // e.g., "DRIFT:SOL-PERP" → "SOL"
    const asset = extractAsset(rate.market);
    if (!asset) continue;
    
    if (!groups[asset]) {
      groups[asset] = [];
    }
    groups[asset].push(rate);
  }
  
  return groups;
}

/**
 * Extract base asset from market name
 */
function extractAsset(market: string): string | null {
  // Handle formats like "DRIFT:SOL-PERP", "JUP:SOL-PERP", "SOL-PERP"
  const match = market.match(/(?:^|\:)([A-Z]+)-PERP$/);
  return match ? match[1] : null;
}

/**
 * Determine risk level based on protocol liquidity and rate stability
 */
function getRiskLevel(high: UnifiedRate, low: UnifiedRate): 'low' | 'medium' | 'high' {
  const majorProtocols = ['Drift', 'Jupiter', 'Mango'];
  
  const highIsMajor = majorProtocols.includes(high.protocol);
  const lowIsMajor = majorProtocols.includes(low.protocol);
  
  if (highIsMajor && lowIsMajor) return 'low';
  if (highIsMajor || lowIsMajor) return 'medium';
  return 'high';
}

/**
 * Format opportunity for display
 */
export function formatOpportunity(opp: ArbOpportunity): string {
  const emoji = opp.riskLevel === 'low' ? '🟢' : opp.riskLevel === 'medium' ? '🟡' : '🔴';
  
  return `${emoji} ${opp.asset}: ${opp.netApy.toFixed(1)}% APY
   Long ${opp.longProtocol} (${(opp.longRate * 100).toFixed(4)}%/hr)
   Short ${opp.shortProtocol} (${(opp.shortRate * 100).toFixed(4)}%/hr)
   Spread: ${opp.spreadApy.toFixed(1)}% | Risk: ${opp.riskLevel}`;
}
