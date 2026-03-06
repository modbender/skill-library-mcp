/**
 * X Profile Scraper
 *
 * Scrapes public X (Twitter) profiles without requiring API access
 * Uses web scraping for MVP - can be replaced with official API later
 */

export interface XProfileData {
  handle: string;
  displayName: string;
  bio: string;
  followerCount: number;
  followingCount: number;
  tweetCount: number;
  joinedDate: string;
  verified: boolean;

  // Recent activity
  recentTweets: XTweet[];

  // Engagement metrics
  avgLikes: number;
  avgRetweets: number;
  engagementRate: number; // (likes + retweets) / followers

  // Following list (sample)
  following: string[];

  // Metadata
  scrapedAt: number;
}

export interface XTweet {
  id: string;
  text: string;
  timestamp: number;
  likes: number;
  retweets: number;
  replies: number;
  url: string;
}

/**
 * X Profile Scraper
 *
 * For MVP, this uses mock data patterns
 * In production, you can use:
 * - Puppeteer/Playwright for browser automation
 * - Apify Twitter Scraper
 * - Twitter API (if budget allows)
 */
export class XProfileScraper {
  /**
   * Scrape a user's public profile
   */
  async scrapeProfile(handle: string): Promise<XProfileData> {
    console.log(`🔍 Scraping X profile: @${handle}`);

    // TODO: Implement actual scraping
    // For now, return realistic mock data for testing

    try {
      // In production, this would:
      // 1. Use Puppeteer to navigate to twitter.com/{handle}
      // 2. Extract bio, follower count, recent tweets
      // 3. Calculate engagement metrics

      const profileData = await this.mockScrape(handle);

      console.log(`✅ Scraped @${handle}: ${profileData.followerCount} followers`);

      return profileData;
    } catch (error) {
      console.error(`❌ Failed to scrape @${handle}:`, error);
      throw error;
    }
  }

  /**
   * Scrape multiple profiles in batch
   */
  async scrapeProfiles(handles: string[]): Promise<XProfileData[]> {
    console.log(`🔍 Scraping ${handles.length} profiles...`);

    const results: XProfileData[] = [];

    for (const handle of handles) {
      try {
        const profile = await this.scrapeProfile(handle);
        results.push(profile);

        // Rate limiting: wait 2-5 seconds between requests
        await this.sleep(2000 + Math.random() * 3000);
      } catch (error) {
        console.warn(`⚠️  Skipping @${handle}:`, error);
      }
    }

    return results;
  }

  /**
   * Extract recent tweets from profile
   */
  async scrapeRecentTweets(handle: string, limit: number = 20): Promise<XTweet[]> {
    console.log(`📝 Scraping recent tweets from @${handle}...`);

    // TODO: Implement actual tweet scraping
    const tweets = await this.mockScrapeTweets(handle, limit);

    return tweets;
  }

  /**
   * Scrape user's following list (sample)
   */
  async scrapeFollowing(handle: string, limit: number = 100): Promise<string[]> {
    console.log(`👥 Scraping following list for @${handle}...`);

    // TODO: Implement actual following scraping
    const following = await this.mockScrapeFollowing(handle, limit);

    return following;
  }

  /**
   * Calculate engagement rate
   */
  calculateEngagementRate(profile: XProfileData): number {
    if (profile.recentTweets.length === 0 || profile.followerCount === 0) {
      return 0;
    }

    const totalEngagement = profile.recentTweets.reduce(
      (sum, tweet) => sum + tweet.likes + tweet.retweets,
      0
    );

    const avgEngagement = totalEngagement / profile.recentTweets.length;
    const engagementRate = (avgEngagement / profile.followerCount) * 100;

    return Math.round(engagementRate * 100) / 100; // Round to 2 decimals
  }

  /**
   * Check if profile has builder keywords
   */
  hasBuilderKeywords(bio: string): boolean {
    const keywords = [
      'indie', 'builder', 'maker', 'founder', 'dev', 'developer',
      'entrepreneur', 'startup', 'building', 'shipping', 'creator',
      'hacker', 'solo', 'bootstrapped', 'side project', 'saas',
    ];

    const bioLower = bio.toLowerCase();
    return keywords.some(keyword => bioLower.includes(keyword));
  }

  // ============================================
  // MOCK DATA (for testing without actual scraping)
  // Replace with real scraping in production
  // ============================================

