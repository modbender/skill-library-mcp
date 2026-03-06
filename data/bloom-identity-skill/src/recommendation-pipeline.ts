/**
 * Recommendation Pipeline (Standalone)
 *
 * Extracted from BloomIdentitySkillV2 so the backend can refresh
 * recommendations independently via Bull queue jobs.
 *
 * Sources: ClawHub registry (verified via GitHub cross-check) + Claude Code awesome-lists.
 * Deduplicates by URL, groups by user categories, applies personality scoring.
 */

import { ClaudeCodeClient, createClaudeCodeClient } from './integrations/claude-code-client';
import { ClawHubClient, createClawHubClient } from './integrations/clawhub-client';
import { PersonalityType } from './types/personality';
import {
  CANONICAL_CATEGORIES,
  CATEGORY_KEYWORDS,
  DEFAULT_FALLBACK_CATEGORIES,
  containsBlockedKeyword,
} from './types/categories';

export interface RefreshIdentityInput {
  mainCategories: string[];
  subCategories: string[];
  personalityType: string;
  dimensions?: {
    conviction: number;
    intuition: number;
    contribution: number;
  };
  tasteSpectrums?: {
    learning: number;
    decision: number;
    novelty: number;
    risk: number;
  };
  feedback?: {
    categoryWeights?: Record<string, number>;
    excludeSkillIds?: string[];
  };
}

export interface SkillRecommendation {
  skillId: string;
  skillName: string;
  description: string;
  url: string;
  categories: string[];
  matchScore: number;
  reason?: string;
  creator?: string;
  creatorUserId?: number | string;
  source?: 'ClaudeCode' | 'ClawHub';
  stars?: number;
  downloads?: number;
  language?: string;
  categoryGroup?: string;
}

// ─── Quality & language helpers ─────────────────────────────────────────

/**
 * Reject text that is likely non-English (e.g. Chinese descriptions from GitHub/ClawHub).
 * Heuristic: if more than 30% of characters are non-ASCII, consider it non-English.
 */
function isLikelyEnglish(text: string): boolean {
  if (!text || text.length === 0) return true;
  let nonAscii = 0;
  for (let i = 0; i < text.length; i++) {
    if (text.charCodeAt(i) > 127) nonAscii++;
  }
  return nonAscii / text.length <= 0.3;
}

/**
 * Normalize free-form category strings to canonical categories.
 * "DeFi" → Crypto, "Web3" → Crypto, "Blockchain" → Crypto, etc.
 * Deduplicates the result. Falls back to DEFAULT_FALLBACK_CATEGORIES if nothing matches.
 */
function normalizeToCanonical(categories: string[]): string[] {
  const matched = new Set<string>();

  for (const cat of categories) {
    const lower = cat.toLowerCase().trim();

    // Direct match against canonical list (case-insensitive)
    const direct = CANONICAL_CATEGORIES.find(c => c.toLowerCase() === lower);
    if (direct) {
      matched.add(direct);
      continue;
    }

    // Keyword match — scan each canonical category's keyword list
    for (const [canonical, keywords] of Object.entries(CATEGORY_KEYWORDS)) {
      if (keywords.some(kw => lower.includes(kw) || kw.includes(lower))) {
        matched.add(canonical);
        break; // one match per input category is enough
      }
    }
  }

  if (matched.size === 0) {
    return [...DEFAULT_FALLBACK_CATEGORIES];
  }

  return Array.from(matched);
}

// ─── GitHub cross-check (verify skill exists in openclaw/skills monorepo) ───

const GITHUB_SKILLS_REPO = 'openclaw/skills';

/**
 * Verify a ClawHub skill exists in the openclaw/skills GitHub monorepo.
 * Path: skills/{owner.toLowerCase()}/{slug}/SKILL.md
 * Uses unauthenticated GitHub contents API (60 req/hr, enough for 20 checks).
 */
async function verifySkillOnGitHub(owner: string, slug: string): Promise<boolean> {
  try {
    const path = `skills/${owner.toLowerCase()}/${slug}/SKILL.md`;
    const url = `https://api.github.com/repos/${GITHUB_SKILLS_REPO}/contents/${path}`;
    const response = await fetch(url, {
      method: 'HEAD',
      headers: {
        'User-Agent': 'Bloom-Identity-Skill',
        'Accept': 'application/vnd.github.v3+json',
      },
    });
    return response.status === 200;
  } catch {
    // Network error — treat as unverified
    return false;
  }
}

// ─── Main pipeline ──────────────────────────────────────────────────────

