/**
 * Claude Code Client
 *
 * Aggregates official and community Claude Code skills from GitHub repositories
 *
 * Data Sources:
 * - anthropics/skills (Official Anthropic skills)
 * - travisvn/awesome-claude-skills (Community curated)
 * - VoltAgent/awesome-agent-skills (200+ cross-compatible skills)
 * - hesreallyhim/awesome-claude-code (Broader ecosystem)
 */

import { containsBlockedKeyword } from '../types/categories';

const SKILL_REPOS = [
  {
    owner: 'anthropics',
    repo: 'skills',
    url: 'https://github.com/anthropics/skills',
    type: 'official' as const,
  },
  {
    owner: 'travisvn',
    repo: 'awesome-claude-skills',
    url: 'https://github.com/travisvn/awesome-claude-skills',
    type: 'community' as const,
  },
  {
    owner: 'VoltAgent',
    repo: 'awesome-agent-skills',
    url: 'https://github.com/VoltAgent/awesome-agent-skills',
    type: 'community' as const,
  },
  {
    owner: 'hesreallyhim',
    repo: 'awesome-claude-code',
    url: 'https://github.com/hesreallyhim/awesome-claude-code',
    type: 'community' as const,
  },
  {
    owner: 'jqueryscript',
    repo: 'awesome-claude-code',
    url: 'https://github.com/jqueryscript/awesome-claude-code',
    type: 'community' as const,
  },
  {
    owner: 'tonysurfly',
    repo: 'awesome-claude',
    url: 'https://github.com/tonysurfly/awesome-claude',
    type: 'community' as const,
  },
  {
    owner: 'VoltAgent',
    repo: 'awesome-openclaw-skills',
    url: 'https://github.com/VoltAgent/awesome-openclaw-skills',
    type: 'community' as const,
  },
];

export interface ClaudeCodeSkill {
  skillName: string;
  description: string;
  url: string;
  category?: string;
  creator?: string;
  type: 'official' | 'community';
  source: 'ClaudeCode';
  matchScore?: number; // Raw keyword match score from matchSkills()
}

export interface ClaudeCodeSearchOptions {
  mainCategories: string[];
  subCategories: string[];
  limit?: number;
}

/**
 * Claude Code Client
 *
 * Fetches and parses Claude Code skills from GitHub repositories
 */
export class ClaudeCodeClient {
  private cache: Map<string, ClaudeCodeSkill[]> = new Map();
  private cacheExpiry: number = 1000 * 60 * 60; // 1 hour

  /**
   * Get recommendations based on user's categories
   */
  async getRecommendations(options: ClaudeCodeSearchOptions): Promise<ClaudeCodeSkill[]> {
    const { mainCategories, subCategories, limit = 10 } = options;

    console.log(`🔍 Searching Claude Code skills for categories: ${mainCategories.join(', ')}`);

    try {
      // Fetch all skills from repos
      const allSkills = await this.fetchAllSkills();

      // Match skills to user's categories
      const matchedSkills = this.matchSkills(allSkills, mainCategories, subCategories);

      // Limit results
      const limitedSkills = matchedSkills.slice(0, limit);

      console.log(`✅ Found ${limitedSkills.length} Claude Code skills`);
      return limitedSkills;
    } catch (error) {
      console.error('❌ Claude Code search failed:', error);
      return [];
    }
  }

  /**
   * Fetch skills from all GitHub repositories
   */
  private async fetchAllSkills(): Promise<ClaudeCodeSkill[]> {
    const cacheKey = 'all_skills';
    const cached = this.cache.get(cacheKey);

    if (cached) {
      console.log('📦 Using cached Claude Code skills');
      return cached;
    }

    console.log('🌐 Fetching Claude Code skills from GitHub...');

    // Fetch from all repos in parallel
    const skillsPromises = SKILL_REPOS.map(repo => this.fetchRepoSkills(repo));
    const skillsArrays = await Promise.all(skillsPromises);

    // Flatten and deduplicate
    const allSkills = skillsArrays.flat();
    const uniqueSkills = this.deduplicateSkills(allSkills);

    // Cache results
    this.cache.set(cacheKey, uniqueSkills);
    setTimeout(() => this.cache.delete(cacheKey), this.cacheExpiry);

    console.log(`✅ Fetched ${uniqueSkills.length} unique skills from ${SKILL_REPOS.length} repos`);
    return uniqueSkills;
  }

