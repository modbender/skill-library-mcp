/**
 * Personality Analyzer V2 — 2-Axis Dimension System
 *
 * Calculates two independent dimensions (Conviction/Intuition) and contribution score
 * to determine supporter personality type through a 2x2 quadrant classification.
 */

import { PersonalityType } from '../types/personality';

export interface UserData {
  sources: string[];
  twitter?: {
    following: string[];
    tweets: any[];
    bio: string;
  };
  farcaster?: {
    casts: any[];
    channels: string[];
    bio: string;
  };
  wallet?: {
    transactions: any[];
    nfts: any[];
    tokens: any[];
    contracts: string[]; // Unique contracts interacted with
  };
  conversationMemory?: {
    topics: string[];
    interests: string[];
    preferences: string[];
    history: string[];
  };
}

export interface DimensionScores {
  conviction: number;    // 0-100: Conviction (high) ← → Curiosity (low)
  intuition: number;     // 0-100: Intuition (high) ← → Analysis (low)
  contribution: number;  // 0-100: Contribution behavior score
}

export interface PersonalityAnalysis {
  personalityType: PersonalityType;
  tagline: string;
  description: string;
  detectedInterests: string[];
  detectedCategories: string[]; // Top categories for tagline generation
  dimensions: DimensionScores;
  confidence: number;
}

/**
 * Category keywords for tagline generation
 */
const CATEGORY_KEYWORDS = {
  'AI Tools': ['ai', 'gpt', 'llm', 'machine learning', 'neural', 'model'],
  'Productivity': ['productivity', 'workflow', 'automation', 'efficiency', 'task'],
  'Wellness': ['wellness', 'health', 'fitness', 'meditation', 'mental'],
  'Education': ['education', 'learning', 'course', 'teach', 'knowledge'],
  'Crypto': ['crypto', 'defi', 'web3', 'blockchain', 'token', 'dao'],
  'Lifestyle': ['lifestyle', 'design', 'art', 'fashion', 'travel'],
};

/**
 * Tagline templates by personality type
 */
const TAGLINE_TEMPLATES = {
  [PersonalityType.THE_VISIONARY]: (category: string) => `The ${category} Pioneer`,
  [PersonalityType.THE_EXPLORER]: (category: string) => `The ${category} Nomad`,
  [PersonalityType.THE_CULTIVATOR]: (category: string) => `The ${category} Gardener`,
  [PersonalityType.THE_OPTIMIZER]: (category: string) => `The ${category} Analyst`,
  [PersonalityType.THE_INNOVATOR]: (category: string) => `The ${category} Architect`,
};

export class PersonalityAnalyzer {
  /**
   * Main analysis method — calculates dimensions and determines personality
   */
  async analyze(userData: UserData): Promise<PersonalityAnalysis> {
    console.log('🤖 Analyzing user data for 2-axis personality classification...');

    // Step 1: Calculate dimension scores
    const dimensions = this.calculateDimensions(userData);
    console.log(`📊 Dimensions: Conviction=${dimensions.conviction}, Intuition=${dimensions.intuition}, Contribution=${dimensions.contribution}`);

    // Step 2: Classify personality type (contribution override logic)
    const personalityType = this.classifyPersonality(dimensions);
    console.log(`✨ Personality Type: ${personalityType}`);

    // Step 3: Detect categories for tagline
    const detectedCategories = this.detectCategories(userData);
    const topCategory = detectedCategories[0] || 'Tech';

    // Step 4: Generate dynamic tagline
    const tagline = TAGLINE_TEMPLATES[personalityType](topCategory);

    // Step 5: Generate personalized description
    const description = await this.generateDescription(personalityType, detectedCategories, dimensions);

    // Step 6: Extract detailed interests
    const detectedInterests = this.extractInterests(userData);

    // Step 7: Calculate confidence (based on data sources)
    const confidence = this.calculateConfidence(userData);

    return {
      personalityType,
      tagline,
      description,
      detectedInterests,
      detectedCategories,
      dimensions,
      confidence,
    };
  }