/**
 * Run the full recommendation pipeline: fetch, score, deduplicate, group.
 * Stateless — creates fresh client instances each call.
 */
export async function refreshRecommendations(
  identity: RefreshIdentityInput,
): Promise<SkillRecommendation[]> {
  const claudeCodeClient = createClaudeCodeClient();
  const clawHubClient = createClawHubClient();

  // Normalize categories before anything else (Fix 2)
  const normalizedCategories = normalizeToCanonical(identity.mainCategories);
  const normalizedIdentity: RefreshIdentityInput = {
    ...identity,
    mainCategories: normalizedCategories,
  };

  console.log(
    `[recommendation-pipeline] Searching for ${identity.personalityType}...` +
    ` (categories: ${identity.mainCategories.join(', ')} → ${normalizedCategories.join(', ')})`,
  );

  try {
    // Search both sources in parallel
    const [claudeCodeSkills, clawHubSkills] = await Promise.all([
      getClaudeCodeRecommendations(claudeCodeClient, normalizedIdentity),
      getClawHubRecommendations(clawHubClient, normalizedIdentity).catch(err => {
        console.error('[recommendation-pipeline] ClawHub search failed:', err);
        return [] as SkillRecommendation[];
      }),
    ]);

    // Merge and deduplicate by URL — keep highest-scoring entry
    const all = [...claudeCodeSkills, ...clawHubSkills];
    const byUrl = new Map<string, SkillRecommendation>();
    for (const rec of all) {
      const key = rec.url.toLowerCase().replace(/\/+$/, '');
      const existing = byUrl.get(key);
      if (!existing || rec.matchScore > existing.matchScore) {
        byUrl.set(key, rec);
      }
    }
    let deduplicated = Array.from(byUrl.values());

    // Apply feedback filters: exclude dismissed skills
    if (identity.feedback?.excludeSkillIds?.length) {
      const excludeSet = new Set(identity.feedback.excludeSkillIds.map(id => id.toLowerCase()));
      const before = deduplicated.length;
      deduplicated = deduplicated.filter(s => !excludeSet.has(s.skillId.toLowerCase()));
      if (before !== deduplicated.length) {
        console.log(`[recommendation-pipeline] Excluded ${before - deduplicated.length} dismissed skills`);
      }
    }

    // Apply feedback category weights as score multiplier
    if (identity.feedback?.categoryWeights) {
      const weights = identity.feedback.categoryWeights;
      for (const skill of deduplicated) {
        for (const cat of skill.categories) {
          const w = weights[cat];
          if (w !== undefined && w !== 1.0) {
            skill.matchScore = Math.min(Math.round(skill.matchScore * w), 100);
            break; // Apply best matching category weight once
          }
        }
      }
    }

    // Group by normalized categories (3-7 per category)
    const grouped = groupByCategory(deduplicated, normalizedCategories);

    console.log(
      `[recommendation-pipeline] ${claudeCodeSkills.length} Claude Code + ${clawHubSkills.length} ClawHub => ${grouped.length} grouped`,
    );

    return grouped;
  } catch (error) {
    console.error('[recommendation-pipeline] Failed:', error);
    return [];
  }
}

// ─── ClawHub recommendations (Fix 1: replaces GitHub) ───────────────────

