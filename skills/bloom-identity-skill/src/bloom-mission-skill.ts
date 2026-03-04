/**
 * Bloom Mission Skill
 *
 * OpenClaw skill that:
 * 1. Pings agent heartbeat (lottery eligibility)
 * 2. Fetches active missions from discover API
 * 3. Fetches agent taste profile for personalized matching
 * 4. Scores + ranks missions by taste overlap, quality, and freshness
 * 5. Supports mission submission + status checking
 */

import 'dotenv/config';

const BLOOM_API_BASE = process.env.BLOOM_API_URL || 'https://api.bloomprotocol.ai';

// =====================================================
// Interfaces — matches backend discover response shape
// =====================================================

interface Mission {
  missionId: string;
  tweetId: string;
  title: string;
  description: string | null;
  status: 'live' | 'ended';
  postedBy: string;
  originalPostUrl: string;
  startTime: string;
  endTime: string | null;
  totalSubmissions: number;
  criteria: any;
  categories: string[];
  rewards: Array<{
    name: string;
    amount: number;
    icon: string;
  }>;
  // Scoring fields (added by personalization)
  matchScore?: number;
}

interface TasteProfile {
  agentUserId: number;
  personalityType: string;
  mainCategories: string[];
  subCategories: string[];
  dimensions?: {
    conviction: number;
    intuition: number;
    contribution: number;
  };
}

interface HeartbeatResponse {
  success: boolean;
  data: {
    registered: boolean;
    streak: number;
    lotteryEligible: boolean;
    nextHeartbeatBy: string;
  };
}

interface DiscoverResponse {
  missions: Mission[];
  total: number;
}

interface SubmissionResult {
  success: boolean;
  data: {
    submissionId: string;
    recordId: number;
    missionId: string;
    status: string;
    message: string;
  } | null;
  message?: string;
}

interface SubmissionStatusResult {
  success: boolean;
  data: {
    agentId: string;
    total: number;
    submissions: Array<{
      recordId: number;
      missionId: string;
      submissionId: string | null;
      status: string;
      dropsStatus: any;
      tokenStatus: any;
      submittedAt: string;
    }>;
  } | null;
}

export interface MissionSkillResult {
  success: boolean;
  heartbeat: {
    streak: number;
    lotteryEligible: boolean;
  } | null;
  missions: Mission[];
  formattedOutput: string;
  error?: string;
}

export class BloomMissionSkill {
  private apiBase: string;

  constructor(apiBase?: string) {
    this.apiBase = apiBase || BLOOM_API_BASE;
  }

  /**
   * Execute the mission skill
   * @param walletAddress - Agent wallet address for heartbeat
   * @param context - Optional conversation context for personalization
   * @param agentUserId - Optional agent user ID for taste-profile matching
   */
  async execute(
    walletAddress: string,
    context?: string,
    agentUserId?: number,
  ): Promise<MissionSkillResult> {
    // Run heartbeat, missions fetch, and taste profile in parallel
    const promises: [
      Promise<{ streak: number; lotteryEligible: boolean }>,
      Promise<Mission[]>,
      Promise<TasteProfile | null>,
    ] = [
      this.pingHeartbeat(walletAddress),
      this.fetchMissions(),
      agentUserId ? this.fetchTasteProfile(agentUserId) : Promise.resolve(null),
    ];

    const [heartbeatResult, missionsResult, tasteResult] = await Promise.allSettled(promises);

    const heartbeat = heartbeatResult.status === 'fulfilled' ? heartbeatResult.value : null;
    const missions = missionsResult.status === 'fulfilled' ? missionsResult.value : [];
    const tasteProfile = tasteResult.status === 'fulfilled' ? tasteResult.value : null;

    if (heartbeatResult.status === 'rejected') {
      console.error('Heartbeat failed (non-blocking):', heartbeatResult.reason);
    }

    // Personalize: taste-profile scoring if available, else keyword fallback
    const sorted = tasteProfile
      ? this.scoreMissionsByTaste(missions, tasteProfile)
      : this.personalizeMissionsByKeywords(missions, context);

    // Format output
    const formattedOutput = this.formatOutput(sorted, heartbeat, tasteProfile);

    return {
      success: true,
      heartbeat,
      missions: sorted,
      formattedOutput,
    };
  }