  /**
   * Fetch skills from a single GitHub repository
   */
  private async fetchRepoSkills(repo: typeof SKILL_REPOS[0]): Promise<ClaudeCodeSkill[]> {
    try {
      // Fetch README from GitHub API
      const url = `https://api.github.com/repos/${repo.owner}/${repo.repo}/readme`;
      const response = await fetch(url, {
        headers: {
          'Accept': 'application/vnd.github.v3.raw',
          'User-Agent': 'Bloom-Identity-Skill',
        },
      });

      if (!response.ok) {
        console.warn(`⚠️  Failed to fetch ${repo.owner}/${repo.repo}: ${response.status}`);
        return [];
      }

      const markdown = await response.text();

      // Parse markdown to extract skills
      const skills = this.parseMarkdown(markdown, repo);

      console.log(`✅ Parsed ${skills.length} skills from ${repo.owner}/${repo.repo}`);
      return skills;
    } catch (error) {
      console.error(`❌ Error fetching ${repo.owner}/${repo.repo}:`, error);
      return [];
    }
  }

  /**
   * Parse markdown README to extract skills
   *
   * Common patterns:
   * - [Skill Name](url) - Description
   * - **[Skill Name](url)** - Description
   * - ### Category\n- [Skill Name](url) - Description
   */
  private parseMarkdown(markdown: string, repo: typeof SKILL_REPOS[0]): ClaudeCodeSkill[] {
    const skills: ClaudeCodeSkill[] = [];
    const lines = markdown.split('\n');

    let currentCategory = 'General';

    for (const line of lines) {
      // Detect category headers (### Category or ## Category)
      const categoryMatch = line.match(/^#{2,3}\s+(.+)$/);
      if (categoryMatch) {
        currentCategory = categoryMatch[1].trim();
        continue;
      }

      // Match skill links: - [Skill Name](url) - Description
      // Also matches: * [Skill Name](url) - Description
      const skillMatch = line.match(/^[\s-*]+\[([^\]]+)\]\(([^\)]+)\)\s*[-–—]\s*(.+)$/);
      if (skillMatch) {
        const [, skillName, url, description] = skillMatch;

        skills.push({
          skillName: skillName.trim(),
          description: description.trim(),
          url: url.trim(),
          category: currentCategory,
          creator: repo.owner === 'anthropics' ? 'Anthropic' : undefined,
          type: repo.type,
          source: 'ClaudeCode',
        });
        continue;
      }

      // Alternative pattern: - [Skill Name](url): Description
      const altMatch = line.match(/^[\s-*]+\[([^\]]+)\]\(([^\)]+)\):\s*(.+)$/);
      if (altMatch) {
        const [, skillName, url, description] = altMatch;

        skills.push({
          skillName: skillName.trim(),
          description: description.trim(),
          url: url.trim(),
          category: currentCategory,
          creator: repo.owner === 'anthropics' ? 'Anthropic' : undefined,
          type: repo.type,
          source: 'ClaudeCode',
        });
      }
    }

    return skills;
  }

  /**
   * Match skills to user's categories using keyword matching
   */
  private matchSkills(
    skills: ClaudeCodeSkill[],
    mainCategories: string[],
    subCategories: string[]
  ): ClaudeCodeSkill[] {
    const allCategories = [...mainCategories, ...subCategories].map(c => c.toLowerCase());

    return skills
      .map(skill => {
        let score = 0;

        // Match skill name and description against categories
        const searchText = `${skill.skillName} ${skill.description} ${skill.category || ''}`.toLowerCase();

        for (const category of allCategories) {
          if (searchText.includes(category)) {
            score += 10;
          }

          // Partial matches
          const words = category.split(' ');
          for (const word of words) {
            if (word.length > 3 && searchText.includes(word)) {
              score += 2;
            }
          }
        }

        // Boost official skills
        if (skill.type === 'official') {
          score += 5;
        }

        return { skill, score };
      })
      .filter(({ score }) => score > 0) // Only include matches
      .filter(({ skill }) => {
        // Block skills with malicious keywords in name or description
        const textToCheck = `${skill.skillName} ${skill.description}`;
        if (containsBlockedKeyword(textToCheck)) {
          console.log(`🚫 Blocked skill: ${skill.skillName} (matched blocklist)`);
          return false;
        }
        return true;
      })
      .sort((a, b) => b.score - a.score) // Sort by score
      .map(({ skill, score }) => ({ ...skill, matchScore: score })); // Preserve score
  }

  /**
   * Remove duplicate skills (same URL)
   */
  private deduplicateSkills(skills: ClaudeCodeSkill[]): ClaudeCodeSkill[] {
    const seen = new Set<string>();
    const unique: ClaudeCodeSkill[] = [];

    for (const skill of skills) {
      if (!seen.has(skill.url)) {
        seen.add(skill.url);
        unique.push(skill);
      }
    }

    return unique;
  }
}

/**
 * Create a ClaudeCodeClient instance
 */
export function createClaudeCodeClient(): ClaudeCodeClient {
  return new ClaudeCodeClient();
}