async function getClawHubRecommendations(
  client: ClawHubClient,
  identity: RefreshIdentityInput,
): Promise<SkillRecommendation[]> {
  try {
    // 1. Search ClawHub for skills matching user categories
    const rawSkills = await client.getRecommendations({
      mainCategories: identity.mainCategories,
      subCategories: identity.subCategories,
      limit: 20,
    });

    if (rawSkills.length === 0) return [];

    // 2. For each result, fetch details first (search results don't include owner)
    //    then GitHub cross-check with the owner from details
    const verifiedSkills = await Promise.all(
      rawSkills.map(async (skill): Promise<SkillRecommendation | null> => {
        // Step A: Fetch full details (includes owner, stats, moderation)
        const details = await client.getSkillDetails(skill.slug).catch(() => null);
        if (!details) return null;

        // Step B: GitHub cross-check using owner from details
        const owner = details.creator;
        if (!owner) {
          console.log(`[clawhub] Skipped ${skill.slug}: no owner`);
          return null;
        }

        const isVerified = await verifySkillOnGitHub(owner, skill.slug);
        if (!isVerified) {
          console.log(`[clawhub] Skipped ${skill.slug}: GitHub cross-check failed (owner: ${owner})`);
          return null;
        }

        // Quality gates

        // Traction — read early, used in moderation gate below
        const downloads = details.stats?.downloads ?? 0;

        // Moderation flags: always block malware; suspicious is OK if high traction
        if (details.moderation?.isMalwareBlocked === true) {
          console.log(`[clawhub] Skipped ${skill.slug}: malware blocked`);
          return null;
        }
        if (details.moderation?.isSuspicious === true && downloads <= 200) {
          console.log(`[clawhub] Skipped ${skill.slug}: suspicious + low downloads (${downloads})`);
          return null;
        }

        const description = details.description || '';

        // Description quality
        if (description.length < 20) return null;

        // English-only filter (Fix 3)
        if (!isLikelyEnglish(description)) {
          console.log(`[clawhub] Skipped ${skill.slug}: non-English description`);
          return null;
        }

        // Blocked keywords
        if (containsBlockedKeyword(`${details.name} ${description}`)) {
          console.log(`[clawhub] Skipped ${skill.slug}: blocked keyword`);
          return null;
        }

        // Traction gate: minimum 20 downloads
        if (downloads < 20) return null;

        // Relevance gate: similarity score minimum
        if (skill.similarityScore < 0.5) return null;

        // Map to SkillRecommendation
        const normalizedScore = Math.min(Math.round((skill.similarityScore / 4) * 100), 100);

        const searchText = `${details.name} ${description} ${(details.categories || []).join(' ')}`.toLowerCase();
        const matchedCategory = [...identity.mainCategories, ...identity.subCategories]
          .find(c => searchText.includes(c.toLowerCase()));

        const { boost, matchedKeywords } = calculatePersonalityBoost(
          { description, categories: details.categories || [] },
          identity,
        );

        const downloadsDisplay = downloads >= 1000
          ? `${(downloads / 1000).toFixed(1)}k`
          : `${downloads}`;

        const typeName = identity.personalityType.replace(/^The /, '');
        const reason = matchedCategory && matchedKeywords.length > 0
          ? `Because you're into ${matchedCategory} — ${downloadsDisplay} downloads`
          : matchedCategory
            ? `Because you're into ${matchedCategory} — ${downloadsDisplay} downloads`
            : matchedKeywords.length > 0
              ? `Fits your ${typeName} style — ${downloadsDisplay} downloads`
              : `Fits your ${typeName} profile — ${downloadsDisplay} downloads`;

        return {
          skillId: skill.slug,
          skillName: details.name || skill.name,
          description,
          url: `https://clawhub.ai/skills/${skill.slug}`,
          categories: details.categories || ['General'],
          matchScore: Math.min(normalizedScore + boost, 100),
          reason,
          creator: owner,
          creatorUserId: details.creatorUserId,
          source: 'ClawHub' as const,
          downloads,
        };
      }),
    );

    return verifiedSkills.filter((s): s is SkillRecommendation => s !== null);
  } catch (error) {
    console.error('[recommendation-pipeline] ClawHub recommendations failed:', error);
    return [];
  }
}

// ─── Claude Code recommendations ────────────────────────────────────────

async function getClaudeCodeRecommendations(
  client: ClaudeCodeClient,
  identity: RefreshIdentityInput,
): Promise<SkillRecommendation[]> {
  try {
    const claudeCodeSkills = await client.getRecommendations({
      mainCategories: identity.mainCategories,
      subCategories: identity.subCategories,
      limit: 20,
    });

    return claudeCodeSkills
      .filter(skill => {
        // English-only filter (Fix 3)
        if (!isLikelyEnglish(skill.description)) {
          console.log(`[claude-code] Skipped ${skill.skillName}: non-English description`);
          return false;
        }
        return true;
      })
      .map(skill => {
        const CLAUDE_CODE_SCORE_CEILING = 30;
        const rawScore = skill.matchScore || 0;
        const normalizedScore = Math.min(Math.round((rawScore / CLAUDE_CODE_SCORE_CEILING) * 100), 100);

        const searchText = `${skill.skillName} ${skill.description} ${skill.category || ''}`.toLowerCase();
        const matchedCategory = [...identity.mainCategories, ...identity.subCategories]
          .find(c => searchText.includes(c.toLowerCase()));

        const { boost, matchedKeywords } = calculatePersonalityBoost(
          { description: skill.description, categories: skill.category ? [skill.category] : [] },
          identity,
        );

        const typeName = identity.personalityType.replace(/^The /, '');
        const reason = matchedCategory && matchedKeywords.length > 0
          ? `Because you're into ${matchedCategory} — fits your ${typeName} style`
          : matchedCategory
            ? `Because you're into ${matchedCategory}`
            : matchedKeywords.length > 0
              ? `Fits your ${typeName} style`
              : `Fits your ${typeName} profile`;

        return {
          skillId: skill.url,
          skillName: skill.skillName,
          matchScore: Math.min(normalizedScore + boost, 100),
          reason,
          description: skill.description,
          url: skill.url,
          categories: skill.category ? [skill.category] : ['General'],
          creator: skill.creator,
          source: 'ClaudeCode' as const,
        };
      });
  } catch (error) {
    console.error('[recommendation-pipeline] Claude Code search failed:', error);
    return [];
  }
}

