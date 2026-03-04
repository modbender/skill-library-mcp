export interface Agent {
  id: string;
  handle: string;
  walletAddress: string;
  bio?: string;
  skills: string[];
  fusedScore: number;
  onChainScore: number;
  moltbookKarma: number;
  tier: string;
  erc8004TokenId?: string;
  moltDomain?: string;
  isVerified: boolean;
  autonomyStatus: "active" | "warm" | "cooling" | "dormant" | "inactive";
  bondTier: "UNBONDED" | "LOW_BOND" | "MODERATE_BOND" | "HIGH_BOND";
  totalBonded: number;
  availableBond: number;
  lockedBond: number;
  riskIndex: number;
  totalGigsCompleted: number;
  totalEarned: number;
  lastHeartbeat?: string;
  registeredAt: string;
}

export interface RegisterAgentInput {
  handle: string;
  skills: Array<{ name: string; desc?: string }>;
  bio?: string;
  walletAddress?: string;
  mcpEndpoint?: string;
  telegramHandle?: string;
}

export interface RegisterAgentResponse {
  agent: Agent;
  message?: string;
}

export interface Passport {
  valid: boolean;
  standard: "ERC-8004";
  chain: "base-sepolia";
  onChain: boolean;
  contract: {
    clawCardNFT: string;
    tokenId: string;
    basescanUrl: string;
  };
  identity: {
    wallet: string;
    moltDomain?: string;
    skills: string[];
    active: boolean;
  };
  reputation: {
    fusedScore: number;
    tier: string;
    riskLevel: "low" | "medium" | "high";
  };
  trust: {
    verdict: "TRUSTED" | "CAUTION" | "UNTRUSTED";
    hireRecommendation: boolean;
    bondStatus: string;
  };
  scanUrl: string;
  metadataUri: string;
}

export interface TrustCheck {
  hireable: boolean;
  score: number;
  confidence: number;
  reason: string;
  riskIndex: number;
  bonded: boolean;
  bondTier: "UNBONDED" | "LOW_BOND" | "MODERATE_BOND" | "HIGH_BOND";
  availableBond: number;
  performanceScore: number;
  bondReliability: number;
  cleanStreakDays: number;
  fusedScoreVersion: string;
  weights: {
    onChain: number;
    moltbook: number;
    performance: number;
    bondReliability: number;
  };
  details: {
    wallet: string;
    fusedScore: number;
    tier: string;
    badges: string[];
    hasActiveDisputes: boolean;
    lastActive: string;
    rank: string;
    riskLevel: "low" | "medium" | "high";
    scoreComponents: Record<string, number>;
    followerQuality: {
      avgScore: number;
      totalFollowers: number;
      highTierFollowers: number;
    };
  };
}

export interface RiskProfile {
  agentId: string;
  riskIndex: number;
  riskLevel: "low" | "medium" | "high";
  breakdown: {
    slashComponent: number;
    failedGigComponent: number;
    disputeComponent: number;
    inactivityComponent: number;
    bondDepletionComponent: number;
    cleanStreakBonus: number;
  };
  cleanStreakDays: number;
  feeMultiplier: number;
}

export interface MoltDomainCheck {
  available: boolean;
  name: string;
  display: string;
}

export interface MoltDomainRegisterResponse {
  success: boolean;
  moltDomain: string;
  foundingMoltNumber?: number;
  profileUrl: string;
  onChain: boolean;
  txHash?: string;
}

export interface Gig {
  id: string;
  title: string;
  description: string;
  budget: number;
  chain: "BASE_SEPOLIA" | "SOL_DEVNET";
  skills: string[];
  status: "open" | "in_progress" | "completed" | "disputed";
  posterId?: string;
  assigneeId?: string;
  createdAt: string;
}

export interface GigApplication {
  gigId: string;
  agentId: string;
  message: string;
}

export interface GigDeliverable {
  gigId: string;
  deliverableUrl: string;
  deliverableNote?: string;
  requestValidation?: boolean;
}

export interface Credential {
  credential: {
    agentId: string;
    handle: string;
    fusedScore: number;
    tier: string;
    bondTier: string;
    riskIndex: number;
    isVerified: boolean;
    activityStatus: string;
    issuedAt: string;
    expiresAt: string;
    issuer: string;
    version: string;
  };
  signature: string;
  signatureAlgorithm: string;
  verifyEndpoint: string;
}

export interface BondStatus {
  totalBonded: number;
  availableBond: number;
  lockedBond: number;
  bondTier: "UNBONDED" | "LOW_BOND" | "MODERATE_BOND" | "HIGH_BOND";
  bondReliability: number;
  bondWalletId?: string | null;
  bondWalletAddress?: string | null;
  lastSlashAt?: string | null;
  circleConfigured: boolean;
}

export interface EscrowStatus {
  gigId: string;
  amount: number;
  status: "pending" | "funded" | "released" | "disputed" | "refunded";
  chain: string;
  txHash?: string;
}

export interface CrewMember {
  id: string;
  crewId: string;
  agentId: string;
  role: "LEAD" | "RESEARCHER" | "CODER" | "DESIGNER" | "VALIDATOR";
  joinedAt: string;
  agent?: {
    id: string;
    handle: string;
    avatar?: string | null;
    fusedScore: number;
  };
}

export interface Crew {
  id: string;
  name: string;
  handle: string;
  description?: string;
  ownerWallet: string;
  fusedScore: number;
  bondPool: number;
  gigsCompleted: number;
  totalEarned: number;
  tier: string;
  members: CrewMember[];
  memberCount: number;
  createdAt: string;
}

export interface ValidationVote {
  validationId: string;
  voterId: string;
  voterWallet: string;
  vote: "approve" | "reject";
  reasoning?: string;
}

export interface Review {
  gigId: string;
  reviewerId: string;
  revieweeId: string;
  rating: 1 | 2 | 3 | 4 | 5;
  comment?: string;
}

export interface X402Payment {
  endpoint: string;
  amount: number;
  currency: string;
  timestamp: string;
  txHash?: string;
}

export interface LeaderboardEntry {
  id: string;
  handle: string;
  fusedScore: number;
  tier: string;
  moltDomain?: string;
  erc8004TokenId?: string;
  totalGigsCompleted: number;
  isVerified: boolean;
}

export interface AgentDiscoverFilters {
  skills?: string;
  minScore?: number;
  maxRisk?: number;
  minBond?: number;
  activityStatus?: "active" | "warm" | "cooling" | "dormant";
  sortBy?: "score_desc" | "score_asc" | "risk_asc" | "newest";
  limit?: number;
  offset?: number;
}

export interface GigDiscoverFilters {
  skills?: string;
  minBudget?: number;
  maxBudget?: number;
  chain?: "BASE_SEPOLIA";
  sortBy?: "newest" | "budget_high" | "budget_low";
  limit?: number;
  offset?: number;
}

export interface ClawTrustConfig {
  baseUrl?: string;
  agentId?: string;
}
