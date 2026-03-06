import { ContractAddresses } from "@agentxpay/sdk";

// ─── Skill Configuration ───────────────────────────────────

export interface AgentXPaySkillConfig {
  /** Monad RPC URL */
  rpcUrl: string;
  /** Agent private key (or injected via secure vault) */
  privateKey: string;
  /** Contract addresses for all AgentXPay modules */
  contracts: ContractAddresses;
  /** Network identifier */
  network?: "local" | "testnet" | "mainnet";
}

// ─── Tool Parameter Types ──────────────────────────────────

export interface DiscoverServicesParams {
  /** Filter by service category (e.g., "LLM", "Image", "Code") */
  category?: string;
  /** Maximum price per call in MON (e.g., "0.05") */
  maxPrice?: string;
}

export interface PayAndCallParams {
  /** AI service endpoint URL */
  url: string;
  /** HTTP method */
  method: "GET" | "POST" | "PUT" | "DELETE";
  /** Request body (will be JSON.stringify'd) */
  body?: Record<string, unknown>;
  /** Additional HTTP headers */
  headers?: Record<string, string>;
  /** On-chain service ID (from discoverServices). Validates against provider's 402 serviceId — mismatch throws an error. */
  serviceId?: string;
  /** On-chain pricePerCall in wei (from discoverServices). Validates against provider's 402 amount. */
  pricePerCall?: string;
}

export interface ManageWalletParams {
  /** Action to perform */
  action: "create" | "fund" | "get_info" | "set_limit" | "authorize_agent" | "revoke_agent" | "pay";
  /** Daily spending limit in MON (for create / set_limit) */
  dailyLimit?: string;
  /** Amount in MON (for fund / pay) */
  amount?: string;
  /** Wallet address (required for fund / get_info / set_limit / authorize_agent / revoke_agent / pay) */
  walletAddress?: string;
  /** Agent address to authorize or revoke */
  agentAddress?: string;
  /** On-chain service ID (for pay) */
  serviceId?: number;
}

export interface SubscribeServiceParams {
  /** On-chain service ID */
  serviceId: number;
  /** Subscription plan ID (auto-selects first plan if omitted) */
  planId?: number;
}

export interface CreateEscrowParams {
  /** On-chain service ID */
  serviceId: number;
  /** Escrow amount in MON */
  amount: string;
  /** Deadline in days from now */
  deadlineDays: number;
  /** Job description */
  description: string;
}

export interface SmartCallParams {
  /** Task description (e.g., "Generate a cyberpunk cat image") */
  task: string;
  /** Filter by category */
  category?: string;
  /** Maximum budget in MON */
  maxBudget?: string;
  /** Prefer the cheapest matching service */
  preferCheapest?: boolean;
}

// ─── Tool Return Types ─────────────────────────────────────

export interface ServiceInfo {
  id: string;
  provider: string;
  name: string;
  description: string;
  endpoint: string;
  category: string;
  pricePerCall: string; // MON
  isActive: boolean;
}

export interface DiscoverServicesResult {
  services: ServiceInfo[];
  totalCount: number;
}

export interface PayAndCallResult {
  status: number;
  data: unknown;
  payment: {
    txHash: string;
    amount: string; // MON
    serviceId: string;
  } | null;
  latencyMs: number;
}

export interface WalletInfo {
  walletAddress: string;
  balance: string;     // MON
  dailyLimit: string;  // MON
  dailySpent: string;  // MON
  remainingAllowance: string; // MON
  txHash?: string;
  /** Authorized agent address (for authorize_agent / revoke_agent) */
  agentAddress?: string;
  /** Whether the agent is currently authorized */
  isAuthorized?: boolean;
  /** Payment details (for pay action) */
  paymentServiceId?: string;
  paymentAmount?: string;
}

export interface SubscribeResult {
  subscriptionId: string;
  serviceId: string;
  planName: string;
  price: string;     // MON
  txHash: string;
  hasAccess: boolean;
}

export interface EscrowResult {
  escrowId: string;
  serviceId: string;
  amount: string;    // MON
  deadline: string;  // ISO date
  txHash: string;
}

export interface SmartCallResult {
  selectedService: {
    id: string;
    name: string;
    price: string;   // MON
    category: string;
  };
  response: unknown;
  payment: {
    txHash: string;
    amount: string;
  } | null;
  latencyMs: number;
}

// ─── Tool Definition (for Function Calling / MCP) ──────────

export interface ToolDefinition {
  name: string;
  description: string;
  parameters: Record<string, unknown>; // JSON Schema
}

// ─── Skill Metadata ────────────────────────────────────────

export interface SkillMetadata {
  name: string;
  version: string;
  description: string;
  author: string;
  chain: string;
  protocol: string;
  capabilities: string[];
  tools: ToolDefinition[];
}
