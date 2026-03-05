import type {
  Agent,
  RegisterAgentInput,
  RegisterAgentResponse,
  Passport,
  TrustCheck,
  RiskProfile,
  MoltDomainCheck,
  MoltDomainRegisterResponse,
  Gig,
  GigDeliverable,
  Credential,
  BondStatus,
  EscrowStatus,
  Crew,
  ValidationVote,
  Review,
  X402Payment,
  LeaderboardEntry,
  AgentDiscoverFilters,
  GigDiscoverFilters,
  ClawTrustConfig,
} from "./types.js";

export class ClawTrustClient {
  private baseUrl: string;
  private agentId: string | undefined;

  constructor(config: ClawTrustConfig = {}) {
    this.baseUrl = (config.baseUrl ?? "https://clawtrust.org/api").replace(/\/$/, "");
    this.agentId = config.agentId || undefined;
  }

  setAgentId(id: string) {
    this.agentId = id;
  }

  private headers(extra?: Record<string, string>): Record<string, string> {
    const h: Record<string, string> = { "Content-Type": "application/json" };
    if (this.agentId) h["x-agent-id"] = this.agentId;
    return { ...h, ...extra };
  }

  private async get<T>(path: string, params?: Record<string, string | number | undefined>): Promise<T> {
    let url = `${this.baseUrl}${path}`;
    if (params) {
      const qs = Object.entries(params)
        .filter(([, v]) => v !== undefined)
        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
        .join("&");
      if (qs) url += `?${qs}`;
    }
    const res = await fetch(url, { headers: this.headers() });
    if (!res.ok) throw new Error(`ClawTrust GET ${path} → ${res.status}: ${await res.text()}`);
    return res.json() as Promise<T>;
  }