  /**
   * Calculate all three dimension scores (0-100 each)
   */
  private calculateDimensions(userData: UserData): DimensionScores {
    const conviction = this.calculateConviction(userData);
    const intuition = this.calculateIntuition(userData);
    const contribution = this.calculateContribution(userData);

    return {
      conviction: Math.min(Math.max(Math.round(conviction), 0), 100),
      intuition: Math.min(Math.max(Math.round(intuition), 0), 100),
      contribution: Math.min(Math.max(Math.round(contribution), 0), 100),
    };
  }

  /**
   * Calculate Conviction (0-100)
   * High = Few deep commitments, long-term holding, repeated interactions
   * Low = Diverse portfolio, short-term, always exploring
   */
  private calculateConviction(userData: UserData): number {
    let score = 50; // Start at midpoint

    if (userData.wallet) {
      const { transactions = [], contracts = [], tokens = [] } = userData.wallet;

      // Factor 1: Portfolio concentration (fewer contracts = higher conviction)
      const uniqueContracts = new Set(contracts).size;
      if (uniqueContracts > 0) {
        if (uniqueContracts <= 5) score += 20;
        else if (uniqueContracts <= 10) score += 10;
        else if (uniqueContracts > 30) score -= 20;
      }

      // Factor 2: Repeat interactions (multiple txs to same contract = conviction)
      const contractCounts = contracts.reduce((acc, addr) => {
        acc[addr] = (acc[addr] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);
      const avgInteractionsPerContract = Object.values(contractCounts).reduce((a, b) => a + b, 0) / uniqueContracts;
      if (avgInteractionsPerContract > 5) score += 15;
      else if (avgInteractionsPerContract > 2) score += 5;
      else if (avgInteractionsPerContract < 1.5) score -= 10;

      // Factor 3: Token holding (long-term holding = conviction)
      const uniqueTokens = new Set(tokens.map((t: any) => t.symbol)).size;
      if (uniqueTokens > 20) score -= 15; // Too diversified
      else if (uniqueTokens < 5) score += 10; // Focused
    }

    // Social signals: Follow few but engage deeply
    if (userData.twitter) {
      const followingCount = userData.twitter.following.length;
      if (followingCount < 100) score += 5;
      else if (followingCount > 500) score -= 5;
    }

    return score;
  }

  /**
   * Calculate Intuition (0-100)
   * High = Vision-driven, backs pre-launch, trend-spotter
   * Low = Data-driven, waits for metrics, mature protocols
   */
  private calculateIntuition(userData: UserData): number {
    let score = 50; // Start at midpoint

    const allText = this.extractAllText(userData).toLowerCase();

    // Factor 1: Vision/narrative language vs data/metrics language
    const visionKeywords = ['vision', 'future', 'believe', 'potential', 'revolutionary', 'paradigm', 'early', 'first'];
    const analysisKeywords = ['data', 'metrics', 'roi', 'tvl', 'apy', 'analysis', 'performance', 'track record'];

    const visionScore = visionKeywords.filter(k => allText.includes(k)).length;
    const analysisScore = analysisKeywords.filter(k => allText.includes(k)).length;

    score += (visionScore - analysisScore) * 5;

    // Factor 2: Wallet activity - pre-launch vs established protocols
    if (userData.wallet) {
      const { transactions = [] } = userData.wallet;

      // Pre-launch signals: interacting with new contracts (deployed < 30 days ago)
      // Established signals: using high-TVL mature protocols
      // Note: In production, this would call blockchain APIs to check contract age and TVL
      // For hackathon, we'll use heuristics

      const establishedProtocols = ['uniswap', 'aave', 'compound', 'curve', 'maker'];
      const establishedTxCount = transactions.filter((tx: any) =>
        establishedProtocols.some(p => tx.to?.toLowerCase().includes(p))
      ).length;

      if (establishedTxCount > 10) score -= 10; // Prefers mature protocols
      else if (establishedTxCount < 3) score += 10; // Avoids established

      // High transaction count = willing to experiment early
      if (transactions.length > 100) score += 5;
    }

    // Factor 3: Social behavior - talks about trends vs analysis
    if (userData.twitter) {
      const tweets = userData.twitter.tweets || [];
      const trendKeywords = ['trend', 'new', 'launch', 'alpha', 'early'];
      const trendMentions = tweets.filter((t: any) =>
        trendKeywords.some(k => t.text?.toLowerCase().includes(k))
      ).length;

      score += trendMentions * 2;
    }

    return score;
  }

  /**
   * Calculate Contribution (0-100)
   * >65 = The Cultivator (override personality classification)
   * Detects: content creation, feedback, referrals, governance
   */
  private calculateContribution(userData: UserData): number {
    let score = 0;

    const allText = this.extractAllText(userData).toLowerCase();

    // Factor 1: Content creation
    const contentKeywords = ['wrote', 'published', 'created', 'shared', 'tutorial', 'guide', 'review'];
    score += contentKeywords.filter(k => allText.includes(k)).length * 5;

    // Factor 2: Community engagement
    const engagementKeywords = ['feedback', 'suggestion', 'improvement', 'helped', 'support', 'community'];
    score += engagementKeywords.filter(k => allText.includes(k)).length * 5;

    // Factor 3: Referrals and evangelism
    const referralKeywords = ['recommend', 'check out', 'try this', 'using', 'love this'];
    score += referralKeywords.filter(k => allText.includes(k)).length * 3;

    // Factor 4: Governance participation
    if (userData.wallet) {
      const { transactions = [] } = userData.wallet;
      const governanceTxs = transactions.filter((tx: any) =>
        tx.method?.includes('vote') || tx.method?.includes('propose')
      ).length;
      score += governanceTxs * 10;
    }

    // Factor 5: Twitter/Farcaster engagement volume
    if (userData.twitter) {
      const tweets = userData.twitter.tweets || [];
      if (tweets.length > 100) score += 10;
      else if (tweets.length > 50) score += 5;
    }

    if (userData.farcaster) {
      const casts = userData.farcaster.casts || [];
      if (casts.length > 100) score += 10;
      else if (casts.length > 50) score += 5;
    }

    return Math.min(score, 100);
  }

  /**
   * Classify personality based on 2x2 quadrant + contribution override
   */
  private classifyPersonality(dimensions: DimensionScores): PersonalityType {
    const { conviction, intuition, contribution } = dimensions;

    // Override: If contribution > 65, user is The Cultivator
    if (contribution > 65) {
      return PersonalityType.THE_CULTIVATOR;
    }

    // 2x2 Quadrant Classification:
    // Conviction ≥ 50 AND Intuition ≥ 50 → The Visionary 💜
    // Conviction < 50 AND Intuition ≥ 50 → The Explorer 💚
    // Conviction ≥ 50 AND Intuition < 50 → The Optimizer 🧡
    // Conviction < 50 AND Intuition < 50 → The Innovator 💙

    if (conviction >= 50 && intuition >= 50) {
      return PersonalityType.THE_VISIONARY;
    } else if (conviction < 50 && intuition >= 50) {
      return PersonalityType.THE_EXPLORER;
    } else if (conviction >= 50 && intuition < 50) {
      return PersonalityType.THE_OPTIMIZER;
    } else {
      return PersonalityType.THE_INNOVATOR;
    }
  }

  /**
   * Detect top categories from user data
   */
  private detectCategories(userData: UserData): string[] {
    const allText = this.extractAllText(userData).toLowerCase();
    const categoryScores: Record<string, number> = {};

    for (const [category, keywords] of Object.entries(CATEGORY_KEYWORDS)) {
      let score = 0;
      for (const keyword of keywords) {
        const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
        const matches = allText.match(regex);
        if (matches) {
          score += matches.length;
        }
      }
      categoryScores[category] = score;
    }

    // Sort by score descending
    return Object.entries(categoryScores)
      .sort(([, a], [, b]) => b - a)
      .map(([category]) => category)
      .slice(0, 3); // Top 3 categories
  }

  /**
   * Generate personalized description
   */
  private async generateDescription(
    type: PersonalityType,
    categories: string[],
    dimensions: DimensionScores
  ): Promise<string> {
    const descriptions = {
      [PersonalityType.THE_VISIONARY]: [
        `You back bold ideas before they're obvious. Your conviction is your edge, and you see potential where others see risk. ${categories[0]} is where you spot the next paradigm shift.`,
        `Vision-driven and future-oriented, you champion projects that challenge the status quo. You're not waiting for proof — you're building the proof.`,
      ],
      [PersonalityType.THE_EXPLORER]: [
        `Every project is a new adventure. You're curious, open-minded, and always discovering. Your diverse interests across ${categories.join(', ')} fuel your supporter journey.`,
        `You don't settle into one niche — the whole landscape is your playground. Exploration is your strategy, and variety is your strength.`,
      ],
      [PersonalityType.THE_CULTIVATOR]: [
        `You don't just support projects — you help them grow. Through feedback, content, and community building in ${categories[0]}, you're the supporter every builder dreams of.`,
        `Your contribution score speaks volumes. You're an active participant, not a passive observer. Projects thrive when you're involved.`,
      ],
      [PersonalityType.THE_OPTIMIZER]: [
        `Always leveling up. You're data-driven, focused, and relentless about improvement. ${categories[0]} tools that maximize efficiency earn your support.`,
        `There's always a better way, and you're determined to find it. You iterate, optimize, and refine until it's right.`,
      ],
      [PersonalityType.THE_INNOVATOR]: [
        `First to back breakthrough technology. You spot the future before it arrives, especially in ${categories[0]}. While others wait, you're already there.`,
        `Technical depth meets early adoption. You understand how things work under the hood, and you're not afraid to back the bleeding edge.`,
      ],
    };

    const options = descriptions[type];
    const randomIndex = Math.floor(Math.random() * options.length);
    return options[randomIndex];
  }

  /**
   * Extract all text from user data
   */
  private extractAllText(userData: UserData): string {
    const textParts: string[] = [];

    if (userData.twitter) {
      textParts.push(userData.twitter.bio);
      textParts.push(...userData.twitter.tweets.map(t => t.text || ''));
      textParts.push(...userData.twitter.following);
    }

    if (userData.farcaster) {
      textParts.push(userData.farcaster.bio);
      textParts.push(...userData.farcaster.casts.map(c => c.text || ''));
      textParts.push(...userData.farcaster.channels);
    }

    if (userData.conversationMemory) {
      textParts.push(...userData.conversationMemory.topics);
      textParts.push(...userData.conversationMemory.interests);
      textParts.push(...userData.conversationMemory.preferences);
      textParts.push(...userData.conversationMemory.history);
    }

    return textParts.join(' ');
  }

  /**
   * Extract specific interests
   */
  private extractInterests(userData: UserData): string[] {
    const interests = new Set<string>();
    const allText = this.extractAllText(userData).toLowerCase();

    const interestKeywords = [
      'AI Tools', 'Machine Learning', 'Crypto', 'DeFi', 'NFTs',
      'Education', 'Wellness', 'Fitness', 'Productivity', 'Meditation',
      'Web3', 'DAOs', 'Gaming', 'Art', 'Music', 'Writing',
      'Coding', 'Design', 'Marketing', 'Finance', 'Health',
    ];

    for (const keyword of interestKeywords) {
      if (allText.includes(keyword.toLowerCase())) {
        interests.add(keyword);
      }
    }

    return Array.from(interests).slice(0, 10);
  }

  /**
   * Calculate confidence based on data quality
   */
  private calculateConfidence(userData: UserData): number {
    let confidence = 30; // Base confidence

    if (userData.twitter && userData.twitter.tweets.length > 10) confidence += 20;
    if (userData.farcaster && userData.farcaster.casts.length > 10) confidence += 15;
    if (userData.wallet && userData.wallet.transactions.length > 20) confidence += 25;
    if (userData.conversationMemory && userData.conversationMemory.history.length > 5) confidence += 10;

    return Math.min(confidence, 100);
  }
}
