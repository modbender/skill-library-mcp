// Energy Oracle Types

export interface EnergyData {
  zone: string;
  pricePerKwh: number;         // $/kWh (converted from €/MWh)
  carbonIntensity: number;     // gCO2eq/kWh
  renewablePercent: number;    // 0-100
  curtailmentActive: boolean;
  source: string;
  lastUpdated: Date;
}

export interface EnergyCostSurface {
  locations: Record<string, EnergyData>;
  cheapestLocation: string;
  greenestLocation: string;
  lastUpdated: Date;
}

// Spatial Router Types

export type RoutingMode = 'cheapest' | 'greenest' | 'balanced';

export interface NodeHealth {
  nodeId: string;
  healthy: boolean;
  latencyMs: number;
  lastChecked: Date;
}

export interface RoutingDecision {
  nodeId: string;
  nodeName: string;
  nodeIp: string;
  mode: RoutingMode;
  energyData: EnergyData;
  reason: string;
}

// Inference Types

export interface InferenceRequest {
  model?: string;
  messages: Array<{
    role: 'system' | 'user' | 'assistant';
    content: string;
  }>;
  mode?: RoutingMode;
  temperature?: number;
  max_tokens?: number;
  stream?: boolean;
}

export interface InferenceResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: Array<{
    index: number;
    message: {
      role: string;
      content: string;
    };
    finish_reason: string;
  }>;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  // Windfall extensions
  windfall: {
    node: string;
    location: string;
    mode: RoutingMode;
    energyPricePerKwh: number;
    carbonIntensityGCO2: number;
    renewablePercent: number;
    curtailmentActive: boolean;
    costUsd: number;
    cached?: boolean;
    engagement?: string;
    savedUsd?: number;
    attestationUid?: string;
    easscanUrl?: string;
  };
}

// Payment Types

export type PaymentMethod = 'eth_transfer' | 'free_tier' | 'api_key_balance' | 'cache_hit' | 'x402' | 'agent_session' | 'none';

export interface PaymentInfo {
  walletAddress: string;
  method: PaymentMethod;
  amountUsd: number;
  txHash?: string;
}

// Database Types

export interface RequestLog {
  id: string;
  timestamp: Date;
  walletAddress: string;
  nodeId: string;
  model: string;
  mode: RoutingMode;
  inputTokens: number;
  outputTokens: number;
  energyPricePerKwh: number;
  carbonIntensity: number;
  costUsd: number;
  paymentMethod: string;
  responseTimeMs: number;
  attestationUid?: string;
}

// Attestation Types

export interface AttestationData {
  timestamp: number;
  nodeId: string;
  lat: number;
  lon: number;
  energyPricePerKwh: number;
  carbonIntensity: number;
  curtailmentActive: boolean;
  model: string;
  responseHash: string;
  requestCount: number; // for batched attestations
}
