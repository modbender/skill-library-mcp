import { config } from '../config';
import { getCostSurface, getEnergyForNode } from './energy-oracle';
import { RoutingMode, RoutingDecision, EnergyData } from '../types';

// Node health tracking
const nodeHealth: Map<string, { healthy: boolean; latencyMs: number; lastChecked: Date }> = new Map();

// Initialize all nodes as healthy
for (const node of config.nodes) {
  nodeHealth.set(node.id, { healthy: true, latencyMs: 0, lastChecked: new Date() });
}

export async function checkNodeHealth(nodeId: string, ip: string): Promise<void> {
  try {
    const start = Date.now();
    const res = await fetch(`http://${ip}:${config.port}/health`, {
      signal: AbortSignal.timeout(5000),
    });
    const latency = Date.now() - start;
    nodeHealth.set(nodeId, {
      healthy: res.ok,
      latencyMs: latency,
      lastChecked: new Date(),
    });
  } catch {
    nodeHealth.set(nodeId, {
      healthy: false,
      latencyMs: -1,
      lastChecked: new Date(),
    });
  }
}

export function routeRequest(mode: RoutingMode): RoutingDecision {
  const surface = getCostSurface();
  const candidates = config.nodes.filter(n => {
    const health = nodeHealth.get(n.id);
    return health?.healthy !== false; // include if healthy or unknown
  });

  if (candidates.length === 0) {
    // All nodes appear down — fall back to self
    const self = config.nodes.find(n => n.id === config.nodeId) || config.nodes[0];
    return buildDecision(self, mode, getEnergyForNode(self.id), 'all peers unavailable, routing to self');
  }

  let selected: typeof config.nodes[number];
  let reason: string;

  switch (mode) {
    case 'cheapest': {
      selected = candidates.reduce((best, node) => {
        const energy = surface.locations[node.id];
        const bestEnergy = surface.locations[best.id];
        if (!energy) return best;
        if (!bestEnergy) return node;
        return energy.pricePerKwh < bestEnergy.pricePerKwh ? node : best;
      }, candidates[0]);
      const energy = surface.locations[selected.id];
      reason = `lowest energy price: $${energy?.pricePerKwh.toFixed(4)}/kWh`;
      break;
    }

    case 'greenest': {
      selected = candidates.reduce((best, node) => {
        const energy = surface.locations[node.id];
        const bestEnergy = surface.locations[best.id];
        if (!energy) return best;
        if (!bestEnergy) return node;
        return energy.carbonIntensity < bestEnergy.carbonIntensity ? node : best;
      }, candidates[0]);
      const energy = surface.locations[selected.id];
      reason = `lowest carbon: ${energy?.carbonIntensity}g CO2/kWh`;
      break;
    }

    case 'balanced': {
      // Pareto-optimal: minimize (normalized_price * normalized_carbon)
      // Normalize both to 0-1 range across candidates
      const energies = candidates.map(n => ({
        node: n,
        energy: surface.locations[n.id],
      })).filter(e => e.energy);

      if (energies.length === 0) {
        selected = candidates[0];
        reason = 'no energy data, defaulting to first candidate';
        break;
      }

      const maxPrice = Math.max(...energies.map(e => e.energy.pricePerKwh));
      const minPrice = Math.min(...energies.map(e => e.energy.pricePerKwh));
      const maxCarbon = Math.max(...energies.map(e => e.energy.carbonIntensity));
      const minCarbon = Math.min(...energies.map(e => e.energy.carbonIntensity));

      const priceRange = maxPrice - minPrice || 1;
      const carbonRange = maxCarbon - minCarbon || 1;

      const scored = energies.map(e => {
        const normPrice = (e.energy.pricePerKwh - minPrice) / priceRange;
        const normCarbon = (e.energy.carbonIntensity - minCarbon) / carbonRange;
        // Lower score = better (both normalized to 0-1, 0 is best)
        const score = normPrice * 0.5 + normCarbon * 0.5;
        return { ...e, score };
      });

      scored.sort((a, b) => a.score - b.score);
      selected = scored[0].node;
      const bestEnergy = scored[0].energy;
      reason = `balanced: $${bestEnergy.pricePerKwh.toFixed(4)}/kWh + ${bestEnergy.carbonIntensity}g CO2/kWh (score: ${scored[0].score.toFixed(3)})`;
      break;
    }

    default:
      selected = candidates[0];
      reason = 'default';
  }

  return buildDecision(selected, mode, surface.locations[selected.id], reason);
}

function buildDecision(
  node: typeof config.nodes[number],
  mode: RoutingMode,
  energy: EnergyData | null | undefined,
  reason: string
): RoutingDecision {
  return {
    nodeId: node.id,
    nodeName: node.name,
    nodeIp: node.ip,
    mode,
    energyData: energy || {
      zone: node.gridZone,
      pricePerKwh: node.energyCostPerKwh,
      carbonIntensity: 0,
      renewablePercent: 0,
      curtailmentActive: false,
      source: 'fallback',
      lastUpdated: new Date(),
    },
    reason,
  };
}

export function isLocalNode(nodeId: string): boolean {
  return nodeId === config.nodeId;
}

export function getNodeHealth() {
  return Object.fromEntries(nodeHealth);
}
