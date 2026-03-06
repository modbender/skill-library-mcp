/**
 * ClawHub Client
 *
 * Integrates with ClawHub registry to search and recommend OpenClaw skills
 *
 * References:
 * - ClawHub: https://clawhub.ai/
 * - API Documentation: https://docs.openclaw.ai/tools/clawhub
 * - HTTP API: https://clawhub.ai/api/v1/
 */

const CLAWHUB_API_BASE = 'https://clawhub.ai/api/v1';

export interface ClawHubSkill {
  slug: string;
  version: string;
  name: string;
  description: string;
  similarityScore: number;
  url: string;
  categories?: string[];
  creator?: string;
  creatorUserId?: number;
}

export interface ClawHubSearchOptions {
  query: string;
  limit?: number;
}

/**
 * ClawHub Client
 *
 * Searches OpenClaw skills using ClawHub registry
 */
export class ClawHubClient {
  /**
   * Search for skills using ClawHub HTTP API
   *
   * Uses vector search (OpenAI embeddings) for semantic matching
   */
  async searchSkills(options: ClawHubSearchOptions): Promise<ClawHubSkill[]> {
    const { query, limit = 10 } = options;

    console.log(`🔍 Searching ClawHub for: "${query}"...`);

    try {
      // Call ClawHub search API
      const url = `${CLAWHUB_API_BASE}/search?q=${encodeURIComponent(query)}&limit=${limit}`;
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      // Parse API response
      const skills = this.parseApiResponse(data);
      console.log(`✅ Found ${skills.length} skills`);

      return skills;
    } catch (error) {
      console.error('❌ ClawHub search failed:', error);
      return [];
    }
  }

  /**
   * Search multiple categories and merge results (parallel execution for speed)
   */
  async searchMultipleCategories(categories: string[], limitPerCategory: number = 3): Promise<ClawHubSkill[]> {
    console.log(`🔍 Searching ${categories.length} categories in parallel...`);

    // Execute all searches in parallel for better performance
    const searchPromises = categories.map(category =>
      this.searchSkills({
        query: category,
        limit: limitPerCategory,
      })
    );

    const resultsArrays = await Promise.all(searchPromises);

    // Flatten and deduplicate by slug
    const allResults: ClawHubSkill[] = [];
    const seenSlugs = new Set<string>();

    for (const results of resultsArrays) {
      for (const skill of results) {
        if (!seenSlugs.has(skill.slug)) {
          seenSlugs.add(skill.slug);
          allResults.push(skill);
        }
      }
    }

    // Sort by similarity score (descending)
    return allResults.sort((a, b) => b.similarityScore - a.similarityScore);
  }

  /**
   * Get skill details using HTTP API
   */
  async getSkillDetails(slug: string): Promise<ClawHubSkill | null> {
    try {
      const url = `${CLAWHUB_API_BASE}/skills/${encodeURIComponent(slug)}`;
      const response = await fetch(url);

      if (!response.ok) {
        if (response.status === 404) {
          return null;
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return this.parseSkillObject(data);
    } catch (error) {
      console.error(`❌ Failed to get skill details for ${slug}:`, error);
      return null;
    }
  }

  /**
   * Parse ClawHub API search response
   *
   * Response format:
   * { results: [{ slug, version, displayName, summary, score, ... }] }
   */
  private parseApiResponse(data: any): ClawHubSkill[] {
    if (!data || !Array.isArray(data.results)) {
      return [];
    }

    return data.results.map((item: any) => this.parseSkillObject(item));
  }

  /**
   * Parse a single skill object from API
   */
  private parseSkillObject(item: any): ClawHubSkill {
    const slug = item.slug || '';
    const version = item.version || item.latestVersion?.version || '1.0.0';
    const name = item.displayName || item.name || this.extractName(item.summary || '');
    const description = item.summary || item.description || '';
    const similarityScore = item.score ?? 0;
    const tags = item.tags || [];

    return {
      slug,
      version: version.startsWith('v') ? version : `v${version}`,
      name,
      description,
      similarityScore,
      url: `https://clawhub.ai/skills/${slug}`,
      categories: this.inferCategories(slug, `${description} ${tags.join(' ')}`),
      creator: item.owner?.username,
      creatorUserId: item.owner?.id,
    };
  }

  /**
   * Extract skill name from description
   * (First part before dash or full description if no dash)
   */
  private extractName(description: string): string {
    const parts = description.split('-');
    return parts[0].trim();
  }

  /**
   * Infer categories from slug and description
   */
  private inferCategories(slug: string, description: string): string[] {
    const categories: string[] = [];
    const text = `${slug} ${description}`.toLowerCase();

    // Category keywords mapping
    const categoryKeywords: Record<string, string[]> = {
      'Crypto': ['crypto', 'blockchain', 'defi', 'web3', 'token', 'wallet', 'nft', 'dao'],
      'AI Tools': ['ai', 'gpt', 'llm', 'machine learning', 'ml', 'chatbot', 'openai'],
      'Productivity': ['productivity', 'workflow', 'automation', 'task', 'calendar', 'note'],
      'Marketing': ['marketing', 'seo', 'analytics', 'growth', 'email', 'social'],
      'Developer Tools': ['dev', 'developer', 'code', 'git', 'github', 'api', 'sdk'],
      'Data': ['data', 'database', 'sql', 'analytics', 'visualization'],
      'Trading': ['trading', 'exchange', 'binance', 'stock', 'market'],
      'Content': ['content', 'writing', 'blog', 'article', 'editor'],
    };

    for (const [category, keywords] of Object.entries(categoryKeywords)) {
      if (keywords.some(keyword => text.includes(keyword))) {
        categories.push(category);
      }
    }

    return categories.length > 0 ? categories : ['General'];
  }

  /**
   * Get recommended skills based on personality and interests
   */
  async getRecommendations(options: {
    mainCategories: string[];
    subCategories: string[];
    limit?: number;
  }): Promise<ClawHubSkill[]> {
    const { mainCategories, subCategories, limit = 10 } = options;

    console.log(`🎯 Getting recommendations for categories: ${mainCategories.join(', ')}`);

    // Search main categories (higher priority)
    const mainResults = await this.searchMultipleCategories(mainCategories, 4);

    // Search sub-categories if we need more
    let allResults = mainResults;
    if (allResults.length < limit && subCategories.length > 0) {
      const subResults = await this.searchMultipleCategories(subCategories.slice(0, 3), 2);

      // Merge and deduplicate
      const seenSlugs = new Set(mainResults.map(s => s.slug));
      const uniqueSubResults = subResults.filter(s => !seenSlugs.has(s.slug));

      allResults = [...mainResults, ...uniqueSubResults];
    }

    // Return top N by similarity score
    return allResults
      .sort((a, b) => b.similarityScore - a.similarityScore)
      .slice(0, limit);
  }
}

/**
 * Create a ClawHub client instance
 */
export function createClawHubClient(): ClawHubClient {
  return new ClawHubClient();
}