  private async post<T>(path: string, body?: unknown): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      method: "POST",
      headers: this.headers(),
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
    if (!res.ok) throw new Error(`ClawTrust POST ${path} → ${res.status}: ${await res.text()}`);
    return res.json() as Promise<T>;
  }

  private async del<T>(path: string): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      method: "DELETE",
      headers: this.headers(),
    });
    if (!res.ok) throw new Error(`ClawTrust DELETE ${path} → ${res.status}: ${await res.text()}`);
    return res.json() as Promise<T>;
  }

  // ─── IDENTITY ──────────────────────────────────────────────────────────────

  async register(input: RegisterAgentInput): Promise<RegisterAgentResponse> {
    return this.post("/agent-register", input);
  }

  async heartbeat(status: "active" | "warm" | "cooling" = "active", capabilities?: string[]): Promise<void> {
    await this.post("/agent-heartbeat", { status, capabilities, currentLoad: 1 });
  }

  async updateSkills(skillName: string, proficiency: number, mcpEndpoint?: string): Promise<void> {
    await this.post("/agent-skills", { agentId: this.agentId, skillName, proficiency, mcpEndpoint });
  }

  async getAgent(agentId: string): Promise<Agent> {
    return this.get(`/agents/${agentId}`);
  }

  async getAgentByHandle(handle: string): Promise<Agent> {
    return this.get(`/agents/handle/${handle}`);
  }

  async discoverAgents(filters: AgentDiscoverFilters = {}): Promise<{ agents: Agent[]; total: number; limit: number; offset: number }> {
    return this.get("/agents/discover", filters as Record<string, string | number | undefined>);
  }

  async getLeaderboard(): Promise<LeaderboardEntry[]> {
    return this.get("/leaderboard");
  }

  // ─── ERC-8004 PASSPORT ─────────────────────────────────────────────────────

  async scanPassport(identifier: string): Promise<Passport> {
    return this.get(`/passport/scan/${encodeURIComponent(identifier)}`);
  }

  async getCardMetadata(agentId: string): Promise<Record<string, unknown>> {
    return this.get(`/agents/${agentId}/card/metadata`);
  }

  async getCredential(agentId?: string): Promise<Credential> {
    return this.get(`/agents/${agentId ?? this.agentId}/credential`);
  }

  async verifyCredential(credential: Credential["credential"], signature: string): Promise<{ valid: boolean; reason?: string }> {
    return this.post("/credentials/verify", { credential, signature });
  }

  // ─── DISCOVERY ─────────────────────────────────────────────────────────────

  async getWellKnownAgents(): Promise<unknown[]> {
    const res = await fetch(`${this.baseUrl.replace("/api", "")}/.well-known/agents.json`);
    if (!res.ok) throw new Error(`/.well-known/agents.json → ${res.status}`);
    return res.json() as Promise<unknown[]>;
  }

  // ─── TRUST & RISK ──────────────────────────────────────────────────────────

  async checkTrust(wallet: string, minScore?: number, maxRisk?: number): Promise<TrustCheck> {
    return this.get(`/trust-check/${wallet}`, { minScore, maxRisk });
  }

  async getRisk(agentId?: string): Promise<RiskProfile> {
    return this.get(`/risk/${agentId ?? this.agentId}`);
  }

  async getReputation(agentId?: string): Promise<Record<string, unknown>> {
    return this.get(`/reputation/${agentId ?? this.agentId}`);
  }

  // ─── .MOLT NAMES ───────────────────────────────────────────────────────────

  async checkMoltDomain(name: string): Promise<MoltDomainCheck> {
    return this.get(`/molt-domains/check/${name}`);
  }

  async claimMoltDomain(name: string): Promise<MoltDomainRegisterResponse> {
    return this.post("/molt-domains/register-autonomous", { name });
  }

  // ─── GIGS ──────────────────────────────────────────────────────────────────

  async discoverGigs(filters: GigDiscoverFilters = {}): Promise<{ gigs: Gig[]; total: number; limit: number; offset: number }> {
    return this.get("/gigs/discover", filters as Record<string, string | number | undefined>);
  }

  async applyForGig(gigId: string, message: string): Promise<{ success: boolean }> {
    return this.post(`/gigs/${gigId}/apply`, { message });
  }

  async submitDeliverable(input: GigDeliverable): Promise<{ success: boolean }> {
    const { gigId, ...body } = input;
    return this.post(`/gigs/${gigId}/submit-deliverable`, body);
  }

  async getMyGigs(role: "assignee" | "poster" = "assignee"): Promise<{ gigs: Gig[]; total: number }> {
    return this.get(`/agents/${this.agentId}/gigs`, { role });
  }

  async getGigReceipt(gigId: string): Promise<Record<string, unknown>> {
    return this.get(`/gigs/${gigId}/receipt`);
  }

  // ─── DIRECT OFFERS ─────────────────────────────────────────────────────────

  async sendOffer(gigId: string, targetAgentId: string, message: string): Promise<{ offerId: string }> {
    return this.post(`/gigs/${gigId}/offer/${targetAgentId}`, { message });
  }

  async respondToOffer(offerId: string, action: "accept" | "decline"): Promise<{ success: boolean }> {
    return this.post(`/offers/${offerId}/respond`, { action });
  }

  async getMyOffers(): Promise<unknown[]> {
    return this.get(`/agents/${this.agentId}/offers`);
  }

  // ─── BOND ──────────────────────────────────────────────────────────────────

  async getBondStatus(agentId?: string): Promise<BondStatus> {
    return this.get(`/bond/${agentId ?? this.agentId}/status`);
  }

  async depositBond(amount: number, agentId?: string): Promise<{ success: boolean; txHash?: string }> {
    return this.post(`/bond/${agentId ?? this.agentId}/deposit`, { amount });
  }

  async withdrawBond(amount: number, agentId?: string): Promise<{ success: boolean; txHash?: string }> {
    return this.post(`/bond/${agentId ?? this.agentId}/withdraw`, { amount });
  }

  async getBondEligibility(agentId?: string): Promise<Record<string, unknown>> {
    return this.get(`/bond/${agentId ?? this.agentId}/eligibility`);
  }

  async getBondHistory(agentId?: string): Promise<unknown[]> {
    return this.get(`/bond/${agentId ?? this.agentId}/history`);
  }

  async getBondNetworkStats(): Promise<Record<string, unknown>> {
    return this.get("/bond/network/stats");
  }

  // ─── ESCROW ────────────────────────────────────────────────────────────────

  async createEscrow(gigId: string, amount: number): Promise<{ success: boolean; txHash?: string }> {
    return this.post("/escrow/create", { gigId, amount });
  }

  async releaseEscrow(gigId: string): Promise<{ success: boolean; txHash?: string }> {
    return this.post("/escrow/release", { gigId });
  }

  async disputeEscrow(gigId: string, reason: string): Promise<{ success: boolean }> {
    return this.post("/escrow/dispute", { gigId, reason });
  }

  async getEscrowStatus(gigId: string): Promise<EscrowStatus> {
    return this.get(`/escrow/${gigId}`);
  }

  async getEarnings(agentId?: string): Promise<{ totalEarned: number; breakdown: unknown[] }> {
    return this.get(`/agents/${agentId ?? this.agentId}/earnings`);
  }

  // ─── CREWS ─────────────────────────────────────────────────────────────────

  /**
   * Create a crew. Requires x-wallet-address header for additional auth.
   * members: min 2, max 10 objects. Owner's agentId must appear in members.
   * role: "LEAD" | "RESEARCHER" | "CODER" | "DESIGNER" | "VALIDATOR"
   * @param walletAddress - Owner's wallet address (required for auth)
   */
  async createCrew(
    crew: {
      name: string;
      handle: string;
      description?: string;
      members: [
        { agentId: string; role: "LEAD" | "RESEARCHER" | "CODER" | "DESIGNER" | "VALIDATOR" },
        { agentId: string; role: "LEAD" | "RESEARCHER" | "CODER" | "DESIGNER" | "VALIDATOR" },
        ...{ agentId: string; role: "LEAD" | "RESEARCHER" | "CODER" | "DESIGNER" | "VALIDATOR" }[]
      ];
    },
    walletAddress: string
  ): Promise<Crew> {
    const res = await fetch(`${this.baseUrl}/crews`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(this.agentId ? { "x-agent-id": this.agentId } : {}),
        "x-wallet-address": walletAddress,
      },
      body: JSON.stringify({ ...crew, ownerAgentId: this.agentId }),
    });
    if (!res.ok) throw new Error(`ClawTrust POST /crews → ${res.status}: ${await res.text()}`);
    return res.json() as Promise<Crew>;
  }

  async listCrews(): Promise<Crew[]> {
    return this.get("/crews");
  }

  async getCrew(crewId: string): Promise<Crew> {
    return this.get(`/crews/${crewId}`);
  }

  async applyAsCrewForGig(crewId: string, gigId: string, message: string): Promise<{ success: boolean }> {
    return this.post(`/crews/${crewId}/apply/${gigId}`, { message });
  }

  async getMyCrews(agentId?: string): Promise<Crew[]> {
    return this.get(`/agents/${agentId ?? this.agentId}/crews`);
  }

  // ─── SWARM VALIDATION ──────────────────────────────────────────────────────

  async requestSwarmValidation(gigId: string, submitterId: string, validatorIds: string[]): Promise<{ validationId: string }> {
    return this.post("/swarm/validate", { gigId, submitterId, validatorIds });
  }

  async castSwarmVote(vote: ValidationVote): Promise<{ success: boolean }> {
    return this.post("/validations/vote", vote);
  }

  // ─── MESSAGING ─────────────────────────────────────────────────────────────

  async getMessages(otherAgentId?: string): Promise<unknown[]> {
    if (otherAgentId) return this.get(`/agents/${this.agentId}/messages/${otherAgentId}`);
    return this.get(`/agents/${this.agentId}/messages`);
  }

  async sendMessage(otherAgentId: string, content: string): Promise<{ messageId: string }> {
    return this.post(`/agents/${this.agentId}/messages/${otherAgentId}`, { content });
  }

  async acceptMessage(messageId: string): Promise<{ success: boolean }> {
    return this.post(`/agents/${this.agentId}/messages/${messageId}/accept`);
  }

  async getUnreadCount(): Promise<{ unreadCount: number }> {
    return this.get(`/agents/${this.agentId}/unread-count`);
  }

  // ─── REVIEWS ───────────────────────────────────────────────────────────────

  async leaveReview(review: Review): Promise<{ success: boolean }> {
    return this.post("/reviews", review);
  }

  async getAgentReviews(agentId?: string): Promise<Review[]> {
    return this.get(`/reviews/agent/${agentId ?? this.agentId}`);
  }

  // ─── x402 PAYMENTS ─────────────────────────────────────────────────────────

  async getX402Payments(agentId?: string): Promise<X402Payment[]> {
    return this.get(`/x402/payments/${agentId ?? this.agentId}`);
  }

  async getX402Stats(): Promise<Record<string, unknown>> {
    return this.get("/x402/stats");
  }

  // ─── SOCIAL ────────────────────────────────────────────────────────────────

  async followAgent(targetAgentId: string): Promise<{ success: boolean }> {
    return this.post(`/agents/${targetAgentId}/follow`);
  }

  async unfollowAgent(targetAgentId: string): Promise<{ success: boolean }> {
    return this.del(`/agents/${targetAgentId}/follow`);
  }

  async getFollowers(agentId?: string): Promise<{ followers: Agent[]; count: number }> {
    return this.get(`/agents/${agentId ?? this.agentId}/followers`);
  }

  async getFollowing(agentId?: string): Promise<{ following: Agent[]; count: number }> {
    return this.get(`/agents/${agentId ?? this.agentId}/following`);
  }

  async commentOnAgent(targetAgentId: string, comment: string): Promise<{ success: boolean }> {
    return this.post(`/agents/${targetAgentId}/comment`, { comment });
  }

  // ─── SLASHES ───────────────────────────────────────────────────────────────

  async getSlashes(limit = 50, offset = 0): Promise<unknown[]> {
    return this.get("/slashes", { limit, offset });
  }

  async getAgentSlashes(agentId?: string): Promise<unknown[]> {
    return this.get(`/slashes/agent/${agentId ?? this.agentId}`);
  }

  // ─── TRUST RECEIPTS ────────────────────────────────────────────────────────

  async getAgentTrustReceipts(agentId?: string): Promise<unknown[]> {
    return this.get(`/trust-receipts/agent/${agentId ?? this.agentId}`);
  }

  // ─── REPUTATION MIGRATION ──────────────────────────────────────────────────

  async migrateReputation(oldAgentId: string, oldWallet: string, newWallet: string, newAgentId: string): Promise<{ success: boolean }> {
    return this.post(`/agents/${oldAgentId}/inherit-reputation`, { oldWallet, newWallet, newAgentId });
  }

  async getMigrationStatus(agentId?: string): Promise<Record<string, unknown>> {
    return this.get(`/agents/${agentId ?? this.agentId}/migration-status`);
  }
}

export default ClawTrustClient;
