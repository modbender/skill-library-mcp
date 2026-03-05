import { config } from '../config';
import { EnergyData, EnergyCostSurface } from '../types';

const POLL_INTERVAL_MS = 5 * 60 * 1000; // 5 minutes
const EUR_TO_USD = 1.05; // approximate, updated periodically
const MWH_TO_KWH = 1000;

let costSurface: EnergyCostSurface = {
  locations: {},
  cheapestLocation: '',
  greenestLocation: '',
  lastUpdated: new Date(0),
};

// Electricity Maps API v3
// Docs: https://docs.electricitymaps.com/
async function fetchElectricityMaps(zone: string): Promise<EnergyData | null> {
  try {
    const [powerRes, carbonRes] = await Promise.all([
      fetch(`https://api.electricitymap.org/v3/power-breakdown/latest?zone=${zone}`, {
        headers: { 'auth-token': config.electricityMapsApiKey },
      }),
      fetch(`https://api.electricitymap.org/v3/carbon-intensity/latest?zone=${zone}`, {
        headers: { 'auth-token': config.electricityMapsApiKey },
      }),
    ]);

    if (!powerRes.ok || !carbonRes.ok) {
      console.error(`[oracle] Electricity Maps error for ${zone}: power=${powerRes.status}, carbon=${carbonRes.status}`);
      return null;
    }

    const power = await powerRes.json() as any;
    const carbon = await carbonRes.json() as any;

    // Calculate renewable percentage from power breakdown
    const renewableSources = ['wind', 'solar', 'hydro', 'biomass', 'geothermal'];
    let renewableTotal = 0;
    let totalPower = 0;

    if (power.powerConsumptionBreakdown) {
      for (const [source, value] of Object.entries(power.powerConsumptionBreakdown)) {
        const numVal = value as number;
        if (numVal > 0) {
          totalPower += numVal;
          if (renewableSources.some(r => source.toLowerCase().includes(r))) {
            renewableTotal += numVal;
          }
        }
      }
    }

    const renewablePercent = totalPower > 0 ? (renewableTotal / totalPower) * 100 : 0;

    // Estimate price from zone (Electricity Maps free tier doesn't include price)
    // Use known grid prices as baseline, adjust by renewable % as proxy for spot price
    const basePrices: Record<string, number> = {
      'DE': 0.08,  // Germany: ~€80/MWh avg
      'FI': 0.033, // Finland: ~€33/MWh avg (Nordic hydro)
    };
    const basePrice = basePrices[zone] || 0.06;

    // When renewable % is very high (>80%), prices tend to be lower (potential curtailment)
    // This is a rough heuristic until we add spot price APIs
    let priceMultiplier = 1.0;
    if (renewablePercent > 90) priceMultiplier = 0.3; // very likely curtailment
    else if (renewablePercent > 80) priceMultiplier = 0.5;
    else if (renewablePercent > 70) priceMultiplier = 0.7;

    const estimatedPrice = basePrice * priceMultiplier;

    // Curtailment heuristic: very high renewable + low carbon = likely curtailment
    const curtailmentActive = renewablePercent > 85 && (carbon.carbonIntensity || 999) < 50;

    return {
      zone,
      pricePerKwh: estimatedPrice,
      carbonIntensity: carbon.carbonIntensity || 0,
      renewablePercent: Math.round(renewablePercent * 10) / 10,
      curtailmentActive,
      source: 'electricity_maps',
      lastUpdated: new Date(),
    };
  } catch (err) {
    console.error(`[oracle] Failed to fetch Electricity Maps for ${zone}:`, err);
    return null;
  }
}

// Fallback: use static data if API fails
function getFallback(zone: string): EnergyData {
  const fallbacks: Record<string, Partial<EnergyData>> = {
    'DE': { pricePerKwh: 0.08, carbonIntensity: 350, renewablePercent: 50 },
    'FI': { pricePerKwh: 0.033, carbonIntensity: 90, renewablePercent: 75 },
  };
  const fb = fallbacks[zone] || { pricePerKwh: 0.06, carbonIntensity: 200, renewablePercent: 40 };
  return {
    zone,
    pricePerKwh: fb.pricePerKwh!,
    carbonIntensity: fb.carbonIntensity!,
    renewablePercent: fb.renewablePercent!,
    curtailmentActive: false,
    source: 'fallback',
    lastUpdated: new Date(),
  };
}

export async function pollEnergyData(): Promise<void> {
  console.log('[oracle] Polling energy data...');

  const zones = config.nodes.map(n => ({
    nodeId: n.id,
    zone: n.electricityMapsZone,
  }));

  const results = await Promise.all(
    zones.map(async ({ nodeId, zone }) => {
      const data = await fetchElectricityMaps(zone);
      return { nodeId, data: data || getFallback(zone) };
    })
  );

  const locations: Record<string, EnergyData> = {};
  let cheapest = { id: '', price: Infinity };
  let greenest = { id: '', carbon: Infinity };

  for (const { nodeId, data } of results) {
    locations[nodeId] = data;

    if (data.pricePerKwh < cheapest.price) {
      cheapest = { id: nodeId, price: data.pricePerKwh };
    }
    if (data.carbonIntensity < greenest.carbon) {
      greenest = { id: nodeId, carbon: data.carbonIntensity };
    }
  }

  costSurface = {
    locations,
    cheapestLocation: cheapest.id,
    greenestLocation: greenest.id,
    lastUpdated: new Date(),
  };

  // Log summary
  for (const [nodeId, data] of Object.entries(locations)) {
    const flags = [];
    if (nodeId === costSurface.cheapestLocation) flags.push('CHEAPEST');
    if (nodeId === costSurface.greenestLocation) flags.push('GREENEST');
    if (data.curtailmentActive) flags.push('CURTAILMENT');
    const flagStr = flags.length > 0 ? ` [${flags.join(', ')}]` : '';

    console.log(
      `[oracle] ${nodeId}: $${data.pricePerKwh.toFixed(4)}/kWh | ` +
      `${data.carbonIntensity}g CO2/kWh | ` +
      `${data.renewablePercent}% renewable | ` +
      `src=${data.source}${flagStr}`
    );
  }
}

export function getCostSurface(): EnergyCostSurface {
  return costSurface;
}

export function getEnergyForNode(nodeId: string): EnergyData | null {
  return costSurface.locations[nodeId] || null;
}

export function isOracleHealthy(): boolean {
  const staleThreshold = 15 * 60 * 1000; // 15 minutes
  return (Date.now() - costSurface.lastUpdated.getTime()) < staleThreshold;
}

let pollTimer: ReturnType<typeof setInterval> | null = null;

export function startOracle(): void {
  console.log('[oracle] Starting energy oracle (polling every 5 min)...');
  // Poll immediately, then on interval
  pollEnergyData();
  pollTimer = setInterval(pollEnergyData, POLL_INTERVAL_MS);
}

export function stopOracle(): void {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

// Run standalone for testing: tsx src/services/energy-oracle.ts
if (require.main === module) {
  console.log('=== Windfall Energy Oracle — Standalone Test ===\n');
  pollEnergyData().then(() => {
    console.log('\n=== Cost Surface ===');
    const surface = getCostSurface();
    console.log(`Cheapest: ${surface.cheapestLocation}`);
    console.log(`Greenest: ${surface.greenestLocation}`);
    console.log(`Updated: ${surface.lastUpdated.toISOString()}`);
  });
}