  // =====================================================
  // API Methods
  // =====================================================

  /**
   * Ping the heartbeat endpoint
   */
  private async pingHeartbeat(walletAddress: string): Promise<{
    streak: number;
    lotteryEligible: boolean;
  }> {
    const res = await fetch(`${this.apiBase}/agent/heartbeat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ walletAddress }),
    });

    if (!res.ok) {
      throw new Error(`Heartbeat failed: ${res.status}`);
    }

    const data: HeartbeatResponse = await res.json();
    return {
      streak: data.data.streak,
      lotteryEligible: data.data.lotteryEligible,
    };
  }

  /**
   * Fetch missions from discover API (replaces /public/missions)
   */
  private async fetchMissions(): Promise<Mission[]> {
    const res = await fetch(`${this.apiBase}/social-missions/discover?status=live&limit=20`);

    if (!res.ok) {
      throw new Error(`Failed to fetch missions: ${res.status}`);
    }

    const data: DiscoverResponse = await res.json();
    return data.missions;
  }

  /**
   * Fetch agent taste profile from identity endpoint
   */
  private async fetchTasteProfile(agentUserId: number): Promise<TasteProfile | null> {
    const res = await fetch(`${this.apiBase}/ai-agents/agent/${agentUserId}`);

    if (!res.ok) {
      console.error(`Failed to fetch taste profile: ${res.status}`);
      return null;
    }

    const json = await res.json();
    if (!json.success || !json.data) return null;

    return {
      agentUserId: json.data.agentUserId,
      personalityType: json.data.personalityType || '',
      mainCategories: json.data.mainCategories || [],
      subCategories: json.data.subCategories || [],
      dimensions: json.data.dimensions,
    };
  }

  /**
   * Submit content to a mission
   */
  async submitMission(params: {
    agentId: string;
    missionId: string;
    text: string;
    xPostUrl?: string;
    tweetId?: string;
    walletAddress?: string;
    xHandle?: string;
  }): Promise<SubmissionResult> {
    const res = await fetch(`${this.apiBase}/ai-agents/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });

    if (!res.ok) {
      const text = await res.text().catch(() => '');
      return { success: false, data: null, message: `Submit failed: ${res.status} ${text}` };
    }

