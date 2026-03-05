/**
 * Vibe Score Calculator
 *
 * Calculates a "builder vibe" score for X profiles
 * to determine if they're good targets for proactive outreach
 *
 * Score breakdown:
 * - Bio keywords (30 points): indie, builder, maker, founder, etc.
 * - Activity level (20 points): recent tweets, engagement
 * - Follower range (20 points): sweet spot 1k-50k (not too small, not too big)
 * - Engagement rate (15 points): good community interaction
 * - Builder network (15 points): follows other builders
 */

import { XProfileData } from '../integrations/x-profile-scraper';

export interface VibeScoreResult {
  totalScore: number;
  breakdown: {
    bioKeywords: number;
    activityLevel: number;
    followerRange: number;
    engagementRate: number;
    builderNetwork: number;
  };
  isTarget: boolean;
  targetTier: 'high' | 'medium' | 'low' | 'none';
  reasoning: string[];
}

export class VibeScoreCalculator {
  /**
   * Calculate builder vibe score for a profile
   */
  calculateScore(profile: XProfileData): VibeScoreResult {
    const breakdown = {
      bioKeywords: this.scoreBioKeywords(profile),
      activityLevel: this.scoreActivityLevel(profile),
      followerRange: this.scoreFollowerRange(profile),
      engagementRate: this.scoreEngagementRate(profile),
      builderNetwork: this.scoreBuilderNetwork(profile),
    };

    const totalScore =
      breakdown.bioKeywords +
      breakdown.activityLevel +
      breakdown.followerRange +
      breakdown.engagementRate +
      breakdown.builderNetwork;

    const reasoning = this.generateReasoning(profile, breakdown);

    // Determine target tier
    let targetTier: 'high' | 'medium' | 'low' | 'none';
    if (totalScore >= 80) targetTier = 'high';
    else if (totalScore >= 60) targetTier = 'medium';
    else if (totalScore >= 40) targetTier = 'low';
    else targetTier = 'none';

    return {
      totalScore,
      breakdown,
      isTarget: totalScore >= 60, // Threshold for engagement
      targetTier,
      reasoning,
    };
  }

  /**
   * Score based on bio keywords
   * Max: 30 points
   */
  private scoreBioKeywords(profile: XProfileData): number {
    const bioLower = profile.bio.toLowerCase();

    // Tier 1: Strong builder signals (10 points each)
    const tier1Keywords = ['indie', 'builder', 'maker', 'founder', 'building', 'shipping'];
    const tier1Matches = tier1Keywords.filter(kw => bioLower.includes(kw)).length;

    // Tier 2: Tech/dev signals (5 points each)
    const tier2Keywords = ['dev', 'developer', 'engineer', 'coder', 'hacker', 'startup'];
    const tier2Matches = tier2Keywords.filter(kw => bioLower.includes(kw)).length;

    // Tier 3: Adjacent signals (3 points each)
    const tier3Keywords = ['entrepreneur', 'creator', 'bootstrapped', 'saas', 'ai', 'web3'];
    const tier3Matches = tier3Keywords.filter(kw => bioLower.includes(kw)).length;

    const score = Math.min(30, tier1Matches * 10 + tier2Matches * 5 + tier3Matches * 3);

    return score;
  }

  /**
   * Score based on activity level
   * Max: 20 points
   */
  private scoreActivityLevel(profile: XProfileData): number {
    let score = 0;

    // Recent tweets (10 points)
    const last7DaysTweets = profile.recentTweets.filter(tweet => {
      const daysSince = (Date.now() - tweet.timestamp) / (1000 * 60 * 60 * 24);
      return daysSince <= 7;
    }).length;

    if (last7DaysTweets >= 5) score += 10;
    else if (last7DaysTweets >= 3) score += 7;
    else if (last7DaysTweets >= 1) score += 4;

    // Tweet consistency (5 points)
    if (profile.tweetCount > 1000) score += 5;
    else if (profile.tweetCount > 500) score += 3;

    // Recent engagement (5 points)
    if (profile.avgLikes > 20) score += 5;
    else if (profile.avgLikes > 10) score += 3;

    return Math.min(20, score);
  }

  /**
   * Score based on follower count
   * Sweet spot: 1k-50k followers (not too small, not influencer)
   * Max: 20 points
   */
  private scoreFollowerRange(profile: XProfileData): number {
    const followers = profile.followerCount;

    // Sweet spot: 2k-20k (full points)
    if (followers >= 2000 && followers <= 20000) return 20;

    // Good range: 1k-2k or 20k-50k (15 points)
    if ((followers >= 1000 && followers < 2000) || (followers > 20000 && followers <= 50000))
      return 15;

    // Acceptable: 500-1k or 50k-100k (10 points)
    if ((followers >= 500 && followers < 1000) || (followers > 50000 && followers <= 100000))
      return 10;

    // Too small or too big (5 points)
    if (followers >= 200 && followers < 500) return 5;

    // Outside range (0 points)
    return 0;
  }

