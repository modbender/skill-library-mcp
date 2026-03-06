import dotenv from 'dotenv';
import path from 'path';

dotenv.config({ path: path.resolve(__dirname, '../.env') });

function required(key: string): string {
  const val = process.env[key];
  if (!val) throw new Error(`Missing required env var: ${key}`);
  return val;
}

export const config = {
  // OpenRouter
  openrouterApiKey: required('OPENROUTER_API_KEY'),
  defaultModel: process.env.DEFAULT_MODEL || 'deepseek/deepseek-chat-v3-0324',

  // Energy Oracle
  electricityMapsApiKey: required('ELECTRICITY_MAPS_API_KEY'),

  // Base Mainnet
  baseRpcUrl: required('BASE_RPC_URL'),
  walletPrivateKey: required('WALLET_PRIVATE_KEY'),
  walletAddress: required('WALLET_ADDRESS'),

  // Server Identity
  nodeId: process.env.NODE_ID || 'local',
  nodeLocation: process.env.NODE_LOCATION || 'Local',
  nodeLat: parseFloat(process.env.NODE_LAT || '0'),
  nodeLon: parseFloat(process.env.NODE_LON || '0'),
  nodeGridZone: process.env.NODE_GRID_ZONE || 'unknown',

  // Gateway
  port: parseInt(process.env.PORT || '3402', 10),
  pricePerRequest: parseFloat(process.env.PRICE_PER_REQUEST || '0.004'),
  premiumPricePerRequest: parseFloat(process.env.PREMIUM_PRICE_PER_REQUEST || '0.008'),
  greenSurcharge: parseFloat(process.env.GREEN_SURCHARGE || '0.10'),

  // Peer Nodes
  peerNodes: (process.env.PEER_NODES || '').split(',').filter(Boolean),

  // EAS
  easContract: process.env.EAS_CONTRACT || '0x4200000000000000000000000000000000000021',
  easSchemaRegistry: process.env.EAS_SCHEMA_REGISTRY || '0x4200000000000000000000000000000000000020',
  attestationBatchSize: parseInt(process.env.ATTESTATION_BATCH_SIZE || '50', 10),

  // Stripe
  stripeSecretKey: process.env.STRIPE_SECRET_KEY || '',
  stripePublishableKey: process.env.STRIPE_PUBLISHABLE_KEY || '',
  stripeWebhookSecret: process.env.STRIPE_WEBHOOK_SECRET || '',

  // Dashboard
  dashboardPassword: process.env.DASHBOARD_PASSWORD || '',

  // ACP (Virtuals Agent Commerce Protocol)
  acpEnabled: process.env.ACP_ENABLED === 'true',
  acpWalletKey: process.env.ACP_WALLET_KEY || '',
  acpEntityId: parseInt(process.env.ACP_ENTITY_ID || '1', 10),
  acpAgentWallet: process.env.ACP_AGENT_WALLET || '',

  // Contract Addresses
  usdcAddress: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',

  // Node Definitions (static — all known nodes in the mesh)
  nodes: [
    {
      id: 'nbg1',
      name: 'Nuremberg',
      country: 'DE',
      lat: 49.4521,
      lon: 11.0767,
      gridZone: 'DE',
      electricityMapsZone: 'DE',
      ip: '46.225.135.67',
      energyCostPerKwh: 0.08, // fallback if oracle is down
    },
    {
      id: 'hel1',
      name: 'Helsinki',
      country: 'FI',
      lat: 60.1699,
      lon: 24.9384,
      gridZone: 'FI',
      electricityMapsZone: 'FI',
      ip: '89.167.47.71',
      energyCostPerKwh: 0.033, // fallback if oracle is down
    },
  ],
} as const;
