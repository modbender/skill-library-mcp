/**
 * GitHub Repository Recommendations
 *
 * Searches GitHub for relevant repositories based on user's interests
 * and categories, scoring them by relevance, popularity, and activity.
 */

import type { IdentityData } from './bloom-identity-skill-v2';

export interface GitHubRecommendation {
  skillId: string;
  skillName: string;
  description: string;
  url: string;
  categories: string[];
  matchScore: number;
  creator?: string;
  creatorUserId?: number | string;
  source: 'GitHub';
  stars?: number;
  language?: string;
}

interface GitHubRepo {
  full_name: string;
  name: string;
  description: string | null;
  html_url: string;
  stargazers_count: number;
  topics: string[];
  language: string | null;
  owner: {
    login: string;
  };
  updated_at: string;
}

interface GitHubSearchResponse {
  items: GitHubRepo[];
  total_count: number;
}

/**
 * Map Bloom categories to GitHub search topics
 */
const CATEGORY_TO_TOPICS: Record<string, string[]> = {
  'AI Tools': ['ai', 'artificial-intelligence', 'machine-learning', 'llm', 'chatgpt', 'gpt'],
  'Productivity': ['productivity', 'automation', 'workflow', 'tools', 'utilities'],
  'Automation': ['automation', 'workflow', 'bot', 'scripts', 'ci-cd'],
  'Creative Tools': ['creative', 'design', 'art', 'music', 'video'],
  'Developer Tools': ['developer-tools', 'devtools', 'cli', 'sdk', 'library'],
  'Data & Analytics': ['data', 'analytics', 'visualization', 'database', 'sql'],
  'Blockchain': ['blockchain', 'web3', 'crypto', 'ethereum', 'solana'],
  'Consumer Apps': ['app', 'mobile', 'web-app', 'saas', 'platform'],
  'Education': ['education', 'learning', 'tutorial', 'course', 'teaching'],
  'Open Source': ['open-source', 'oss', 'community', 'contribution'],
};

export class GitHubRecommendations {
  private apiToken?: string;
  private baseUrl = 'https://api.github.com';

  constructor(apiToken?: string) {
    this.apiToken = apiToken;
  }

  /**
   * Get GitHub repository recommendations based on identity
   */
  async getRecommendations(identity: IdentityData, limit = 10): Promise<GitHubRecommendation[]> {
    console.log('🔍 Searching GitHub for repositories...');

    try {
      // Build search topics from user's categories
      const searchTopics = this.buildSearchTopics(identity);

      if (searchTopics.length === 0) {
        console.log('⚠️  No matching GitHub topics found');
        return [];
      }

      // Search GitHub for repositories
      const repos = await this.searchRepositories(searchTopics, limit * 2); // Get more to filter

      // Score and rank repositories
      const recommendations = this.scoreRepositories(repos, identity);

      // Return top N
      const topRecommendations = recommendations.slice(0, limit);
      console.log(`✅ Found ${topRecommendations.length} GitHub repositories`);

      return topRecommendations;

    } catch (error) {
      console.error('❌ GitHub search failed:', error);
      return [];
    }
  }

  /**
   * Build GitHub search topics from identity categories
   */
  private buildSearchTopics(identity: IdentityData): string[] {
    const topics = new Set<string>();

    // Map main categories to GitHub topics
    for (const category of identity.mainCategories) {
      const categoryTopics = CATEGORY_TO_TOPICS[category] || [];
      categoryTopics.forEach(t => topics.add(t));
    }

    // Map sub-categories (interests) to topics
    for (const interest of identity.subCategories) {
      const normalized = interest.toLowerCase().replace(/\s+/g, '-');
      topics.add(normalized);
    }

    return Array.from(topics);
  }

  /**
   * Search GitHub repositories by topics
   */
  private async searchRepositories(topics: string[], limit: number): Promise<GitHubRepo[]> {
    const repos: GitHubRepo[] = [];
    const seenRepos = new Set<string>();

    // Search for top 3 topics (GitHub API has query length limits)
    const topTopics = topics.slice(0, 3);

    for (const topic of topTopics) {
      try {
        // Build search query: topic + stars + recent activity
        const query = `topic:${topic} stars:>100 pushed:>2023-01-01`;
        const url = `${this.baseUrl}/search/repositories?q=${encodeURIComponent(query)}&sort=stars&order=desc&per_page=${Math.ceil(limit / topTopics.length)}`;

        const headers: Record<string, string> = {
          'Accept': 'application/vnd.github.v3+json',
          'User-Agent': 'Bloom-Identity-Skill',
        };

        if (this.apiToken) {
          headers['Authorization'] = `token ${this.apiToken}`;
        }

        const response = await fetch(url, { headers });

        if (!response.ok) {
          console.warn(`⚠️  GitHub API returned ${response.status} for topic: ${topic}`);
          continue;
        }

        const data: GitHubSearchResponse = await response.json();

        // Add unique repos
        for (const repo of data.items) {
          if (!seenRepos.has(repo.full_name)) {
            seenRepos.add(repo.full_name);
            repos.push(repo);
          }
        }

      } catch (error) {
        console.warn(`⚠️  Failed to search topic: ${topic}`, error);
      }

      // Small delay to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 300));
    }

    return repos;
  }

  /**
   * Score and rank repositories based on relevance
   */
  private scoreRepositories(repos: GitHubRepo[], identity: IdentityData): GitHubRecommendation[] {
    const recommendations: GitHubRecommendation[] = [];

    for (const repo of repos) {
      let matchScore = 0;

      // 1. Topic match (0-40 points)
      const userTopics = this.buildSearchTopics(identity);
      const topicMatches = repo.topics.filter(t => userTopics.includes(t)).length;
      matchScore += Math.min(topicMatches * 10, 40);

      // 2. Popularity score (0-30 points)
      // Logarithmic scale: 100 stars = 10pts, 1000 stars = 20pts, 10000 stars = 30pts
      const starScore = Math.min(Math.log10(repo.stargazers_count + 1) * 10, 30);
      matchScore += starScore;

      // 3. Recent activity (0-15 points)
      const daysSinceUpdate = Math.floor(
        (Date.now() - new Date(repo.updated_at).getTime()) / (1000 * 60 * 60 * 24)
      );
      const activityScore = Math.max(15 - daysSinceUpdate / 30, 0);
      matchScore += activityScore;

      // 4. Description quality (0-15 points)
      if (repo.description) {
        const descLength = repo.description.length;
        const qualityScore = Math.min(descLength / 10, 15);
        matchScore += qualityScore;
      }

      // Normalize to 0-100
      matchScore = Math.min(Math.round(matchScore), 100);

      // Only include repos with decent match score
      if (matchScore >= 30) {
        recommendations.push({
          skillId: repo.full_name.replace('/', '-'),
          skillName: repo.name,
          description: repo.description || 'No description available',
          url: repo.html_url,
          categories: repo.topics.length > 0 ? repo.topics : ['General'],
          matchScore,
          creator: repo.owner.login,
          source: 'GitHub',
          stars: repo.stargazers_count,
          language: repo.language || undefined,
        });
      }
    }

    // Sort by match score
    return recommendations.sort((a, b) => b.matchScore - a.matchScore);
  }
}