  /**
   * Score based on engagement rate
   * Max: 15 points
   */
  private scoreEngagementRate(profile: XProfileData): number {
    const rate = profile.engagementRate;

    // Excellent engagement (3%+)
    if (rate >= 3) return 15;

    // Good engagement (2-3%)
    if (rate >= 2) return 12;

    // Decent engagement (1-2%)
    if (rate >= 1) return 8;

    // Low engagement (0.5-1%)
    if (rate >= 0.5) return 4;

    // Very low
    return 0;
  }

  /**
   * Score based on builder network
   * Checks if they follow known builders
   * Max: 15 points
   */
  private scoreBuilderNetwork(profile: XProfileData): number {
    const knownBuilders = [
      'levelsio',
      'dvassallo',
      'arvidkahl',
      'tdinh_me',
      'swyx',
      'naval',
      'balajis',
      'sama',
      'paulg',
      'jessepollak',
      'danfinlay',
      'austingriffith',
      'goodside',
      'MoonshotsMaker',
      'Marc_Louvion',
    ];

    const followsBuilders = profile.following.filter(handle =>
      knownBuilders.includes(handle.toLowerCase())
    ).length;

    // Follows 5+ builders (full points)
    if (followsBuilders >= 5) return 15;

    // Follows 3-4 builders (10 points)
    if (followsBuilders >= 3) return 10;

    // Follows 1-2 builders (5 points)
    if (followsBuilders >= 1) return 5;

    // Doesn't follow known builders (0 points)
    return 0;
  }

  /**
   * Generate reasoning for the score
   */
  private generateReasoning(
    profile: XProfileData,
    breakdown: VibeScoreResult['breakdown']
  ): string[] {
    const reasons: string[] = [];

    // Bio keywords
    if (breakdown.bioKeywords >= 20) {
      reasons.push('✅ Strong builder identity in bio');
    } else if (breakdown.bioKeywords >= 10) {
      reasons.push('👍 Some builder keywords in bio');
    } else {
      reasons.push('⚠️  Limited builder keywords in bio');
    }

    // Activity
    if (breakdown.activityLevel >= 15) {
      reasons.push('✅ Very active on X (tweets regularly)');
    } else if (breakdown.activityLevel >= 10) {
      reasons.push('👍 Moderately active');
    } else {
      reasons.push('⚠️  Low activity level');
    }

    // Followers
    if (breakdown.followerRange >= 15) {
      reasons.push(`✅ Sweet spot follower count (${profile.followerCount.toLocaleString()})`);
    } else if (breakdown.followerRange >= 10) {
      reasons.push(`👍 Acceptable follower count (${profile.followerCount.toLocaleString()})`);
    } else {
      reasons.push(`⚠️  Follower count outside ideal range (${profile.followerCount.toLocaleString()})`);
    }

    // Engagement
    if (breakdown.engagementRate >= 12) {
      reasons.push(`✅ Excellent engagement rate (${profile.engagementRate}%)`);
    } else if (breakdown.engagementRate >= 8) {
      reasons.push(`👍 Good engagement rate (${profile.engagementRate}%)`);
    } else {
      reasons.push(`⚠️  Low engagement rate (${profile.engagementRate}%)`);
    }

    // Network
    if (breakdown.builderNetwork >= 10) {
      reasons.push('✅ Well-connected in builder community');
    } else if (breakdown.builderNetwork >= 5) {
      reasons.push('👍 Some builder network connections');
    } else {
      reasons.push('⚠️  Limited builder network');
    }

    return reasons;
  }

  /**
   * Batch calculate scores for multiple profiles
   */
  calculateBatch(profiles: XProfileData[]): Map<string, VibeScoreResult> {
    const results = new Map<string, VibeScoreResult>();

    for (const profile of profiles) {
      const score = this.calculateScore(profile);
      results.set(profile.handle, score);
    }

    return results;
  }

  /**
   * Filter profiles by minimum score
   */
  filterByScore(
    profiles: XProfileData[],
    minScore: number = 60
  ): Array<{ profile: XProfileData; score: VibeScoreResult }> {
    const results: Array<{ profile: XProfileData; score: VibeScoreResult }> = [];

    for (const profile of profiles) {
      const score = this.calculateScore(profile);
      if (score.totalScore >= minScore) {
        results.push({ profile, score });
      }
    }

    // Sort by score (highest first)
    return results.sort((a, b) => b.score.totalScore - a.score.totalScore);
  }
}

/**
 * Create Vibe Score Calculator instance
 */
export function createVibeScoreCalculator(): VibeScoreCalculator {
  return new VibeScoreCalculator();
}