// ─── Category grouping ──────────────────────────────────────────────────

function groupByCategory(
  skills: SkillRecommendation[],
  mainCategories: string[],
): SkillRecommendation[] {
  const MIN_PER_CATEGORY = 3;
  const MAX_PER_CATEGORY = 7;
  const SCORE_THRESHOLD = 25;

  const buckets = new Map<string, SkillRecommendation[]>();
  for (const cat of mainCategories) {
    buckets.set(cat, []);
  }

  for (const skill of skills) {
    const bestCategory = findBestCategory(skill, mainCategories);
    if (bestCategory) {
      buckets.get(bestCategory)!.push({ ...skill, categoryGroup: bestCategory });
    }
  }

  const result: SkillRecommendation[] = [];
  for (const cat of mainCategories) {
    const bucket = buckets.get(cat)!;
    bucket.sort((a, b) => b.matchScore - a.matchScore);

    let count = bucket.filter(s => s.matchScore >= SCORE_THRESHOLD).length;
    count = Math.max(Math.min(count, MAX_PER_CATEGORY), Math.min(MIN_PER_CATEGORY, bucket.length));

    result.push(...bucket.slice(0, count));
  }

  return result;
}

function findBestCategory(skill: SkillRecommendation, mainCategories: string[]): string | null {
  const skillText = [
    ...skill.categories,
    skill.description,
    skill.skillName,
  ].join(' ').toLowerCase();

  let bestCat: string | null = null;
  let bestScore = 0;

  for (const cat of mainCategories) {
    let score = 0;

    if (skill.categories.some(c => c.toLowerCase() === cat.toLowerCase())) {
      score += 10;
    }

    const keywords = CATEGORY_KEYWORDS[cat as keyof typeof CATEGORY_KEYWORDS] || [];
    for (const kw of keywords) {
      if (skillText.includes(kw)) {
        score += 2;
      }
    }

    if (score > bestScore) {
      bestScore = score;
      bestCat = cat;
    }
  }

  if (bestScore === 0 && mainCategories.length > 0) {
    bestCat = mainCategories[0];
  }

  return bestCat;
}

// ─── Personality scoring ────────────────────────────────────────────────