    return res.json();
  }

  /**
   * Check submission status for an agent
   */
  async checkSubmissionStatus(agentId: string, missionId?: string): Promise<SubmissionStatusResult> {
    const params = new URLSearchParams({ agentId });
    if (missionId) params.append('missionId', missionId);

    const res = await fetch(`${this.apiBase}/ai-agents/submission-status?${params}`);

    if (!res.ok) {
      return { success: false, data: null };
    }

    return res.json();
  }

  // =====================================================
  // Taste-Profile Scoring
  // =====================================================

  /**
   * Score missions using taste profile (category overlap + quality + freshness)
   * Total possible: 70 points
   *   - Category overlap: 0-40 pts
   *   - Quality signal: 0-20 pts
   *   - Freshness: 0-10 pts
   */
  private scoreMissionsByTaste(missions: Mission[], profile: TasteProfile): Mission[] {
    if (missions.length === 0) return missions;

    const profileCategories = new Set(
      [...profile.mainCategories, ...profile.subCategories].map(c => c.toLowerCase()),
    );

    const now = Date.now();

    return missions
      .map((mission) => {
        let score = 0;

        // Category overlap (0-40 pts)
        const missionCats = (mission.categories || []).map(c => c.toLowerCase());
        let catOverlap = 0;
        for (const cat of missionCats) {
          if (profileCategories.has(cat)) {
            catOverlap++;
          } else {
            // Partial match: check if any profile category is a substring
            for (const pCat of profileCategories) {
              if (cat.includes(pCat) || pCat.includes(cat)) {
                catOverlap += 0.5;
                break;
              }
            }
          }
        }
        score += Math.min(catOverlap * 15, 40);

        // Quality signal (0-20 pts): based on submissions + rewards
        const submissionSignal = Math.min(mission.totalSubmissions * 2, 10);
        const rewardSignal = mission.rewards.length > 0 ? 10 : 0;
        score += submissionSignal + rewardSignal;

        // Freshness (0-10 pts): newer missions score higher
        if (mission.startTime) {
          const ageMs = now - new Date(mission.startTime).getTime();
          const ageDays = ageMs / (1000 * 60 * 60 * 24);
          score += Math.max(10 - ageDays, 0);
        }

        return { ...mission, matchScore: Math.round(score) };
      })
      .sort((a, b) => (b.matchScore || 0) - (a.matchScore || 0));
  }

  // =====================================================
  // Keyword Fallback (when no taste profile)
  // =====================================================

  /**
   * Fallback: keyword-based personalization from conversation context
   */
  private personalizeMissionsByKeywords(missions: Mission[], context?: string): Mission[] {
    if (!context || missions.length === 0) return missions;

    const contextLower = context.toLowerCase();

    const signals: string[] = [];
    const keywords: Record<string, string[]> = {
      'crypto': ['crypto', 'defi', 'blockchain', 'web3', 'token', 'nft', 'wallet'],
      'ai': ['ai', 'artificial intelligence', 'llm', 'agent', 'machine learning'],
      'social': ['twitter', 'x.com', 'social', 'community', 'engagement'],
      'development': ['code', 'develop', 'build', 'engineering', 'github'],
      'trading': ['trade', 'swap', 'dex', 'exchange', 'yield'],
    };

    for (const [category, terms] of Object.entries(keywords)) {
      if (terms.some(t => contextLower.includes(t))) {
        signals.push(category);
      }
    }

    if (signals.length === 0) return missions;

    return [...missions].sort((a, b) => {
      const scoreA = this.keywordScore(a, signals);
      const scoreB = this.keywordScore(b, signals);
      return scoreB - scoreA;
    });
  }

  private keywordScore(mission: Mission, signals: string[]): number {
    const text = `${mission.title} ${mission.description || ''} ${(mission.categories || []).join(' ')}`.toLowerCase();
    let score = 0;
    for (const signal of signals) {
      if (text.includes(signal)) score += 1;
    }
    return score;
  }

  // =====================================================
  // Output Formatting
  // =====================================================

  /**
   * Format the output for CLI display
   */
  private formatOutput(
    missions: Mission[],
    heartbeat: { streak: number; lotteryEligible: boolean } | null,
    tasteProfile?: TasteProfile | null,
  ): string {
    const lines: string[] = [];
    const baseUrl = process.env.BLOOM_DASHBOARD_URL || 'https://bloomprotocol.ai';

    lines.push('Bloom Missions');
    lines.push('==============');
    lines.push('');

    // Heartbeat status
    if (heartbeat) {
      lines.push(`Heartbeat: ${heartbeat.streak}-day streak${heartbeat.lotteryEligible ? ' (lottery eligible!)' : ''}`);
      lines.push('');
    }

    // Taste profile info
    if (tasteProfile) {
      lines.push(`Taste Profile: ${tasteProfile.personalityType}`);
      lines.push(`Interests: ${tasteProfile.mainCategories.join(', ')}`);
      lines.push('');
    }

    // Missions list
    if (missions.length === 0) {
      lines.push('No active missions right now. Check back later!');
    } else {
      lines.push(`${missions.length} Active Mission${missions.length > 1 ? 's' : ''}:`);
      lines.push('');

      for (const mission of missions) {
        const rewards = mission.rewards
          .map(r => `${r.amount || ''} ${r.name}`.trim())
          .join(', ');

        const categories = (mission.categories || []).join(', ');
        const scoreTag = mission.matchScore ? ` [match: ${mission.matchScore}]` : '';
        const url = `${baseUrl}/social-missions/${mission.tweetId}`;

        lines.push(`- ${mission.title}${scoreTag}`);
        if (categories) lines.push(`  Categories: ${categories}`);
        if (rewards) lines.push(`  Rewards: ${rewards}`);
        lines.push(`  Submissions: ${mission.totalSubmissions}`);
        lines.push(`  ${url}`);
        lines.push('');
      }
    }

    return lines.join('\n');
  }
}