  private async mockScrape(handle: string): Promise<XProfileData> {
    // Simulate realistic profiles for testing
    const profiles: Record<string, Partial<XProfileData>> = {
      'levelsio': {
        displayName: 'Pieter Levels',
        bio: '🏝 Nomad • Indie maker of @nomadlist @remoteok @PhotoAI etc • Building 12 startups in 12 months',
        followerCount: 500000,
        followingCount: 2000,
        verified: true,
      },
      'dvassallo': {
        displayName: 'Daniel Vassallo',
        bio: 'Building portfolio of small bets. Author of The Good Parts of AWS. Sold my SaaS for $675K. Ex-AWS engineer.',
        followerCount: 80000,
        followingCount: 500,
        verified: false,
      },
      'arvidkahl': {
        displayName: 'Arvid Kahl',
        bio: 'Bootstrapped founder • Author of Zero to Sold & The Embedded Entrepreneur • Building @podscan_fm',
        followerCount: 120000,
        followingCount: 1000,
        verified: true,
      },
    };

    const baseProfile = profiles[handle] || {
      displayName: handle,
      bio: 'Indie builder | Shipping products | Building in public',
      followerCount: 5000 + Math.floor(Math.random() * 45000),
      followingCount: 500 + Math.floor(Math.random() * 2000),
      verified: false,
    };

    const recentTweets = await this.mockScrapeTweets(handle, 20);
    const following = await this.mockScrapeFollowing(handle, 100);

    const avgLikes = recentTweets.reduce((sum, t) => sum + t.likes, 0) / recentTweets.length;
    const avgRetweets = recentTweets.reduce((sum, t) => sum + t.retweets, 0) / recentTweets.length;

    const profile: XProfileData = {
      handle,
      displayName: baseProfile.displayName!,
      bio: baseProfile.bio!,
      followerCount: baseProfile.followerCount!,
      followingCount: baseProfile.followingCount!,
      tweetCount: 5000 + Math.floor(Math.random() * 15000),
      joinedDate: '2019-01-01',
      verified: baseProfile.verified!,
      recentTweets,
      following,
      avgLikes: Math.round(avgLikes),
      avgRetweets: Math.round(avgRetweets),
      engagementRate: 0,
      scrapedAt: Date.now(),
    };

    profile.engagementRate = this.calculateEngagementRate(profile);

    return profile;
  }

  private async mockScrapeTweets(handle: string, limit: number): Promise<XTweet[]> {
    const tweets: XTweet[] = [];
    const now = Date.now();

    const tweetTemplates = [
      'Just shipped a new feature for my SaaS! ',
      'Building in public: here\'s what I learned this week...',
      'Indie hacker tip: ',
      'Working on something new 👀',
      'Revenue update: ',
      'Just crossed $10k MRR! ',
      'Bootstrapping is hard but worth it',
      'New blog post: ',
      'Side project update: ',
      'Shipping fast and learning faster',
    ];

    for (let i = 0; i < limit; i++) {
      const template = tweetTemplates[i % tweetTemplates.length];
      const timestamp = now - (i * 24 * 60 * 60 * 1000); // One per day

      tweets.push({
        id: `${handle}_${i}`,
        text: `${template} #buildinpublic`,
        timestamp,
        likes: Math.floor(Math.random() * 200) + 10,
        retweets: Math.floor(Math.random() * 50) + 2,
        replies: Math.floor(Math.random() * 30) + 1,
        url: `https://x.com/${handle}/status/${Date.now() + i}`,
      });
    }

    return tweets;
  }

  private async mockScrapeFollowing(handle: string, limit: number): Promise<string[]> {
    const builderAccounts = [
      'levelsio', 'dvassallo', 'arvidkahl', 'tdinh_me', 'swyx',
      'naval', 'balajis', 'sama', 'paulg', 'jessepollak',
      'danfinlay', 'austingriffith', 'goodside', 'ai_for_success',
      'MoonshotsMaker', 'Marc_Louvion', 'dinkydani21',
    ];

    const following: string[] = [];
    const count = Math.min(limit, 100);

    for (let i = 0; i < count; i++) {
      following.push(builderAccounts[i % builderAccounts.length]);
    }

    return following;
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

/**
 * Create X Profile Scraper instance
 */
export function createXProfileScraper(): XProfileScraper {
  return new XProfileScraper();
}