function calculatePersonalityBoost(
  skill: { description: string; categories?: string[]; stars?: number },
  identity: RefreshIdentityInput,
): { boost: number; matchedKeywords: string[] } {
  const personalityKeywords = getPersonalityKeywords(identity.personalityType as PersonalityType);
  const descLower = skill.description.toLowerCase();
  const catText = (skill.categories || []).join(' ').toLowerCase();
  const searchText = `${descLower} ${catText}`;

  const matchedKeywords = personalityKeywords.filter(k => searchText.includes(k));
  let keywordBoost = 0;
  for (let i = 0; i < matchedKeywords.length; i++) {
    if (i < 3) keywordBoost += 3;
    else if (i < 6) keywordBoost += 2;
    else keywordBoost += 1;
  }
  keywordBoost = Math.min(keywordBoost, 15);

  let dimensionBoost = 0;
  const dims = identity.dimensions;
  if (dims) {
    if (dims.conviction > 65) {
      const hasExactCategory = (skill.categories || []).some(c => {
        const lower = c.toLowerCase();
        return identity.mainCategories.some(mc => mc.toLowerCase() === lower) ||
               identity.subCategories.some(sc => sc.toLowerCase() === lower);
      });
      if (hasExactCategory) dimensionBoost += 8;
    }

    if (dims.conviction < 35) {
      const hasNovelCategory = (skill.categories || []).some(c => {
        const lower = c.toLowerCase();
        return !identity.mainCategories.some(mc => mc.toLowerCase() === lower) &&
               !identity.subCategories.some(sc => sc.toLowerCase() === lower);
      });
      if (hasNovelCategory) dimensionBoost += 5;
    }

    if (dims.intuition > 65) {
      const earlyKeywords = /\b(early|beta|alpha|experimental)\b/i;
      const isEarlyStage = (skill.stars != null && skill.stars < 500) ||
        earlyKeywords.test(searchText);
      if (isEarlyStage) dimensionBoost += 6;
    }

    if (dims.intuition < 35) {
      const isEstablished = skill.stars != null && skill.stars > 5000;
      if (isEstablished) dimensionBoost += 6;
    }

    if (dims.contribution > 55) {
      const isCommunity = searchText.includes('community') || searchText.includes('collaborat') ||
        searchText.includes('contribut') || searchText.includes('open-source') || searchText.includes('governance');
      if (isCommunity) dimensionBoost += 6;
    }

    dimensionBoost = Math.min(dimensionBoost, 15);
  }

  // Taste spectrum boosts
  let tasteBoost = 0;
  const taste = identity.tasteSpectrums;
  if (taste) {
    // Learning: try-first (< 40) → tools, templates, CLIs, starter kits
    if (taste.learning < 40) {
      if (/\b(tool|template|cli|starter|kit|scaffold|boilerplate)\b/i.test(searchText)) {
        tasteBoost += 6;
      }
    }
    // Learning: study-first (> 60) → tutorials, guides, courses, documentation
    if (taste.learning > 60) {
      if (/\b(tutorial|guide|course|documentation|docs|learn|education)\b/i.test(searchText)) {
        tasteBoost += 6;
      }
    }
    // Decision: gut (< 40) → tools, templates, quick-start
    if (taste.decision < 40) {
      if (/\b(tool|template|quick[- ]?start|scaffold|instant|rapid)\b/i.test(searchText)) {
        tasteBoost += 5;
      }
    }
    // Decision: deliberate (> 60) → docs, guides, comparisons
    if (taste.decision > 60) {
      if (/\b(documentation|docs|guide|comparison|benchmark|evaluat|review)\b/i.test(searchText)) {
        tasteBoost += 5;
      }
    }
    // Novelty: early-adopter (< 40) → beta, new, cutting-edge
    if (taste.novelty < 40) {
      if (/\b(beta|new|cutting[- ]?edge|alpha|experimental|preview|early[- ]?access)\b/i.test(searchText)) {
        tasteBoost += 5;
      }
    }
    // Novelty: wait-and-see (> 60) → established, proven, mature
    if (taste.novelty > 60) {
      if (/\b(established|proven|mature|stable|reliable|battle[- ]?tested|mainstream)\b/i.test(searchText)) {
        tasteBoost += 5;
      }
    }
    // Risk: bold (< 40) → high-risk, moonshot, experimental
    if (taste.risk < 40) {
      if (/\b(moonshot|experimental|high[- ]?risk|ambitious|disrupt|breakthrough|radical)\b/i.test(searchText)) {
        tasteBoost += 4;
      }
    }
    // Risk: cautious (> 60) → stable, established, safe
    if (taste.risk > 60) {
      if (/\b(stable|established|safe|reliable|secure|conservative|trusted)\b/i.test(searchText)) {
        tasteBoost += 4;
      }
    }
    tasteBoost = Math.min(tasteBoost, 15);
  }

  return { boost: keywordBoost + dimensionBoost + tasteBoost, matchedKeywords };
}

function getPersonalityKeywords(type: PersonalityType): string[] {
  const keywordMap: Record<string, string[]> = {
    [PersonalityType.THE_VISIONARY]: [
      'innovative', 'early-stage', 'vision', 'future', 'paradigm',
      'pioneer', 'disrupt', 'bold', 'ambitious', 'frontier', 'emerging', 'breakthrough',
    ],
    [PersonalityType.THE_EXPLORER]: [
      'diverse', 'experimental', 'discovery', 'research', 'explore',
      'curiosity', 'variety', 'breadth', 'survey', 'sandbox', 'prototype', 'tinker',
    ],
    [PersonalityType.THE_CULTIVATOR]: [
      'community', 'social', 'collaborate', 'nurture', 'build',
      'ecosystem', 'mentor', 'contribute', 'share', 'governance', 'collective', 'stewardship',
    ],
    [PersonalityType.THE_OPTIMIZER]: [
      'efficiency', 'data-driven', 'optimize', 'systematic', 'analytics',
      'performance', 'metrics', 'roi', 'benchmark', 'refine', 'precision', 'reliable',
    ],
    [PersonalityType.THE_INNOVATOR]: [
      'technology', 'ai', 'automation', 'creative', 'cutting-edge',
      'novel', 'hybrid', 'synthesis', 'interdisciplinary', 'integrate', 'cross-domain', 'generative',
    ],
  };
  return keywordMap[type] || [];
}
